# Recursive Repository Context Engine (R2CE)

> **📊 [Evaluators please see reference for each evaluation point](EVALUATION.md)** 

## 📍 Overview

The **Recursive Repository Context Engine (R2CE)** is an AI-native
developer tool designed to solve the \"Context Wall\" in AI-assisted
development. While standard LLMs struggle with large codebases due to
token limits, R2CE creates a **Bottom-Up Recursive Summary** of any Git
repository. It transforms raw code into a hierarchical map of Markdown
and YAML summaries, allowing agents to navigate complex architectures
with high precision and low token cost.

The user can crawl any public git repository with an LLM, currently 
DeepSeek Coder, and store development summaries and embeddings (RAG) 
and ask questions or talk with the repository.

Both the RAG and the summaries can be used to create an AI Dev Tool that
 already understands the input repository and knows how to extend it.

## 🤖 Problem Description

As projects scale, feeding an entire codebase into an AI context window
becomes expensive, slow, and inaccurate. R2CE addresses this by:

-   **Recursive Analysis:** Summarizing individual files first (leaves),
    then using those summaries to describe folders (branches), and
    finally the entire project (root).
-   **Hybrid RAG:** Utilizing **PostgreSQL + pgvector** to allow for
    semantic search across code summaries.
-   **Agent-First Design:** Exporting structured *.context/* data that
    AI agents can use to \"re-program\" or modify the project without
    reading every line of source code.
### What the Project Does

R2CE is a web application that:
1. **Clones and analyzes** any Git repository (public or private with passphrase)
2. **Recursively generates AI summaries** using LLMs (OpenAI, DeepSeek, or Ollama)
3. **Creates embeddings** for semantic search across code
4. **Provides interactive interfaces** for:
   - Browsing the analyzed repository structure
   - Searching through code summaries
   - Asking questions about the codebase
   - Viewing hierarchical tree representations
5. **Exposes MCP tools** for AI agents to interact with analyzed repositories

## Running Demo
- **Backend**: https://r2ce-backend.onrender.com
  - API documentation available at `/docs`
  - Health check at `/health`
- **Frontend**: https://r2ce-frontend.onrender.com
  - Fully functional UI
  - Connected to production backend
- **Database**: PostgreSQL managed service on Render

## 🔮 Features

-   **Automatic Git Cloning:** Connect any public or private repository.
-   **Bottom-Up Processing:** Ensures high-level summaries are grounded
    in actual code logic.
-   **Hybrid Search:** Combine SQL metadata filters with Vector
    similarity search.
-   **Interactive Tree View:** A React-based explorer to visualize
    AI-generated insights.
-   **API-First Architecture:** Fully documented with OpenAPI/Swagger.

## 🏗 System Architecture

The system consists of three core layers:

1.  **Frontend:** React + TypeScript + Vite + Tailwind CSS
    - **Components:** RepoAnalyzer, QAInterface, SearchBar, BrowseView, TreeView
    - **API Client:** Centralized API communication via `services/api.ts`
    - **Testing:** Vitest + React Testing Library for unit and integration tests
    - **Styling:** CSS modules with Tailwind CSS utilities

2.  **Backend:** FastAPI (Python) implementing the recursive logic and LLM orchestration
    - **Services:** GitService (cloning), LLMService (summarization), EmbeddingService (vectors)
    - **API Routes:** `/analyze`, `/status/{task_id}`, `/tree/{repo_id}`, `/search`, `/qa`, `/browse/{repo_id}`, `/cache`
    - **Database:** SQLAlchemy ORM with Alembic migrations
    - **Testing:** pytest with unit and integration test suites
    - **Background Tasks:** Async task processing for repository analysis

3.  **Database:** PostgreSQL with the *pgvector* extension for storing hierarchical metadata and embeddings
    - **Models:** Repository, Node (hierarchical tree), Task (async jobs)
    - **Dev/Prod:** SQLite for development, PostgreSQL for production
    - **Migrations:** Alembic for version control

## 🛠 Tech Stack

### Frontend
-   **Framework:** React 18 with TypeScript
-   **Build Tool:** Vite (fast HMR, optimized builds)
-   **HTTP Client:** Axios with interceptors
-   **Styling:** CSS Modules + Tailwind CSS
-   **Markdown:** react-markdown for rendering AI responses
-   **Testing:** Vitest + React Testing Library + @testing-library/user-event

### Backend
-   **Framework:** FastAPI (Python 3.10+) with async/await
-   **LLM Integration:** LangChain for OpenAI, DeepSeek, Ollama
-   **Git Operations:** GitPython for repository cloning and analysis
-   **Database:** SQLAlchemy (ORM) + Alembic (migrations)
-   **Vector Store:** pgvector extension for PostgreSQL
-   **Testing:** pytest + pytest-asyncio + pytest-cov
-   **Background Jobs:** BackgroundTasks for async processing

### Database
-   **Development:** SQLite (lightweight, file-based)
-   **Production:** PostgreSQL 14+ with pgvector extension
-   **Migrations:** Alembic for schema version control

### DevOps & Deployment
-   **Containerization:** Docker + Docker Compose (multi-service orchestration)
-   **CI/CD:** GitHub Actions for automated testing
-   **Deployment:** Render / Railway (Cloud) with environment-based configuration
-   **Monitoring:** Structured logging with JSON format

## 📄 API Specification (OpenAPI)

The project follows a **Contract-First** approach. The API is fully
defined in `docs/openapi.yaml` and used as the contract for backend development.

Key Endpoints:

-   `POST /api/analyze`: Trigger a new repository analysis.
-   `GET /api/status/{task_id}`: Poll for analysis progress.
-   `GET /api/tree/{repo_id}`: Retrieve the full recursive summary tree.
-   `GET /api/search`: Semantic search over project summaries.
-   `POST /api/qa`: Answer questions about a repository.

API documentation is available at `/docs` when the backend is running.

## 🤖 AI System Development & MCP

This project was developed using AI-assisted development with **Cursor** and **Claude Sonnet**.

-   **AGENTS.md:** Contains specific instructions for AI agents regarding recursive summarization logic and code style.
-   **DEVELOPMENT_LOG.md:** Comprehensive log of all AI interactions, prompts used, and decisions made during development.
-   **MCP (Model Context Protocol):** 
    - **Filesystem MCP**: Used during development to maintain context of the evolving project structure.
    - **R2CE MCP Server**: Created MCP server (`mcp/r2ce-server/`) that exposes repository analysis tools for AI agents.
-   **Documentation:** See `AGENTS.md` for detailed development workflow and MCP usage.

## �️ Database Layer

The database layer is **environment-agnostic** and supports multiple database backends:

### Supported Databases

**Development (SQLite):**
- Lightweight, file-based database
- Zero configuration required
- Perfect for local development and testing
- Database file: `backend/r2ce.db`

**Production (PostgreSQL):**
- Full-featured relational database with pgvector extension
- Supports vector similarity search for embeddings
- Configured via `DATABASE_URL` environment variable
- Included in `docker-compose.yml` for easy deployment

### Database Configuration

The database is configured via the `DATABASE_URL` environment variable:

```bash
# SQLite (Development) - Default
DATABASE_URL=sqlite:///r2ce.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Database Schema

**Models:**
- `Repository`: Tracks analyzed repositories (id, url, name, status, created_at)
- `Node`: Hierarchical tree structure (id, repo_id, path, node_type, summary, embedding, parent_id)
- `Task`: Async job tracking (id, status, progress, result_id, created_at)

**Migrations:**
- Managed by Alembic for version control
- Located in `backend/db/migrations/`
- Run with: `alembic upgrade head`

### Environment Switching

The system automatically adapts based on `DATABASE_URL`:

```python
# backend/db/base.py
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.environment == "development",
)
```

**SQLite-specific:**
- `check_same_thread=False` for multi-threaded access
- Simple file-based storage

**PostgreSQL-specific:**
- Connection pooling
- pgvector extension for embeddings
- Full ACID compliance

### Docker Compose Database

The `docker-compose.yml` includes a PostgreSQL service:

```yaml
db:
  image: postgres:15
  environment:
    POSTGRES_USER: r2ce
    POSTGRES_PASSWORD: r2ce_password
    POSTGRES_DB: r2ce
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

Backend automatically connects to PostgreSQL when running via Docker.

## �🚀 Getting Started
> **🎯 Quick Start:** For a complete walkthrough from setup to deployment, see **[END_TO_END_GUIDE.md](END_TO_END_GUIDE.md)** - a comprehensive guide covering setup, running, testing, and deployment.
### Prerequisites

- Docker & Docker Compose
- LLM API Key (OpenAI, DeepSeek, or Ollama running locally)

### Installation & Local Setup

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/r2ce.git
cd r2ce
```

2. **Environment Variables:** Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `LLM_PROVIDER`: Choose `openai`, `ollama`, or `deepseek`
- `DEEPSEEK_API_KEY`: If using DeepSeek (recommended)
- `OPENAI_API_KEY`: If using OpenAI
- `OLLAMA_BASE_URL`: If using Ollama (default: `http://localhost:11434`)
- `MAX_GIT_SIZE_KB`: Maximum repository size in KB (default: `10` for demo version, set to `0` for no limit)

For development, the default SQLite database is used. For production, set `DATABASE_URL` to a PostgreSQL connection string.

**Note:** The demo version limits repository size to 10KB by default. Repositories exceeding this limit will be rejected with an error message. Set `MAX_GIT_SIZE_KB=0` to disable this limit. Size checking uses the GitHub API, so it only works for GitHub repositories. Non-GitHub repositories will proceed without size checking.

3. **Run with Docker Compose:**

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Running Tests

**Backend Tests:**

The backend includes comprehensive test coverage with unit and integration tests:

```bash
# Run all backend tests
docker-compose exec backend pytest

# Run unit tests only (services: Git, LLM, Embedding)
docker-compose exec backend pytest backend/tests/unit/

# Run integration tests only (API endpoints, database operations)
docker-compose exec backend pytest backend/tests/integration/

# Run with coverage report
docker-compose exec backend pytest --cov=backend --cov-report=html
```

**Test Structure (Backend):**
- `unit/test_git_service.py` - Git cloning and repository operations
- `unit/test_llm_service.py` - LLM summarization with mocked API calls
- `unit/test_embedding_service.py` - Embedding generation and storage
- `integration/test_api_endpoints.py` - Full API workflow tests (analyze→status→tree, search, browse, Q&A)
- `integration/test_database.py` - Database operation tests (CRUD, hierarchical relationships, status workflows)

**Integration Test Workflows:**
1. **Complete Analysis Workflow**: POST /analyze → GET /status → GET /tree
2. **Search with Repository Filter**: Create repo → Add nodes → Search with filter
3. **Browse Repository Structure**: Hierarchical navigation and folder browsing
4. **Hierarchical Node Relationships**: Parent-child folder/file relationships
5. **Repository Status Transitions**: PENDING → PROCESSING → COMPLETED
6. **Task Progress Tracking**: Async task lifecycle (0→50→100% progress)
7. **Q&A Workflow**: Repository context → Question → Answer with sources

**Frontend Tests:**

The frontend includes tests for core components and services:

```bash
# Run all frontend tests
docker-compose exec frontend npm test

# Run with UI (interactive)
docker-compose exec frontend npm run test:ui

# Run with coverage
docker-compose exec frontend npm run test:coverage
```

**Test Structure (Frontend):**
- `components/__tests__/RepoAnalyzer.test.tsx` - Repository analysis form
- `components/__tests__/QAInterface.test.tsx` - Q&A interface with passphrase
- `components/__tests__/SearchBar.test.tsx` - Search functionality
- `services/__tests__/api.test.ts` - API client service with all endpoints

**Test Coverage:**
- ✅ **Backend:** Unit tests for all services, integration tests for API workflows
- ✅ **Frontend:** Component tests with user interactions, API client tests with mocked responses
- ✅ **Contract Testing:** Tests verify OpenAPI specification compliance

See `backend/tests/README.md` for detailed testing documentation.

### Example Repositories for Testing

To test R2CE with small repositories, you can find repositories under 10KB using GitHub's advanced search:

🔗 [GitHub Search: Repositories under 10KB](https://github.com/search?q=size%3A10&type=repositories&ref=advsearch)

These small repositories are perfect for quick testing and understanding how R2CE processes and summarizes codebases.

We have pre-crawled https://github.com/denissimon/prediction-builder so you can browse and see the results.

### Local Development (Without Docker)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

**Running Migrations:**

```bash
# For Docker deployment
docker-compose exec backend alembic upgrade head

# For local development
cd backend
alembic upgrade head
```

**Creating New Migrations:**

```bash
# Auto-generate migration from model changes
docker-compose exec backend alembic revision --autogenerate -m "description"

# For local development
cd backend
alembic revision --autogenerate -m "description"
```

**Migration History:**

```bash
# View current version
alembic current

# View migration history
alembic history
```

### Switching Between Databases

**Local Development (SQLite):**
```bash
# .env file
DATABASE_URL=sqlite:///r2ce.db

# Start backend
cd backend
uvicorn main:app --reload
```

**Docker (PostgreSQL):**
```bash
# Uses DATABASE_URL from docker-compose.yml automatically
docker-compose up --build
```

**Production (External PostgreSQL):**
```bash
# Set DATABASE_URL to your production database
export DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/r2ce

# Run migrations
alembic upgrade head

# Start application
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🚀 Deployment & CI/CD

-   **CI (Continuous Integration):** GitHub Actions automatically runs all tests on every Pull Request and push to `main` (see `.github/workflows/ci.yml`).
-   **CD (Continuous Deployment):** Automatic deployment to Render when tests pass on `main` branch.
-   **Setup Guide:** See [CI_CD_SETUP.md](CI_CD_SETUP.md) for complete CI/CD pipeline configuration.
-   **Deployment Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive step-by-step deployment instructions.
-   **Test-Driven Deployment:** Code is only deployed after all backend and frontend tests pass successfully.

### Quick Deploy to Render

1. Create PostgreSQL database on Render
2. Deploy backend service (Python 3, connect to database)
3. Deploy frontend as static site (connect to backend)
4. Run database migrations: `alembic upgrade head`
5. Test deployed application at your URLs

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions with all commands and configuration details.**

---

## 📚 Documentation Index

Quick links to all project documentation:

- **[END_TO_END_GUIDE.md](END_TO_END_GUIDE.md)** ⭐ - **Complete walkthrough: Setup → Run → Test → Deploy**
- **[DEPLOYMENT_SECURITY.md](DEPLOYMENT_SECURITY.md)** 🔒 - **Security & secrets management explained**
- **[README.md](README.md)** - Main project documentation (this file)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Step-by-step deployment to Render/Railway
- **[CI_CD_SETUP.md](CI_CD_SETUP.md)** - CI/CD pipeline configuration guide
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing strategy and instructions
- **[AGENTS.md](AGENTS.md)** - AI agent development workflow and MCP usage
- **[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)** - Complete AI development session log
- **[EDGE_CASES.md](EDGE_CASES.md)** - Edge cases and error handling
- **[docs/openapi.yaml](docs/openapi.yaml)** - OpenAPI specification
- **[backend/tests/README.md](backend/tests/README.md)** - Backend test documentation
- **[mcp/r2ce-server/README.md](mcp/r2ce-server/README.md)** - MCP server documentation
