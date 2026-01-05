# End-to-End Setup Guide

This guide walks you through **setting up, running, testing, and deploying R2CE** from scratch. Follow these steps in order for a complete end-to-end workflow.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [Running the Application](#running-the-application)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [CI/CD Setup](#cicd-setup)
7. [Verification](#verification)

---

## Prerequisites

Before you begin, ensure you have:

✅ **Required:**
- Git installed
- Docker and Docker Compose installed
- LLM API key (DeepSeek recommended, or OpenAI/Ollama)
- GitHub account (for CI/CD)
- Render account (for deployment) - [Sign up free](https://render.com)

✅ **Verify Installation:**
```bash
git --version           # Should show git version
docker --version        # Should show Docker version
docker-compose --version # Should show docker-compose version
```

---

## Local Setup

### Step 1: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/yourusername/r2ce.git
cd r2ce
```

### Step 2: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

**Required Configuration:**
```bash
# LLM Provider (choose one)
LLM_PROVIDER=deepseek              # Recommended: deepseek, openai, or ollama

# DeepSeek Configuration (if using deepseek)
DEEPSEEK_API_KEY=your-api-key-here # Get from https://platform.deepseek.com
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-coder

# OR OpenAI Configuration (if using openai)
# OPENAI_API_KEY=your-openai-key
# OPENAI_MODEL=gpt-4

# OR Ollama Configuration (if using ollama)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3

# Repository Size Limit
MAX_GIT_SIZE_KB=10                 # 10KB for demo, 0 for no limit

# Database (auto-configured for Docker)
DATABASE_URL=postgresql://r2ce:r2ce_password@db:5432/r2ce
```

### Step 3: Verify Docker Compose Configuration

Check that `docker-compose.yml` exists and is properly configured:

```bash
# View docker-compose.yml
cat docker-compose.yml

# Should show three services: db, backend, frontend
```

---

## Running the Application

### Step 1: Start All Services

```bash
# Build and start all services (database, backend, frontend)
docker-compose up --build
```

**What happens:**
- 🐘 PostgreSQL database starts on port 5432
- 🐍 Backend API starts on port 8000
- ⚛️  Frontend starts on port 3000

**Wait for:**
```
frontend_1  | ➜  Local:   http://localhost:3000/
backend_1   | INFO:     Application startup complete.
db_1        | database system is ready to accept connections
```

### Step 2: Verify Services Are Running

Open a **new terminal** and check:

```bash
# Check running containers
docker-compose ps

# Should show 3 containers: r2ce-db-1, r2ce-backend-1, r2ce-frontend-1
```

### Step 3: Access the Application

🌐 **Frontend**: http://localhost:3000
- Web interface for analyzing repositories

📡 **Backend API**: http://localhost:8000
- REST API endpoints

📚 **API Documentation**: http://localhost:8000/docs
- Interactive Swagger documentation

### Step 4: Test Basic Functionality

1. **Open Frontend**: http://localhost:3000
2. **Analyze a small repository**:
   - URL: `https://github.com/octocat/Hello-World`
   - Passphrase: `test`
   - Click "Analyze"
3. **Wait for completion** (30-60 seconds)
4. **View results** in Tree, Browse, or Search tabs

---

## Testing

### Backend Tests

Run all backend tests (unit + integration):

```bash
# Run all backend tests
docker-compose exec backend pytest

# Run with verbose output
docker-compose exec backend pytest -v

# Run with coverage report
docker-compose exec backend pytest --cov=backend --cov-report=term-missing
```

**Expected Output:**
```
=================== test session starts ===================
backend/tests/unit/test_git_service.py ......     [ 28%]
backend/tests/unit/test_llm_service.py .....      [ 57%]
backend/tests/integration/test_api_endpoints.py ............ [ 85%]
backend/tests/integration/test_database.py .........        [100%]

=================== 21 passed in 5.23s ====================
```

### Frontend Tests

Run all frontend tests:

```bash
# Run all frontend tests
docker-compose exec frontend npm test -- --run

# Run with UI (interactive)
docker-compose exec frontend npm run test:ui

# Run with coverage
docker-compose exec frontend npm run test:coverage
```

**Expected Output:**
```
✓ src/components/__tests__/RepoAnalyzer.test.tsx (4)
✓ src/components/__tests__/QAInterface.test.tsx (7)
✓ src/components/__tests__/SearchBar.test.tsx (11)
✓ src/services/__tests__/api.test.ts (1)

Test Files  4 passed (4)
Tests  21 passed (21)
```

### Test Specific Components

```bash
# Backend unit tests only
docker-compose exec backend pytest backend/tests/unit/

# Backend integration tests only
docker-compose exec backend pytest backend/tests/integration/

# Specific test file
docker-compose exec backend pytest backend/tests/integration/test_api_endpoints.py

# Specific test function
docker-compose exec backend pytest backend/tests/integration/test_api_endpoints.py::test_complete_analysis_workflow
```

### Verify Test Coverage

```bash
# Generate HTML coverage report
docker-compose exec backend pytest --cov=backend --cov-report=html

# Open coverage report
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
```

---

## Deployment

### Overview

We'll deploy to **Render** (free tier available) with:
- PostgreSQL database
- Backend API (Python web service)
- Frontend (Static site)

**Estimated Time:** 15-20 minutes

### Step 1: Prepare Code for Deployment

```bash
# Ensure all tests pass
docker-compose exec backend pytest
docker-compose exec frontend npm test -- --run

# Stop local services
docker-compose down

# Commit any changes
git add .
git commit -m "Ready for deployment"

# Push to GitHub
git push origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Deploy PostgreSQL Database

1. **Render Dashboard** → **New +** → **PostgreSQL**
2. **Configure**:
   - Name: `r2ce-db`
   - Database: `r2ce`
   - User: `r2ce` (auto-generated)
   - Region: Choose closest to you
   - Plan: **Free**
3. **Create Database**
4. **Copy Internal Database URL** (starts with `postgresql://`)
   - Save this - you'll need it for backend

### Step 4: Deploy Backend

1. **Render Dashboard** → **New +** → **Web Service**
2. **Connect Repository**: Select your R2CE repository
3. **Configure**:
   - Name: `r2ce-backend`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: *(leave empty)*
   - Environment: `Python 3`
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables** (click "Advanced"):
   ```bash
   DATABASE_URL=<paste-your-database-internal-url>
   LLM_PROVIDER=deepseek
   DEEPSEEK_API_KEY=<your-api-key>
   DEEPSEEK_API_BASE=https://api.deepseek.com
   DEEPSEEK_MODEL=deepseek-coder
   ENVIRONMENT=production
   MAX_GIT_SIZE_KB=10000
   ```
5. **Create Web Service**
6. **Wait for deployment** (2-3 minutes)
7. **Note your backend URL**: `https://r2ce-backend-xxxx.onrender.com`

### Step 5: Run Database Migrations

1. In Render Dashboard → Your backend service
2. Click **Shell** tab
3. Run:
   ```bash
   cd backend && alembic upgrade head
   ```
4. Verify: `alembic current` (should show latest version)

### Step 6: Verify Backend

Test backend endpoints:

```bash
# Health check
curl https://your-backend-url.onrender.com/health
# Should return: {"status":"healthy"}

# API docs (open in browser)
https://your-backend-url.onrender.com/docs
```

### Step 7: Deploy Frontend

1. **Render Dashboard** → **New +** → **Static Site**
2. **Connect**: Same repository
3. **Configure**:
   - Name: `r2ce-frontend`
   - Branch: `main`
   - Root Directory: *(leave empty)*
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
4. **Environment Variables**:
   ```bash
   VITE_API_URL=<your-backend-url-from-step-4>
   ```
   Example: `https://r2ce-backend-xxxx.onrender.com`
5. **Create Static Site**
6. **Wait for deployment** (3-5 minutes)
7. **Note your frontend URL**: `https://r2ce-frontend-xxxx.onrender.com`

### Step 8: Update Backend CORS

1. **Go back to backend service** on Render
2. **Environment** tab → **Add Environment Variable**:
   ```bash
   FRONTEND_URL=<your-frontend-url-from-step-7>
   ```
3. **Manual Deploy** → **Deploy latest commit**
4. Wait for redeployment (~2 minutes)

---

## CI/CD Setup

### Overview

Automate testing and deployment with GitHub Actions:
- ✅ Tests run on every Pull Request
- ✅ Auto-deploy when tests pass on `main` branch

### Step 1: Verify GitHub Actions Workflow

Check that `.github/workflows/ci.yml` exists:

```bash
cat .github/workflows/ci.yml
```

Should show a workflow with `test` and `deploy` jobs.

### Step 2: Enable Auto-Deploy on Render

**For each service (backend and frontend):**

1. Go to Render Dashboard → Your Service
2. **Settings** → **Build & Deploy**
3. **Auto-Deploy**: Verify it's set to **"Yes"**
4. **Branch**: Verify it's set to **"main"**

**That's it!** Render automatically deploys when you push to `main`.

### Step 3: Test CI/CD Pipeline

```bash
# Create test branch
git checkout -b test-cicd

# Make a small change
echo "# Testing CI/CD" >> README.md
git add README.md
git commit -m "test: Verify CI/CD pipeline"

# Push to GitHub
git push origin test-cicd
```

**What happens:**
1. Go to GitHub → Your repository → **Pull Requests**
2. Create PR from `test-cicd` to `main`
3. **GitHub Actions runs automatically**:
   - Runs all backend tests
   - Runs all frontend tests
   - Shows ✅ or ❌ status
4. **Merge PR** (after tests pass)
5. **Render auto-deploys** to production

### Step 4: Monitor Deployment

**GitHub Actions:**
- Repository → **Actions** tab
- View test results and deployment status

**Render Dashboard:**
- Click on your service
- **Events** tab shows deployment history
- **Logs** tab shows build/runtime logs

---

## Verification

### Complete End-to-End Test

#### 1. Local Verification

```bash
# Start local services
docker-compose up

# Run all tests
docker-compose exec backend pytest
docker-compose exec frontend npm test -- --run

# Test application
open http://localhost:3000
```

**Verify:**
- ✅ Frontend loads without errors
- ✅ Can analyze a test repository
- ✅ Results display in Tree/Browse/Search tabs
- ✅ All tests pass

#### 2. Production Verification

**Open your deployed frontend**: `https://your-frontend.onrender.com`

**Test Analysis:**
1. Enter repository: `https://github.com/octocat/Hello-World`
2. Enter passphrase: `test`
3. Click **Analyze**
4. Wait for completion
5. View results

**Verify:**
- ✅ Backend `/health` returns `{"status":"healthy"}`
- ✅ Frontend loads without console errors
- ✅ Can successfully analyze a repository
- ✅ Results display correctly
- ✅ No CORS errors in browser console

#### 3. CI/CD Verification

**Check GitHub Actions:**
1. Go to repository → **Actions**
2. Verify latest workflow run shows ✅
3. Check test results

**Check Render:**
1. Go to Render Dashboard
2. All services show "Live" status
3. No errors in logs

---

## Troubleshooting

### Local Issues

**Services won't start:**
```bash
# Check for port conflicts
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # Database

# Clean and rebuild
docker-compose down -v
docker-compose up --build
```

**Tests fail:**
```bash
# Ensure services are running
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

### Deployment Issues

**Backend deployment fails:**
- Check Render logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is complete

**Frontend can't reach backend:**
- Verify `VITE_API_URL` in frontend env vars
- Check backend CORS: `FRONTEND_URL` must be set
- Test backend directly: `curl https://your-backend/health`

**Database connection fails:**
- Verify `DATABASE_URL` in backend env vars
- Check database is "Available" on Render
- Run migrations: `alembic upgrade head`

### Getting Help

**Check Documentation:**
- [README.md](README.md) - Main documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [CI_CD_SETUP.md](CI_CD_SETUP.md) - CI/CD configuration
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing documentation

**Check Logs:**
```bash
# Local logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Production logs
# Go to Render Dashboard → Service → Logs tab
```

---

## Success Checklist

✅ **Setup:**
- [ ] Repository cloned
- [ ] Environment variables configured
- [ ] Docker Compose running

✅ **Running:**
- [ ] All three services running (db, backend, frontend)
- [ ] Can access frontend at http://localhost:3000
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can analyze a test repository successfully

✅ **Testing:**
- [ ] All backend tests pass (21 tests)
- [ ] All frontend tests pass (21 tests)
- [ ] Test coverage reports generated

✅ **Deployment:**
- [ ] Database created on Render
- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Database migrations completed
- [ ] CORS configured correctly
- [ ] Can analyze repository in production

✅ **CI/CD:**
- [ ] GitHub Actions workflow exists
- [ ] Tests run on Pull Requests
- [ ] Auto-deploy enabled on Render
- [ ] Full CI/CD pipeline tested

---

## Quick Reference Commands

```bash
# Local Development
docker-compose up                    # Start all services
docker-compose down                  # Stop all services
docker-compose logs -f backend       # View backend logs

# Testing
docker-compose exec backend pytest   # Backend tests
docker-compose exec frontend npm test -- --run  # Frontend tests

# Database
docker-compose exec backend alembic upgrade head  # Run migrations
docker-compose exec backend alembic current       # Check version

# Deployment
git push origin main                 # Triggers CI/CD
curl https://your-backend/health     # Check backend health
```

---

## Next Steps

🎉 **Congratulations!** You've successfully set up, run, tested, and deployed R2CE end-to-end.

**What's Next:**
- Explore the API at `/docs` endpoint
- Try analyzing your own repositories
- Customize LLM prompts in `backend/services/llm_service.py`
- Add new features and submit PRs
- Check MCP integration in `mcp/r2ce-server/`

**Resources:**
- [API Documentation](http://localhost:8000/docs) (local)
- [OpenAPI Specification](docs/openapi.yaml)
- [Backend Tests](backend/tests/README.md)
- [Development Log](DEVELOPMENT_LOG.md)
