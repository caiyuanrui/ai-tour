"""
CostTracker — Measures tokens, cost, and success per episode.

Provides:
- Per-episode tracking with all budget/effort decisions
- Comparison against baseline (naive ReAct without budget control)
- Aggregate statistics across multiple episodes
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .budget_controller import TokenBudgetController, BudgetSignal


@dataclass
class EpisodeResult:
    """Result of a single ReAct episode with budget control."""
    episode_id: int
    task_description: str
    success: bool
    total_tokens: int
    total_steps: int
    estimated_cost_usd: float
    effort_level_changes: int
    tokens_saved_vs_baseline: int
    cost_saved_vs_baseline: float
    budget_signal: str
    duration_seconds: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))
    notes: str = ""


class CostTracker:
    """Aggregates episode results across multiple runs."""

    def __init__(self, baseline_cost_per_1k: float = 0.0006):
        self.episodes: list[EpisodeResult] = []
        self.baseline_cost_per_1k = baseline_cost_per_1k  # gpt-4o-mini completion

    def record(
        self,
        controller: TokenBudgetController,
        task: str,
        success: bool,
        baseline_tokens: Optional[int] = None,
        duration: float = 0.0,
        notes: str = "",
    ) -> EpisodeResult:
        """Record an episode from a TokenBudgetController state."""
        if baseline_tokens is None:
            baseline_tokens = int(controller.cumulative_tokens * 1.3)  # estimate 30% overhead
        
        effort_changes = len([
            i for i in range(1, len(controller.steps))
            if controller.steps[i].effort_level != controller.steps[i-1].effort_level
        ])
        
        result = EpisodeResult(
            episode_id=len(self.episodes) + 1,
            task_description=task,
            success=success,
            total_tokens=controller.cumulative_tokens,
            total_steps=len(controller.steps),
            estimated_cost_usd=controller.estimated_cost,
            effort_level_changes=effort_changes,
            tokens_saved_vs_baseline=baseline_tokens - controller.cumulative_tokens,
            cost_saved_vs_baseline=(
                (baseline_tokens - controller.cumulative_tokens)
                / 1000 * self.baseline_cost_per_1k
            ),
            budget_signal=controller.summary()["signal"],
            duration_seconds=duration,
            notes=notes,
        )
        self.episodes.append(result)
        return result

    def aggregate(self) -> dict:
        """Compute aggregate statistics across all episodes."""
        if not self.episodes:
            return {"episodes": 0}

        total_tokens = sum(e.total_tokens for e in self.episodes)
        total_cost = sum(e.estimated_cost_usd for e in self.episodes)
        total_saved = sum(e.tokens_saved_vs_baseline for e in self.episodes)
        total_cost_saved = sum(e.cost_saved_vs_baseline for e in self.episodes)
        successes = sum(1 for e in self.episodes if e.success)

        return {
            "total_episodes": len(self.episodes),
            "success_rate": round(successes / len(self.episodes), 3),
            "total_tokens": total_tokens,
            "avg_tokens_per_episode": round(total_tokens / len(self.episodes), 1),
            "total_cost_usd": round(total_cost, 6),
            "tokens_saved_vs_baseline": total_saved,
            "cost_saved_vs_baseline": round(total_cost_saved, 6),
            "avg_savings_per_episode_pct": round(
                (total_saved / (total_tokens + total_saved)) * 100, 1
            ) if (total_tokens + total_saved) > 0 else 0.0,
            "avg_steps_per_episode": round(
                sum(e.total_steps for e in self.episodes) / len(self.episodes), 1
            ),
            "avg_duration_seconds": round(
                sum(e.duration_seconds for e in self.episodes) / len(self.episodes), 1
            ),
        }

    def report(self) -> str:
        """Return a human-readable report string."""
        agg = self.aggregate()
        if agg["total_episodes"] == 0:
            return "No episodes recorded yet."
        
        lines = [
            "=" * 60,
            f"  Cost Tracker Report ({agg['total_episodes']} episodes)",
            "=" * 60,
            f"  Success rate:       {agg['success_rate']:.1%}",
            f"  Total tokens:       {agg['total_tokens']:,}",
            f"  Avg tokens/ep:      {agg['avg_tokens_per_episode']:,.1f}",
            f"  Total cost:         ${agg['total_cost_usd']:.6f}",
            f"  Tokens saved:       {agg['tokens_saved_vs_baseline']:,}",
            f"  Cost saved:         ${agg['cost_saved_vs_baseline']:.6f}",
            f"  Avg savings/ep:     {agg['avg_savings_per_episode_pct']:.1f}%",
            f"  Avg steps/ep:       {agg['avg_steps_per_episode']:.1f}",
            f"  Avg duration:       {agg['avg_duration_seconds']:.1f}s",
            "=" * 60,
        ]
        return '\n'.join(lines)
