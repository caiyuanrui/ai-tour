"""
BudgetEnforcer + FallbackHandler — P3v2 Layer-2 budget enforcement (SDB contract).

Implements the Stochastic-Deterministic Boundary (SDB) contract for budget
signals from the 2026-07-25 P3v2 architecture design:

    proposer:  StatefulEffortRouter.propose(step_context) -> budget_level
    verifier:  BudgetEnforcer.verify(level) -> OK | WARNING | HARD_STOP | OVER_BUDGET
    commit:    Executor.commit(level) -> step tokens   (wrapped by SDBRuntime)
    reject:    FallbackHandler.reject(stage) -> graceful degradation action

Graceful degradation protocol (design table from 2026-07-25):

    | Stage       | Trigger                                   | Action                                    |
    |-------------|-------------------------------------------|-------------------------------------------|
    | OK          | remaining > 80% of budget                 | run step at proposed level                 |
    | WARNING     | 50% < remaining <= 80%                    | downgrade to ECONOMY for remaining steps   |
    | HARD_STOP   | budget exhausted (remaining <= 0)         | complete current step if < 20% over, stop  |
    | OVER_BUDGET | exceeded budget + 20% margin              | force stop, emit collected results, notify |

Design rationale:
- Two-layer budget architecture: this is Layer 2 (system-level hard enforcement).
  Layer 1 (prompt-level hints) is a later build task.
- Every emitted budget signal has a DEFINED CONSUMER (FallbackHandler) — this
  directly fixes the "interface incompleteness" failure from 2026-07-11
  (emitting budget signals without explicit handlers).
- Episode-scoped state: reset() guarantees no cross-episode budget leakage —
  directly fixes the "cross-episode budget leakage" incident class from the
  Token Budgets catalog (arXiv 2606.04056).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable

from .budget_controller import (
    TokenBudgetController,
    TokenBudgetConfig,
    BudgetLevel,
    BudgetSignal,
)
from .stateful_effort_router import StatefulEffortRouter, EpisodeState


class BudgetStage(Enum):
    """Verifier output stages — a superset of the old BudgetSignal with the
    explicit downgrade stage for the SDB contract."""

    OK = auto()
    WARNING = auto()          # 50-80% remaining → downgrade to ECONOMY
    HARD_STOP = auto()        # exhausted → stop loop, emit partial result
    OVER_BUDGET = auto()      # over budget + margin → force stop + notify


class FallbackAction(Enum):
    """Actions the FallbackHandler takes for a rejected/limited step."""

    CONTINUE = auto()                 # OK — run normally
    DOWNGRADE_ECONOMY = auto()        # WARNING — run but at ECONOMY level
    EMIT_PARTIAL_STOP = auto()        # HARD_STOP — stop loop, emit partial result
    EMIT_PARTIAL_NOTIFY = auto()      # OVER_BUDGET — force stop + notify operator


@dataclass
class EnforcementConfig:
    """Layer-2 enforcement configuration."""

    budget_tokens: int = 16_000
    warning_high_ratio: float = 0.80   # remaining > 80% → OK
    warning_low_ratio: float = 0.50    # 50% < remaining <= 80% → WARNING
    margin_ratio: float = 0.20         # allow finishing a step up to 20% over
    provider: str = "gpt-4o-mini"
    routing_classifier_tokens: int = 50  # hypothetical LLM classifier cost per decision


@dataclass
class VerifyResult:
    """Result of the verifier's pre-step check."""

    stage: BudgetStage
    proposed_level: BudgetLevel
    effective_level: BudgetLevel      # may be downgraded to ECONOMY on WARNING
    remaining_tokens: int
    remaining_pct: float
    note: str = ""


@dataclass
class SettleResult:
    """Result of the verifier's post-step settlement."""

    stage: BudgetStage
    step_tokens: int
    cumulative_tokens: int
    remaining_tokens: int
    action: FallbackAction
    note: str = ""


class BudgetEnforcer:
    """SDB verifier: checks budget before each step and settles after.

    Wraps a TokenBudgetController for token accounting but owns the
    degradation-stage logic and the explicit consumer mapping.
    """

    def __init__(self, config: Optional[EnforcementConfig] = None):
        self.config = config or EnforcementConfig()
        self._controller = TokenBudgetController(
            TokenBudgetConfig(
                budget_tokens=self.config.budget_tokens,
                provider=self.config.provider,
            )
        )
        self._downgrade_count = 0
        self._hard_stop_count = 0
        self._over_budget_count = 0
        self._episode_start: float = 0.0

    # -- episode lifecycle ----------------------------------------------------

    def start_episode(self) -> None:
        """Reset ALL per-episode state — no cross-episode budget leakage."""
        self._controller.reset()
        self._downgrade_count = 0
        self._hard_stop_count = 0
        self._over_budget_count = 0
        self._episode_start = time.time()

    # -- verifier API ----------------------------------------------------------

    def verify(self, proposed_level: BudgetLevel) -> VerifyResult:
        """Pre-step check. Returns the stage + the effective (possibly
        downgraded) level to execute at."""
        remaining = self.remaining_tokens
        pct = remaining / self.config.budget_tokens if self.config.budget_tokens else 0.0

        if pct > self.config.warning_high_ratio:
            return VerifyResult(
                stage=BudgetStage.OK,
                proposed_level=proposed_level,
                effective_level=proposed_level,
                remaining_tokens=remaining,
                remaining_pct=pct,
                note="Budget healthy — run at proposed level.",
            )
        if pct > self.config.warning_low_ratio:
            return VerifyResult(
                stage=BudgetStage.WARNING,
                proposed_level=proposed_level,
                effective_level=BudgetLevel.ECONOMY,
                remaining_tokens=remaining,
                remaining_pct=pct,
                note="WARNING (50-80% remaining) — downgrade to ECONOMY.",
            )
        if remaining > 0:
            # 0-50% remaining: still technically positive, but the protocol
            # treats this as max-conservation; the next step likely stops.
            return VerifyResult(
                stage=BudgetStage.WARNING,
                proposed_level=proposed_level,
                effective_level=BudgetLevel.ECONOMY,
                remaining_tokens=remaining,
                remaining_pct=pct,
                note="CRITICAL WARNING (0-50% remaining) — ECONOMY, stop imminent.",
            )
        return VerifyResult(
            stage=BudgetStage.HARD_STOP,
            proposed_level=proposed_level,
            effective_level=proposed_level,
            remaining_tokens=remaining,
            remaining_pct=pct,
            note="Budget exhausted — do not run step; emit partial result.",
        )

    def settle(self, level: BudgetLevel, prompt_tokens: int,
               completion_tokens: int, tool_call_type: str = "none") -> SettleResult:
        """Post-step settlement: record actual usage and decide the outcome.

        Executes the HARD_STOP margin rule: if this step pushed us over the
        budget by LESS than margin_ratio, we allow it (the step already ran)
        but stop the loop (HARD_STOP). If it exceeded by MORE, it's a
        catastrophic OVER_BUDGET → force stop + notify operator.
        """
        step_tokens = prompt_tokens + completion_tokens
        before = self._controller.cumulative_tokens
        self._controller.record_step(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            tool_call_type=tool_call_type,
        )
        cumulative = before + step_tokens
        remaining = self.remaining_tokens

        if cumulative <= self.config.budget_tokens:
            pct = remaining / self.config.budget_tokens if self.config.budget_tokens else 0.0
            stage = BudgetStage.WARNING if pct <= self.config.warning_high_ratio else BudgetStage.OK
            action = (
                FallbackAction.DOWNGRADE_ECONOMY
                if stage == BudgetStage.WARNING
                else FallbackAction.CONTINUE
            )
            if stage == BudgetStage.WARNING:
                self._downgrade_count += 1
            return SettleResult(
                stage=stage, step_tokens=step_tokens, cumulative_tokens=cumulative,
                remaining_tokens=remaining, action=action,
                note=f"Within budget ({cumulative}/{self.config.budget_tokens}).",
            )

        # Over budget. Margin rule: within margin → finish step, then stop.
        margin = self.config.margin_ratio * self.config.budget_tokens
        if cumulative <= self.config.budget_tokens + margin:
            self._hard_stop_count += 1
            return SettleResult(
                stage=BudgetStage.HARD_STOP, step_tokens=step_tokens,
                cumulative_tokens=cumulative, remaining_tokens=0,
                action=FallbackAction.EMIT_PARTIAL_STOP,
                note=(
                    f"Over by {cumulative - self.config.budget_tokens} tokens "
                    f"(within {self.config.margin_ratio:.0%} margin) — "
                    f"current step completes, loop stops."
                ),
            )

        # Beyond budget + margin → catastrophic overrun.
        self._over_budget_count += 1
        return SettleResult(
            stage=BudgetStage.OVER_BUDGET, step_tokens=step_tokens,
            cumulative_tokens=cumulative, remaining_tokens=0,
            action=FallbackAction.EMIT_PARTIAL_NOTIFY,
            note=(
                f"OVER_BUDGET: exceeded by {cumulative - self.config.budget_tokens} "
                f"tokens (> {self.config.margin_ratio:.0%} margin) — force stop, "
                f"notify operator."
            ),
        )

    # -- accessors --------------------------------------------------------------

    @property
    def remaining_tokens(self) -> int:
        return self._controller.remaining_tokens

    @property
    def cumulative_tokens(self) -> int:
        return self._controller.cumulative_tokens

    @property
    def steps(self) -> list:
        return self._controller.steps

    @property
    def downgrade_count(self) -> int:
        return self._downgrade_count

    @property
    def hard_stop_count(self) -> int:
        return self._hard_stop_count

    @property
    def over_budget_count(self) -> int:
        return self._over_budget_count

    @property
    def estimated_cost(self) -> float:
        return self._controller.estimated_cost

    @property
    def stage_histogram(self) -> dict:
        return {
            "warning_downgrades": self._downgrade_count,
            "hard_stops": self._hard_stop_count,
            "over_budgets": self._over_budget_count,
        }


class FallbackHandler:
    """SDB reject consumer — every budget signal has a defined action.

    Fixes the 2026-07-11 'interface incompleteness' failure: in Cycle 1 the
    controller emitted signals with no consumer. Here the handler owns the
    graceful degradation behavior.
    """

    def handle(self, stage: BudgetStage, context: dict) -> FallbackAction:
        if stage == BudgetStage.OK:
            return FallbackAction.CONTINUE
        if stage == BudgetStage.WARNING:
            return FallbackAction.DOWNGRADE_ECONOMY
        if stage == BudgetStage.HARD_STOP:
            self._emit_partial_result(context)
            return FallbackAction.EMIT_PARTIAL_STOP
        if stage == BudgetStage.OVER_BUDGET:
            self._emit_partial_result(context)
            self._notify_operator(context)
            return FallbackAction.EMIT_PARTIAL_NOTIFY
        return FallbackAction.CONTINUE

    @staticmethod
    def _emit_partial_result(context: dict) -> None:
        """Preserve whatever the agent collected so far (graceful failure)."""
        collected = context.get("collected_results", [])
        print(f"    [fallback] emitting partial result: {len(collected)} item(s) "
              f"collected so far")

    @staticmethod
    def _notify_operator(context: dict) -> None:
        print("    [fallback] ⚠ operator notified: budget overrun "
              f"(episode={context.get('episode_id')}, "
              f"cumulative={context.get('cumulative_tokens')} tokens)")


# ---------------------------------------------------------------------------
# SDBRuntime — ties proposer → verifier → commit/reject into one loop step.
# ---------------------------------------------------------------------------

class SDBRuntime:
    """Runs a single ReAct step through the SDB budget contract.

    step() flow:
        1. proposer.route(episode_state)      → proposed level
        2. verifier.verify(proposed_level)    → OK / WARNING / HARD_STOP
        3a. OK/WARNING → executor runs at effective level → verifier.settle()
        3b. HARD_STOP  → fallback emits partial result, loop stops
        4. OVER_BUDGET → fallback force-stops + notifies operator
    """

    def __init__(
        self,
        enforcer: Optional[BudgetEnforcer] = None,
        router: Optional[StatefulEffortRouter] = None,
        fallback: Optional[FallbackHandler] = None,
        executor: Optional[Callable[[BudgetLevel, list], tuple[int, int]]] = None,
    ):
        self.enforcer = enforcer or BudgetEnforcer()
        self.router = router or StatefulEffortRouter()
        self.fallback = fallback or FallbackHandler()
        self.executor = executor  # (level, observations) -> (prompt_tokens, completion_tokens)
        self.episode_state = EpisodeState(
            episode_budget_tokens=self.enforcer.config.budget_tokens,
        )
        self.episode_id: int = 0
        self._routing_decisions: int = 0
        self._total_tokens_all_episodes: int = 0
        self._step_log: list[dict] = []

    def start_episode(self, instruction: str) -> None:
        # Persist previous episode's spend before reset (for aggregate metrics)
        self._total_tokens_all_episodes += self.enforcer.cumulative_tokens
        self.episode_id += 1
        self.enforcer.start_episode()
        self.episode_state = EpisodeState(
            instruction=instruction,
            episode_budget_tokens=self.enforcer.config.budget_tokens,
            remaining_budget_tokens=self.enforcer.config.budget_tokens,
        )
        self._step_log = []

    def step(
        self,
        observations: Optional[list[tuple[str, str]]] = None,
        executor: Optional[Callable[[BudgetLevel, list], tuple[int, int]]] = None,
    ) -> dict:
        """Run one step through the SDB contract. Returns an outcome dict."""
        if observations is None:
            observations = []
        # 1. PROPOSE (stateful multi-signal)
        decision = self.router.route(self.episode_state)
        self._routing_decisions += 1

        # 2. VERIFY (pre-step budget check)
        verify = self.enforcer.verify(decision.level)

        # 3a. REJECT at verifier: HARD_STOP before running
        if verify.stage == BudgetStage.HARD_STOP:
            action = self.fallback.handle(
                BudgetStage.HARD_STOP,
                {
                    "episode_id": self.episode_id,
                    "collected_results": self._step_log,
                },
            )
            outcome = {
                "step": len(self._step_log) + 1,
                "proposed_level": decision.level,
                "effective_level": None,
                "stage": BudgetStage.HARD_STOP.name,
                "action": action.name,
                "tokens": 0,
                "cumulative": self.enforcer.cumulative_tokens,
                "remaining": self.enforcer.remaining_tokens,
                "note": verify.note,
            }
            self._step_log.append(outcome)
            return outcome

        # 3b. COMMIT — run the executor at the effective (possibly downgraded) level
        run = executor or self.executor
        if run is None:
            raise ValueError("SDBRuntime needs an executor callable")
        prompt_tokens, completion_tokens = run(verify.effective_level, observations)
        settle = self.enforcer.settle(
            verify.effective_level,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            tool_call_type=f"{verify.effective_level.name.lower()}:{len(observations)}tools",
        )

        # 4. REJECT at settle: HARD_STOP / OVER_BUDGET post-step handling
        if settle.stage in (BudgetStage.HARD_STOP, BudgetStage.OVER_BUDGET):
            self.fallback.handle(
                settle.stage,
                {
                    "episode_id": self.episode_id,
                    "cumulative_tokens": settle.cumulative_tokens,
                    "collected_results": self._step_log,
                },
            )

        # Update stateful episode signals for the NEXT routing decision
        self.episode_state.step_count += 1
        self.episode_state.tool_call_count += len(observations)
        obs_chars = sum(len(o) for _, o in observations)
        self.episode_state.total_tool_output_chars += obs_chars
        self.episode_state.max_observation_chars = max(
            self.episode_state.max_observation_chars, obs_chars
        )
        self.episode_state.remaining_budget_tokens = self.enforcer.remaining_tokens

        outcome = {
            "step": len(self._step_log) + 1,
            "proposed_level": decision.level,
            "effective_level": verify.effective_level,
            "stage": settle.stage.name,
            "action": settle.action.name,
            "tokens": settle.step_tokens,
            "cumulative": settle.cumulative_tokens,
            "remaining": settle.remaining_tokens,
            "note": settle.note,
        }
        self._step_log.append(outcome)
        return outcome

    def stop_condition(self) -> bool:
        """True when the loop must stop (any terminal signal)."""
        return any(
            o["stage"] in (BudgetStage.HARD_STOP.name, BudgetStage.OVER_BUDGET.name)
            for o in self._step_log
        )

    def routing_overhead(self) -> dict:
        """Routing overhead decomposition (aggregated across all episodes).

        Actual overhead = 0 tokens (rule-based, no LLM calls).
        Hypothetical overhead = cost if the proposer were a small LLM
        classifier (e.g. 50 tokens per decision) — the comparison that
        matters for the 'routing overhead' evaluation metric.
        """
        total_tokens = self._total_tokens_all_episodes
        n = self._routing_decisions
        classifier_cost = n * self.enforcer.config.routing_classifier_tokens
        return {
            "routing_decisions": n,
            "actual_routing_tokens": 0,
            "hypothetical_classifier_tokens": classifier_cost,
            "total_all_episode_tokens": total_tokens,
            "hypothetical_overhead_pct": round(
                classifier_cost / total_tokens * 100, 2
            ) if total_tokens else 0.0,
        }

    def episode_summary(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "steps": len(self._step_log),
            "total_tokens": self.enforcer.cumulative_tokens,
            "estimated_cost_usd": round(self.enforcer.estimated_cost, 6),
            "stage_histogram": self.enforcer.stage_histogram,
            "terminal_stage": (
                self._step_log[-1]["stage"] if self._step_log else "NONE"
            ),
        }
