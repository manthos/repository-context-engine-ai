"""R2CE MCP Server - Exposes repository analysis tools via MCP."""
import asyncio
import json
import sys
from typing import Any, Sequence
import httpx

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server
app = Server("r2ce-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="analyze_repository",
            description="Analyze a Git repository and generate recursive summaries",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "URL of the Git repository to analyze"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Analysis depth",
                        "default": 3
                    }
                },
                "required": ["repo_url"]
            }
        ),
        Tool(
            name="get_repository_tree",
            description="Get the recursive summary tree for a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_id": {
                        "type": "string",
                        "description": "Repository ID"
                    }
                },
                "required": ["repo_id"]
            }
        ),
        Tool(
            name="search_repository",
            description="Search across repository summaries",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="ask_repository_question",
            description="Ask a question about a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_id": {
                        "type": "string",
                        "description": "Repository ID"
                    },
                    "question": {
                        "type": "string",
                        "description": "Question to ask"
                    }
                },
                "required": ["repo_id", "question"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Call a tool."""
    import os
    
    # Get API URL from environment or use default
    api_base_url = os.getenv("R2CE_API_URL", "http://localhost:8000/api")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            if name == "analyze_repository":
                response = await client.post(
                    f"{api_base_url}/analyze",
                    json={
                        "repo_url": arguments["repo_url"],
                        "depth": arguments.get("depth", 3)
                    }
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            
            elif name == "get_repository_tree":
                response = await client.get(
                    f"{api_base_url}/tree/{arguments['repo_id']}"
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            
            elif name == "search_repository":
                response = await client.get(
                    f"{api_base_url}/search",
                    params={"q": arguments["query"]}
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            
            elif name == "ask_repository_question":
                response = await client.post(
                    f"{api_base_url}/qa",
                    json={
                        "repo_id": arguments["repo_id"],
                        "question": arguments["question"]
                    }
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        except httpx.HTTPError as e:
            error_msg = f"HTTP error calling R2CE API: {str(e)}"
            return [TextContent(type="text", text=json.dumps({"error": error_msg}, indent=2))]
        except Exception as e:
            error_msg = f"Error executing tool {name}: {str(e)}"
            return [TextContent(type="text", text=json.dumps({"error": error_msg}, indent=2))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
