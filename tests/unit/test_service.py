import pytest

from ai_commit import service
from ai_commit.llm_provider import LLMProvider


# The fake provider must conform to the async protocol
class FakeLLMProvider(LLMProvider):
    def __init__(self, response: str):
        self.system_prompt_received = None
        self.user_prompt_received = None
        self.response = response

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.system_prompt_received = system_prompt
        self.user_prompt_received = user_prompt
        return self.response


@pytest.mark.asyncio
async def test_generate_commit_orchestrates_correctly(monkeypatch):
    """
    Verify that async generate_commit correctly orchestrates its dependencies.
    """
    test_diff = "diff --git a/file.py b/file.py"
    test_style = "conventional"
    expected_system_prompt = "You are a helpful AI assistant."
    llm_response = "  fix(service): implement core logic  \n\n"

    monkeypatch.setattr(
        "ai_commit.prompt_manager.load_style",
        lambda style: expected_system_prompt if style == test_style else ""
    )

    fake_provider = FakeLLMProvider(response=llm_response)

    result = await service.generate_commit(
        diff=test_diff,
        style=test_style,
        provider=fake_provider,
    )

    assert fake_provider.system_prompt_received == expected_system_prompt
    assert fake_provider.user_prompt_received == test_diff
    assert result == "fix(service): implement core logic"
