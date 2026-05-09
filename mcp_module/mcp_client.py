import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from bot.config import ANTHROPIC_API_KEY, CLAUDE_HAIKU, MAX_TOKENS

from mcp.types import CreateMessageRequestParams, CreateMessageResult, TextContent, Root, ListRootsResult

client = Anthropic(api_key=ANTHROPIC_API_KEY)


async def sampling_handler(
    context,
    params: CreateMessageRequestParams
) -> CreateMessageResult:
    """Handle sampling requests from MCP server."""
    messages = [
        {"role": msg.role, "content": msg.content.text}
        for msg in params.messages
    ]

    response = client.messages.create(
        model=CLAUDE_HAIKU,
        max_tokens=params.maxTokens or 1000,
        system=params.systemPrompt or "",
        messages=messages
    )

    return CreateMessageResult(
        role="assistant",
        content=TextContent(type="text", text=response.content[0].text),
        model=CLAUDE_HAIKU,
        stopReason="end_turn"
    )


async def run_mcp_agent(user_message: str) -> str:
    """
    Run an agent that uses MCP server tools to handle user request.
    Starts MCP server, connects client, runs agentic loop.
    Roots define which directories the server has access to.
    """
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_module/mcp_server.py"],
    )

    # Define roots - directories the server is allowed to access
    roots = [
        Root(
            uri=f"file://{os.path.abspath('.')}",
            name="Project root"
        )
    ]

    async def roots_callback(context) -> ListRootsResult:
        """Callback for when server requests roots."""
        return ListRootsResult(roots=roots)


    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
                read, write,
                sampling_callback=sampling_handler,
                list_roots_callback=roots_callback,
        ) as session:
            await session.initialize()

            tools_response = await session.list_tools()
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools_response.tools
            ]

            messages = [{"role": "user", "content": user_message}]

            while True:
                response = client.messages.create(
                    model=CLAUDE_HAIKU,
                    max_tokens=MAX_TOKENS,
                    tools=tools,
                    messages=messages
                )

                if response.stop_reason == "end_turn":
                    return response.content[0].text

                if response.stop_reason == "tool_use":
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            result = await session.call_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text
                            })

                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                else:
                    break

    return "Something went wrong."