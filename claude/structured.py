import json
from claude.client import ask_claude
from bot.config import CLAUDE_HAIKU


def get_structured_response(user_input: str, output_schema: str) -> dict:
    """
    Get structured JSON response from Claude.
    user_input - user's request
    output_schema - description of expected JSON structure
    """
    messages = [
        {
            "role": "user",
            "content": f"""{user_input}

Respond ONLY with a valid JSON object matching this schema:
{output_schema}

No explanation, no markdown, no code blocks. Just raw JSON."""
        }
    ]

    response = ask_claude(messages=messages, model=CLAUDE_HAIKU)

    # Strip Markdown code blocks if Claude added them anyway
    clean = response.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    return json.loads(clean)


def analyze_sentiment(text: str) -> str:
    """Analyze sentiment of text and return formatted result."""
    schema = """{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,
    "key_emotions": ["emotion1", "emotion2"],
    "summary": "one sentence summary"
}"""

    result = get_structured_response(
        f"Analyze the sentiment of this text: {text}",
        schema
    )

    emoji = {"positive": "😊", "negative": "😔", "neutral": "😐"}
    sentiment = result.get("sentiment", "neutral")

    return (
        f"{emoji.get(sentiment, '😐')} Sentiment: <b>{sentiment}</b>\n"
        f"Confidence: {int(result.get('confidence', 0) * 100)}%\n"
        f"Emotions: {', '.join(result.get('key_emotions', []))}\n"
        f"Summary: {result.get('summary', '')}"
    )


def extract_tasks(text: str) -> str:
    """Extract action items and tasks from text."""
    schema = """{
    "tasks": [
        {
            "task": "task description",
            "priority": "high|medium|low",
            "deadline": "deadline or null"
        }
    ]
}"""

    result = get_structured_response(
        f"Extract all tasks and action items from this text: {text}",
        schema
    )

    tasks = result.get("tasks", [])
    if not tasks:
        return "No tasks found in the text."

    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    lines = ["📋 <b>Extracted tasks:</b>\n"]

    for t in tasks:
        priority = t.get("priority", "medium")
        emoji = priority_emoji.get(priority, "🟡")
        deadline = t.get("deadline")
        deadline_str = f" — {deadline}" if deadline else ""
        lines.append(f"{emoji} {t.get('task', '')}{deadline_str}")

    return "\n".join(lines)