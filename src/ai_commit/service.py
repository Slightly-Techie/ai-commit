from ai_commit import prompt_manager
from ai_commit.llm_provider import LLMProvider


def generate_commit(diff: str, style: str, provider: LLMProvider) -> str:
    """
    Generates a commit message by orchestrating prompt loading and an LLM call.

    This is a pure domain function, decoupled from I/O. It relies on a
    prompt loader and an LLM provider passed in as dependencies.

    Args:
        diff: The git diff to be used as the user prompt.
        style: The name of the prompt style to use.
        provider: An object that conforms to the LLMProvider protocol.

    Returns:
        The generated commit message, stripped of leading/trailing whitespace.
    """
    # Build the system prompt from the specified style
    system_prompt = prompt_manager.load_style(style)

    # The user prompt is the git diff itself
    user_prompt = diff

    # Call the provider to get the completion
    completion = provider.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    return completion.strip()
