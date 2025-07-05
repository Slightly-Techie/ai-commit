import os


def _get_env_var(name: str, default: str) -> str:
    """
    Retrieves an environment variable, returning a default if not set.
    Raises ValueError if the environment variable is set to an empty string.
    """
    value = os.environ.get(name, default)
    if value == "":
        raise ValueError(f"{name} environment variable cannot be an empty string.")
    return value


def get_ollama_url() -> str:
    """
    Returns the Ollama API URL.

    - Defaults to "http://localhost:11434".
    - Can be overridden by the OLLAMA_URL environment variable.
    """
    return _get_env_var("OLLAMA_URL", "http://localhost:11434")


def get_ollama_model() -> str:
    """
    Returns the Ollama model name.

    - Defaults to "llama3".
    - Can be overridden by the OLLAMA_MODEL environment variable.
    """
    return _get_env_var("OLLAMA_MODEL", "llama3.2")
