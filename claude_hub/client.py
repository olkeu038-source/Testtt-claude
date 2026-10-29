"""Single place where the app talks to the Claude API."""

import anthropic

from .store import build_system_prompt, get_api_key, load_settings


def ask(history):
    """Send the conversation so far and return Claude's reply text."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "No API key set. Add one in the admin panel or set ANTHROPIC_API_KEY."
        )

    settings = load_settings()
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=settings["model"],
        max_tokens=settings["max_tokens"],
        system=build_system_prompt(),
        messages=history,
    )
    return response.content[0].text
