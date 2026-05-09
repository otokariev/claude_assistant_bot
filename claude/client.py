import anthropic
from bot.config import ANTHROPIC_API_KEY, CLAUDE_HAIKU, MAX_TOKENS
from claude.tools import NOTES_TOOLS, process_tool_call

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def ask_claude(messages: list, system: str = None, model: str = CLAUDE_HAIKU) -> str:
    """
    Basic request to Claude.
    messages - conversation history in format [{"role": "user", "content": "..."}]
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

    response = client.messages.create(**params)
    return response.content[0].text


from claude.tools import NOTES_TOOLS, process_tool_call


def ask_claude_with_tools(messages: list, system: str = None, model: str = CLAUDE_HAIKU) -> str:
    """
    Request to Claude with tool use support.
    Claude can call tools to save/get/delete notes.
    Automatically handles tool calls in a loop until final response.
    """
    params = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
        "tools": NOTES_TOOLS,
    }
    if system:
        params["system"] = system

    # Agentic loop - continue until Claude stops calling tools
    current_messages = messages.copy()

    while True:
        response = client.messages.create(**params)

        # If Claude finished - return text response
        if response.stop_reason == "end_turn":
            return response.content[0].text

        # If Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Add Claude's response to messages
            current_messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Process all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Add tool results to messages
            current_messages.append({
                "role": "user",
                "content": tool_results
            })

            # Update messages for next iteration
            params["messages"] = current_messages
        else:
            # Unexpected stop reason
            break

    return "Something went wrong."