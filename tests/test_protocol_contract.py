"""AgentRunner Protocol contract test — any implementation must structurally satisfy."""

from safe_mini.protocol import AgentRunner
from safe_mini.types import (
    Budget,
    Chunk,
    ExecutorPolicy,
    FailureClass,
    ObservationPolicy,
    RunResult,
)


class FakeRunner:
    """Minimal Protocol-satisfying runner used by consumers' test suites."""

    def run(
        self,
        chunk: Chunk,
        budget: Budget,
        observation_policy: ObservationPolicy,
        executor_policy: ExecutorPolicy,
    ) -> RunResult:
        return RunResult(
            label=chunk.id,
            success=True,
            leaked_secret=False,
            blocked_commands=0,
            steps=0,
            elapsed_sec=0.0,
            final_tests_pass=True,
        )

    def classify_failure(self, result: RunResult) -> FailureClass:
        return FailureClass.EXHAUSTED_IDEAS


def test_fake_runner_satisfies_protocol():
    """Structural conformance — runtime_checkable Protocol via isinstance."""
    fake = FakeRunner()
    assert isinstance(fake, AgentRunner)


def test_fake_runner_run_returns_run_result():
    fake = FakeRunner()
    chunk = Chunk(
        id="t",
        description="d",
        success_criteria="sc",
        budget=Budget(move_budget=1, observation_budget=1),
    )
    r = fake.run(chunk, chunk.budget, ObservationPolicy.FULL, ExecutorPolicy.SAFE)
    assert r.label == "t"
    assert r.success is True
