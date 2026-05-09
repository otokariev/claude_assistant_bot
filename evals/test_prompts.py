import json
from claude.client import ask_claude
from claude.structured import get_structured_response
from bot.config import CLAUDE_HAIKU


def evaluate_response(response: str, criteria: list[str]) -> dict:
    """
    Evaluate Claude's response against given criteria using Claude itself.
    Returns scores and feedback for each criterion.
    """
    schema = """{
    "scores": {
        "criterion_name": 0-10
    },
    "overall_score": 0-10,
    "feedback": "brief feedback",
    "passed": true|false
}"""

    eval_prompt = f"""Evaluate this AI response against the following criteria.
Score each criterion from 0 to 10.
Consider the response "passed" if overall score is 7 or higher.

Response to evaluate:
{response}

Criteria:
{json.dumps(criteria, indent=2)}"""

    return get_structured_response(eval_prompt, schema)


def run_prompt_tests() -> str:
    """
    Run a series of prompt tests and return results.
    Tests different aspects of Claude's responses.
    """
    tests = [
        {
            "name": "Conciseness test",
            "prompt": "Explain what Python is in one sentence.",
            "criteria": ["conciseness", "accuracy", "clarity"]
        },
        {
            "name": "Multilingual test",
            "prompt": "Привет! Как дела?",
            "criteria": ["responds_in_russian", "friendliness", "naturalness"]
        },
        {
            "name": "Code test",
            "prompt": "Write a Python function that adds two numbers.",
            "criteria": ["correctness", "simplicity", "includes_example"]
        }
    ]

    results = []
    passed = 0

    for test in tests:
        # Get Claude's response
        messages = [{"role": "user", "content": test["prompt"]}]
        response = ask_claude(messages=messages, model=CLAUDE_HAIKU)

        # Evaluate the response
        evaluation = evaluate_response(response, test["criteria"])

        test_passed = evaluation.get("passed", False)
        if test_passed:
            passed += 1

        results.append({
            "name": test["name"],
            "passed": test_passed,
            "overall_score": evaluation.get("overall_score", 0),
            "feedback": evaluation.get("feedback", "")
        })

    # Format results
    lines = [f"🧪 <b>Prompt Tests ({passed}/{len(tests)} passed)</b>\n"]
    for r in results:
        icon = "✅" if r["passed"] else "❌"
        lines.append(
            f"{icon} <b>{r['name']}</b>\n"
            f"Score: {r['overall_score']}/10\n"
            f"Feedback: {r['feedback']}\n"
        )

    return "\n".join(lines)