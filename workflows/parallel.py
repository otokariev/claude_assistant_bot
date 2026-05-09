import asyncio
from anthropic import Anthropic
from bot.config import ANTHROPIC_API_KEY, CLAUDE_HAIKU, MAX_TOKENS

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def ask_claude_sync(prompt: str) -> str:
    """Single synchronous request to Claude."""
    response = client.messages.create(
        model=CLAUDE_HAIKU,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


async def run_parallel(user_input: str) -> str:
    """
    Parallel workflow - analyze text from multiple perspectives simultaneously.
    All requests run at the same time, not sequentially.
    """
    prompts = [
        f"Analyze the main idea of this text in 2 sentences:\n\n{user_input}",
        f"What are the key facts in this text? List them briefly:\n\n{user_input}",
        f"What questions does this text raise? List 3 questions:\n\n{user_input}",
    ]

    # Run all requests in parallel using thread pool
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, ask_claude_sync, prompt)
        for prompt in prompts
    ]
    results = await asyncio.gather(*tasks)

    return (
        f"⚡ Parallel analysis:\n\n"
        f"📌 Main idea:\n{results[0]}\n\n"
        f"📊 Key facts:\n{results[1]}\n\n"
        f"❓ Questions raised:\n{results[2]}"
    )