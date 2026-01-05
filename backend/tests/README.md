# Testing Guide

## Test Organization

Tests are **clearly separated** into two categories:

### Unit Tests (\`backend/tests/unit/\`)
**Purpose:** Test individual components in isolation with mocked dependencies.

**Characteristics:**
- Fast execution (no I/O operations)
- No database connections  
- No external API calls
- Mock all dependencies (LLM APIs, Git operations, etc.)

**Files:**
- \`test_git_service.py\` - Git cloning and repository operations (mocked)
- \`test_llm_service.py\` - LLM summarization with mocked API calls
- \`test_embedding_service.py\` - Embedding generation without real API calls

### Integration Tests (\`backend/tests/integration/\`)
**Purpose:** Test complete workflows with real database interactions and API endpoints.

**Characteristics:**
- Tests full request/response cycles
- Uses real database (in-memory SQLite for tests)
- Tests multiple components working together
- Validates end-to-end functionality

**Files:**
- \`test_api_endpoints.py\` - API workflow integration tests
- \`test_database.py\` - Database operation integration tests

**Key Integration Test Workflows:**

#### 1. Complete Analysis Workflow (\`test_api_endpoints.py\`)
Tests the complete repository analysis pipeline: POST /analyze → GET /status → GET /tree

#### 2. Search with Repository Filter (\`test_api_endpoints.py\`)
Tests database interactions: Create repo → Add nodes → Search with filter

#### 3. Browse Repository Structure (\`test_api_endpoints.py\`)
Tests navigation: Create hierarchical structure → Browse root → Browse subfolder

#### 4. Hierarchical Node Structure (\`test_database.py\`)
Tests parent-child relationships: Create parent folder → Create child file → Verify relationships

#### 5. Repository Status Workflow (\`test_database.py\`)
Tests state transitions: PENDING → PROCESSING → COMPLETED

#### 6. Task Progress Tracking (\`test_database.py\`)
Tests async task lifecycle: Create task → Update progress (0→50→100) → Mark completed

#### 7. Q&A Workflow (\`test_api_endpoints.py\`)
Tests Q&A feature: Create completed repo → Add nodes → Ask question → Get answer

## Running Tests

### Unit Tests
\`\`\`bash
pytest backend/tests/unit/
\`\`\`

### Integration Tests
\`\`\`bash
pytest backend/tests/integration/
\`\`\`

### All Tests
\`\`\`bash
pytest backend/tests/
\`\`\`

### With Coverage
\`\`\`bash
pytest backend/tests/ --cov=backend --cov-report=html
\`\`\`

## Test Database

**Unit Tests:**
- Use mocks and do NOT connect to any database
- Fastest execution

**Integration Tests:**
- Use in-memory SQLite database (\`sqlite:///:memory:\`)
- Fresh database for each test via \`conftest.py\` fixtures
- Automatically cleaned up after each test
