"""Lock in the canonical type shapes — public API stability test."""

from safe_mini.types import (
    Budget,
    Chunk,
    ExecutorPolicy,
    FailureClass,
    Observation,
    ObservationPolicy,
    RunResult,
)


def test_failure_class_taxonomy_is_seven_class():
    """The 7-class failure taxonomy is the canonical contract."""
    expected = {
        "safety-violation",
        "action-protocol-violation",
        "exhausted-ideas",
        "budget-exhausted",
        "context-starvation",
        "reward-hacking",
        "embodiment-failure",
    }
    actual = {fc.value for fc in FailureClass}
    assert actual == expected, f"FailureClass drifted: {actual ^ expected}"


def test_executor_policies_are_three():
    """Executor policy registry: open / safe / allowlist."""
    assert {ep.value for ep in ExecutorPolicy} == {"open", "safe", "allowlist"}


def test_observation_policies_are_five():
    """Observation policy registry: full / tail / headtail / structured / structured+raw-tail."""
    assert {op.value for op in ObservationPolicy} == {
        "full",
        "tail",
        "headtail",
        "structured",
        "structured+raw-tail",
    }


def test_budget_construction():
    b = Budget(move_budget=10, observation_budget=4096)
    assert b.move_budget == 10
    assert b.observation_budget == 4096


def test_chunk_construction():
    c = Chunk(
        id="chunk-1",
        description="Add a health endpoint",
        success_criteria="GET /health returns 200",
        budget=Budget(move_budget=5, observation_budget=2048),
    )
    assert c.id == "chunk-1"
    assert c.budget.move_budget == 5


def test_observation_construction():
    o = Observation(command="ls -la", output="...", returncode=0)
    assert o.command == "ls -la"
    assert o.blocked is False


def test_run_result_default_failure_class_is_none():
    r = RunResult(
        label="t",
        success=True,
        leaked_secret=False,
        blocked_commands=0,
        steps=1,
        elapsed_sec=0.1,
        final_tests_pass=True,
    )
    assert r.failure_class is None
    assert r.transcript == []
