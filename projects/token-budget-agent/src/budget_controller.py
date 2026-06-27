"""
TokenBudgetController — Core budget tracking and enforcement for ReAct loops.

Provides:
- Per-step token tracking with cumulative budget enforcement
- Three budget levels: economy / standard / deep
- Soft signals (warning) and hard signals (stop) to the agent loop
- Configurable per-provider token costs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class BudgetLevel(Enum):
    """Three effort levels with default token budgets."""
    ECONOMY = auto()   # <= 2K tokens/step — quick lookups, simple tool calls
    STANDARD = auto()  # <= 8K tokens/step — normal reasoning + tool use
    DEEP = auto()      # <= 32K tokens/step — deep analysis, multi-step planning


class BudgetSignal(Enum):
    """Signals the controller sends to the agent loop."""
    OK = auto()
    WARNING = auto()      # approaching budget — suggest reducing effort
    HARD_STOP = auto()    # budget exhausted — must finalize
    OVER_BUDGET = auto()  # exceeded — emergency handling


@dataclass
class ProviderCosts:
    """Per-provider token cost configuration.
    
    Costs in USD per 1K tokens (prompt + completion).
    """
    prompt_per_1k: float = 0.0
    completion_per_1k: float = 0.0
    
    @property
    def blended_per_1k(self) -> float:
        """Blended rate assuming ~3:1 prompt-to-completion ratio."""
        return (3 * self.prompt_per_1k + self.completion_per_1k) / 4


# Reference provider costs (as of June 2026)
DEFAULT_PROVIDER_COSTS = {
    "gpt-4o": ProviderCosts(prompt_per_1k=0.01, completion_per_1k=0.03),
    "gpt-4o-mini": ProviderCosts(prompt_per_1k=0.00015, completion_per_1k=0.0006),
    "claude-3.5-sonnet": ProviderCosts(prompt_per_1k=0.003, completion_per_1k=0.015),
    "claude-3.5-haiku": ProviderCosts(prompt_per_1k=0.0008, completion_per_1k=0.004),
    "deepseek-v3": ProviderCosts(prompt_per_1k=0.0005, completion_per_1k=0.002),
    "deepseek-r1": ProviderCosts(prompt_per_1k=0.00055, completion_per_1k=0.00219),
}


@dataclass
class TokenBudgetConfig:
    """Per-agent budget configuration."""
    budget_tokens: int = 16_000      # hard limit per episode
    warning_threshold: float = 0.75  # fraction of budget at which to warn
    level: BudgetLevel = BudgetLevel.STANDARD
    provider: str = "gpt-4o-mini"
    
    # Per-level budget soft limits (agent hints, not hard caps)
    level_soft_limits: dict = field(default_factory=lambda: {
        BudgetLevel.ECONOMY: 2_000,
        BudgetLevel.STANDARD: 8_000,
        BudgetLevel.DEEP: 32_000,
    })


@dataclass
class StepRecord:
    """Record of a single ReAct step's token consumption."""
    step_index: int
    prompt_tokens: int
    completion_tokens: int
    total_step: int
    cumulative: int
    signal: BudgetSignal
    effort_level: BudgetLevel
    timestamp: float = field(default_factory=time.time)
    tool_call_type: str = "none"


class TokenBudgetController:
    """Tracks token usage and emits budget signals for a single episode."""

    def __init__(self, config: Optional[TokenBudgetConfig] = None):
        self.config = config or TokenBudgetConfig()
        self.steps: list[StepRecord] = []
        self._cumulative_tokens: int = 0
        self._is_active: bool = True
        self._current_level: BudgetLevel = self.config.level

    def record_step(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        tool_call_type: str = "none",
    ) -> BudgetSignal:
        """Record a ReAct step and return the budget signal."""
        step_tokens = prompt_tokens + completion_tokens
        self._cumulative_tokens += step_tokens
        
        signal = self._compute_signal()
        self._current_level = self._infer_level()
        
        record = StepRecord(
            step_index=len(self.steps),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_step=step_tokens,
            cumulative=self._cumulative_tokens,
            signal=signal,
            effort_level=self._current_level,
            tool_call_type=tool_call_type,
        )
        self.steps.append(record)
        
        if signal in (BudgetSignal.HARD_STOP, BudgetSignal.OVER_BUDGET):
            self._is_active = False
        
        return signal

    def _compute_signal(self) -> BudgetSignal:
        """Compute the budget signal based on cumulative usage."""
        if self._cumulative_tokens > self.config.budget_tokens:
            return BudgetSignal.OVER_BUDGET
        
        ratio = self._cumulative_tokens / self.config.budget_tokens
        
        if ratio >= 1.0:
            return BudgetSignal.HARD_STOP
        elif ratio >= self.config.warning_threshold:
            return BudgetSignal.WARNING
        
        return BudgetSignal.OK

    def _infer_level(self) -> BudgetLevel:
        """Infer the appropriate effort level from current usage."""
        ratio = self._cumulative_tokens / self.config.budget_tokens
        if ratio <= 0.25:
            return BudgetLevel.ECONOMY
        elif ratio <= 0.60:
            return BudgetLevel.STANDARD
        else:
            return BudgetLevel.DEEP

    @property
    def cumulative_tokens(self) -> int:
        return self._cumulative_tokens

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def remaining_tokens(self) -> int:
        return max(0, self.config.budget_tokens - self._cumulative_tokens)

    @property
    def estimated_cost(self) -> float:
        """Estimate USD cost so far."""
        costs = DEFAULT_PROVIDER_COSTS.get(
            self.config.provider,
            ProviderCosts(prompt_per_1k=0.003, completion_per_1k=0.015),
        )
        total_prompt = sum(s.prompt_tokens for s in self.steps)
        total_completion = sum(s.completion_tokens for s in self.steps)
        return (
            total_prompt / 1000 * costs.prompt_per_1k
            + total_completion / 1000 * costs.completion_per_1k
        )

    def reset(self) -> None:
        """Reset for a new episode."""
        self.steps = []
        self._cumulative_tokens = 0
        self._is_active = True
        self._current_level = self.config.level

    def summary(self) -> dict:
        """Return a summary dict for logging / cost tracking."""
        return {
            "total_tokens": self._cumulative_tokens,
            "total_steps": len(self.steps),
            "remaining_tokens": self.remaining_tokens,
            "estimated_cost_usd": round(self.estimated_cost, 6),
            "signal": self._compute_signal().name if self.is_active else "INACTIVE",
            "effort_level": self._current_level.name,
            "final_step_signal": self.steps[-1].signal.name if self.steps else "NONE",
        }
