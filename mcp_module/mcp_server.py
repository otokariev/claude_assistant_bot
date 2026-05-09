import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP, Context
from tools.notes_tool import add_note, get_note, list_notes, delete_note, edit_note

from mcp.types import SamplingMessage, TextContent

mcp = FastMCP("NotesServer")


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
    """Get a list of all saved notes."""
    return list_notes()


@mcp.tool()
def tool_delete_note(title: str) -> str:
    """Delete a note by its title."""
    return delete_note(title)


@mcp.tool()
def tool_edit_note(title: str, content: str) -> str:
    """Edit an existing note by title."""
    return edit_note(title, content)


@mcp.tool()
async def tool_summarize_note_with_sampling(title: str, language: str, ctx: Context) -> str:
    """
    Get a note and summarize it using sampling.
    Server requests LLM generation via client — demonstrates sampling.
    language - language for the summary (e.g. 'Russian', 'English')
    """
    note_content = get_note(title)
    if "not found" in note_content:
        return note_content

    prompt = f"Summarize this note in {language}:\n\n{note_content}"

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=prompt)
            )
        ],
        max_tokens=200,
        system_prompt=f"You are a helpful assistant that summarizes notes concisely.",
    )

    if result.content.type == "text":
        return f"Summary of '{title}':\n{result.content.text}"
    else:
        raise ValueError("Sampling failed")


@mcp.tool()
async def tool_process_notes_with_progress(ctx: Context) -> str:
    """
    Process all notes with progress notifications.
    Demonstrates log and progress notifications in MCP.
    """
    from tools.notes_tool import _load_notes

    notes = _load_notes()
    if not notes:
        return "No notes to process."

    total = len(notes)
    results = []

    await ctx.info(f"Starting processing of {total} notes...")

    for i, (title, content) in enumerate(notes.items()):
        # Send progress notification
        await ctx.report_progress(i, total)

        # Send log notification
        await ctx.info(f"Processing note: '{title}'")

        results.append(f"- {title}: {len(content)} characters")

    # Final progress
    await ctx.report_progress(total, total)
    await ctx.info("Processing complete!")

    return f"Processed {total} notes:\n" + "\n".join(results)


@mcp.tool()
async def tool_list_roots(ctx: Context) -> str:
    """
    List all directories accessible to this server.
    Demonstrates roots feature of MCP.
    """
    roots_result = await ctx.session.list_roots()
    client_roots = roots_result.roots

    if not client_roots:
        return "No roots defined."

    lines = ["Accessible roots:\n"]
    for root in client_roots:
        lines.append(f"- {root.name}: {root.uri}")

    return "\n".join(lines)


@mcp.resource("notes://all")
def resource_all_notes() -> str:
    """Expose all notes as a resource."""
    return list_notes()


@mcp.prompt()
def prompt_summarize_notes() -> str:
    """Prompt to summarize all notes."""
    notes_list = list_notes()
    return f"""Please summarize the following notes briefly:

{notes_list}

Give a short overview of what topics are covered."""


if __name__ == "__main__":
    mcp.run()