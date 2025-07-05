from typer.testing import CliRunner

from ai_commit import cli
from ai_commit.git_integration import NoStagedChanges

# Instantiate the runner
runner = CliRunner()


def test_cli_dry_run_happy_path(monkeypatch):
    """
    Test the happy path with --dry-run.
    It should use the MockProvider and print the formatted mock output.
    """

    mock_diff = "diff --git a/file.py b/file.py"
    mock_prompt_content = "System prompt for testing"
    monkeypatch.setattr("ai_commit.git_integration.get_staged_diff", lambda: mock_diff)
    monkeypatch.setattr("ai_commit.prompt_manager.load_style",
                        lambda style: mock_prompt_content)

    result = runner.invoke(cli.app, ["--style", "conventional", "--print", "--dry-run"])

    assert result.exit_code == 0
    assert "Dry run mode" in result.stdout
    assert "Generating commit message..." in result.stdout
    assert "Generated Commit Message:" in result.stdout
    # Check that the mock provider's output (which includes prompts) is present
    assert "Mock Response" in result.stdout
    assert f"System Prompt: {mock_prompt_content}" in result.stdout
    assert f"User Prompt: {mock_diff}" in result.stdout


def test_cli_no_staged_changes_error(monkeypatch):
    """
    Test that the CLI handles the NoStagedChanges exception gracefully.
    """

    def raise_no_staged_changes():
        raise NoStagedChanges("No changes to diff.")

    monkeypatch.setattr(
        "ai_commit.git_integration.get_staged_diff", raise_no_staged_changes
    )

    result = runner.invoke(cli.app, ["--print"])

    assert result.exit_code == 1
    assert "Error:" in result.stdout
    assert "No changes to diff." in result.stdout
