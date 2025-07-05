import os
import stat
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_commit import hook_manager


@pytest.fixture
def git_repo(tmp_path: Path):
    """Creates a temporary, initialized git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    original_cwd = Path.cwd()
    os.chdir(repo_path)
    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        yield repo_path
    finally:
        os.chdir(original_cwd)


def test_install_local_hook(git_repo: Path):
    """Verify local hook installation creates
    an executable file with correct content."""
    hook_path = hook_manager.install_hook(is_global=False)

    expected_path = git_repo / ".git" / "hooks" / "prepare-commit-msg"
    assert hook_path == expected_path
    assert expected_path.exists()
    assert hook_manager.HOOK_SCRIPT_CONTENT in expected_path.read_text()
    assert os.stat(expected_path).st_mode & stat.S_IXUSR


def test_install_global_hook_with_config(monkeypatch, tmp_path: Path):
    """Verify global hook installation respects `core.hooksPath`."""
    global_hooks_dir = tmp_path / "my_global_hooks"

    mock_run = MagicMock(return_value=subprocess.CompletedProcess(
        args=[], returncode=0, stdout=str(global_hooks_dir)
    ))
    monkeypatch.setattr(subprocess, "run", mock_run)

    hook_path = hook_manager.install_hook(is_global=True)

    expected_path = global_hooks_dir / "prepare-commit-msg"

    assert hook_path == expected_path
    assert expected_path.exists()
    assert hook_manager.HOOK_SCRIPT_CONTENT in expected_path.read_text()
    assert os.stat(expected_path).st_mode & stat.S_IXUSR


def test_install_global_hook_fallback(monkeypatch, tmp_path: Path):
    """Verify global hook installation falls back to ~/.git_templates."""
    mock_run = MagicMock(side_effect=subprocess.CalledProcessError(1, "git"))
    monkeypatch.setattr(subprocess, "run", mock_run)
    mock_home = tmp_path / "fake_home"
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    hook_path = hook_manager.install_hook(is_global=True)

    expected_path = mock_home / ".git_templates" / "hooks" / "prepare-commit-msg"
    assert hook_path == expected_path
    assert expected_path.exists()


def test_get_local_hook_path_not_in_repo(tmp_path: Path):
    """Verify that trying to get a local hook path outside a repo fails."""
    # Ensure CWD is outside the git_repo fixture if it's used elsewhere
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(hook_manager.NotAGitRepositoryError):
            hook_manager._get_local_hooks_path()
    finally:
        os.chdir(original_cwd)
