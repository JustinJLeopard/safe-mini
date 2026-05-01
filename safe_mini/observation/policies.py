"""Observation shaping policies and final test checks."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from safe_mini.types import Observation, ObservationPolicy
from safe_mini.worktree import SANITIZED_PATH


def apply_observation_policy(
    observation: Observation, policy: ObservationPolicy, limit: int
) -> Observation:
    """Return a copy of ``observation`` with output shaped to the requested policy."""

    limit = max(limit, 0)
    if policy in {ObservationPolicy.FULL, ObservationPolicy.TAIL}:
        output, truncated = _truncate_tail(observation.raw_output or observation.output, limit)
    elif policy == ObservationPolicy.HEADTAIL:
        output, truncated = _headtail(observation.raw_output or observation.output, limit)
    elif policy == ObservationPolicy.STRUCTURED:
        output, truncated = _structured(observation, include_raw_tail=False, limit=limit)
    elif policy == ObservationPolicy.STRUCTURED_RAW_TAIL:
        output, truncated = _structured(observation, include_raw_tail=True, limit=limit)
    else:
        raise ValueError(f"unknown observation policy: {policy}")

    return Observation(
        command=observation.command,
        output=output,
        returncode=observation.returncode,
        blocked=observation.blocked,
        stdout=observation.stdout,
        stderr=observation.stderr,
        raw_output=observation.raw_output,
        truncated=observation.truncated or truncated,
        timed_out=observation.timed_out,
    )


def final_tests_pass(cwd: str | Path, *, command: str = "python3 tests/run_tests.py") -> bool:
    """Run the repo's final verification command in the scoped environment."""

    cwd_path = Path(cwd)
    proc = subprocess.run(
        command,
        shell=True,
        cwd=cwd_path,
        env={
            "PATH": os.environ.get("PATH") or SANITIZED_PATH,
            "PYTHONPATH": str(cwd_path),
            "HOME": str(cwd_path / ".agent-home"),
            "LANG": "C.UTF-8",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=10,
    )
    return proc.returncode == 0


def _truncate_tail(text: str, limit: int) -> tuple[str, bool]:
    if limit == 0:
        return "", bool(text)
    if len(text) <= limit:
        return text, False
    return f"[truncated to last {limit} chars]\n{text[-limit:]}", True


def _headtail(text: str, limit: int) -> tuple[str, bool]:
    if limit == 0:
        return "", bool(text)
    if len(text) <= limit:
        return text, False
    head_len = limit // 2
    tail_len = limit - head_len
    return (
        f"[truncated to first {head_len} and last {tail_len} chars]\n"
        f"{text[:head_len]}\n...\n{text[-tail_len:]}",
        True,
    )


def _structured(
    observation: Observation, *, include_raw_tail: bool, limit: int
) -> tuple[str, bool]:
    payload: dict[str, object] = {
        "command": observation.command,
        "returncode": observation.returncode,
        "blocked": observation.blocked,
        "timed_out": observation.timed_out,
        "stdout_chars": len(observation.stdout),
        "stderr_chars": len(observation.stderr),
    }
    truncated = False
    if include_raw_tail:
        raw_tail, truncated = _truncate_tail(observation.raw_output or observation.output, limit)
        payload["raw_tail"] = raw_tail
    else:
        payload["stdout"] = observation.stdout
        payload["stderr"] = observation.stderr
    return json.dumps(payload, sort_keys=True), truncated
