"""AgentRunner Protocol — the contract that consumers depend on.

JustAi (orchestrator) and local-resident (experiment driver) both import
this Protocol. Concrete implementations include SafeMiniRunner (in this repo)
and FakeRunner (in consumer test suites).

Per memory key justai-two-repo-ship-pattern.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .types import Budget, Chunk, ExecutorPolicy, FailureClass, ObservationPolicy, RunResult


@runtime_checkable
class AgentRunner(Protocol):
    """Substrate-level contract for executing one chunk through a sandboxed bash-action loop."""

    def run(
        self,
        chunk: Chunk,
        budget: Budget,
        observation_policy: ObservationPolicy,
        executor_policy: ExecutorPolicy,
    ) -> RunResult:
        """Execute the chunk inside the substrate and return a RunResult.

        Implementations MUST:
        - Provision a fresh worktree per call (no cross-call mutation of CWD).
        - Scrub the environment per the executor policy.
        - Apply command/path guards per the executor policy.
        - Enforce both move budget and observation budget from `budget`.
        - Emit an incident artifact if a guard fires.
        - Return RunResult populated with trajectory + failure_class on failure.
        """
        ...

    def classify_failure(self, result: RunResult) -> FailureClass:
        """Classify a failed run into the 7-class taxonomy.

        Pure function over RunResult.transcript + outcomes; no I/O.
        """
        ...
