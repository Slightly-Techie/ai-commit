import pytest

from ai_commit import config


# Fixture to automatically clean up environment variables after each test
@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Ensure a clean environment by removing test-related env vars."""
    monkeypatch.delenv("OLLAMA_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)


def test_get_ollama_url_default():
    """
    Test that get_ollama_url() returns the default value
    when the environment variable is not set.
    """
    assert config.get_ollama_url() == "http://localhost:11434"


def test_get_ollama_url_override(monkeypatch):
    """
    Test that get_ollama_url() returns the value from the
    environment variable when it is set.
    """
    test_url = "http://custom.ollama.host:12345"
    monkeypatch.setenv("OLLAMA_URL", test_url)
    assert config.get_ollama_url() == test_url


def test_get_ollama_url_empty_raises_error(monkeypatch):
    """
    Test that get_ollama_url() raises a ValueError
    if the environment variable is an empty string.
    """
    monkeypatch.setenv("OLLAMA_URL", "")
    with pytest.raises(ValueError, match="OLLAMA_URL.*cannot be an empty string"):
        config.get_ollama_url()


def test_get_ollama_model_default():
    """
    Test that get_ollama_model() returns the default value
    when the environment variable is not set.
    """
    assert config.get_ollama_model() == "llama3"


def test_get_ollama_model_override(monkeypatch):
    """
    Test that get_ollama_model() returns the value from the
    environment variable when it is set.
    """
    test_model = "codellama:latest"
    monkeypatch.setenv("OLLAMA_MODEL", test_model)
    assert config.get_ollama_model() == test_model


def test_get_ollama_model_empty_raises_error(monkeypatch):
    """
    Test that get_ollama_model() raises a ValueError
    if the environment variable is an empty string.
    """
    monkeypatch.setenv("OLLAMA_MODEL", "")
    with pytest.raises(ValueError, match="OLLAMA_MODEL.*cannot be an empty string"):
        config.get_ollama_model()
