import time
from claude.client import ask_claude
from bot.config import CLAUDE_HAIKU, CLAUDE_SONNET


def benchmark_model(model: str, prompt: str, runs: int = 3) -> dict:
    """
    Benchmark a model's response time over multiple runs.
    Returns average, min and max response times.
    """
    times = []

    for _ in range(runs):
        start = time.time()
        messages = [{"role": "user", "content": prompt}]
        ask_claude(messages=messages, model=model)
        elapsed = time.time() - start
        times.append(elapsed)

    return {
        "model": model,
        "runs": runs,
        "avg": round(sum(times) / len(times), 2),
        "min": round(min(times), 2),
        "max": round(max(times), 2),
    }


def run_benchmarks() -> str:
    """
    Compare Haiku and Sonnet performance on the same prompt.
    """
    prompt = "Explain what artificial intelligence is in 2 sentences."

    lines = ["⏱ <b>Model Benchmarks</b> (3 runs each)\n"]

    for model in [CLAUDE_HAIKU, CLAUDE_SONNET]:
        result = benchmark_model(model, prompt)
        model_name = "Haiku" if "haiku" in model else "Sonnet"
        lines.append(
            f"🤖 <b>{model_name}</b>\n"
            f"Avg: {result['avg']}s | "
            f"Min: {result['min']}s | "
            f"Max: {result['max']}s\n"
        )

    return "\n".join(lines)