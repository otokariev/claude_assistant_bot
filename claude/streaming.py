from anthropic import Anthropic
from bot.config import ANTHROPIC_API_KEY, CLAUDE_HAIKU, MAX_TOKENS

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def stream_claude(messages: list, system: str = None, model: str = CLAUDE_HAIKU):
    """
    Stream response from Claude word by word.
    Returns a generator that yields text chunks.
    messages - conversation history
    system - system prompt
    model - Claude model
    """
    params = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
    }
    if system:
        params["system"] = system

    with client.messages.stream(**params) as stream:
        for text in stream.text_stream:
            yield text