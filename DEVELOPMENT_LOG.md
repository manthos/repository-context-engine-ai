# AI-Assisted Development Log

## Overview
This document tracks all interactions with AI assistants (Cursor/Claude Sonnet) during development of R2CE (Recursive Repository Context Engine). It documents the AI-assisted development workflow, MCP usage, technology choices, and architectural decisions.

## Development Sessions

### 2025-01-XX - Project Setup & Foundation
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Initial project structure setup and foundation  
**Prompts Used**:
- "Implement the plan as specified, it is attached for your reference..."
- "Create project directory structure (backend/, frontend/, docs/, mcp/)..."

**Decisions Made**:
- **Backend Framework**: Chose FastAPI over Flask for native async support, automatic OpenAPI generation, and better type hints
- **Database Strategy**: SQLite for development (simplicity), PostgreSQL with pgvector for production (vector search)
- **Frontend Framework**: React + TypeScript + Vite for modern, type-safe frontend development
- **Containerization**: Docker Compose for full stack orchestration
- **LLM Provider**: DeepSeek Coding as default (cost-effective, code-focused), with support for OpenAI and Ollama

**Code Generated**: 
- Project directory structure (`backend/`, `frontend/`, `docs/`, `mcp/`)
- Base configuration files (`docker-compose.yml`, `.env.example`, `requirements.txt`, `package.json`)
- Docker setup (Dockerfiles for backend and frontend)

**Review Notes**: Foundation established following contract-first approach with OpenAPI spec

---

### 2025-01-XX - Database Layer Implementation
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Set up database layer with SQLAlchemy models and Alembic migrations  
**Prompts Used**:
- "Set up database layer supporting both SQLite (dev) and PostgreSQL (prod) with pgvector..."

**Decisions Made**:
- **ORM**: SQLAlchemy for database abstraction
- **Migrations**: Alembic for version control
- **Models**: Three core models - Repository (tracks repos), Node (files/folders with summaries), Task (async processing)
- **Database Abstraction**: Environment-based URL switching (`DATABASE_URL`) allows seamless dev/prod transition
- **Vector Support**: Graceful degradation - pgvector for PostgreSQL, simple hash-based embeddings for SQLite

**Code Generated**:
- `backend/db/base.py` - Database session management
- `backend/models/repository.py` - Repository model with status tracking
- `backend/models/node.py` - Hierarchical node model with embeddings
- `backend/models/task.py` - Task model for async processing
- `backend/db/migrations/` - Alembic migration files

**Architecture Notes**:
- Database layer abstracts storage differences between SQLite and PostgreSQL
- Models support recursive tree structure (parent-child relationships)
- Embedding field uses PostgreSQL arrays, nullable for SQLite compatibility

---

### 2025-01-XX - Backend API Implementation
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Implement FastAPI endpoints following OpenAPI contract  
**Prompts Used**:
- "Implement all 4 API endpoints (/analyze, /status/{task_id}, /tree/{repo_id}, /search) plus /qa endpoint..."

**Decisions Made**:
- **API Contract**: Strict adherence to OpenAPI spec in `docs/openapi.yaml` (contract-first approach)
- **Endpoint Structure**: All endpoints prefixed with `/api` for clear separation
- **Async Processing**: FastAPI BackgroundTasks for long-running analysis jobs
- **Request/Response**: Pydantic schemas matching OpenAPI spec exactly
- **Error Handling**: HTTPException with appropriate status codes

**Code Generated**:
- `backend/api/routes/analyze.py` - POST /api/analyze (starts analysis, returns task_id)
- `backend/api/routes/status.py` - GET /api/status/{task_id} (polls progress)
- `backend/api/routes/tree.py` - GET /api/tree/{repo_id} (recursive tree structure)
- `backend/api/routes/search.py` - GET /api/search (semantic search)
- `backend/api/routes/qa.py` - POST /api/qa (question answering)
- `backend/schemas/` - Pydantic schemas matching OpenAPI spec

**Architecture Notes**:
- API follows RESTful principles
- Background task pattern allows non-blocking analysis
- Tree endpoint builds recursive structure from flat database records
- Search uses simple text matching (MVP), ready for vector search upgrade

---

### 2025-01-XX - LLM Service Abstraction
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Create multi-provider LLM service supporting OpenAI, Ollama, and DeepSeek  
**Prompts Used**:
- "Create LLM abstraction layer supporting OpenAI, Ollama, and DeepSeek Coding providers..."

**Decisions Made**:
- **Abstraction Pattern**: Abstract base class `LLMService` with provider-specific implementations
- **Provider Selection**: Environment variable `LLM_PROVIDER` for runtime switching
- **DeepSeek Integration**: Uses OpenAI-compatible API (same library, different endpoint)
- **Error Handling**: Clear error messages for missing API keys
- **Async Support**: All LLM calls are async for better performance

**Code Generated**:
- `backend/services/llm_service.py` - LLM abstraction with three providers:
  - `OpenAIService` - OpenAI GPT models
  - `OllamaService` - Local Ollama instance
  - `DeepSeekService` - DeepSeek Coding (recommended for code analysis)

**Architecture Notes**:
- Provider abstraction allows easy addition of new LLM providers
- Consistent interface across providers simplifies usage
- DeepSeek chosen as default for cost-effectiveness and code understanding

---

### 2025-01-XX - Recursive Analysis Engine
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Implement bottom-up recursive summarization algorithm  
**Prompts Used**:
- "Build recursive analyzer.py that processes files bottom-up, generates summaries..."

**Decisions Made**:
- **Algorithm**: Bottom-up processing (files → folders → root)
- **File Processing**: Respect .gitignore, skip binary files, size limits
- **Summary Generation**: Different prompts for files vs folders vs root
- **Progress Tracking**: Update task progress throughout analysis
- **Error Handling**: Graceful failure with error messages in task status

**Code Generated**:
- `backend/services/analyzer.py` - Core recursive analysis logic
- `backend/services/git_service.py` - Git cloning and file tree traversal
- `backend/services/embedding_service.py` - Vector embedding generation

**Architecture Notes**:
- Bottom-up approach ensures high-level summaries are grounded in actual code
- File tree built from Git repository (respects .gitignore)
- Summaries stored hierarchically matching repository structure
- Background processing allows API to return immediately

---

### 2025-01-XX - Frontend Implementation
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Build React frontend with tree view, search, and Q&A interface  
**Prompts Used**:
- "Create React frontend with tree view component, search interface, Q&A interface..."

**Decisions Made**:
- **Framework**: React 18 with TypeScript for type safety
- **Build Tool**: Vite for fast development and optimized builds
- **API Client**: Centralized API client (`frontend/src/services/api.ts`) - critical for evaluation
- **Component Structure**: Modular components (RepoAnalyzer, TreeView, SearchBar, QAInterface)
- **State Management**: React hooks (useState, useEffect) for local state

**Code Generated**:
- `frontend/src/App.tsx` - Main application component
- `frontend/src/components/RepoAnalyzer.tsx` - Repository analysis trigger with progress
- `frontend/src/components/TreeView.tsx` - Recursive tree display with expand/collapse
- `frontend/src/components/SearchBar.tsx` - Search interface with results
- `frontend/src/components/QAInterface.tsx` - Question answering interface
- `frontend/src/services/api.ts` - **Centralized API client** (all API calls go through this)
- `frontend/src/types/index.ts` - TypeScript types matching API schemas

**Architecture Notes**:
- Centralized API client ensures consistent error handling and request formatting
- Components are reusable and well-separated
- TypeScript types match backend Pydantic schemas for type safety
- UI provides real-time feedback during analysis

---

### 2025-01-XX - Testing Implementation
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Create comprehensive test suite (unit and integration tests)  
**Prompts Used**:
- "Write unit tests for analyzer logic, LLM service, git service..."
- "Create clearly separated integration tests covering full workflows..."

**Decisions Made**:
- **Test Framework**: pytest for backend, Vitest for frontend
- **Test Separation**: Clear separation between unit tests (`tests/unit/`) and integration tests (`tests/integration/`)
- **Test Database**: In-memory SQLite for speed and isolation
- **Mocking**: Mock LLM calls in unit tests to avoid API costs
- **Coverage**: Aim for core functionality coverage

**Code Generated**:
- `backend/tests/conftest.py` - Pytest fixtures (database session)
- `backend/tests/unit/test_git_service.py` - Git service unit tests
- `backend/tests/unit/test_llm_service.py` - LLM service unit tests (with mocks)
- `backend/tests/unit/test_embedding_service.py` - Embedding service tests
- `backend/tests/integration/test_api_endpoints.py` - API endpoint integration tests
- `backend/tests/integration/test_database.py` - Database operation tests
- `frontend/src/components/__tests__/RepoAnalyzer.test.tsx` - Frontend component tests
- `backend/tests/README.md` - Testing documentation

**Architecture Notes**:
- Unit tests test individual components in isolation
- Integration tests verify full workflows including database interactions
- Tests use fixtures for consistent test environment
- Clear documentation for running tests

---

### 2025-01-XX - MCP Integration
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Create MCP server exposing repository analysis tools  
**Prompts Used**:
- "Create MCP server for R2CE (exposes repository analysis tools)..."

**Decisions Made**:
- **MCP Server**: Created R2CE MCP server that exposes API endpoints as MCP tools
- **Tool Exposure**: Four tools - analyze_repository, get_repository_tree, search_repository, ask_repository_question
- **Integration**: MCP server calls backend API endpoints (HTTP-based)
- **Development MCP**: Used Filesystem MCP during development for context

**Code Generated**:
- `mcp/r2ce-server/server.py` - MCP server implementation
- `mcp/r2ce-server/requirements.txt` - MCP server dependencies
- `AGENTS.md` - Documentation of MCP usage

**Architecture Notes**:
- MCP server acts as bridge between AI agents and R2CE API
- Tools match API endpoints for consistency
- Allows AI agents to interact with R2CE system programmatically
- Filesystem MCP used during development to maintain project context

**MCP Usage**:
1. **Filesystem MCP** (Development): Used by AI assistant (Cursor) to navigate and understand project structure during development
2. **R2CE MCP Server** (Production): Exposes repository analysis capabilities to AI agents via standardized MCP protocol

---

### 2025-01-XX - CI/CD Pipeline
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Set up GitHub Actions CI/CD pipeline  
**Prompts Used**:
- "Create GitHub Actions CI/CD pipeline that runs tests and deploys application..."

**Decisions Made**:
- **CI**: Run tests on every PR and push
- **Test Matrix**: Backend (Python) and frontend (Node.js) tests
- **Database**: PostgreSQL service in GitHub Actions
- **CD**: Deploy on merge to main (placeholder for Render/Railway)

**Code Generated**:
- `.github/workflows/ci.yml` - GitHub Actions workflow

**Architecture Notes**:
- Automated testing ensures code quality
- PostgreSQL service matches production environment
- Deployment can be extended with platform-specific steps

---

### 2025-01-XX - MCP Server Completion
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Complete MCP server implementation with virtual environment setup  
**Prompts Used**:
- "yes and add environment in this folder the r2ce folder dont install globally"
- "what would the mcp server do / what tools would be needed and how is it done now?"

**Decisions Made**:
- Created virtual environment locally in `mcp/r2ce-server/venv/` (not global installation)
- Installed MCP SDK v1.25.0 and all dependencies locally
- Completed all imports and error handling
- Added environment variable support for API URL (`R2CE_API_URL`)
- Implemented proper error handling for HTTP requests

**Code Generated**:
- `mcp/r2ce-server/server.py` - Complete MCP server implementation with all 4 tools
- `mcp/r2ce-server/setup.sh` - Automated setup script for virtual environment
- `mcp/r2ce-server/test_server.py` - Verification script to test server imports
- `mcp/r2ce-server/README.md` - Complete documentation
- `mcp/r2ce-server/MCP_SETUP_COMPLETE.md` - Setup completion summary
- Virtual environment (`venv/`) with MCP SDK and dependencies

**Architecture Notes**:
- MCP server communicates via stdio with AI clients (Cursor/Claude Desktop)
- Makes HTTP requests to R2CE backend API (configurable via `R2CE_API_URL`)
- Exposes 4 tools matching API endpoints:
  - `analyze_repository` → POST /api/analyze
  - `get_repository_tree` → GET /api/tree/{repo_id}
  - `search_repository` → GET /api/search
  - `ask_repository_question` → POST /api/qa
- Virtual environment ensures isolated dependencies (not installed globally)
- Server tested and verified working

**Review Notes**: MCP server fully functional and ready for integration with MCP clients. Virtual environment setup allows local development without global package pollution.

---

### 2025-01-04 - Permanent Caching & File System Summaries
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Implement permanent repository caching and file system-based summaries  
**Prompts Used**:
- "i want the repository to get to a permanent folder cache/<git repository> and also I wanted the summaries to be .md in their respective folders/files localtion..."

**Decisions Made**:
- **Permanent Cache**: Changed from temporary `/tmp/r2ce/` to permanent `cache/<owner>-<repo>/` directory
- **File System Summaries**: Summaries saved as `.md` files in repository structure:
  - Files: `<file>.md` alongside original files
  - Folders: `<folder>.md` inside each folder
  - Root: `README.md` at repository root
- **Incremental Analysis**: Only summarize files/folders that don't have existing summaries
- **Dual Storage**: Summaries stored in both database (for fast queries) and file system (for browsing)
- **Smart Caching**: Repositories are not re-downloaded if already cached, only updated via `git pull`
- **AI-Agent Optimized Prompts**: Enhanced LLM prompts to generate comprehensive summaries with:
  - Purpose, key functions/classes, dependencies
  - Configuration options and data flow
  - Modification guides for AI agents
  - Important patterns and conventions

**Code Generated**:
- `backend/services/summary_files.py` - Helper functions for reading/writing summary files
- Updated `backend/services/git_service.py`:
  - `get_repo_cache_path()` - Generate cache path from repo URL
  - `clone_repository()` - Uses permanent cache, checks for existing repos, updates via git pull
  - `cleanup_repository()` - Now a no-op (repositories kept permanently)
- Updated `backend/services/analyzer.py`:
  - Checks for existing summaries before generating new ones
  - Saves summaries to `.md` files in repository structure
  - Reads existing summaries when summarizing parent folders
  - Only processes files/folders without summaries
- Updated `backend/services/llm_service.py`:
  - Enhanced prompts for AI-agent-ready summaries
  - Added `item_type` parameter to distinguish file vs folder summaries
- Updated `backend/config.py`:
  - Added `cache_dir` setting (default: "cache")

**Architecture Notes**:
- Repository cache structure: `cache/<owner>-<repo>/` (e.g., `cache/octocat-Hello-World/`)
- Summary files are human-readable markdown, enabling:
  - Direct browsing of repository structure
  - Version control of summaries (if desired)
  - Easy inspection without database access
- Incremental analysis significantly reduces API costs and processing time
- File system summaries enable AI agents to understand repository structure without database queries
- Database still used for fast search and query operations

**Review Notes**: This is a critical architectural change that enables the commercial vision of AI agents being able to program repositories. The file system-based summaries make it easy for AI agents to understand and modify code, while the database provides fast query capabilities. The incremental analysis feature reduces costs and improves performance for large repositories.

---

### 2025-01-04 - Markdown Rendering & LLM Call Logging
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Add markdown rendering for LLM responses and comprehensive LLM call logging  
**Prompts Used**:
- "There should also be a global summary for the repository (root folder) just like for the sub folders..."
- "The reply to the answer worked but its markdown not text at least for DeepSeek so can it also be displayed in markdown?"
- "Additionally can you add a log directory where each LLM call input and output is logged in a separate file for our review."

**Decisions Made**:
- **Markdown Rendering**: Added `react-markdown` library to frontend for proper markdown display
- **LLM Call Logging**: Created comprehensive logging system that logs every LLM call to separate JSON files
- **Log Structure**: Each LLM call logged as `llm_call_<timestamp>.json` with:
  - Timestamp, provider, model, item_type
  - Full prompt and response
  - Context (if provided)
  - Prompt and response lengths
- **Root Summary**: Verified root folder summary is generated and saved as `README.md` in repository cache
- **Frontend Updates**: Updated QAInterface and TreeView components to render markdown properly

**Code Generated**:
- `backend/services/llm_logger.py` - LLM call logging service
  - `log_llm_call()` - Logs each LLM call to timestamped JSON file
  - `get_log_dir()` - Creates and returns logs directory
- Updated `backend/services/llm_service.py`:
  - Added logging calls to all three providers (OpenAI, Ollama, DeepSeek)
  - Logs are written after each successful LLM call
- Updated `frontend/src/components/QAInterface.tsx`:
  - Added `react-markdown` import
  - Wrapped answer display in `<ReactMarkdown>` component
- Updated `frontend/src/components/TreeView.tsx`:
  - Added `react-markdown` import
  - Wrapped summary display in `<ReactMarkdown>` component
- Updated `frontend/package.json`:
  - Added `react-markdown` dependency
- Updated `.gitignore`:
  - Added `logs/` directory to ignore LLM call logs

**Architecture Notes**:
- LLM logs stored in `logs/` directory at project root
- Each log file is a self-contained JSON with all call information
- Logs enable review of:
  - Prompt quality and effectiveness
  - Response quality and consistency
  - Provider comparison (OpenAI vs Ollama vs DeepSeek)
  - Cost analysis (prompt/response lengths)
- Markdown rendering ensures LLM responses with formatting (headers, lists, code blocks) display correctly
- Root summary is generated using folder summarization logic and saved as `README.md` in cache directory
- Logging is non-blocking - if logging fails, it doesn't affect LLM calls

**Review Notes**: Markdown rendering significantly improves readability of LLM responses, especially for DeepSeek which returns well-formatted markdown. The comprehensive logging system enables detailed review and analysis of LLM interactions, which is crucial for:
- Improving prompt engineering
- Debugging issues with specific LLM calls
- Comparing provider performance
- Cost optimization (analyzing prompt/response lengths)
- Quality assurance (reviewing response quality)

---

### 2025-01-04 - Folder Summary Fixes & Root Summary Enhancement
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Fix folder summaries to include actual structure and fix root summary naming  
**Prompts Used**:
- "We also said to analyze folders but the folder summary for coding is not working due to the prompt which seems to also not provide the summary of the files and folders contained therein..."
- "Plus we also said to analyze at the end the whole project (giving the root folder & file summaries in the prompt and as above). This should be named <gitrepository>.md but it is not done yet."

**Decisions Made**:
- **Folder Summary Location**: Changed from `<folder>.md` inside folder to `<folder>.md` in parent directory
- **Folder Structure in Prompts**: Added `get_folder_structure()` function to provide actual folder contents (tree-like format) to LLM prompts
- **Root Summary Naming**: Changed from `README.md` to `<gitrepository>.md` (e.g., `octocat-Hello-World.md`)
- **Root Summary Content**: Enhanced to include ALL folder and file summaries in the prompt for comprehensive project overview
- **Folder Prompt Fix**: Updated all LLM service prompts to include actual folder structure in the `content` parameter instead of asking for it

**Code Generated**:
- Updated `backend/services/git_service.py`:
  - Added `get_folder_structure()` function - Returns tree-like string representation of folder contents
- Updated `backend/services/summary_files.py`:
  - Modified `get_summary_file_path()` to save folder summaries in parent directory
  - Added `repo_name` parameter for root summary naming
  - Updated all helper functions to accept `repo_name` parameter
- Updated `backend/services/analyzer.py`:
  - Gets repository name from cache path
  - Includes folder structure in folder summary prompts
  - Enhanced root summary to include all folder and file summaries
  - Root summary saved as `<gitrepository>.md` instead of `README.md`
- Updated `backend/services/llm_service.py`:
  - Fixed folder prompts in all three providers (OpenAI, Ollama, DeepSeek)
  - Folder prompts now use `content` parameter for folder structure instead of asking for it

**Architecture Notes**:
- Folder summaries now saved in parent directory (e.g., `src/components.md` in `src/` directory)
- Root summary includes comprehensive context: repository structure + all folder summaries + all file summaries
- Folder structure provided as tree-like format (├── and └──) for better LLM understanding
- Root summary file named after repository (e.g., `octocat-Hello-World.md`) for easy identification
- All LLM prompts updated to provide actual folder structure instead of asking LLM to request it

**Review Notes**: These fixes ensure folder summaries work correctly by providing the actual folder structure to the LLM, and root summaries are comprehensive and properly named. The folder summary location change (parent directory) makes it easier to browse repository structure while keeping summaries organized.

---

### 2025-01-04 - Summary Truncation Fix & Root Node Naming
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Fix summaries being cut off and root node display issue  
**Prompts Used**:
- "It almost works but the summaries see cut off and unfinished..."
- "Also when it finishes it displays the README.md.md for that run but it should display the <repository>.md global summary for the repository"

**Decisions Made**:
- **Token Limit Increase**: Increased `max_tokens` from 500 to 4000 for all LLM providers
  - 500 tokens was too low, causing summaries to be cut off mid-sentence
  - 4000 tokens allows for comprehensive, detailed summaries
- **Root Node Naming**: Fixed root node name to use repository name instead of URL basename
  - Root node now displays as repository name (e.g., "appleboy-CodeIgniter-Log-Library")
  - Ensures frontend displays correct repository name, not "README.md.md"
- **Empty Repository Fix**: Empty repository case now also saves root summary with correct repo name

**Code Generated**:
- Updated `backend/services/llm_service.py`:
  - Changed `max_tokens=500` to `max_tokens=4000` in OpenAI and DeepSeek services
  - Added comment explaining the increase
- Updated `backend/services/analyzer.py`:
  - Root node name now uses `repo_name` variable instead of URL basename
  - Empty repository case also saves root summary file with repo name
  - Existing root nodes are updated with correct name

**Architecture Notes**:
- Token limit of 4000 allows for:
  - Comprehensive file summaries with all sections (purpose, functions, dependencies, etc.)
  - Detailed folder summaries with structure analysis
  - Complete root summaries with all folder and file summaries included
- Root node name fix ensures frontend displays repository name correctly
- Database Text field has no practical limit, so no database constraints
- LLM API limits: DeepSeek supports up to 16k tokens, OpenAI GPT-3.5/4 support up to 16k/128k tokens

**Review Notes**: The token limit increase is critical for generating comprehensive summaries. The previous 500 token limit was causing summaries to be cut off mid-sentence, making them incomplete and less useful for AI agents. The root node naming fix ensures users see the correct repository name in the frontend instead of confusing "README.md.md" text.

---

## Technology Stack & Architecture

### Frontend Technologies
- **React 18**: Component-based UI framework
- **TypeScript**: Type safety and better developer experience
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API communication
- **Role**: Provides user interface for repository analysis, visualization, and Q&A

### Backend Technologies
- **FastAPI**: Modern Python web framework with async support
- **SQLAlchemy**: ORM for database abstraction
- **Alembic**: Database migration tool
- **GitPython**: Git repository operations
- **Pydantic**: Data validation using Python type hints
- **Role**: Handles repository cloning, recursive analysis, LLM orchestration, and API endpoints

### Database Technologies
- **SQLite**: Development database (file-based, no setup required)
- **PostgreSQL**: Production database (robust, scalable)
- **pgvector**: PostgreSQL extension for vector similarity search
- **Role**: Stores repository metadata, hierarchical summaries, embeddings, and task status

### Containerization
- **Docker**: Containerization for consistent environments
- **Docker Compose**: Multi-container orchestration
- **Role**: Simplifies deployment, ensures consistency across environments, enables easy scaling

### CI/CD
- **GitHub Actions**: Automated testing and deployment
- **Role**: Ensures code quality, runs tests automatically, enables continuous deployment

### LLM Integration
- **OpenAI API**: GPT models for summarization
- **Ollama**: Local LLM option (privacy-focused)
- **DeepSeek Coding**: Cost-effective code-focused LLM (recommended)
- **Role**: Generates summaries at file, folder, and project levels

### MCP (Model Context Protocol)
- **Filesystem MCP**: Used during development for project context
- **R2CE MCP Server**: Exposes repository analysis tools to AI agents
- **Role**: Enables AI agents to interact with R2CE system programmatically

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                         │
│  React + TypeScript + Vite                                   │
│  - RepoAnalyzer (trigger analysis)                           │
│  - TreeView (visualize summaries)                             │
│  - SearchBar (search summaries)                               │
│  - QAInterface (ask questions)                               │
│  - Centralized API Client (api.ts)                            │
└───────────────────────┬───────────────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼───────────────────────────────────────┐
│                        Backend Layer                           │
│  FastAPI + Python                                              │
│  - API Routes (/api/analyze, /status, /tree, /search, /qa)    │
│  - Recursive Analyzer (bottom-up summarization)                │
│  - LLM Service (OpenAI/Ollama/DeepSeek abstraction)            │
│  - Git Service (clone & traverse)                              │
│  - Q&A Service (context-aware answering)                       │
│  - Background Tasks (async processing)                         │
└───────────────────────┬───────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌────────▼────────┐
│  Database      │            │  File System     │
│  SQLite/       │            │  Cloned Repos    │
│  PostgreSQL    │            │  (temporary)     │
│  + pgvector    │            │                  │
└────────────────┘            └──────────────────┘
```

## How Technologies Fit Together

1. **Frontend ↔ Backend**: React frontend communicates with FastAPI backend via REST API (centralized in `api.ts`)
2. **Backend ↔ Database**: SQLAlchemy abstracts database differences, Alembic manages schema changes
3. **Backend ↔ LLM**: LLM service abstraction allows switching providers without code changes
4. **Backend ↔ Git**: GitPython handles repository cloning and traversal
5. **Containerization**: Docker Compose orchestrates all services (frontend, backend, database)
6. **CI/CD**: GitHub Actions runs tests and can deploy to cloud platforms
7. **MCP**: Bridges AI agents with R2CE system, enabling programmatic access

## Key Architectural Decisions

1. **Contract-First API**: OpenAPI spec drives backend implementation
2. **Database Abstraction**: Single codebase works with SQLite (dev) and PostgreSQL (prod)
3. **Provider Abstraction**: LLM provider switching via environment variable
4. **Centralized API Client**: All frontend API calls go through single module
5. **Bottom-Up Analysis**: Ensures summaries are grounded in actual code
6. **Async Processing**: Background tasks prevent API blocking
7. **Type Safety**: TypeScript frontend + Pydantic backend = end-to-end type safety

## MCP Implementation Status

**MCP Server**: ✅ **COMPLETE** - Fully implemented and tested in `mcp/r2ce-server/server.py`:
- ✅ Virtual environment created locally (`mcp/r2ce-server/venv/`)
- ✅ MCP SDK v1.25.0 installed and working
- ✅ All imports working correctly (Server, stdio_server, Tool, TextContent)
- ✅ Four tools fully implemented and tested:
  - `analyze_repository` - Trigger repository analysis
  - `get_repository_tree` - Get hierarchical summary tree
  - `search_repository` - Search across summaries
  - `ask_repository_question` - Answer questions about repositories
- ✅ HTTP-based integration with backend API
- ✅ Error handling implemented (HTTP errors, import errors)
- ✅ Environment variable support (`R2CE_API_URL`)
- ✅ Tested and verified working (`test_server.py` passes)
- ✅ Setup scripts and documentation complete

**Filesystem MCP**: Used during development via Cursor IDE to:
- Navigate project structure
- Understand file relationships
- Maintain context across development sessions

**MCP Client Configuration**: Ready for integration with Cursor/Claude Desktop:
- Command: `mcp/r2ce-server/venv/bin/python`
- Args: `["mcp/r2ce-server/server.py"]`
- Env: `R2CE_API_URL=http://localhost:8000/api`

---

### 2025-01-04 - Browse Feature, Filesystem Precedence & DeepSeek Coder
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Add browse feature for cache summaries, implement filesystem precedence, switch to DeepSeek Coder model  
**Prompts Used**:
- "can you also provide a browse section for the repository cache summaries for all files and folders in their structure? Make it secure/safe. Also should i delete the database entries too? I dont want to have to delete those so can we make the filesystem cache take presedence (so if the file does not exist it gets re-summarized and database is updated also even if it exists in the db). And if possible instead of deepseek.chat can we use a coder specific model?"

**Decisions Made**:
- **Browse Feature**: Created secure API endpoint (`/api/browse/{repo_id}`) with path traversal protection
- **Filesystem Precedence**: Analyzer now checks filesystem cache first - if summary file doesn't exist, it re-summarizes even if DB has entry
- **DeepSeek Coder**: Changed default model from `deepseek-chat` to `deepseek-coder` for better code understanding
- **Security**: Implemented `secure_path_join()` function to prevent directory traversal attacks
- **No DB Deletion Required**: Filesystem cache is authoritative - DB entries are updated when summaries are regenerated

**Code Generated**:
- `backend/api/routes/browse.py` - New secure browse endpoint with:
  - Path traversal protection using `secure_path_join()`
  - Directory listing with summary indicators
  - File content and summary display
  - Root summary display for folders
- `frontend/src/components/BrowseView.tsx` - New React component for browsing cache:
  - Navigation (back, parent, click to navigate)
  - Folder/file listing with summary badges
  - Markdown rendering for summaries
  - File content display
- `frontend/src/components/BrowseView.css` - Styling for browse component
- Updated `backend/main.py` - Added browse router
- Updated `frontend/src/services/api.ts` - Added `browse()` method
- Updated `frontend/src/App.tsx` - Added BrowseView component
- Updated `docs/openapi.yaml` - Added `/browse/{repo_id}` endpoint specification
- Updated `backend/config.py` - Changed `deepseek_model` to `deepseek-coder`
- Updated `backend/services/analyzer.py` - Added comments clarifying filesystem precedence

**Architecture Notes**:
- **Security**: All paths are validated to ensure they stay within the cache directory, preventing directory traversal attacks
- **Filesystem Authority**: Summary files on disk are the source of truth - if a file doesn't exist, it will be regenerated regardless of DB state
- **Browse Feature**: Enables users to explore repository structure and summaries directly from the file system, complementing the tree view
- **DeepSeek Coder**: Specialized model for code understanding provides better summaries for programming tasks

**Review Notes**: The browse feature provides a file-system view of summaries, making it easy to explore cached repositories. Filesystem precedence ensures consistency - summaries are always regenerated if files are missing, keeping DB in sync. The security measures prevent any path traversal vulnerabilities.

---

### 2025-01-04 - Progress Bar Fix, Status Messages & Cache Browser
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Fix progress bar display, add detailed status messages, fix tree view root display, fix browse navigation, add cache browser  
**Prompts Used**:
- "ok so now the summaries are good but its taking a long time even for small repositories so the Status processing... and the bar is not enough feedback for the process..."
- "i get Error: Failed to load cached repositories and in the chrome dev console: [vite] hot updated: /src/App.tsx..."

**Decisions Made**:
- **Progress Bar Fix**: Changed from inline `width` style to CSS custom property `--progress-width` to fix display bug (bar showing full at 10%, 50%, etc.)
- **Status Messages**: Added `status_message` field to Task model to provide detailed progress updates:
  - "Getting repository..."
  - "Cloning repository..."
  - "Processing X files..."
  - "Processing file: <filename>"
  - "Processing folder: <foldername>"
  - "Generating repository summary..."
  - "Analysis completed!"
- **Tree View Root Fix**: Updated tree endpoint to explicitly find root node (`path=""` and `parent_id=None`) to ensure global repository summary is displayed
- **Browse Navigation Fix**: Fixed path splitting to handle empty strings and filter out empty path parts
- **Cache Browser**: Added `/api/cache` endpoint and `CacheBrowser` component to list and browse cached repositories
- **CORS Fix**: Added additional allowed origins including Vite default port (5173) and 127.0.0.1 variants
- **Error Handling**: Added try-catch in cache endpoint to handle path resolution errors gracefully

**Code Generated**:
- Updated `backend/models/task.py` - Added `status_message` field
- Updated `backend/schemas/task.py` - Added `status_message` to schema
- Updated `backend/api/routes/status.py` - Returns `status_message` in response
- Updated `backend/services/analyzer.py` - Sets detailed status messages throughout analysis process
- Updated `backend/api/routes/tree.py` - Fixed to explicitly find and return root node
- Updated `backend/api/routes/browse.py` - Fixed path handling for folder navigation
- `backend/api/routes/cache.py` - New endpoint for listing cached repositories
- `backend/db/migrations/versions/002_add_status_message.py` - Migration for status_message field
- Updated `frontend/src/components/RepoAnalyzer.tsx` - Display status_message, fixed progress bar CSS
- Updated `frontend/src/components/RepoAnalyzer.css` - Fixed progress bar using CSS custom properties
- `frontend/src/components/CacheBrowser.tsx` - New component for browsing cached repos
- `frontend/src/components/CacheBrowser.css` - Styling for cache browser
- Updated `frontend/src/services/api.ts` - Added `listCachedRepos` method
- Updated `frontend/src/App.tsx` - Added CacheBrowser component to home page
- Updated `backend/main.py` - Added cache router, expanded CORS origins

**Architecture Notes**:
- **Status Messages**: Provide real-time feedback during long-running analysis operations
- **Progress Bar**: CSS custom properties ensure correct width calculation and display
- **Tree View**: Root node is now correctly identified and displayed with global summary
- **Cache Browser**: Enables users to browse and select previously analyzed repositories
- **CORS**: Expanded allowed origins to support different development setups (Vite, different ports)

**Review Notes**: These improvements significantly enhance user experience by providing detailed feedback during analysis and enabling easy browsing of cached repositories. The progress bar fix ensures accurate visual feedback, and status messages help users understand what's happening during long operations.

---

### 2025-01-04 - Browse Feature Fixes: File Display & Parent Navigation
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Fix browse feature to display files correctly and add parent folder navigation  
**Prompts Used**:
- "it now works but its not displaying the files it says Folder is empty when folder when has a file. It should also browse the files. And there is also no way to go back in folder to the parent folder it does not show .."

**Decisions Made**:
- **File Display Fix**: Changed filter logic to show all files (including .md files) - only skip `.git` directory and hidden files starting with `.`
- **Summary Detection**: Fixed summary detection logic to properly check for summary files:
  - Files: Check for `<filename>.md` summary file
  - Folders: Check for `<foldername>.md` summary in parent directory
- **Parent Navigation**: Added ".." entry at the beginning of folder listings when not at root
- **Navigation Handling**: Updated frontend to handle ".." clicks to navigate to parent directory

**Code Generated**:
- Updated `backend/api/routes/browse.py`:
  - Fixed file filtering to show all files (not just non-.md files)
  - Only skip `.git` directory and hidden files/folders
  - Added parent folder ".." entry to items list when not at root
  - Fixed summary detection for both files and folders
- Updated `frontend/src/components/BrowseView.tsx`:
  - Added special handling for ".." navigation
  - Updated icon display to show ⬆️ for parent directory
  - Fixed key prop to handle ".." entries properly

**Architecture Notes**:
- **File Visibility**: All files are now visible in browse view, including summary `.md` files
- **Parent Navigation**: ".." entry provides intuitive way to navigate up directory tree
- **Summary Detection**: Properly distinguishes between original files and their summary files
- **User Experience**: Users can now browse complete repository structure including all files

**Review Notes**: These fixes make the browse feature fully functional - users can now see all files in folders and navigate back to parent directories easily. The ".." entry provides standard file browser navigation pattern that users expect.

---

### 2025-01-04 - Browse Feature: File Filtering & Summary Display Fixes
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Fix file display to show files in all folders, filter out summary .md files, and properly display file summaries  
**Prompts Used**:
- "it now shows the files for the root folder only not the inner folders, it should show the files for the inner folders as well. And it should not show the generated .md files..."

**Decisions Made**:
- **Summary File Filtering**: Implemented logic to detect and filter out generated summary `.md` files
  - Summary files are `<filename>.md` alongside original files
  - Detection: if a `.md` file exists and there's another file with the same base name, it's a summary
  - Original `.md` files (like README.md) are still shown
- **File Display**: Fixed to show files in all folders (not just root)
- **Summary Display**: When clicking a file, show its summary from the corresponding `.md` file
- **Missing Summary Handling**: Display message when summary hasn't been generated yet
- **Error Prevention**: Prevent clicking on summary files (they're filtered out)

**Code Generated**:
- Updated `backend/api/routes/browse.py`:
  - Added logic to detect summary files by checking if a `.md` file has a corresponding original file
  - Filter out summary `.md` files from directory listings
  - Added `summary_exists` flag to file response
  - Fixed file display to work in all folders
- Updated `frontend/src/components/BrowseView.tsx`:
  - Handle `summary_exists` flag to show appropriate message when summary is missing
  - Display "Summary has not been generated for this file yet" message
- Updated `frontend/src/components/BrowseView.css`:
  - Added styling for missing summary message

**Architecture Notes**:
- **Summary File Detection**: Checks if a `.md` file is a summary by looking for corresponding original file
- **File Browsing**: All original repository files are now visible in all folders
- **Summary Access**: Clicking a file shows its summary from the corresponding `.md` file
- **User Experience**: Clear indication when summaries haven't been generated yet

**Review Notes**: These fixes ensure users can browse all original files in the repository structure, while summary files (metadata) are hidden. When viewing a file, users see its summary if available, or a clear message if it hasn't been generated yet. This provides a clean browsing experience focused on the actual repository files.

---

### 2025-01-04 - Q&A & Search Improvements: Repository-Specific Results & Better Answers
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Fix Q&A to provide specific answers and fix search to work with selected repository  
**Prompts Used**:
- "tell me how is the ask_repository_question working? I clicked it with question 'how can i change the log format' and it took a long time and the answer was just the whole repository summary..."

**Decisions Made**:
- **Search Repository Filtering**: Added `repo_id` parameter to search functions to filter results by repository
- **Search UI**: Updated SearchBar to accept `repoId` prop and show error if no repository selected
- **Q&A Improvements**: 
  - Search now filters by repository (not all repositories)
  - Improved prompt to ask for specific file paths and code references
  - Better context building with file paths included in summaries
  - More actionable answers with specific code locations
- **Search Scoring**: Enhanced relevance scoring with:
  - Exact phrase match = highest score (2.0)
  - All words present = high score (1.5)
  - Some words present = medium score (1.0)
  - Path matching bonus (+0.5)

**Code Generated**:
- Updated `backend/services/embedding_service.py`:
  - Added `repo_id` parameter to `search_summaries()` function
  - Enhanced scoring algorithm for better relevance
  - Filters results by repository when `repo_id` provided
- Updated `backend/api/routes/search.py`:
  - Added `repo_id` query parameter
  - Passes `repo_id` to search function
- Updated `backend/services/qa_service.py`:
  - Now searches within specific repository only
  - Improved prompt to ask for specific file/line references
  - Better context building with file paths
  - Uses top 5 results instead of 3 for better context
- Updated `frontend/src/components/SearchBar.tsx`:
  - Added `repoId` prop
  - Shows error if no repository selected
  - Displays "No results found" message
  - Shows result count
- Updated `frontend/src/services/api.ts`:
  - Added `repoId` parameter to `search()` method
- Updated `frontend/src/App.tsx`:
  - Passes `selectedRepoId` to SearchBar component
- Updated `frontend/src/components/SearchBar.css`:
  - Added error message styling
- Updated `docs/openapi.yaml`:
  - Added `repo_id` parameter to search endpoint

**Architecture Notes**:
- **Repository-Specific Search**: Search now works within the context of the selected repository
- **Better Q&A Answers**: Improved prompts ensure LLM provides specific file paths and code references
- **Enhanced Relevance**: Better scoring algorithm provides more relevant search results
- **User Experience**: Clear error messages guide users to select a repository first

**Review Notes**: These improvements make search and Q&A much more useful. Search now works within the selected repository context, and Q&A provides specific, actionable answers with file paths and code references instead of generic repository summaries. The enhanced scoring ensures more relevant results are shown first.

---

### 2025-01-04 - Q&A Prompt & Model Fix: Proper Q&A Method and DeepSeek Coder
**AI Tool**: Cursor (Claude Sonnet)  
**Task**: Fix Q&A to use proper Q&A prompt instead of file summarization prompt, and ensure DeepSeek uses coder model  
**Prompts Used**:
- "The ask_repository_question is not using the deepseek coder but chat model first of all. Second the prompt is completely wrong..."

**Decisions Made**:
- **Separate Q&A Method**: Created dedicated `answer_question()` method in LLM service instead of reusing `generate_summary()`
- **Proper Q&A Prompt**: Q&A now uses a question-answering prompt instead of file analysis prompt
- **DeepSeek Coder Model**: Added auto-upgrade from `deepseek-chat` to `deepseek-coder` in DeepSeekService initialization
- **Context Filtering**: Q&A service now properly filters context from search results (only relevant summaries)
- **All Providers Support Q&A**: Added `answer_question()` implementations for OpenAI, Ollama, and DeepSeek

**Code Generated**:
- Updated `backend/services/llm_service.py`:
  - Added `answer_question()` abstract method to `LLMService` base class with default implementation
  - Added explicit `answer_question()` implementations for `OpenAIService`, `OllamaService`, and `DeepSeekService`
  - Each uses proper Q&A prompt (not file summarization prompt)
  - DeepSeekService auto-upgrades `deepseek-chat` to `deepseek-coder` in `__init__`
  - Q&A calls log with `item_type="qa"` for better tracking
- Updated `backend/services/qa_service.py`:
  - Changed from `llm_service.generate_summary(prompt, item_type="file")` to `llm_service.answer_question(question, context)`
  - Removed duplicate prompt building (now handled by LLM service)

**Architecture Notes**:
- **Separation of Concerns**: Q&A and summarization are now separate methods with different prompts
- **Model Selection**: DeepSeek automatically uses the coder model for better code understanding
- **Context Management**: Q&A receives filtered, relevant context from search results
- **Consistency**: All LLM providers now support Q&A with consistent interface

**Review Notes**: This fix ensures Q&A uses the correct prompt format and model. The Q&A prompt is specifically designed for answering questions with actionable information, while the summarization prompt is for analyzing code structure. DeepSeek now correctly uses the coder model which is better suited for code-related questions.

## Next Steps

1. Test with small GitHub repository
2. Fix any issues discovered during testing
3. Complete Docker setup and test
4. Deploy to cloud platform
5. Enhance MCP server implementation if needed
