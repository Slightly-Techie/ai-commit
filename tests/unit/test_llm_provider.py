from ai_commit.llm_provider import LLMProvider, MockProvider


def test_mock_provider_conforms_to_protocol():
    """
    Verify that MockProvider is a valid implementation of the LLMProvider protocol.
    This test leverages Python's structural typing with Protocols.
    """
    provider = MockProvider()

    assert isinstance(provider, LLMProvider)

def test_mock_provider_returns_templated_string():
    """
    Verify that MockProvider.complete returns a predictable, templated string
    that includes placeholders for the system and user prompts.
    """
    provider = MockProvider()
    system_prompt = "You are a test assistant."
    user_prompt = "This is a test diff."

    result = provider.complete(system_prompt, user_prompt)

    assert "Mock Response" in result
    assert f"System Prompt: {system_prompt}" in result
    assert f"User Prompt: {user_prompt}" in result

def test_mock_provider_with_empty_prompts():
    """
    Ensure the MockProvider handles empty strings without errors.
    """
    provider = MockProvider()
    system_prompt = ""
    user_prompt = ""

    result = provider.complete(system_prompt, user_prompt)

    assert "Mock Response" in result
    assert "System Prompt: " in result
    assert "User Prompt: " in result
