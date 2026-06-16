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

    
def is_authorized(user_id: int) -> bool:
    """Check if user is authorized."""
    memory = _load_memory()
    return memory.get(f"auth_{user_id}", False)


def authorize_user(user_id: int):
    """Mark user as authorized."""
    memory = _load_memory()
    memory[f"auth_{user_id}"] = True
    _save_memory(memory)


def get_current_project(user_id: int) -> str | None:
    """Get the current project name for user. Returns None if no project set."""
    memory = _load_memory()
    return memory.get(f"project_{user_id}")


def set_current_project(user_id: int, project_name: str):
    """Set the current project for user and register it in the project list."""
    memory = _load_memory()
    memory[f"project_{user_id}"] = project_name

    projects_key = f"projects_{user_id}"
    projects = memory.get(projects_key, [])
    if project_name not in projects:
        projects.append(project_name)
    memory[projects_key] = projects

    _save_memory(memory)


def get_projects(user_id: int) -> list[str]:
    """Get list of all project names for user."""
    memory = _load_memory()
    return memory.get(f"projects_{user_id}", [])


def delete_project(user_id: int, project_name: str) -> bool:
    """Delete a project from the project list. Returns False if project not found or is current."""
    memory = _load_memory()
    projects_key = f"projects_{user_id}"
    current = memory.get(f"project_{user_id}", "default")

    if project_name == current:
        return False  # Can't delete current project

    projects = memory.get(projects_key, [])
    if project_name not in projects:
        return False

    projects.remove(project_name)
    memory[projects_key] = projects
    _save_memory(memory)
    return True