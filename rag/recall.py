from rag.conversation_memory import search_history
from claude.client import ask_claude
from bot.config import CLAUDE_SONNET, MULTILINGUAL_INSTRUCTION


def answer_with_recall(user_id: int, question: str, project: str) -> str:
    """Answer a question based on stored conversation history of a project."""
    relevant = search_history(user_id, question, project, n_results=5)

    if not relevant:
        return "No relevant history found in this project."

    context = "\n\n".join([f"{m['role']}: {m['text']}" for m in relevant])

    system_prompt = f"""You are a helpful assistant that answers questions based on past conversation history.
Answer only based on the context provided. If the answer is not in the context, say so.
{MULTILINGUAL_INSTRUCTION}"""

    messages = [
        {"role": "user", "content": f"Past conversation excerpts:\n{context}\n\nQuestion: {question}"}
    ]

    return ask_claude(messages=messages, system=system_prompt, model=CLAUDE_SONNET)