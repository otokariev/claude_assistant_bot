from tools.notes_tool import add_note, get_note, list_notes, edit_note, delete_note

# Tool definitions for Claude API
NOTES_TOOLS = [
    {
        "name": "add_note",
        "description": "Save a new note with a title and content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the note"
                },
                "content": {
                    "type": "string",
                    "description": "Content of the note"
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "get_note",
        "description": "Get a note by its title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the note to retrieve"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "list_notes",
        "description": "Get a list of ALL saved notes. Always use this tool when user asks to show, list or view all notes.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "edit_note",
        "description": "Edit an existing note by title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the note to edit"
                },
                "content": {
                    "type": "string",
                    "description": "New content for the note"
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "delete_note",
        "description": "Delete a note by its title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the note to delete"
                }
            },
            "required": ["title"]
        }
    }
]


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return the result."""
    if tool_name == "add_note":
        return add_note(**tool_input)
    elif tool_name == "get_note":
        return get_note(**tool_input)
    elif tool_name == "list_notes":
        return list_notes()
    elif tool_name == "edit_note":
        return edit_note(**tool_input)
    elif tool_name == "delete_note":
        return delete_note(**tool_input)
    else:
        return f"Unknown tool: {tool_name}"