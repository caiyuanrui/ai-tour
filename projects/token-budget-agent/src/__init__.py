"""
token-budget-agent: Practical Token-Budget-Controlled ReAct Agent (P3 / P3v2)

Cycle 1 (2026-06-27):
- TokenBudgetController — tracks token usage, enforces budgets, emits signals
- ObservationPurifier — strips low-information content from tool outputs
- EffortRouter — maps context to thinking effort levels using cheap signals
- CostTracker — measures tokens, cost, and success per episode

Cycle 3 / P3v2 (2026-08-01) — SDB-contract budget enforcement core:
- StatefulEffortRouter — multi-signal stateful routing function (SDB proposer)
- BudgetEnforcer — Layer-2 system-level budget enforcement (SDB verifier)
- FallbackHandler — graceful degradation consumer for every budget signal
- SDBRuntime — proposer → verifier → commit/reject loop orchestration
"""

from .budget_controller import TokenBudgetController, BudgetLevel, BudgetSignal
from .observation_purifier import ObservationPurifier, PurificationConfig
from .effort_router import EffortRouter, EffortLevel, RoutingDecision, RoutingFeatures
from .cost_tracker import CostTracker, EpisodeResult
from .stateful_effort_router import (
    StatefulEffortRouter,
    EpisodeState,
    RoutingDecision as StatefulRoutingDecision,
    DEFAULT_SIGNAL_WEIGHTS,
)
from .budget_enforcer import (
    BudgetEnforcer,
    FallbackHandler,
    FallbackAction,
    BudgetStage,
    EnforcementConfig,
    SDBRuntime,
)

__version__ = "0.2.0"
