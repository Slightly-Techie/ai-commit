import subprocess
from unittest.mock import MagicMock

import pytest

from ai_commit import git_integration


def test_get_staged_diff_with_changes(monkeypatch):
    """
    Verify get_staged_diff returns the diff when changes are staged.
    """
    expected_diff = "diff --git a/file.py b/file.py\n--- a/file.py\n+++ b/file.py"
    mock_result = subprocess.CompletedProcess(
        args=["git", "diff", "--staged"],
        returncode=0,
        stdout=expected_diff,
        stderr=""
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    diff = git_integration.get_staged_diff()

    assert diff == expected_diff


def test_get_staged_diff_no_changes_raises_exception(monkeypatch):
    """
    Verify get_staged_diff raises NoStagedChanges when the diff is empty.
    """

    mock_result = subprocess.CompletedProcess(
        args=["git", "diff", "--staged"],
        returncode=0,
        stdout="",
        stderr=""
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    with pytest.raises(
            git_integration.NoStagedChanges,
            match="No staged changes found"):
        git_integration.get_staged_diff()


def test_get_staged_diff_git_error_propagates_exception(monkeypatch):
    """
    Verify get_staged_diff propagates CalledProcessError if git command fails.
    """
    error = subprocess.CalledProcessError(
        returncode=128,
        cmd=["git", "diff", "--staged"],
        stderr="fatal: not a git repository"
    )
    monkeypatch.setattr(
        subprocess, "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(error))

    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        git_integration.get_staged_diff()

    assert exc_info.value.returncode == 128
    assert "fatal: not a git repository" in exc_info.value.stderr


# tests/unit/test_git_integration.py
# (Add this new test function to the existing file)

def test_commit_calls_subprocess_correctly(monkeypatch):
    """
    Verify commit() calls `git commit -m <message>` via subprocess.run.
    """
    # Arrange
    test_message = "feat: add interactive commit feature"
    # We need a mock to capture the arguments passed to subprocess.run
    mock_run = MagicMock(
        return_value=subprocess.CompletedProcess(args=[], returncode=0))
    monkeypatch.setattr(subprocess, "run", mock_run)

    # Act
    git_integration.commit(test_message)

    # Assert
    expected_command = ["git", "commit", "-m", test_message]
    mock_run.assert_called_once_with(
        expected_command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
