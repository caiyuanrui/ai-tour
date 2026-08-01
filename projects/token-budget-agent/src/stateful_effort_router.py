"""
StatefulEffortRouter — P3v2 multi-signal routing function (SDB proposer).

Implements the weighted-sum routing design from the 2026-07-25 project-planning
note:

    signals = {
        "accumulated_steps":      episode_state.step_count,
        "instruction_complexity": estimated from instruction,
        "max_observation_size":   episode_state.max_observation_size_history,
        "tool_call_density":      tool_call_count / max(1, step_count),
        "remaining_budget_pct":   remaining_tokens / episode_budget,
    }
    score = weighted_sum(signals, weights=[0.3, 0.25, 0.2, 0.15, 0.1])
    return quantize(score)  # ECONOMY / STANDARD / DEEP

Key lesson from Cycle 1 (failure-analysis 2026-07-11): per-step instruction
length is a proxy-variable failure — task complexity is determined by
accumulated step state, not per-instruction features. This router is STATEFUL:
it consumes an EpisodeState accumulated across the whole episode, so a short
instruction like "search for papers on attention optimization" (which describes
multi-step work) correctly routes to a higher effort level once tool calls and
large observations have accumulated.

The router is the *proposer* in the SDB contract. It proposes an effort level
purely from complexity signals; the BudgetEnforcer (verifier) is responsible
for budget-driven downgrades and stops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .budget_controller import BudgetLevel


# Per-level default step budgets (tokens) — used as reference points, not hard caps.
LEVEL_REFERENCE_BUDGETS = {
    BudgetLevel.ECONOMY: 2_000,
    BudgetLevel.STANDARD: 8_000,
    BudgetLevel.DEEP: 32_000,
}


@dataclass
class EpisodeState:
    """Accumulated, stateful signal source for routing decisions.

    Unlike Cycle 1's per-step RoutingFeatures, this carries the FULL episode
    history so routing can react to how the task has actually evolved.
    """

    instruction: str = ""
    step_count: int = 0
    tool_call_count: int = 0
    total_tool_output_chars: int = 0
    max_observation_chars: int = 0
    remaining_budget_tokens: int = 0
    episode_budget_tokens: int = 0

    @property
    def tool_call_density(self) -> float:
        """Tool calls per step — high density implies complex multi-tool work."""
        return self.tool_call_count / max(1, self.step_count)

    @property
    def remaining_budget_pct(self) -> float:
        """Fraction of episode budget still available (1.0 = fresh)."""
        if self.episode_budget_tokens <= 0:
            return 0.0
        return max(0.0, self.remaining_budget_tokens / self.episode_budget_tokens)


@dataclass
class RoutingDecision:
    """The proposer's output: an effort level + explanation."""

    level: BudgetLevel
    confidence: float
    signal: str
    features: dict = field(default_factory=dict)


# Default weights from the 2026-07-25 design spec. Empirical calibration is an
# open question (open_questions[0]) — these are the starting point.
DEFAULT_SIGNAL_WEIGHTS = {
    "accumulated_steps": 0.30,
    "instruction_complexity": 0.25,
    "max_observation_size": 0.20,
    "tool_call_density": 0.15,
    "remaining_budget_pct": 0.10,
}


class StatefulEffortRouter:
    """Rule-based multi-signal effort router (SDB proposer).

    Design notes:
    - All signals are normalized to [0, 1] so the weighted sum is comparable.
    - The complexity-side signals (steps, complexity, obs size, density) are
      positively correlated with needed effort. remaining_budget_pct is a
      weak (0.10) *availability* nudge: more budget remaining → can afford
      deeper reasoning.
    - Budget exhaustion is NOT handled here — the verifier downgrades/stops.
    """

    def __init__(self, weights: Optional[dict] = None):
        self.weights = dict(DEFAULT_SIGNAL_WEIGHTS)
        if weights:
            self.weights.update(weights)

    # -- signal normalization -------------------------------------------------

    @staticmethod
    def _steps_signal(state: EpisodeState) -> float:
        # 8+ accumulated steps is a long-horizon task → saturated.
        return min(1.0, state.step_count / 8.0)

    @staticmethod
    def _complexity_signal(state: EpisodeState) -> float:
        """Instruction complexity in [0, 1].

        Uses keyword evidence + length, but deliberately bounded: per-step
        instruction length is a weak signal on its own (Cycle 1 lesson). The
        stateful signals carry most of the weight.
        """
        text = state.instruction.lower()
        heavy = {"analyze", "research", "implement", "design", "compare",
                 "evaluate", "optimize", "investigate", "architect", "refactor"}
        light = {"lookup", "check", "list", "summarize", "get", "find quickly",
                 "what is", "status"}
        heavy_hits = sum(1 for kw in heavy if kw in text)
        light_hits = sum(1 for kw in light if kw in text)

        length = min(1.0, len(state.instruction.split()) / 80.0)
        score = 0.55 * min(1.0, heavy_hits / 2.0) + 0.30 * length
        score -= 0.25 * min(1.0, light_hits / 2.0)
        return max(0.0, min(1.0, score))

    @staticmethod
    def _obs_size_signal(state: EpisodeState) -> float:
        # 32K chars ≈ 8K tokens ≈ a full STANDARD step budget. Saturate there.
        return min(1.0, state.max_observation_chars / 32_000.0)

    @staticmethod
    def _density_signal(state: EpisodeState) -> float:
        # 1.5+ tool calls per step → saturated (heavy tool orchestration).
        return min(1.0, state.tool_call_density / 1.5)

    def _budget_signal(self, state: EpisodeState) -> float:
        return state.remaining_budget_pct

    # -- public API ------------------------------------------------------------

    def route(self, state: EpisodeState) -> RoutingDecision:
        """Propose an effort level from the accumulated episode state."""
        signals = {
            "accumulated_steps": self._steps_signal(state),
            "instruction_complexity": self._complexity_signal(state),
            "max_observation_size": self._obs_size_signal(state),
            "tool_call_density": self._density_signal(state),
            "remaining_budget_pct": self._budget_signal(state),
        }
        score = sum(self.weights[k] * v for k, v in signals.items())

        if score >= 0.70:
            level, conf = BudgetLevel.DEEP, 0.70
        elif score >= 0.40:
            level, conf = BudgetLevel.STANDARD, 0.75
        else:
            level, conf = BudgetLevel.ECONOMY, 0.80

        return RoutingDecision(
            level=level,
            confidence=conf,
            signal=f"multi-signal score={score:.2f} "
                   f"(steps={signals['accumulated_steps']:.2f}, "
                   f"complexity={signals['instruction_complexity']:.2f}, "
                   f"obs={signals['max_observation_size']:.2f}, "
                   f"density={signals['tool_call_density']:.2f}, "
                   f"budget={signals['remaining_budget_pct']:.2f})",
            features=signals,
        )


def describe_signals() -> str:
    """Human-readable signal reference (for docs/notes)."""
    lines = ["StatefulEffortRouter signal weights (P3v2 design):"]
    for name, weight in DEFAULT_SIGNAL_WEIGHTS.items():
        lines.append(f"  {name:<24} {weight:.2f}")
    return "\n".join(lines)
