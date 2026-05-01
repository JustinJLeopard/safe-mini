import json

from safe_mini.observation import apply_observation_policy
from safe_mini.types import Observation, ObservationPolicy


def observation() -> Observation:
    return Observation(
        command="cmd",
        output="",
        returncode=7,
        stdout="out-" + ("x" * 40),
        stderr="err-" + ("y" * 40),
        raw_output="out-" + ("x" * 40) + "err-" + ("y" * 40),
    )


def test_full_truncates_to_budget():
    shaped = apply_observation_policy(observation(), ObservationPolicy.FULL, 20)
    assert shaped.truncated is True
    assert shaped.output.startswith("[truncated to last 20 chars]")


def test_tail_truncates_to_last_chars():
    shaped = apply_observation_policy(observation(), ObservationPolicy.TAIL, 10)
    assert shaped.output.endswith("y" * 10)


def test_headtail_keeps_start_and_end():
    shaped = apply_observation_policy(observation(), ObservationPolicy.HEADTAIL, 20)
    assert "out-" in shaped.output
    assert shaped.output.endswith("y" * 10)


def test_structured_policy_emits_json_shape():
    shaped = apply_observation_policy(observation(), ObservationPolicy.STRUCTURED, 20)
    payload = json.loads(shaped.output)
    assert payload["returncode"] == 7
    assert payload["stdout"].startswith("out-")
    assert payload["stderr"].startswith("err-")


def test_structured_raw_tail_includes_raw_tail():
    shaped = apply_observation_policy(observation(), ObservationPolicy.STRUCTURED_RAW_TAIL, 15)
    payload = json.loads(shaped.output)
    assert payload["raw_tail"].endswith("y" * 15)
