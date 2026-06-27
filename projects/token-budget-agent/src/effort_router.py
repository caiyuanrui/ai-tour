"""
EffortRouter — Decides which thinking effort level to use based on cheap signals.

Uses a small rule-based classifier (no LLM calls):
- Task complexity signals: instruction length, tool count, required precision
- Budget state signals: remaining tokens, current budget ratio
- Combines into a recommended effort level

Can be replaced with a trained classifier later (differentiable router).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class EffortLevel(Enum):
    """Three effort levels mapped to provider thinking budgets."""
    ECONOMY = "economy"     # Fast, cheap — simple lookups, 1-step tool calls
    STANDARD = "standard"   # Normal — moderate reasoning, 2-3 step plans
    DEEP = "deep"           # Expensive — complex multi-step reasoning

    def to_provider_budget(self, provider: str = "default") -> int:
        """Map to provider-specific thinking budget (max_tokens or reasoning_effort)."""
        budgets = {
            "openai": {EffortLevel.ECONOMY: 1024, EffortLevel.STANDARD: 4096, EffortLevel.DEEP: 16384},
            "anthropic": {EffortLevel.ECONOMY: 1024, EffortLevel.STANDARD: 4096, EffortLevel.DEEP: 8192},
            "deepseek": {EffortLevel.ECONOMY: 1024, EffortLevel.STANDARD: 4096, EffortLevel.DEEP: 8192},
            "default": {EffortLevel.ECONOMY: 2048, EffortLevel.STANDARD: 8192, EffortLevel.DEEP: 32768},
        }
        return budgets.get(provider, budgets["default"])[self]


@dataclass
class RoutingFeatures:
    """Cheap-to-compute features for routing decisions."""
    instruction_word_count: int = 0
    num_tools_available: int = 0
    expected_tool_calls: int = 1
    requires_precision: bool = False   # e.g., code generation, math
    is_exploratory: bool = False       # e.g., open-ended research
    budget_ratio: float = 0.0          # 0.0 = fresh, 1.0 = nearly out
    
    @classmethod
    def from_instruction(cls, instruction: str, num_tools: int = 0) -> "RoutingFeatures":
        """Extract features from an instruction string (no LLM calls)."""
        words = instruction.split()
        # Simple complexity heuristics
        precision_keywords = {"calculate", "compute", "generate code", "exact", 
                              "precise", "verify", "validate", "assert"}
        exploration_keywords = {"explore", "research", "investigate", "find",
                                "discover", "survey", "compare", "analyze"}
        
        instruction_lower = instruction.lower()
        
        return cls(
            instruction_word_count=len(words),
            num_tools_available=num_tools,
            requires_precision=any(kw in instruction_lower for kw in precision_keywords),
            is_exploratory=any(kw in instruction_lower for kw in exploration_keywords),
        )


@dataclass
class RoutingDecision:
    """The routing decision with explanation."""
    level: EffortLevel
    confidence: float  # 0.0-1.0 confidence in this decision
    signal: str        # e.g., "low complexity", "budget exhausted", "precision required"
    features: RoutingFeatures = field(default_factory=RoutingFeatures)


class EffortRouter:
    """Rule-based effort router using cheap signals.
    
    Decision logic:
    1. If budget nearly exhausted → ECONOMY (must finalize)
    2. If requires precision + many tools → DEEP
    3. If exploratory + budget healthy → DEEP
    4. If short instruction + 1 tool → ECONOMY
    5. Otherwise → STANDARD
    """

    def __init__(self):
        pass

    def route(
        self,
        features: RoutingFeatures,
        budget_ratio: float = 0.0,
    ) -> RoutingDecision:
        """Route to an effort level based on features and budget state."""
        
        # Budget-driven routing (overrides everything when exhausted)
        if budget_ratio >= 0.90:
            return RoutingDecision(
                level=EffortLevel.ECONOMY,
                confidence=0.95,
                signal=f"Budget exhausted ({budget_ratio:.0%}), must conserve",
                features=features,
            )
        if budget_ratio >= 0.75:
            return RoutingDecision(
                level=EffortLevel.STANDARD if features.requires_precision else EffortLevel.ECONOMY,
                confidence=0.85,
                signal=f"Budget warning ({budget_ratio:.0%}), reducing effort",
                features=features,
            )

        # Complexity-driven routing
        complexity_score = self._compute_complexity(features)
        
        if complexity_score >= 7:
            return RoutingDecision(
                level=EffortLevel.DEEP,
                confidence=0.70,
                signal=f"High complexity (score={complexity_score}): precision + tools + length",
                features=features,
            )
        elif complexity_score <= 2:
            return RoutingDecision(
                level=EffortLevel.ECONOMY,
                confidence=0.80,
                signal=f"Low complexity (score={complexity_score}): simple task",
                features=features,
            )
        else:
            return RoutingDecision(
                level=EffortLevel.STANDARD,
                confidence=0.75,
                signal=f"Moderate complexity (score={complexity_score}): standard effort",
                features=features,
            )

    def _compute_complexity(self, features: RoutingFeatures) -> int:
        """Compute a simple complexity score (0-10) from features."""
        score = 0
        
        # Instruction length (0-3 points)
        if features.instruction_word_count > 100:
            score += 3
        elif features.instruction_word_count > 50:
            score += 2
        elif features.instruction_word_count > 20:
            score += 1
        
        # Tool count (0-2 points)
        if features.num_tools_available > 10:
            score += 2
        elif features.num_tools_available > 5:
            score += 1
        
        # Expected tool calls (0-3 points)
        if features.expected_tool_calls > 5:
            score += 3
        elif features.expected_tool_calls > 3:
            score += 2
        elif features.expected_tool_calls > 1:
            score += 1
        
        # Precision requirement (0-1 point)
        if features.requires_precision:
            score += 1
        
        # Exploratory (0-1 point)
        if features.is_exploratory:
            score += 1
        
        return min(score, 10)
