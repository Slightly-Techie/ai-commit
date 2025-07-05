import stat
import subprocess
from pathlib import Path


class NotAGitRepositoryError(Exception):
    """Raised when a git-specific operation is attempted outside a git repo."""
    pass


HOOK_SCRIPT_CONTENT = """#!/bin/sh
# Hook created by ai-commit.

# --- Skip if not in an interactive session
if ! [ -t 1 ]; then
  exit 0
fi

# --- Skip if a message source is already provided (e.g., -m, -F, -C)
# $2 can be "message", "template", "squash", or "commit".
if [ -n "$2" ]; then
  case "$2" in
    message|template|squash|commit) exit 0;;
  esac
fi

# --- Execute ai-commit interactively
# Re-connect stdin to the terminal for interactive prompts
exec < /dev/tty
# The `ai-commit` command must be in the user's PATH
ai-commit
"""


def _get_git_root() -> Path:
    """Finds the root of the current git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise NotAGitRepositoryError("Not operating inside a git repository.")


def _get_local_hooks_path() -> Path:
    """Gets the path for local git hooks."""
    git_root = _get_git_root()
    return git_root / ".git" / "hooks"


def _get_global_hooks_path() -> Path:
    """Gets the path for global git hooks, using config or a fallback."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            check=True, capture_output=True, text=True
        )
        path_str = result.stdout.strip()
        if path_str:
            return Path(path_str)
    except subprocess.CalledProcessError:
        # This is expected if the config is not set, so we fall through
        pass

    return Path.home() / ".git_templates"


def install_hook(is_global: bool) -> Path:
    """
    Creates the prepare-commit-msg hook script in the appropriate directory.

    Args:
        is_global: If True, installs to the global hooks path.
                   Otherwise, installs to the local .git/hooks directory.

    Returns:
        The path to the created hook file.
    """
    if is_global:
        base_path = _get_global_hooks_path()

        if ".git_templates" in str(base_path):
            target_dir = base_path / "hooks"
        else:
            target_dir = base_path
    else:
        target_dir = _get_local_hooks_path()

    target_dir.mkdir(parents=True, exist_ok=True)
    hook_path = target_dir / "prepare-commit-msg"

    hook_path.write_text(HOOK_SCRIPT_CONTENT)

    hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR)

    return hook_path
