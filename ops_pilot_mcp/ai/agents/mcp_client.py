from fastmcp import Client

client = Client("http://localhost:8000/mcp")

# Cache for OpenAI tools
_openai_tools_cache = None

async def get_openai_tools():
    """Discover MCP tools and convert them into OpenAI's tool-calling schema"""
    global _openai_tools_cache
    if _openai_tools_cache is not None:
        return _openai_tools_cache
    
    mcp_tools = await client.list_tools()
    _openai_tools_cache = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        }
        for tool in mcp_tools
    ]
    return _openai_tools_cache

async def call_mcp_tool(name: str, arguments: dict):
    """INvoke a tool on the MCP server and return its result."""
    result = await client.call_tool(name, arguments)
    return result

# async def main():
#     async with client: 
#         tools = await client.list_tools()
#         result = await client.call_tool("get_ticket", {"ticket_id": 1})
#         print(result)