from ai_commit import service
from ai_commit.llm_provider import LLMProvider


class FakeLLMProvider(LLMProvider):
    """A mock LLM provider for testing purposes."""

    def __init__(self, response: str):
        self.system_prompt_received = None
        self.user_prompt_received = None
        self.response = response

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.system_prompt_received = system_prompt
        self.user_prompt_received = user_prompt
        return self.response


def test_generate_commit_orchestrates_correctly(monkeypatch):
    """
    Verify that generate_commit correctly orchestrates its dependencies.
    - It should load the correct prompt style.
    - It should call the provider with the correct system and user prompts.
    - It should return the stripped result from the provider.
    """
    test_diff = "diff --git a/file.py b/file.py\n--- a/file.py\n+++ b/file.py"
    test_style = "conventional"
    expected_system_prompt = "You are a helpful AI assistant."
    llm_response = "  fix(service): implement core logic  \n\n"

    # Mock the prompt_manager dependency to isolate the service
    monkeypatch.setattr(
        "ai_commit.prompt_manager.load_style",
        lambda style: expected_system_prompt if style == test_style else ""
    )

    # Create an instance of our fake provider
    fake_provider = FakeLLMProvider(response=llm_response)

    result = service.generate_commit(
        diff=test_diff,
        style=test_style,
        provider=fake_provider,
    )

    # Check that the provider was called with the correct prompts
    assert fake_provider.system_prompt_received == expected_system_prompt
    assert fake_provider.user_prompt_received == test_diff

    # Check that the final result is the stripped output of the provider
    assert result == "fix(service): implement core logic"