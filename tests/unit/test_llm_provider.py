import httpx
import pytest
import respx

from ai_commit.llm_provider import (
    LLMProvider,
    MockProvider,
    OllamaConnectionError,
    OllamaProvider,
)

TEST_OLLAMA_URL = "http://testhost:12345"
TEST_MODEL = "test-llama"


@pytest.fixture
def mock_config(monkeypatch):
    """Mocks the config functions to return predictable values."""
    monkeypatch.setattr("ai_commit.config.get_ollama_url", lambda: TEST_OLLAMA_URL)
    monkeypatch.setattr("ai_commit.config.get_ollama_model", lambda: TEST_MODEL)


@respx.mock
@pytest.mark.asyncio
async def test_ollama_provider_success(mock_config):
    """Verify OllamaProvider returns a valid response on HTTP 200."""
    expected_response = "feat: implement the ollama provider"
    respx.post(f"{TEST_OLLAMA_URL}/api/generate").mock(
        return_value=httpx.Response(200, json={"response": expected_response})
    )

    provider = OllamaProvider()

    result = await provider.complete("system prompt", "user prompt")

    assert result == expected_response


@respx.mock
@pytest.mark.asyncio
async def test_ollama_provider_raises_on_timeout(mock_config):
    """Verify OllamaProvider raises OllamaConnectionError on timeout."""

    respx.post(f"{TEST_OLLAMA_URL}/api/generate").mock(
        side_effect=httpx.TimeoutException("Connection timed out")
    )

    provider = OllamaProvider()

    with pytest.raises(OllamaConnectionError, match="Connection to Ollama failed:"):
        await provider.complete("system", "user")


@respx.mock
@pytest.mark.asyncio
async def test_ollama_provider_raises_on_http_error(mock_config):
    """Verify OllamaProvider raises OllamaConnectionError on 500 status."""

    respx.post(f"{TEST_OLLAMA_URL}/api/generate").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )

    provider = OllamaProvider()

    with pytest.raises(OllamaConnectionError,
                       match="Ollama API returned an error: 500"):
        await provider.complete("system", "user")




def test_mock_provider_conforms_to_protocol():
    """
    Verify that MockProvider is a valid implementation of the LLMProvider protocol.
    This test leverages Python's structural typing with Protocols.
    """
    assert isinstance(MockProvider(), LLMProvider)

@pytest.mark.asyncio
async def test_mock_provider_returns_templated_string():
    """
    Verify that MockProvider.complete returns a predictable, templated string
    that includes placeholders for the system and user prompts.
    """
    provider = MockProvider()
    system_prompt = "You are a test assistant."
    user_prompt = "This is a test diff."

    result = await provider.complete(system_prompt, user_prompt)

    assert "Mock Response" in result
    assert f"System Prompt: {system_prompt}" in result
    assert f"User Prompt: {user_prompt}" in result

async def test_mock_provider_with_empty_prompts():
    """
    Ensure the MockProvider handles empty strings without errors.
    """
    provider = MockProvider()
    system_prompt = ""
    user_prompt = ""

    result = await provider.complete(system_prompt, user_prompt)

    assert "Mock Response" in result
    assert "System Prompt: " in result
    assert "User Prompt: " in result
