from claude.client import ask_claude
from bot.config import CLAUDE_HAIKU, MULTILINGUAL_INSTRUCTION


def run_chain(user_input: str) -> str:
    """
    Sequential chain - output of each step is input for the next.
    Example: translate -> summarize -> format as bullet points.
    """

    # Step 1 - translate to English if needed
    step1_messages = [
        {"role": "user", "content": f"Translate the following text to English. If already in English, return as is:\n\n{user_input}"}
    ]
    translated = ask_claude(messages=step1_messages, model=CLAUDE_HAIKU, system=MULTILINGUAL_INSTRUCTION)

    # Step 2 - summarize
    step2_messages = [
        {"role": "user", "content": f"Summarize the following text in 3 sentences:\n\n{translated}"}
    ]
    summarized = ask_claude(messages=step2_messages, model=CLAUDE_HAIKU, system=MULTILINGUAL_INSTRUCTION)

    # Step 3 - format as bullet points
    step3_messages = [
        {"role": "user", "content": f"Convert the following summary into clear bullet points:\n\n{summarized}"}
    ]
    final = ask_claude(messages=step3_messages, model=CLAUDE_HAIKU, system=MULTILINGUAL_INSTRUCTION)

    return f"🔗 Chain result:\n\n{final}"