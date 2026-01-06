# Deployment Guide

## Overview

This guide provides **step-by-step instructions** for deploying R2CE to **Render** (recommended) or **Railway**. Both platforms offer free tiers suitable for testing and small-scale deployments.

**Estimated Time:** 15-20 minutes

## Prerequisites

✅ **Required:**
- GitHub repository with R2CE code
- Account on [Render](https://render.com) or [Railway](https://railway.app)
- LLM API key (DeepSeek recommended, or OpenAI)

✅ **Verified Locally:**
- Application runs successfully with `docker-compose up`
- All tests pass: `pytest backend/tests/` and `npm test` (frontend)
- Database migrations work: `alembic upgrade head`

---

## 🚀 Deployment to Render (Completed)

### Step 1: Create PostgreSQL Database

1. **Log in to Render Dashboard**: https://dashboard.render.com
2. **Create Database**:
   - Click **"New +"** → **"PostgreSQL"**
   - **Name**: `r2ce-db`
   - **Database**: `r2ce`
   - **User**: `r2ce` (auto-generated)
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid for production)
3. **Save Connection Details**:
   - Click on the created database
   - Copy **Internal Database URL** (starts with `postgresql://`)
   - Save this for later (needed for backend configuration)

### Step 2: Deploy Backend API

1. **Create Web Service**:
   - Click **"New +"** → **"Web Service"**
   - Connect your **GitHub repository**
   - Select the repository containing R2CE

2. **Configure Service**:
   - **Name**: `r2ce-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Environment**: `Python 3`
   - **Build Command**:
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Set Environment Variables**:
   Click **"Environment"** tab and add:
   
   ```bash
   DATABASE_URL=<paste-internal-database-url-from-step-1>
   LLM_PROVIDER=deepseek
   DEEPSEEK_API_KEY=<your-deepseek-api-key>
   DEEPSEEK_API_BASE=https://api.deepseek.com
   DEEPSEEK_MODEL=deepseek-coder
   ENVIRONMENT=production
   MAX_GIT_SIZE_KB=10000
   ```
   
   **Note**: Get DeepSeek API key from https://platform.deepseek.com

4. **Deploy**:
   - Click **"Create Web Service"**
   - Wait for deployment (2-3 minutes)
   - Note the **Service URL** (e.g., `https://r2ce-backend.onrender.com`)

5. **Run Database Migrations**:
   - Once deployed, go to **"Shell"** tab in Render dashboard
   - Run:
     ```bash
     cd backend && alembic upgrade head
     ```

6. **Verify Backend**:
   - Visit: `https://your-backend-url.onrender.com/health`
   - Should return: `{"status": "healthy"}`
   - Visit: `https://your-backend-url.onrender.com/docs`
   - Should show OpenAPI documentation

### Step 3: Deploy Frontend

1. **Create Static Site**:
   - Click **"New +"** → **"Static Site"**
   - Connect same GitHub repository

2. **Configure Site**:
   - **Name**: `r2ce-frontend`
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Publish Directory**: `frontend/dist`

3. **Set Environment Variables**:
   ```bash
   VITE_API_URL=<your-backend-url-from-step-2>
   ```
   Example: `VITE_API_URL=https://r2ce-backend.onrender.com`

4. **Deploy**:
   - Click **"Create Static Site"**
   - Wait for build and deployment (3-5 minutes)
   - Note the **Site URL** (e.g., `https://r2ce-frontend.onrender.com`)

### Step 4: Update Backend CORS

1. **Go back to Backend Service** on Render
2. **Add Environment Variable**:
   ```bash
   FRONTEND_URL=<your-frontend-url-from-step-3>
   ```
   Example: `FRONTEND_URL=https://r2ce-frontend.onrender.com`

3. **Redeploy Backend**:
   - Click **"Manual Deploy"** → **"Deploy latest commit"**
   - Wait for redeployment (~2 minutes)

### Step 5: Test Deployment

1. **Visit Frontend**: Open your frontend URL
2. **Test Health**: Should load without errors
3. **Test Analysis**:
   - Enter a small GitHub repository URL (e.g., `https://github.com/octocat/Hello-World`)
   - Enter a passphrase: `test`
   - Click **"Analyze"**
   - Wait for analysis to complete
   - View results in **Tree** or **Browse** tab

**✅ Deployment Complete!** Your application is now live.

---

## 🚂 Deployment to Railway (Alternative)

### Step 1: Create Project

1. **Log in to Railway**: https://railway.app
2. **Create New Project**: Click **"New Project"**
3. **Add PostgreSQL**:
   - Click **"+ New"** → **"Database"** → **"PostgreSQL"**
   - Copy connection string from **"Variables"** tab

### Step 2: Deploy Backend

1. **Add Service**:
   - Click **"+ New"** → **"GitHub Repo"**
   - Select your R2CE repository

2. **Configure**:
   - Railway auto-detects Python
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Variables** (in "Variables" tab):
   ```bash
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   LLM_PROVIDER=deepseek
   DEEPSEEK_API_KEY=<your-key>
   DEEPSEEK_API_BASE=https://api.deepseek.com
   ENVIRONMENT=production
   ```

4. **Deploy**: Railway deploys automatically
5. **Run Migrations**: Use Railway CLI or shell
6. **Note Public URL** from "Settings" → "Generate Domain"

### Step 3: Deploy Frontend

1. **Add Frontend Service**:
   - Click **"+ New"** → **"GitHub Repo"** (same repo)
   
2. **Configure**:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview`

3. **Set Variables**:
   ```bash
   VITE_API_URL=<backend-url>
   ```

4. **Deploy**: Railway deploys automatically

---

## 📋 Post-Deployment Checklist

- [ ] Backend `/health` endpoint returns `{"status": "healthy"}`
- [ ] Backend `/docs` shows OpenAPI documentation
- [ ] Frontend loads without console errors
- [ ] Can analyze a test repository successfully
- [ ] Database migrations completed (`alembic current` shows latest version)
- [ ] Environment variables are set correctly
- [ ] CORS is configured (frontend can call backend)
- [ ] Logs show no errors

## Environment Variables Reference

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# LLM Provider
LLM_PROVIDER=deepseek  # or openai, ollama

# DeepSeek
DEEPSEEK_API_KEY=your_key
DEEPSEEK_API_BASE=https://api.deepseek.com

# OpenAI (if using)
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-3.5-turbo

# Application
FRONTEND_URL=https://your-frontend-url.com
ENVIRONMENT=production
```

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check PostgreSQL service is running
- Ensure migrations have been run

### LLM API Issues
- Verify API keys are set correctly
- Check API rate limits
- Test API key with curl

### CORS Issues
- Ensure `FRONTEND_URL` matches actual frontend URL
- Check backend CORS configuration

## CI/CD Integration

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs tests on every PR and can be extended to automatically deploy on merge to main.

To enable auto-deployment:
1. Add deployment secrets to GitHub
2. Configure Render/Railway webhook
3. Update CI/CD workflow with deployment steps

