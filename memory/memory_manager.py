from claude.client import ask_claude
from claude.structured import get_structured_response
from memory.memory_store import save_fact, get_facts
from bot.config import CLAUDE_HAIKU


def extract_and_save_facts(user_id: int, user_message: str):
    """
    Extract important facts from user message and save to memory.
    Only saves facts worth remembering long-term.
    """
    schema = """{
    "has_facts": true|false,
    "facts": ["fact1", "fact2"]
}"""

    prompt = f"""Analyze this message and extract important personal facts worth remembering long-term.
Examples of facts to save: name, profession, location, interests, preferences, goals.
Examples of what NOT to save: questions, greetings, temporary requests.

Message: {user_message}"""

    result = get_structured_response(prompt, schema)

    if result.get("has_facts"):
        for fact in result.get("facts", []):
            save_fact(user_id, fact)


def build_memory_prompt(user_id: int) -> str:
    """
    Build a memory context string to inject into system prompt.
    Returns empty string if no facts saved.
    """
    facts = get_facts(user_id)
    if not facts:
        return ""

    facts_text = "\n".join(f"- {fact}" for fact in facts)
    return f"\n\nWhat you know about this user:\n{facts_text}"


def ask_claude_with_memory(user_id: int, messages: list, base_system: str) -> str:
    """
    Ask Claude with long-term memory injected into system prompt.
    """
    memory_context = build_memory_prompt(user_id)
    system_with_memory = base_system + memory_context

    return ask_claude(messages=messages, system=system_with_memory, model=CLAUDE_HAIKU)