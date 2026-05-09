from claude.client import ask_claude
from bot.config import CLAUDE_HAIKU, MULTILINGUAL_INSTRUCTION


def route_request(user_input: str) -> str:
    """
    Routing workflow - Claude determines the type of request
    and routes it to the appropriate handler.
    """

    # Step 1 - determine request type
    routing_messages = [
        {
            "role": "user",
            "content": f"""Classify the following user request into one of these categories:
- QUESTION: user asks a question and wants an answer
- TRANSLATION: user wants to translate text
- SUMMARY: user wants a summary of text
- CODE: user wants help with code
- OTHER: anything else

Reply with ONLY the category name, nothing else.

Request: {user_input}"""
        }
    ]

    route = ask_claude(messages=routing_messages, model=CLAUDE_HAIKU).strip()

    # Step 2 - handle based on route
    if route == "QUESTION":
        system = "You are a knowledgeable assistant. Answer the question clearly and concisely."
    elif route == "TRANSLATION":
        system = "You are a professional translator. Translate the text accurately."
    elif route == "SUMMARY":
        system = "You are an expert at summarizing. Create a concise and informative summary."
    elif route == "CODE":
        system = "You are an experienced software engineer. Help with the code clearly and efficiently."
    else:
        system = "You are a helpful assistant. Help the user with their request."

    response_messages = [{"role": "user", "content": user_input}]
    response = ask_claude(messages=response_messages, system=f"{system} {MULTILINGUAL_INSTRUCTION}", model=CLAUDE_HAIKU)

    return f"🔀 Route: {route}\n\n{response}"