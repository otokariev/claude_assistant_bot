from anthropic import Anthropic
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from bot.config import ANTHROPIC_API_KEY, CLAUDE_HAIKU, MAX_TOKENS

client = Anthropic(api_key=ANTHROPIC_API_KEY)

MCP_SERVER_URL = "http://localhost:8000/mcp"


async def run_mcp_http_agent(user_message: str) -> str:
    """
    Run an agent using HTTP transport instead of STDIO.
    Connects to MCP server via HTTP URL.
    """
    async with streamable_http_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
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