from pathlib import Path

import pytest

import safe_mini.worktree as worktree_module
from safe_mini.worktree import WorktreeProvisioner


def test_provision_returns_fresh_writable_copy(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "file.txt").write_text("original")

    provisioner = WorktreeProvisioner(source)
    copy_path = provisioner.provision()
    assert copy_path.exists()
    assert (copy_path / "file.txt").read_text() == "original"

    (copy_path / "file.txt").write_text("changed")
    assert (source / "file.txt").read_text() == "original"

    provisioner.cleanup()
    assert not copy_path.exists()


def test_context_manager_cleans_up(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "file.txt").write_text("original")

    with WorktreeProvisioner(source) as copy_path:
        assert copy_path.exists()
        held = copy_path
    assert not held.exists()


def test_provision_failure_removes_its_allocated_tempdir(tmp_path: Path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "file.txt").write_text("original")

    def fail_copy(*_args, **_kwargs):
        raise OSError("simulated copy failure")

    monkeypatch.setattr(worktree_module.shutil, "copytree", fail_copy)
    provisioner = WorktreeProvisioner(source, tmp_root=tmp_path)

    with pytest.raises(OSError, match="simulated copy failure"):
        provisioner.provision()

    assert provisioner.path is None
    assert not list(tmp_path.glob("safe-mini-*"))
