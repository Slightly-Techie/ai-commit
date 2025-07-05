import subprocess
from unittest.mock import ANY, MagicMock

import pytest
from typer.testing import CliRunner

from ai_commit import cli
from ai_commit.git_integration import NoStagedChanges

runner = CliRunner()


@pytest.fixture
def mock_dependencies(monkeypatch):
    """A central fixture to mock dependencies, but NOT subprocess.run."""
    monkeypatch.setattr(
        "ai_commit.git_integration.get_staged_diff", lambda: "fake diff")

    generated_msg = "feat: implement new feature"
    monkeypatch.setattr(
        "ai_commit.service.generate_commit",
        lambda **kwargs: generated_msg
    )

    mock_commit_func = MagicMock()
    monkeypatch.setattr("ai_commit.git_integration.commit", mock_commit_func)

    return generated_msg, mock_commit_func


def test_cli_confirm_yes(mock_dependencies):
    """Test the flow where user confirms with 'y'."""
    generated_msg, mock_commit = mock_dependencies

    result = runner.invoke(cli.app, input="y\n")

    assert result.exit_code == 0, result.stdout
    assert "Commit successful!" in result.stdout
    mock_commit.assert_called_once_with(generated_msg)


def test_cli_confirm_no(mock_dependencies):
    """Test the flow where user aborts with 'n'."""
    _, mock_commit = mock_dependencies

    result = runner.invoke(cli.app, input="n\n")

    assert result.exit_code == 0, result.stdout
    assert "Commit aborted." in result.stdout
    mock_commit.assert_not_called()


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

    result = runner.invoke(cli.app, input="e\ny\n")

    assert result.exit_code == 0, result.stdout

    mock_run.assert_called_once_with(['nano', ANY], check=True)
    mock_commit.assert_called_once_with(edited_msg)


def test_cli_edit_no_editor_set(mock_dependencies, monkeypatch):
    _, mock_commit = mock_dependencies
    monkeypatch.delenv("EDITOR", raising=False)

    result = runner.invoke(cli.app, input="e\n")

    assert result.exit_code == 1
    assert "EDITOR environment variable not set." in result.stdout
    mock_commit.assert_not_called()


def test_cli_no_staged_changes_error(monkeypatch):
    monkeypatch.setattr(
        "ai_commit.git_integration.get_staged_diff",
        lambda: (_ for _ in ()).throw(NoStagedChanges("No changes to diff."))
    )
    result = runner.invoke(cli.app)
    assert result.exit_code == 1
    assert "Error:" in result.stdout
    assert "No changes to diff." in result.stdout
