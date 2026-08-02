# 2026-08-01 — Implementation Notes: P3v2 SDB-Contract Budget Enforcement (Layer 2)

Course: Research Lab
Topic: Implementation Notes (Cycle 3, Session 1)
Stage: Building P3v2 Layer-2 budget enforcement — SDB contract runtime, multi-signal routing, graceful degradation
Confidence: 0.0 -> 0.55

## Today's Question

Can I build the P3v2 budget enforcement layer (Layer 2) as specified in the 2026-07-25 project-planning design — the SDB proposer→verifier→commit/reject contract, the five-signal stateful routing function, and the four-stage graceful degradation protocol — and demonstrate that **system-level enforcement stops budget overruns** in a ReAct loop?

Cycle 1 (2026-06-27) proved purification + routing + cost tracking work, but the failure analysis (2026-07-11) exposed four design gaps: proxy-variable routing, interface incompleteness (signals with no consumers), simulation overconfidence, and metric inflation. The P3v2 architecture was designed to fix all four. Today's job: turn that design into running code.

## What Was Built

A new P3v2 module set inside `projects/token-budget-agent/` (v0.1.0 → v0.2.0):

```
token-budget-agent/
├── src/
│   ├── stateful_effort_router.py   — NEW: 5-signal weighted routing (SDB proposer)
│   ├── budget_enforcer.py          — NEW: BudgetEnforcer + FallbackHandler + SDBRuntime
│   ├── budget_controller.py        — Cycle 1 (reused for token accounting)
│   ├── observation_purifier.py     — Cycle 1 (reused)
│   ├── effort_router.py            — Cycle 1 (kept, now superseded by stateful router)
│   └── __init__.py                 — v0.2.0 exports
└── demo_budget_enforcement.py      — NEW: 4-scenario enforcement demo
```

### Component 1: StatefulEffortRouter (SDB proposer)

Implements the weighted-sum design from the 2026-07-25 note. Fixes the **proxy-variable failure**: it consumes an `EpisodeState` accumulated across the whole episode (step count, tool-call count, max observation size, remaining budget) instead of per-step instruction length.

```python
signals = {
    "accumulated_steps":        min(1.0, step_count / 8),          # w=0.30
    "instruction_complexity":   heavy/light keyword + length,       # w=0.25
    "max_observation_size":     min(1.0, max_obs_chars / 32_000),  # w=0.20
    "tool_call_density":        min(1.0, calls_per_step / 1.5),    # w=0.15
    "remaining_budget_pct":     remaining / episode_budget,        # w=0.10
}
score = Σ weight·signal   →  ≥0.70 DEEP · ≥0.40 STANDARD · else ECONOMY
```

Key design choice: complexity signals push **up** (more steps/observations/tools → more effort), budget availability is a weak (0.10) nudge. Budget *exhaustion* is deliberately NOT the router's job — the verifier owns it. This cleanly separates "how hard is this task?" from "how much budget is left?".

### Component 2: BudgetEnforcer (SDB verifier) + FallbackHandler (SDB reject)

Implements the four-stage protocol from the design table with the **explicit consumer mapping** — fixing the interface-incompleteness failure:

| Stage | Trigger | Action (FallbackHandler) |
|-------|---------|--------------------------|
| OK | remaining > 80% | CONTINUE at proposed level |
| WARNING | 50–80% remaining | DOWNGRADE_ECONOMY — run step at ECONOMY |
| HARD_STOP | exhausted mid-step | EMIT_PARTIAL_STOP — step completes if < 20% over, then loop stops |
| OVER_BUDGET | exceeded budget + 20% margin | EMIT_PARTIAL_NOTIFY — force stop, preserve partial results, notify operator |

Every signal the controller emits has a defined consumer — the `FallbackHandler` owns the degradation behavior. The old Cycle-1 controller just set `is_active=False` with no handler.

### Component 3: SDBRuntime (loop orchestration)

```python
step():
  1. proposer.route(episode_state)      → proposed level
  2. verifier.verify(proposed_level)    → OK / WARNING / HARD_STOP
  3a. OK/WARNING → executor runs at effective level → verifier.settle()
  3b. HARD_STOP  → fallback emits partial result, loop stops
  4. OVER_BUDGET → fallback force-stops + notifies operator
```

Episode-scoped `start_episode()` reset guarantees **no cross-episode budget leakage** (the Token Budgets catalog incident class). The runtime also tracks a routing-overhead decomposition: actual = 0 tokens (rule-based), hypothetical = what an LLM classifier would cost.

## Test Results (real output)

Ran `python3 demo_budget_enforcement.py` — four scenarios mapping to Token Budgets catalog failure classes:

```
Ep  tokens   cost        terminal     hist(warning/hardstop/overbudget)
1   1,608    $0.000421   OK           (0/0/0)      — simple lookup, fits budget
2  18,950    $0.003427   HARD_STOP    (1/1/0)      — research task exhausts budget
3  31,331    $0.005492   OVER_BUDGET  (2/0/1)      — runaway retry loop
4     925    $0.000229   OK           (0/0/0)      — fresh budget after overrun
```

**Episode 2 (the interesting one):** routing escalated ECONOMY → STANDARD as steps/observations accumulated. At remaining 36% the verifier downgraded the third step to ECONOMY, but the 32K-char observation (8K tokens) still pushed cumulative to 18,950 — over budget by 2,950, **within the 20% margin (3,200)** → HARD_STOP: current step completes, partial result emitted (2 items), loop stops. Exactly the design intent.

**Episode 3:** a retry loop with growing error payloads (4K→12K→28K chars, blowup 2.2×) blew past budget + margin in one step (cum 31,331, exceeded by 15,331 > 3,200) → OVER_BUDGET: partial results preserved, operator notified. **The loop cannot run unbounded — this is the enforcement guarantee.**

**Episode 4:** after the OVER_BUDGET episode, a fresh episode started at the full 16,000-token budget (rem=15,075 after step 1) — episode-scoped reset works, no leakage.

**Routing overhead decomposition:** 10 routing decisions across 4 episodes; actual cost 0 tokens (rule-based); a hypothetical 50-token/decision LLM classifier would cost 500 tokens = 0.96% of the 51,889 total — cheap enough to justify learned routing later (P3 Priority 3).

## What Surprised Me

1. **The HARD_STOP margin rule is what makes enforcement human-friendly.** Without the 20% margin, a step that overshoots by 3K tokens would be treated as a catastrophe. With it, the agent finishes the in-flight step and then stops cleanly — you lose a bounded amount of work, not a mid-step crash. This single design decision converts "budget enforcement" from a blunt wall into a graceful process.

2. **Observation size dominates everything in a real ReAct loop.** With observation-aware token accounting, one 32K-char tool output costs more than 8 economy steps. The 5-signal router correctly responds to this (obs signal w=0.20 + density w=0.15), but it also means purification (Cycle 1's 87.9% compression) and budget enforcement are **complementary** — purification shrinks what enters context, enforcement bounds what leaves the wallet.

3. **WARNING downgrade to ECONOMY is the highest-leverage cheap win.** In episode 2, the downgrade happened at 36% remaining and the step still cost 8,800 tokens because observation size is the dominant term — the level-based completion budget (2K/8K/32K) matters less than observation intake. This sharpens the P3v2 open question: *prompt-level hints (TALE) that tell the model to compress reasoning may matter more than system-level completion caps when observations are huge.*

## What Broke and What Fixed It

1. **First demo run never hit HARD_STOP/OVER_BUDGET.** The executor consumed a fixed token amount per level regardless of observations, so episodes ended with 50-80% budget left — the WARNING downgrade kept everything cheap. Fixed by making the executor observation-aware: `prompt = base_prompt(level) + sum(obs_chars)/4`. This models the real ReAct pattern where accumulated context grows every step, and is exactly the "observation exceeds cost estimate" incident class from the catalog.

2. **Routing-overhead metric bug.** `routing_overhead()` divided classifier cost by the *current episode's* tokens (500/550 = 90.9% in one early run — absurd). Fixed by accumulating `_total_tokens_all_episodes` across all episodes in the runtime; now reports 0.96% of the 51,889 aggregate. Lesson re-learned from the 2026-07-11 metric-aggregation failure: **always state the denominator** for percentage metrics.

3. **Level-agnostic executor hid routing value.** Before the fix, ECONOMY/STANDARD/DEEP all cost the same, so the router's decision had no economic consequence. Per-level token profiles (DEEP ≈ 8× ECONOMY) made routing decisions visible in cost — episode 2's escalation to STANDARD visibly raised step cost, which is the whole point of effort routing.

4. **Type annotation drift in the SDB contract.** `executor` signature changed from `(level)` to `(level, observations)` when observation-awareness was added; Pyright flagged the mismatched callable types. Fixed the annotations in `SDBRuntime` and the demo — a reminder that the executor is an interface, and interfaces need to be declared, not implied (the interface-incompleteness failure mode again, at the type level).

## Current Understanding

P3v2 Layer-2 enforcement is **working and tested in simulation**. The SDB contract runs end-to-end: stateful proposer → verifier → commit/reject with defined consumers for every signal. The demo proves the three enforcement guarantees that matter:

1. No unbounded runaway loops (OVER_BUDGET force-stops + notifies)
2. Graceful exhaustion (HARD_STOP margin rule finishes the in-flight step, emits partial results)
3. Episode-scoped budgets (no cross-episode leakage)

Of the 5-component P3v2 build plan, components 1–3 (budget enforcement, multi-signal routing, graceful degradation) are substantially done in code. Remaining: **evaluation framework** (cost decomposition, per-budget accuracy, break-even curves — the 2026-07-18 design) and **prompt-level hints** (TALE-style Layer 1). The big honest caveat: this is still **simulated** — no real API calls yet. Cycle-1 failure #3 (simulation overconfidence) is only partially addressed: the demo uses realistic token models, but nothing replaces real billing.

## Key Implementation Insights

- **Separate proposer from verifier.** Complexity routing and budget enforcement are different concerns; merging them (as Cycle 1 did with budget overrides inside the router) creates confusing behavior. The SDB contract keeps each signal's producer and consumer explicit.
- **Observation-aware token accounting is mandatory for realistic simulation.** Fixed per-step tokens produce unrealistically rosy budget behavior — the "observation exceeds estimate" incident class only appears when prompt tokens grow with context.
- **HARD_STOP margin rule = bounded loss, not crash.** The 20% margin converts budget exhaustion into a clean stop with partial results.
- **The SDB contract is a type-level interface, not just a runtime pattern.** The executor signature change broke annotations — declaring interfaces (callables, contracts) catches design changes early.
- **Routing overhead is tiny (0.96% hypothetical)** — learned routing (S-GRPO/T-SPMO direction from 2026-07-25) is economically viable later.

## Open Questions

1. How much of the enforcement behavior survives **real API billing** (latency, retries, provider limits not modeled by token math)?
2. Does the WARNING downgrade to ECONOMY actually reduce cost when observation sizes dominate? (Level caps may be the wrong lever — prompt-level hints may matter more. Needs the Layer-1 build + A/B test.)
3. What is the right HARD_STOP margin? 20% of budget (3,200 tokens) was chosen from the design; empirically it may want to be per-step-size rather than per-budget.
4. Where should the evaluation framework hook in — inside SDBRuntime (instrumented) or as a separate harness around it (per-budget accuracy, routing overhead decomposition)?
5. What does the operator notification look like in a real runtime — a Hermes message, a log line, a callback? (OVER_BUDGET notify is currently a print.)

## Possible Thesis Ideas

1. **Priority 1 (unchanged, now with a working core):** Practical Token-Budget-Controlled ReAct Agent v2 — the SDB contract + multi-signal routing + purification, validated on real API calls with budget-aware evaluation. Today's build is the runtime core of this thesis; the remaining gap is real-API validation and the evaluation framework.
2. **NEW — Observation-Dominated Budget Dynamics:** the finding that observation intake, not completion level, drives token cost in ReAct loops. A thesis angle: *purification + budget enforcement as a joint optimization* — where to spend effort (purify more vs cap more) given an observation-size distribution. This is a sharper, more novel framing than generic "budget control".
3. **Priority 3 (deferred):** Learned routing via token-efficient RL — now economically justified by the 0.96% routing-overhead measurement.

## Next Step

**Advance to experiment-log.** Implementation Notes is a single-session topic. The experiment-log session should:
1. Benchmark the SDB runtime across a **synthetic episode distribution** (varying observation sizes, step counts, complexity) to measure overrun rate, WARNING-downgrade frequency, and routing overhead under load — the first honest measurement of whether enforcement holds at scale.
2. Optionally wire the SDB runtime around **real Hermes tool calls** to start addressing the simulation-overconfidence failure (real API validation).
3. Report median (not just mean) token overrun and degradation-stage histograms — applying the metric-aggregation lesson from 2026-07-11.
