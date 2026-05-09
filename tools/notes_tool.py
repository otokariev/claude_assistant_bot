import json
import os

NOTES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notes.json")


def _load_notes() -> dict:
    """Load notes from JSON file."""
    if not os.path.exists(NOTES_FILE):
        return {}
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_notes(notes: dict):
    """Save notes to JSON file."""
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def add_note(title: str, content: str) -> str:
    """Add a new note. Returns confirmation message."""
    notes = _load_notes()
    notes[title] = content
    _save_notes(notes)
    return f"Note '{title}' saved successfully."


def get_note(title: str) -> str:
    """Get a note by title. Returns note content or error message."""
    notes = _load_notes()
    if title not in notes:
        return f"Note '{title}' not found."
    return notes[title]


def list_notes() -> str:
    """Get list of all note titles. Returns formatted string."""
    notes = _load_notes()
    if not notes:
        return "No notes yet."
    titles = "\n".join(f"- {title}" for title in notes.keys())
    return f"Your notes:\n{titles}"


def edit_note(title: str, content: str) -> str:
    """Edit an existing note. Returns confirmation message."""
    notes = _load_notes()
    if title not in notes:
        return f"Note '{title}' not found."
    notes[title] = content
    _save_notes(notes)
    return f"Note '{title}' updated successfully."


def delete_note(title: str) -> str:
    """Delete a note by title. Returns confirmation message."""
    notes = _load_notes()
    if title not in notes:
        return f"Note '{title}' not found."
    del notes[title]
    _save_notes(notes)
    return f"Note '{title}' deleted."