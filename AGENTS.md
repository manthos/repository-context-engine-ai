# AI Agent Instructions

## Development Workflow

This project was developed using AI-assisted development with Cursor and Claude Sonnet. The development process involved:

1. **Filesystem MCP**: Used Filesystem MCP server during development to maintain context of the evolving project structure
2. **R2CE MCP Server**: Created an MCP server that exposes repository analysis tools for use by AI agents
3. **AI Interaction Logging**: All AI interactions are documented in `DEVELOPMENT_LOG.md`

## Code Style

- **Type Hints**: All Python functions must have type hints
- **Docstrings**: All functions, classes, and modules must have docstrings
- **Formatting**: Follow PEP 8 style guide
- **Imports**: Use absolute imports from `backend.*`
- **Error Handling**: Use proper exception handling with clear error messages

## Recursive Summarization Logic

The core algorithm follows a bottom-up approach:

1. **Files (Leaves)**: Process individual files first
   - Read file content (respecting size limits and binary file detection)
   - Generate summary using LLM
   - Create embedding vector
   - Store in database

2. **Folders (Branches)**: Process folders bottom-up
   - Aggregate child summaries
   - Generate folder-level summary using LLM
   - Store in database

3. **Root**: Generate project-level summary
   - Aggregate all folder summaries
   - Generate comprehensive project overview
   - Store as root node

## LLM Provider Configuration

The system supports multiple LLM providers:
- **OpenAI**: GPT-3.5-turbo or GPT-4
- **Ollama**: Local LLM (llama3 default)
- **DeepSeek Coding**: Recommended for code analysis

Provider is configured via `LLM_PROVIDER` environment variable.

## Database Strategy

- **Development**: SQLite for simplicity and speed
- **Production**: PostgreSQL with pgvector for vector search
- Database URL is configured via `DATABASE_URL` environment variable
- Migrations handled by Alembic

## API Design

- Follow OpenAPI specification in `docs/openapi.yaml`
- All endpoints prefixed with `/api`
- Use Pydantic schemas for request/response validation
- Async task processing for long-running operations

## Testing

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test full workflows including database interactions
- Tests use in-memory SQLite for speed
- Mock LLM calls in unit tests to avoid API costs

## MCP Integration

### Using Filesystem MCP

During development, the Filesystem MCP server was used to:
- Maintain context of project structure
- Navigate codebase efficiently
- Understand relationships between files

### R2CE MCP Server

The R2CE MCP server exposes the following tools:
- `analyze_repository`: Trigger repository analysis
- `get_repository_tree`: Get summary tree
- `search_repository`: Search summaries
- `ask_repository_question`: Ask questions about repositories

These tools can be used by AI agents to interact with the R2CE system.

## Example Prompts

### For File Summarization
```
Summarize this file's purpose, key functions, and role in the project:
[file content]
```

### For Folder Summarization
```
Based on the following child summaries:
[child summaries]

Describe this folder's purpose and structure:
[folder path]
```

### For Root Summarization
```
Provide an overview of this project: what it does, how it's structured, and how to configure/run it:
[all folder summaries]
```

## Development Log

See `DEVELOPMENT_LOG.md` for detailed log of all AI-assisted development sessions.

