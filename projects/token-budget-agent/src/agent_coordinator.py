"""
TokenBudgetAgentCoordinator — Ties budget controller, purifier, and router together.

Provides a single orchestrator that:
1. Receives a task instruction + tool outputs
2. Routes to appropriate effort level
3. Purifies observations before context entry
4. Tracks budget and emits signals
5. Reports episode results

This can be plugged into any ReAct loop as a middleware layer.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .budget_controller import (
    TokenBudgetController,
    TokenBudgetConfig,
    BudgetLevel,
    BudgetSignal,
)
from .observation_purifier import ObservationPurifier, PurificationConfig
from .effort_router import EffortRouter, RoutingFeatures, EffortLevel
from .cost_tracker import CostTracker, EpisodeResult


@dataclass
class CoordinatorConfig:
    """Top-level configuration for the coordinator."""
    budget: TokenBudgetConfig = field(default_factory=TokenBudgetConfig)
    purification: PurificationConfig = field(default_factory=PurificationConfig)
    baseline_overhead: float = 0.30  # naive ReAct uses 30% more tokens


class TokenBudgetAgentCoordinator:
    """Orchestrates budget control, purification, and routing for ReAct loops."""

    def __init__(
        self,
        config: Optional[CoordinatorConfig] = None,
    ):
        self.config = config or CoordinatorConfig()
        self.budget_controller = TokenBudgetController(self.config.budget)
        self.purifier = ObservationPurifier(self.config.purification)
        self.router = EffortRouter()
        self.cost_tracker = CostTracker()
        self._episode_start: float = 0.0
        self._current_task: str = ""

    def start_episode(self, task: str) -> dict:
        """Start a new episode with the given task."""
        self.budget_controller.reset()
        self._episode_start = time.time()
        self._current_task = task
        
        # Initial routing based on task
        features = RoutingFeatures.from_instruction(
            task,
            num_tools=self.config.budget.level_soft_limits.get(BudgetLevel.STANDARD, 8),
        )
        routing = self.router.route(features, budget_ratio=0.0)
        
        return {
            "effort_level": routing.level,
            "effort_budget": routing.level.to_provider_budget(self.config.budget.provider),
            "signal": routing.signal,
            "confidence": routing.confidence,
        }

    def process_step(
        self,
        instruction: str,
        observations: list[tuple[str, str]],
        num_tools: int = 5,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> dict:
        """Process a single ReAct step.
        
        Args:
            instruction: The agent's thought/instruction for this step
            observations: List of (tool_name, output) pairs
            num_tools: Number of tools available
            prompt_tokens: Tokens used for the prompt/input
            completion_tokens: Tokens used for the response
            
        Returns:
            Dict with purification stats, routing decision, and budget signal
        """
        # 1. Purify observations before they enter context
        purification_results = []
        total_original = 0
        total_purified = 0
        for name, obs in observations:
            purified = self.purifier.purify(obs, name)
            stats = self.purifier.stats(obs, purified)
            purification_results.append({
                "tool": name,
                **stats,
            })
            total_original += stats["original_chars"]
            total_purified += stats["purified_chars"]

        # 2. Route to effort level
        features = RoutingFeatures.from_instruction(instruction, num_tools)
        features.budget_ratio = (
            self.budget_controller.cumulative_tokens / self.config.budget.budget_tokens
            if self.config.budget.budget_tokens > 0 else 0.0
        )
        routing = self.router.route(
            features,
            budget_ratio=features.budget_ratio,
        )

        # 3. Record in budget controller
        signal = self.budget_controller.record_step(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            tool_call_type=str(routing.level.value),
        )

        # 4. Build tool_call_type for the step
        tool_types = [p["tool"] for p in purification_results]
        
        return {
            "step_index": len(self.budget_controller.steps) - 1,
            "effort_level": routing.level,
            "effort_budget": routing.level.to_provider_budget(
                self.config.budget.provider
            ),
            "effort_confidence": routing.confidence,
            "effort_signal": routing.signal,
            "budget_signal": signal,
            "purification": {
                "tools_processed": len(purification_results),
                "total_original_chars": total_original,
                "total_purified_chars": total_purified,
                "compression_ratio": round(total_purified / total_original, 3)
                if total_original > 0 else 1.0,
                "per_tool": purification_results,
            },
            "cumulative_tokens": self.budget_controller.cumulative_tokens,
            "remaining_tokens": self.budget_controller.remaining_tokens,
            "estimated_cost": self.budget_controller.estimated_cost,
        }

    def end_episode(
        self,
        success: bool,
        baseline_tokens: Optional[int] = None,
        notes: str = "",
    ) -> EpisodeResult:
        """End the current episode and record results."""
        duration = time.time() - self._episode_start
        
        result = self.cost_tracker.record(
            controller=self.budget_controller,
            task=self._current_task,
            success=success,
            baseline_tokens=baseline_tokens,
            duration=duration,
            notes=notes,
        )
        return result

    def summary(self) -> dict:
        """Return a combined summary of budget + cost tracker."""
        return {
            "current_episode": {
                "task": self._current_task,
                **self.budget_controller.summary(),
            },
            "aggregate": self.cost_tracker.aggregate(),
        }
