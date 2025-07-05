import subprocess
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from ai_commit import cli

runner = CliRunner()


@pytest.fixture
def mock_dependencies(monkeypatch):
    """A central fixture to mock all external dependencies."""
    monkeypatch.setattr(
        "ai_commit.git_integration.get_staged_diff", lambda: "fake diff")

    generated_msg = "feat: implement new feature"

    async def mock_generate_commit(*args, **kwargs):
        return generated_msg

    monkeypatch.setattr("ai_commit.service.generate_commit", mock_generate_commit)

    mock_commit_func = MagicMock()
    monkeypatch.setattr("ai_commit.git_integration.commit", mock_commit_func)

    return generated_msg, mock_commit_func


def test_cli_confirm_yes(mock_dependencies):
    """Test the flow where user confirms with 'y'."""
    generated_msg, mock_commit = mock_dependencies

    result = runner.invoke(cli.app, ["--dry-run"], input="y\n")

    assert result.exit_code == 0, result.stdout
    assert "Commit successful!" in result.stdout
    mock_commit.assert_called_once_with(generated_msg)


def test_cli_confirm_edit(mock_dependencies, monkeypatch):
    """Test the flow where user edits ('e') and then confirms ('y')."""
    _, mock_commit = mock_dependencies
    edited_msg = "fix: correct a bug after editing"

    def simulate_editor(cmd_args, **kwargs):
        temp_file_path = cmd_args[1]
        with open(temp_file_path, "w") as f:
            f.write(edited_msg)
        return subprocess.CompletedProcess(args=cmd_args, returncode=0)

    monkeypatch.setenv("EDITOR", "nano")
    mock_run = MagicMock(side_effect=simulate_editor)
    monkeypatch.setattr("subprocess.run", mock_run)

    result = runner.invoke(cli.app, ["--dry-run"], input="e\ny\n")

    assert result.exit_code == 0, result.stdout
    mock_commit.assert_called_once_with(edited_msg)
