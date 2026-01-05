# R2CE MCP Server

MCP (Model Context Protocol) server that exposes R2CE repository analysis tools to AI agents.

## What It Does

The R2CE MCP server allows AI assistants (like Claude in Cursor) to interact with the R2CE system programmatically. It exposes four tools:

1. **analyze_repository** - Trigger repository analysis
2. **get_repository_tree** - Get hierarchical summary tree
3. **search_repository** - Search across summaries
4. **ask_repository_question** - Ask questions about repositories

## Setup

### Quick Setup

```bash
cd mcp/r2ce-server
./setup.sh
```

This will:
- Create a virtual environment in `venv/`
- Install all dependencies (MCP SDK, httpx)
- Set up the server

### Manual Setup

```bash
cd mcp/r2ce-server

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

### Standalone (for testing)

```bash
cd mcp/r2ce-server
source venv/bin/activate
python server.py
```

### Configure in MCP Client

To use with Cursor or Claude Desktop, configure the MCP server:

**Cursor Configuration** (`.cursor/mcp.json` or similar):
```json
{
  "mcpServers": {
    "r2ce": {
      "command": "/absolute/path/to/R2CE/mcp/r2ce-server/venv/bin/python",
      "args": ["/absolute/path/to/R2CE/mcp/r2ce-server/server.py"],
      "env": {
        "R2CE_API_URL": "http://localhost:8000/api"
      }
    }
  }
}
```

**Claude Desktop Configuration** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "r2ce": {
      "command": "/absolute/path/to/R2CE/mcp/r2ce-server/venv/bin/python",
      "args": ["/absolute/path/to/R2CE/mcp/r2ce-server/server.py"],
      "env": {
        "R2CE_API_URL": "http://localhost:8000/api"
      }
    }
  }
}
```

## Environment Variables

- `R2CE_API_URL` - Backend API URL (default: `http://localhost:8000/api`)

## Usage Example

Once configured, AI agents can use the tools:

```
AI Agent: "Analyze the repository https://github.com/user/repo"
→ Calls: analyze_repository(repo_url="https://github.com/user/repo")
→ Returns: task_id

AI Agent: "Get the summary tree for repo_id"
→ Calls: get_repository_tree(repo_id="...")
→ Returns: Full tree structure

AI Agent: "Search for 'authentication' in summaries"
→ Calls: search_repository(query="authentication")
→ Returns: Matching summaries

AI Agent: "What does this repository do?"
→ Calls: ask_repository_question(repo_id="...", question="What does this repository do?")
→ Returns: Answer with sources
```

## Requirements

- Python 3.11+
- R2CE backend running (default: http://localhost:8000)
- MCP SDK (`pip install mcp`)

## Troubleshooting

### Import Error: MCP SDK not found
```bash
source venv/bin/activate
pip install mcp
```

### Connection Error: Cannot reach backend
- Ensure R2CE backend is running on port 8000
- Check `R2CE_API_URL` environment variable
- Verify backend health: `curl http://localhost:8000/health`

### MCP Client not seeing tools
- Verify server starts without errors
- Check MCP client configuration paths are absolute
- Ensure virtual environment Python path is correct

## Files

- `server.py` - MCP server implementation
- `requirements.txt` - Python dependencies
- `setup.sh` - Setup script
- `README.md` - This file

