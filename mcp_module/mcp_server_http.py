import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from tools.notes_tool import add_note, get_note, list_notes, delete_note, edit_note

# HTTP transport server - for production deployment
# stateless_http=True - no state between requests (suitable for serverless)
# JSON_response=True - returns JSON instead of SSE stream
mcp = FastMCP(
    "NotesServerHTTP",
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def tool_add_note(title: str, content: str) -> str:
    """Save a new note with a title and content."""
    return add_note(title, content)


@mcp.tool()
def tool_get_note(title: str) -> str:
    """Get a note by its title."""
    return get_note(title)


@mcp.tool()
def tool_list_notes() -> str:
    """Get a list of ALL saved notes. Always use this tool when user asks to show, list or view all notes."""
    return list_notes()


@mcp.tool()
def tool_delete_note(title: str) -> str:
    """Delete a note by its title."""
    return delete_note(title)


@mcp.tool()
def tool_edit_note(title: str, content: str) -> str:
    """Edit an existing note by title."""
    return edit_note(title, content)


@mcp.resource("notes://all")
def resource_all_notes() -> str:
    """Expose all notes as a resource."""
    return list_notes()


if __name__ == "__main__":
    import uvicorn
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)