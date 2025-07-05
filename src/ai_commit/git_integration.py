import subprocess


class NoStagedChanges(Exception):
    """Custom exception raised when there are no staged changes to diff."""
    pass


def get_staged_diff() -> str:
    """
    Retrieves the unified diff of all staged changes in the repository.

    Uses `git diff --staged`.

    Returns:
        The git diff as a string.

    Raises:
        NoStagedChanges: If the diff is empty, meaning no files are staged.
        subprocess.CalledProcessError: If the underlying git command fails
                                     (e.g., not in a git repository).
    """
    command = ["git", "diff", "--staged"]

    # `check=True` will raise CalledProcessError on non-zero exit codes.
    # `text=True` decodes stdout/stderr as text.
    # `capture_output=True` captures stdout/stderr.
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8"
    )

    if not result.stdout:
        raise NoStagedChanges(
            "No staged changes found. Use 'git add' to stage your changes."
        )

    return result.stdout


def commit(message: str) -> None:
    """
    Commits staged changes with the provided message using `git commit -m`.

    Args:
        message: The commit message to use.

    Raises:
        subprocess.CalledProcessError: If the git command fails.
    """
    command = ["git", "commit", "-m", message]
    subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
