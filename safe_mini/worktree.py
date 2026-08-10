"""Fresh worktree provisioning for runner executions."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

SANITIZED_PATH = "/usr/local/bin:/usr/bin:/bin"


class WorktreeProvisioner:
    """Copy a base repository or fixture into an isolated temporary worktree."""

    def __init__(self, base_repo: str | Path, *, tmp_root: str | Path | None = None) -> None:
        self.base_repo = Path(base_repo).resolve()
        self.tmp_root = Path(tmp_root).resolve() if tmp_root else None
        self._tempdir: Path | None = None
        self.path: Path | None = None

    def provision(self) -> Path:
        if not self.base_repo.exists() or not self.base_repo.is_dir():
            raise FileNotFoundError(f"base repo does not exist: {self.base_repo}")

        self.cleanup()
        self._tempdir = Path(tempfile.mkdtemp(prefix="safe-mini-", dir=self.tmp_root))
        try:
            target = self._tempdir / "repo"
            ignore = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".mypy_cache")
            shutil.copytree(self.base_repo, target, ignore=ignore)
            home = target / ".agent-home"
            home.mkdir(mode=0o700, exist_ok=True)
            self.path = target
            return target
        except Exception:
            self.cleanup()
            raise

    def env_for(self, cwd: Path) -> dict[str, str]:
        return {
            "PATH": os.environ.get("PATH") or SANITIZED_PATH,
            "PYTHONPATH": str(cwd),
            "HOME": str(cwd / ".agent-home"),
            "LANG": "C.UTF-8",
        }

    def cleanup(self) -> None:
        if self._tempdir is not None:
            if self._tempdir.exists():
                shutil.rmtree(self._tempdir)
            self._tempdir = None
        self.path = None

    def __enter__(self) -> Path:
        return self.provision()

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.cleanup()
