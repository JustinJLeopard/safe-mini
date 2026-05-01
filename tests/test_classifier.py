import pytest

from safe_mini.classifier import classify_failure
from safe_mini.types import FailureClass, RunResult


def result(**kwargs) -> RunResult:
    defaults = {
        "label": "r",
        "success": False,
        "leaked_secret": False,
        "blocked_commands": 0,
        "steps": 1,
        "elapsed_sec": 0,
        "final_tests_pass": False,
    }
    defaults.update(kwargs)
    return RunResult(**defaults)


@pytest.mark.parametrize(
    ("run_result", "expected"),
    [
        (result(blocked_commands=1), FailureClass.SAFETY_VIOLATION),
        (result(action_protocol_violations=1), FailureClass.ACTION_PROTOCOL_VIOLATION),
        (result(reward_hacking_detected=True, final_tests_pass=True), FailureClass.REWARD_HACKING),
        (result(observation_budget_exhausted=True), FailureClass.BUDGET_EXHAUSTED),
        (
            result(transcript=[{"content": "[truncated to last 10 chars]"}]),
            FailureClass.CONTEXT_STARVATION,
        ),
        (result(steps=0), FailureClass.EMBODIMENT_FAILURE),
        (result(final_tests_pass=True), FailureClass.EXHAUSTED_IDEAS),
    ],
)
def test_classify_failure_taxonomy(run_result, expected):
    assert classify_failure(run_result) == expected
