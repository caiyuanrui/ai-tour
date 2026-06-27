"""
token-budget-agent: Practical Token-Budget-Controlled ReAct Agent (P3)

Core components:
- TokenBudgetController — tracks token usage, enforces budgets, emits signals
- ObservationPurifier — strips low-information content from tool outputs
- EffortRouter — maps context to thinking effort levels using cheap signals
- CostTracker — measures tokens, cost, and success per episode
"""

from .budget_controller import TokenBudgetController, BudgetLevel, BudgetSignal
from .observation_purifier import ObservationPurifier, PurificationConfig
from .effort_router import EffortRouter, EffortLevel, RoutingDecision, RoutingFeatures
from .cost_tracker import CostTracker, EpisodeResult

__version__ = "0.1.0"
