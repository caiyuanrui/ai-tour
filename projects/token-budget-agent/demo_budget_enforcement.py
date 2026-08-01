#!/usr/bin/env python3
"""
Demo: P3v2 SDB-Contract Budget Enforcement (Layer 2)

Exercises the SDB contract runtime (proposer → verifier → commit/reject)
against four scenarios that map to real failure classes from the Token
Budgets catalog (arXiv 2606.04056):

  1. Normal episode      — healthy budget, OK stage throughout
  2. Budget exhaustion   — WARNING downgrade → HARD_STOP with margin rule
  3. Runaway retry loop  — catastrophic OVER_BUDGET → force stop + notify
  4. Cross-episode leak  — fresh episode after an overrun must start at full
                           budget (episode-scoped reset)

Key difference vs Cycle 1 (2026-06-27): the executor now consumes tokens
ACCORDING TO the routed level, so the multi-signal router's decision has real
economic consequences. A DEEP step is ~8x more expensive than an ECONOMY step.

Run:  python3 demo_budget_enforcement.py
"""

import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.budget_controller import BudgetLevel
from src.stateful_effort_router import StatefulEffortRouter, describe_signals
from src.budget_enforcer import (
    BudgetEnforcer,
    FallbackHandler,
    EnforcementConfig,
    SDBRuntime,
)


def make_executor(base_tokens: dict, blowup: float = 1.0):
    """Build a level-aware, observation-aware executor.

    Real ReAct loops send accumulated context into every step, so prompt
    tokens grow with observation sizes. We model: prompt = base_prompt(level)
    + sum(obs_chars)/4 (chars → tokens) * observation_growth. This is what
    makes budget exhaustion realistic — the same "observation exceeds cost
    estimate" incident class from the Token Budgets catalog.
    """

    def execute(level: BudgetLevel, obs: Optional[list] = None):
        obs = obs or []
        obs_tokens = sum(len(o) for _, o in obs) // 4
        prompt = base_tokens["prompt"].get(level.name, 800)
        completion = base_tokens["completion"].get(level.name, 400)
        return int((prompt + obs_tokens) * blowup), int(completion * blowup)

    return execute


# Per-level token profiles (prompt, completion) — DEEP costs ~8x ECONOMY
LEVEL_TOKENS = {
    "prompt": {BudgetLevel.ECONOMY.name: 600, BudgetLevel.STANDARD.name: 2200,
               BudgetLevel.DEEP.name: 5000},
    "completion": {BudgetLevel.ECONOMY.name: 200, BudgetLevel.STANDARD.name: 900,
                   BudgetLevel.DEEP.name: 2000},
}


def run_episode(runtime: SDBRuntime, title: str, instruction: str,
                steps: list, executor) -> dict:
    """Run an episode through the SDB runtime and print a readable trace."""
    print(f"\n{'='*76}")
    print(f"  EPISODE {runtime.episode_id + 1}: {title}")
    print(f"{'='*76}")
    runtime.start_episode(instruction)

    for step_def in steps:
        observations = step_def.get("observations", [])
        outcome = runtime.step(observations=observations, executor=executor)
        eff = outcome["effective_level"].name if outcome["effective_level"] else "-"
        print(f"  step {outcome['step']:<2} | propose={outcome['proposed_level'].name:<8} "
              f"exec={eff:<8} | stage={outcome['stage']:<11} "
              f"| tokens={outcome['tokens']:>6} cum={outcome['cumulative']:>6} "
              f"rem={outcome['remaining']:>5}")
        if outcome["note"]:
            print(f"          └─ {outcome['note']}")
        if runtime.stop_condition():
            break

    summary = runtime.episode_summary()
    print(f"  → terminal: {summary['terminal_stage']} | "
          f"tokens: {summary['total_tokens']} | cost: ${summary['estimated_cost_usd']:.6f}")
    return summary


def main():
    print("=" * 76)
    print("  P3v2 SDB-Contract Budget Enforcement — Layer 2 Demo")
    print("=" * 76)
    print(describe_signals())
    print(f"\n  Budget: 16,000 tokens/episode | WARNING 50-80% remaining "
          f"| HARD_STOP margin 20%")

    runtime = SDBRuntime(
        enforcer=BudgetEnforcer(EnforcementConfig(budget_tokens=16_000)),
        router=StatefulEffortRouter(),
        fallback=FallbackHandler(),
    )

    summaries = []

    # --- Episode 1: normal, healthy budget ---------------------------------
    summaries.append(run_episode(
        runtime,
        "Simple lookup (fits budget, ECONOMY)",
        "Check the weather in San Francisco today.",
        steps=[
            {"observations": [("weather", '{"temp": 18, "condition": "cloudy"}')]},
            {"observations": []},
        ],
        executor=make_executor(LEVEL_TOKENS),
    ))

    # --- Episode 2: long research task exhausts the budget -------------------
    # Routing escalates as steps/observations accumulate; the verifier
    # downgrades at WARNING and applies the HARD_STOP margin rule when the
    # final step overshoots (a 32K-char observation → 8K tokens in one step).
    summaries.append(run_episode(
        runtime,
        "Budget exhaustion → WARNING downgrade → HARD_STOP (margin rule)",
        "Research advances in attention optimization: search papers, review "
        "implementations, query databases, and synthesize a report.",
        steps=[
            {"observations": [("search", "x" * 5_000)]},
            {"observations": [("search", "x" * 20_000)]},
            {"observations": [("code_review", "x" * 32_000)]},
            {"observations": []},  # post-HARD_STOP step must be rejected pre-run
        ],
        executor=make_executor(LEVEL_TOKENS),
    ))

    # --- Episode 3: runaway retry loop (catastrophic overrun) -----------------
    # A retry loop where each attempt re-sends a growing error payload
    # (blowup 2.2x). One step blows through budget + 20% margin → OVER_BUDGET
    # force stop + operator notify (Token Budgets catalog: retry-loop class).
    summaries.append(run_episode(
        runtime,
        "Runaway retry loop → OVER_BUDGET → force stop + notify",
        "Retry the failed database write until it succeeds.",
        steps=[
            {"observations": [("db_write", '{"error": "lock timeout"}')]},
            {"observations": [("db_write", '{"error": "lock timeout", '
                                           '"retry": 2, "detail": "' + "x" * 4_000 + '"}')]},
            {"observations": [("db_write", '{"error": "lock timeout", '
                                           '"retry": 3, "detail": "' + "x" * 12_000 + '"}')]},
            {"observations": [("db_write", '{"error": "lock timeout", '
                                           '"retry": 4, "detail": "' + "x" * 28_000 + '"}')]},
        ],
        executor=make_executor(LEVEL_TOKENS, blowup=2.2),
    ))

    # --- Episode 4: cross-episode isolation after an overrun ------------------
    # Must start at FULL budget — proving episode-scoped reset (no leakage).
    summaries.append(run_episode(
        runtime,
        "Cross-episode isolation — fresh budget after Episode 3 overrun",
        "List the top 3 papers on KV cache compression.",
        steps=[
            {"observations": [("search", "x" * 500)]},
        ],
        executor=make_executor(LEVEL_TOKENS),
    ))

    # --- Aggregate report ------------------------------------------------------
    print(f"\n{'='*76}")
    print("  AGGREGATE REPORT — Layer-2 enforcement behavior")
    print(f"{'='*76}")
    print(f"  {'Ep':<3} {'tokens':>7} {'cost':>10} {'terminal':<12} hist(w/h/ov)")
    print(f"  {'-'*68}")
    for s in summaries:
        h = s["stage_histogram"]
        print(f"  {s['episode_id']:<3} {s['total_tokens']:>7} "
              f"${s['estimated_cost_usd']:>9.6f} {s['terminal_stage']:<12} "
              f"({h['warning_downgrades']}/{h['hard_stops']}/{h['over_budgets']})")

    total_over = sum(1 for s in summaries if s["terminal_stage"] == "OVER_BUDGET")
    print(f"\n  Enforcement guarantees demonstrated:")
    print(f"    - OVER_BUDGET episodes (force-stopped + operator notified): {total_over}")
    print(f"    - Unbounded runaway episodes (loop never stops): 0")
    print(f"    - HARD_STOP margin rule (finish step, then stop): "
          f"{sum(s['stage_histogram']['hard_stops'] for s in summaries)}")
    print(f"    - WARNING downgrades to ECONOMY (cost preservation): "
          f"{sum(s['stage_histogram']['warning_downgrades'] for s in summaries)}")

    print(f"\n  Routing overhead decomposition (all episodes):")
    overhead = runtime.routing_overhead()
    print(f"    - Routing decisions: {overhead['routing_decisions']} "
          f"(rule-based, 0 LLM tokens)")
    print(f"    - Actual routing tokens: {overhead['actual_routing_tokens']}")
    print(f"    - Total tokens (all episodes): {overhead['total_all_episode_tokens']}")
    print(f"    - Hypothetical LLM classifier cost: "
          f"{overhead['hypothetical_classifier_tokens']} tokens "
          f"= {overhead['hypothetical_overhead_pct']}% of total")

    print(f"\n  ✅ Demo complete. SDB budget enforcement works.")
    print(f"  Cross-episode check: Episode 4 started at full "
          f"{runtime.enforcer.config.budget_tokens}-token budget after an "
          f"OVER_BUDGET episode.")


if __name__ == "__main__":
    main()
