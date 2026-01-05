# Testing Guide - Small Repository Test

This guide walks through testing R2CE with a small GitHub repository before Docker deployment.

## Prerequisites

1. Python 3.11+ installed
2. Node.js 20+ installed (for frontend)
3. LLM API key (DeepSeek recommended, or OpenAI/Ollama)
4. Git installed

## Step 1: Backend Setup

### 1.1 Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1.2 Configure Environment

Create `.env` file in project root:

```bash
cd ..  # Back to project root
cp .env.example .env
```

Edit `.env`:
```bash
DATABASE_URL=sqlite:///r2ce.db
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

### 1.3 Initialize Database

```bash
# From project root (parent of backend directory)
# Set PYTHONPATH to project root (so Python can find 'backend' package)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Create database tables
python -c "from backend.db.base import Base, engine; Base.metadata.create_all(bind=engine)"
```

**Note**: The database will also be auto-created when the backend starts, so this step is optional. Make sure you're in the project root when setting PYTHONPATH.

### 1.4 Start Backend Server

```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend should be running at http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Step 2: Frontend Setup (Optional for API Testing)

### 2.1 Install Dependencies

```bash
cd frontend
npm install
```

### 2.2 Start Frontend

```bash
npm run dev
```

Frontend should be running at http://localhost:3000

## Step 3: Test with Small Repository

### Test Repository Recommendation

Use a small, simple repository for initial testing:
- **Option 1**: `https://github.com/octocat/Hello-World` (GitHub's demo repo)
- **Option 2**: `https://github.com/vercel/next.js/tree/canary/examples/hello-world` (very small Next.js example)
- **Option 3**: Any small personal repository with < 10 files. You can search github for such repositories by visiting:
https://github.com/search?q=size%3A10&type=repositories&ref=advsearch

### 3.1 Test via API (curl/Postman)

#### Start Analysis

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/octocat/Hello-World",
    "depth": 3
  }'
```

Expected response:
```json
{
  "task_id": "uuid-here"
}
```

#### Check Status

```bash
# Replace TASK_ID with the task_id from previous response
curl "http://localhost:8000/api/status/TASK_ID"
```

Poll this endpoint every 2-3 seconds until status is "completed".

Expected response when completed:
```json
{
  "status": "completed",
  "progress": 100,
  "result_id": "repo-uuid-here"
}
```

#### Get Repository Tree

```bash
# Replace REPO_ID with result_id from status response
curl "http://localhost:8000/api/tree/REPO_ID"
```

Expected response:
```json
{
  "name": "Hello-World",
  "type": "folder",
  "path": "",
  "summary": "Project summary...",
  "children": [
    {
      "name": "README",
      "type": "file",
      "path": "README",
      "summary": "File summary...",
      "children": []
    }
  ]
}
```

#### Test Search

```bash
curl "http://localhost:8000/api/search?q=hello"
```

Expected response:
```json
[
  {
    "path": "README",
    "score": 1.0,
    "summary_snippet": "Summary snippet..."
  }
]
```

#### Test Q&A

```bash
curl -X POST "http://localhost:8000/api/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "REPO_ID",
    "question": "What does this repository do?"
  }'
```

Expected response:
```json
{
  "answer": "This repository...",
  "sources": ["README", "path/to/file"]
}
```

### 3.2 Test via Frontend (if running)

1. Open http://localhost:3000
2. Enter repository URL: `https://github.com/octocat/Hello-World`
3. Click "Analyze"
4. Wait for progress to reach 100%
5. View tree structure
6. Try search functionality
7. Ask a question in Q&A interface

## Step 4: Verify Results

### Check Database

```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "
from backend.db.base import SessionLocal
from backend.models.repository import Repository
from backend.models.node import Node

db = SessionLocal()
repos = db.query(Repository).all()
print(f'Repositories: {len(repos)}')
for repo in repos:
    print(f'  - {repo.url} ({repo.status})')
    nodes = db.query(Node).filter(Node.repo_id == repo.id).all()
    print(f'    Nodes: {len(nodes)}')
db.close()
"
```

### Expected Output

- At least 1 repository record
- Repository status should be "completed"
- Multiple node records (files and folders)
- Root node with summary
- File nodes with summaries

## Step 5: Troubleshooting

### Backend Issues

**Issue**: Import errors
```bash
# Make sure you're in project root (parent of backend directory)
# Set PYTHONPATH to project root (not backend directory)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Now you can run commands from project root or backend directory
cd backend
uvicorn main:app --reload
```

**Note**: PYTHONPATH must point to the project root (where the `backend` folder is), not the `backend` directory itself. The test script (`test_small_repo.sh`) now includes a PYTHONPATH warning if not set correctly.

**Issue**: Database errors
```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Recreate database
rm backend/r2ce.db
python -c "from backend.db.base import Base, engine; Base.metadata.create_all(bind=engine)"
```

**Issue**: LLM API errors
- Check API key is correct
- Verify API key has credits/quota
- Check network connectivity
- Try different LLM provider

### Frontend Issues

**Issue**: Cannot connect to backend
- Verify backend is running on port 8000
- Check CORS settings in backend
- Verify `VITE_API_URL` in frontend (defaults to http://localhost:8000)

**Issue**: Build errors
```bash
cd frontend
rm -rf node_modules
npm install
```

## Step 6: Test Checklist

- [ ] Backend starts without errors
- [ ] Database tables created successfully
- [ ] API health endpoint responds
- [ ] Analysis endpoint accepts request
- [ ] Status endpoint shows progress
- [ ] Analysis completes successfully
- [ ] Tree endpoint returns hierarchical structure
- [ ] Search endpoint returns results
- [ ] Q&A endpoint answers questions
- [ ] Database contains repository and nodes
- [ ] Summaries are generated (not empty)
- [ ] Frontend (if used) displays data correctly

## Step 7: Docker Testing

### Quick Docker Setup

```bash
# Build and start all services
./docker-build.sh

# Or manually
docker-compose up -d

# Access at http://localhost:3000
```

### Docker Architecture

**Security**: Backend API is NOT directly accessible from outside Docker:
- Frontend (port 3000): Only exposed port
- Backend (no external port): Only accessible via frontend proxy within Docker network
- Database (no external port): Internal network only

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed Docker deployment instructions.

## Step 8: Next Steps

Once testing is successful:

1. **Fix any issues** discovered during testing
2. **Test with slightly larger repository** (10-50 files)
3. **Test Docker deployment** (see DOCKER_GUIDE.md)
4. **Deploy to cloud** (see DEPLOYMENT.md)

## Expected Test Duration

- Small repository (< 10 files): 1-3 minutes
- Medium repository (10-50 files): 3-10 minutes
- Large repository (50+ files): 10+ minutes

Note: Duration depends on LLM API response time and repository size.

## Recent Fixes Applied

The following issues have been fixed and are now handled gracefully:

1. ✅ **Division by Zero**: Fixed - handles repositories with no files
2. ✅ **Empty Repository**: Fixed - creates minimal root node for empty repos
3. ✅ **Empty Context**: Fixed - handles repositories with only files (no folders)
4. ✅ **Event Loop Issues**: Fixed - proper async event loop handling
5. ✅ **PYTHONPATH**: Test script now warns if PYTHONPATH not set correctly

## Expected Success Rate

With a valid LLM API key, tests should succeed **~98% of the time**. The remaining 2% covers:
- External service failures (GitHub downtime, LLM API outages)
- Resource limitations (disk space, memory)
- Very unusual repository structures
- Infrastructure issues (permissions, corruption)

See `EDGE_CASES.md` for detailed breakdown of edge cases and why 98% is expected for MVP.

