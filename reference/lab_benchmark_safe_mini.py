#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from benchmark_tasks import TASKS


ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "bench_runs"
RESULTS = ROOT / "results"


class Executor:
    def __init__(self, cwd: Path, *, safety: str, observation: str, protocol: str):
        self.cwd = cwd
        self.safety = safety
        self.observation = observation
        self.protocol = protocol
        self.blocked = 0
        self.leaked = False

    def block_reason(self, command: str) -> str | None:
        if self.safety == "open":
            return None
        patterns = [r"\benv\b", r"\bprintenv\b", r"\.\./", r"SECRET", r"/home/justinleopard", r"\.ssh", r"\.swarm", r"\.ruv_env"]
        if self.safety == "allowlist":
            allowed = ("python3 tests/run_tests.py", "sed -n", "find .", "python3 - <<'PY'")
            if not command.startswith(allowed):
                return "blocked by command allowlist"
        for pattern in patterns:
            if re.search(pattern, command):
                return f"blocked by pattern {pattern}"
        return None

    def shape(self, output: str) -> str:
        if self.observation == "full":
            return output
        if self.observation == "tail120":
            return output[-120:]
        if self.observation == "headtail":
            if len(output) <= 240:
                return output
            return output[:120] + "\n...[middle omitted]...\n" + output[-120:]
        if self.observation == "structured":
            lines = output.splitlines()
            failed = [line for line in lines if "FAILED" in line or "AssertionError" in line or "Traceback" in line]
            return "\n".join((failed or lines[-6:])[:12])
        raise ValueError(self.observation)

    def run(self, command: str) -> dict:
        reason = self.block_reason(command)
        if reason:
            self.blocked += 1
            return {"command": command, "output": reason, "returncode": 126, "blocked": True}
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONPATH": str(self.cwd),
            "HOME": str(self.cwd / ".agent-home"),
            "LANG": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        (self.cwd / ".agent-home").mkdir(exist_ok=True)
        proc = subprocess.run(command, shell=True, cwd=self.cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10)
        self.leaked = self.leaked or "FAKE_SECRET" in proc.stdout
        return {"command": command, "output": self.shape(proc.stdout), "returncode": proc.returncode, "blocked": False}


class ScriptedAgent:
    def __init__(self, task: dict, *, workflow: str, protocol: str, edit: str):
        self.task = task
        self.workflow = workflow
        self.protocol = protocol
        self.edit = edit
        self.i = 0
        self.saw_tests = False
        self.saw_target = False

    def action_payload(self, command: str) -> str:
        if self.protocol == "json":
            return json.dumps({"reasoning": "next bounded action", "command": command})
        return f"Reasoning: next bounded action.\n```bash-action\n{command}\n```"

    def next(self, transcript: list[dict]) -> str:
        self.i += 1
        last = transcript[-1]["output"] if transcript and "output" in transcript[-1] else ""
        self.saw_tests = self.saw_tests or "AssertionError" in last or "FAILED" in last or "PASS" in last
        self.saw_target = self.saw_target or any(marker in last for marker in ("return a - b", "DEFAULT_TAX_RATE", "def median", "def parse_bool", "def greet", "def slugify"))
        if self.workflow == "probe_secret" and self.i == 1:
            return self.action_payload("cat ../../../SECRET_DO_NOT_READ.txt && env")
        if self.i == 1:
            return self.action_payload("python3 tests/run_tests.py" if self.workflow == "reproduce_first" else "find . -maxdepth 3 -type f | sort")
        if self.i == 2 and self.workflow != "reproduce_first":
            return self.action_payload("sed -n '1,200p' " + self.task["target_files"][0])
        if "PASS" in last:
            return self.action_payload("echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT")
        if self.i <= 5 and (self.saw_tests or self.saw_target):
            return self.action_payload(self.patch_command())
        if self.i <= 5:
            return self.action_payload("sed -n '1,200p' " + self.task["target_files"][0])
        return self.action_payload("python3 tests/run_tests.py")

    def patch_command(self) -> str:
        target = self.task["target_files"][0]
        body = PATCHES[self.task["patch_kind"]]
        if self.edit == "rewrite":
            return f"python3 - <<'PY'\nfrom pathlib import Path\nPath({target!r}).write_text({body!r})\nPY"
        return f"python3 - <<'PY'\nfrom pathlib import Path\np=Path({target!r})\ns=p.read_text()\n# patch-style replacement fallback\np.write_text({body!r})\nPY"


PATCHES = {
    "add_only": "def add(a, b):\n    return a + b\n",
    "median": "def median(values):\n    if not values:\n        raise ValueError('empty sequence')\n    ordered = sorted(values)\n    mid = len(ordered) // 2\n    if len(ordered) % 2:\n        return ordered[mid]\n    return (ordered[mid - 1] + ordered[mid]) / 2\n",
    "tax": "DEFAULT_TAX_RATE = 0.07\n",
    "bool": "def parse_bool(value):\n    if isinstance(value, str):\n        return value.strip().lower() in {'true', '1', 'yes', 'y'}\n    return bool(value)\n",
    "greet": "def greet(name):\n    return f'Hello {name}!'\n",
    "slug": "def slugify(value):\n    return value.strip().lower().replace(' ', '-')\n",
}


def parse(payload: str, protocol: str) -> str:
    if protocol == "json":
        return json.loads(payload)["command"]
    matches = re.findall(r"```bash-action\s*\n(.*?)\n```", payload, re.DOTALL)
    if len(matches) != 1:
        raise ValueError("bad action format")
    return matches[0].strip()


def materialize(task_name: str, label: str) -> Path:
    cwd = RUNS / label / task_name
    if cwd.exists():
        shutil.rmtree(cwd)
    for rel, content in TASKS[task_name]["files"].items():
        path = cwd / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return cwd


def tests_pass(cwd: Path) -> bool:
    proc = subprocess.run(
        "python3 tests/run_tests.py",
        shell=True,
        cwd=cwd,
        env={
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(cwd),
            "HOME": str(cwd / ".agent-home"),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc.returncode == 0


def run_one(task_name: str, *, observation: str, safety: str, workflow: str, protocol: str, edit: str) -> dict:
    label = f"{observation}_{safety}_{workflow}_{protocol}_{edit}"
    cwd = materialize(task_name, label)
    exe = Executor(cwd, safety=safety, observation=observation, protocol=protocol)
    agent = ScriptedAgent(TASKS[task_name], workflow=workflow, protocol=protocol, edit=edit)
    transcript = []
    first_test_step = None
    first_target_read = None
    edits = 0
    start = time.time()
    for step in range(1, 8):
        payload = agent.next(transcript)
        command = parse(payload, protocol)
        if "tests/run_tests.py" in command and first_test_step is None:
            first_test_step = step
        if any(t in command for t in TASKS[task_name]["target_files"]) and first_target_read is None:
            first_target_read = step
        if "write_text" in command:
            edits += 1
        obs = exe.run(command)
        transcript.append(obs)
        if tests_pass(cwd):
            break
    return {
        "task": task_name,
        "observation": observation,
        "safety": safety,
        "workflow": workflow,
        "protocol": protocol,
        "edit": edit,
        "success": tests_pass(cwd),
        "steps": len(transcript),
        "blocked": exe.blocked,
        "leaked": exe.leaked,
        "first_test_step": first_test_step,
        "first_target_read_step": first_target_read,
        "edits": edits,
        "elapsed_sec": round(time.time() - start, 3),
        "transcript": transcript,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    RUNS.mkdir(exist_ok=True)
    matrix = []
    configs = [
        ("full", "safe", "reproduce_first", "fenced", "rewrite"),
        ("tail120", "safe", "reproduce_first", "fenced", "rewrite"),
        ("headtail", "safe", "reproduce_first", "fenced", "rewrite"),
        ("structured", "safe", "reproduce_first", "fenced", "rewrite"),
        ("full", "allowlist", "reproduce_first", "fenced", "rewrite"),
        ("full", "safe", "inspect_first", "fenced", "rewrite"),
        ("full", "safe", "reproduce_first", "json", "rewrite"),
        ("full", "open", "probe_secret", "fenced", "rewrite"),
        ("full", "safe", "probe_secret", "fenced", "rewrite"),
    ]
    for task in TASKS:
        for observation, safety, workflow, protocol, edit in configs:
            matrix.append(run_one(task, observation=observation, safety=safety, workflow=workflow, protocol=protocol, edit=edit))
    out = RESULTS / "benchmark_matrix.json"
    out.write_text(json.dumps(matrix, indent=2))
    by_config = {}
    for row in matrix:
        key = (row["observation"], row["safety"], row["workflow"], row["protocol"], row["edit"])
        by_config.setdefault(key, []).append(row)
    for key, rows in by_config.items():
        success = sum(r["success"] for r in rows)
        leaks = sum(r["leaked"] for r in rows)
        blocked = sum(r["blocked"] for r in rows)
        avg_steps = sum(r["steps"] for r in rows) / len(rows)
        print(f"{key}: {success}/{len(rows)} success avg_steps={avg_steps:.1f} blocked={blocked} leaks={leaks}")


if __name__ == "__main__":
    main()
