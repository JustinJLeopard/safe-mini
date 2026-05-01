"""safe-mini: a safe-by-construction local-execution substrate for mini-swe-agent-style coding agents.

Public API (post-port; currently stubs):
- Chunk, Budget, RunResult, FailureClass, ObservationPolicy, ExecutorPolicy (canonical types)
- AgentRunner (Protocol contract)
- SafeMiniRunner (concrete implementation)
- ExecutorPolicies, ObservationPolicies (policy registries)
- classify_failure (failure classifier helper)
"""

__version__ = "0.1.0"

# Stubs — replaced once the careful port from reference/ lab_safe_mini_agent.py lands.
__all__ = [
    "__version__",
]
