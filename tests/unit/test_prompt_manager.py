from pathlib import Path

import pytest

from ai_commit import prompt_manager


@pytest.fixture
def prompt_styles_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory with dummy prompt files for testing."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "pirate.txt").write_text("Ahoy, write a commit like a pirate!")
    ((prompts_dir / "conventional.txt").write_text(
        "Follow the conventional commit spec."
    ))
    # Add a non-txt file to ensure it's ignored
    (prompts_dir / "ignored.md").write_text("This should not be listed.")
    return prompts_dir

def test_list_styles_returns_sorted_names(prompt_styles_dir, monkeypatch):
    """
    Verify that list_styles() finds .txt files and returns their
    names sorted alphabetically.
    """
    monkeypatch.setattr(prompt_manager, "PROMPT_DIR", prompt_styles_dir)
    # Clear cache to ensure we're testing the file system logic
    prompt_manager.list_styles.cache_clear()

    styles = prompt_manager.list_styles()
    assert styles == ["conventional", "pirate"]

def test_load_style_returns_file_content(prompt_styles_dir, monkeypatch):
    """
    Verify that load_style() correctly reads and returns the content
    of a given prompt style.
    """
    monkeypatch.setattr(prompt_manager, "PROMPT_DIR", prompt_styles_dir)
    # Clear cache for this specific test
    prompt_manager.load_style.cache_clear()

    content = prompt_manager.load_style("pirate")
    assert "Ahoy, write a commit like a pirate!" in content

    content = prompt_manager.load_style("conventional")
    assert "Follow the conventional commit spec." in content

def test_load_style_raises_keyerror_for_missing_style(prompt_styles_dir, monkeypatch):
    """
    Verify that load_style() raises a KeyError when the requested
    style does not exist.
    """
    monkeypatch.setattr(prompt_manager, "PROMPT_DIR", prompt_styles_dir)
    prompt_manager.list_styles.cache_clear()
    prompt_manager.load_style.cache_clear()

    with pytest.raises(KeyError, match="Prompt style 'non_existent' not found."):
        prompt_manager.load_style("non_existent")

def test_list_styles_returns_empty_list_if_dir_missing(tmp_path, monkeypatch):
    """
    Verify list_styles() returns an empty list if the prompts dir doesn't exist.
    """
    missing_dir = tmp_path / "non_existent_prompts"
    monkeypatch.setattr(prompt_manager, "PROMPT_DIR", missing_dir)
    prompt_manager.list_styles.cache_clear()

    assert prompt_manager.list_styles() == []
