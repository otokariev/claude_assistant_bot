import json
import os

MEMORY_FILE = "memory.json"


def _load_memory() -> dict:
    """Load all users memory from JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_memory(memory: dict):
    """Save all users memory to JSON file."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def save_fact(user_id: int, fact: str):
    """Save a fact about user to memory."""
    memory = _load_memory()
    if str(user_id) not in memory:
        memory[str(user_id)] = []
    memory[str(user_id)].append(fact)
    _save_memory(memory)


def get_facts(user_id: int) -> list[str]:
    """Get all facts about user."""
    memory = _load_memory()
    return memory.get(str(user_id), [])


def clear_facts(user_id: int):
    """Clear all facts about user."""
    memory = _load_memory()
    memory[str(user_id)] = []
    _save_memory(memory)