from functools import lru_cache
from pathlib import Path

PROMPT_DIR = Path(__file__).parent / "prompts"


@lru_cache(maxsize=1)
def list_styles() -> list[str]:
    """
    Discovers available prompt styles from the prompts directory.

    Returns:
        A sorted list of available style names (filenames without .txt).
    """
    if not PROMPT_DIR.is_dir():
        return []

    return sorted([p.stem for p in PROMPT_DIR.glob("*.txt")])


@lru_cache(maxsize=32)
def load_style(name: str) -> str:
    """
    Loads the content of a specific prompt style.

    Args:
        name: The name of the style to load (e.g., "conventional").

    Returns:
        The content of the prompt file as a string.

    Raises:
        KeyError: If the specified style name does not correspond to a file.
    """
    prompt_file = PROMPT_DIR / f"{name}.txt"
    if not prompt_file.is_file():
        available = list_styles()
        raise KeyError(
            f"Prompt style '{name}' not found. Available styles: {available}"
        )
    print(prompt_file.read_text(encoding="utf-8"))
    return prompt_file.read_text(encoding="utf-8")
