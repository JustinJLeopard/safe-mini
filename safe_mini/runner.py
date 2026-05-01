"""SafeMiniRunner — the concrete substrate runner.

Currently a TODO scaffold pending the careful port of
reference/lab_safe_mini_agent.py into idiomatic module form.

Port checklist:
- [ ] Move SafeExecutor logic into safe_mini.policies.executor module
- [ ] Move ScriptedModel into tests/ as a test double (it's deterministic-stub
      only, not a runtime concern)
- [ ] Move parse_action into safe_mini.action_parser module (support both
      fenced-bash and JSON action protocols)
- [ ] Move fresh_repo into safe_mini.worktree (proper worktree provisioner)
- [ ] Move final_tests_pass into safe_mini.observation.final_check
- [ ] run_case → SafeMiniRunner.run, plumbing through the canonical types
- [ ] Add classify_failure based on transcript + outcomes
- [ ] Tests: unit tests for each policy + integration test with practice_repo
"""

from __future__ import annotations

from .protocol import AgentRunner
from .types import Budget, Chunk, ExecutorPolicy, FailureClass, ObservationPolicy, RunResult


class SafeMiniRunner(AgentRunner):
    """Concrete substrate runner. NOT YET IMPLEMENTED — scaffold only."""

    def __init__(self) -> None:
        raise NotImplementedError(
            "SafeMiniRunner is scaffold-only; the port from "
            "reference/lab_safe_mini_agent.py is pending. See "
            "safe_mini/runner.py docstring for the port checklist."
        )

    def run(
        self,
        chunk: Chunk,
        budget: Budget,
        observation_policy: ObservationPolicy,
        executor_policy: ExecutorPolicy,
    ) -> RunResult:
        raise NotImplementedError

    def classify_failure(self, result: RunResult) -> FailureClass:
        raise NotImplementedError
