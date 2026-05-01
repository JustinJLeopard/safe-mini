"""safe-mini: a safe local-execution substrate for mini-swe-agent-style agents."""

__version__ = "0.1.0"

from .action_parser import ActionFormat, ActionParseError, ParsedAction, parse_action
from .classifier import classify_failure
from .policies import ExecutorPolicies
from .protocol import AgentRunner
from .runner import SafeMiniRunner
from .types import (
    Budget,
    Chunk,
    ExecutorPolicy,
    FailureClass,
    Observation,
    ObservationPolicy,
    RunResult,
)

__all__ = [
    "ActionFormat",
    "ActionParseError",
    "AgentRunner",
    "Budget",
    "Chunk",
    "ExecutorPolicies",
    "ExecutorPolicy",
    "FailureClass",
    "Observation",
    "ObservationPolicy",
    "ParsedAction",
    "RunResult",
    "SafeMiniRunner",
    "__version__",
    "classify_failure",
    "parse_action",
]
