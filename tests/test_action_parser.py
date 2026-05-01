import pytest

from safe_mini.action_parser import ActionFormat, ActionParseError, parse_action
from safe_mini.classifier import classify_failure
from safe_mini.types import FailureClass, RunResult


def test_parse_fenced_bash_action():
    parsed = parse_action("Reasoning\n```bash-action\npython3 tests/run_tests.py\n```")
    assert parsed.command == "python3 tests/run_tests.py"
    assert parsed.format == ActionFormat.FENCED_BASH


def test_parse_json_action():
    parsed = parse_action('{"action": "bash", "command": "echo ok"}')
    assert parsed.command == "echo ok"
    assert parsed.format == ActionFormat.JSON


@pytest.mark.parametrize(
    "text",
    [
        "no action",
        "```bash-action\none\n```\n```bash-action\ntwo\n```",
        '{"action": "read", "command": "echo nope"}',
        '{"action": "bash"}',
        "{not json",
    ],
)
def test_malformed_inputs_classify_as_action_protocol_violation(text):
    with pytest.raises(ActionParseError):
        parse_action(text)
    result = RunResult(
        label="bad-action",
        success=False,
        leaked_secret=False,
        blocked_commands=0,
        steps=0,
        elapsed_sec=0,
        final_tests_pass=False,
        action_protocol_violations=1,
    )
    assert classify_failure(result) == FailureClass.ACTION_PROTOCOL_VIOLATION
