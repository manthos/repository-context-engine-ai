# CI/CD Setup Guide

## Overview

This guide explains how to set up **automated CI/CD** that:
1. ✅ Runs all tests on every Pull Request
2. ✅ Deploys automatically to Render when tests pass on `main` branch

## Current CI/CD Status

### ✅ What's Already Working

- **GitHub Actions Workflow**: `.github/workflows/ci.yml` configured
- **Automated Testing**: Runs on every PR and push to `main`
- **Test Coverage**: Backend (pytest) and Frontend (vitest) tests
- **PostgreSQL Service**: Tests run against real PostgreSQL database

---

## Configured Render for Auto-Deploy

### Render Auto-Deploy from GitHub (Recommended)

This is the **easiest** method - Render automatically deploys when you push to `main`.

1. **Deploy your services to Render** (follow [DEPLOYMENT.md](DEPLOYMENT.md))

2. **Enable Auto-Deploy** (Already enabled by default when connecting GitHub):
   - Go to your Render service → **Settings** → **Build & Deploy**
   - **Auto-Deploy**: Should be **"Yes"** (enabled by default)
   - **Branch**: Set to `main`

3. **How it works**:
   - When you push to `main` branch on GitHub
   - Render automatically detects the push
   - Render rebuilds and redeploys your service
   - **Your GitHub Actions tests run first**, giving you confidence before merge

**No additional configuration needed!** Render handles deployment automatically.

---

## Step 2: Add Required GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Secret Name | Description | Where to Get It |
|------------|-------------|-----------------|
| `RENDER_DEPLOY_HOOK_BACKEND` | Backend deploy hook | Render backend service → Settings → Deploy Hook |
| `RENDER_DEPLOY_HOOK_FRONTEND` | Frontend deploy hook | Render frontend service → Settings → Deploy Hook |

**Note:** Only needed if using Option B (Deploy Hook method). Option A works without secrets.

---

## Step 3: Update GitHub Actions Workflow (Optional)

By the current workflow Render handles deployment automatically.

---

## Step 4: Test Your CI/CD Pipeline

### Test CI (Continuous Integration)

1. **Create a feature branch**:
   ```bash
   git checkout -b test-ci-pipeline
   ```

2. **Make a small change** (e.g., update README):
   ```bash
   echo "Testing CI/CD" >> README.md
   git add README.md
   git commit -m "test: Verify CI/CD pipeline"
   git push origin test-ci-pipeline
   ```

3. **Create Pull Request** on GitHub

4. **Watch GitHub Actions**:
   - Go to your repository → **Actions** tab
   - See the CI workflow running
   - Both backend and frontend tests should pass ✅

### Test CD (Continuous Deployment)

1. **Merge the Pull Request** to `main` branch

2. **Watch Deployment**:
   - **Option A**: Render automatically detects the push and starts deployment
   - **Option B**: GitHub Actions triggers Render deploy hook
   
3. **Verify Deployment**:
   - Check Render Dashboard → Your services should show "Deploying" → "Live"
   - Visit your frontend URL
   - Test a repository analysis to ensure everything works

---

## Complete CI/CD Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Developer pushes code to feature branch                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions: Run Tests (CI)                             │
│  ✓ Backend tests (pytest)                                   │
│  ✓ Frontend tests (vitest)                                  │
│  ✓ Test against PostgreSQL                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
         ┌────────┴────────┐
         │  Tests Pass?    │
         └────────┬────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
    ❌ FAIL             ✅ SUCCESS
        │                   │
        ▼                   ▼
   Cannot merge      Pull Request
   to main            approved
                           │
                           ▼
                  Merge to main branch
                           │
                           ▼
         ┌─────────────────────────────┐
         │  Trigger on main branch     │
         └─────────────┬───────────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
      Option A:           Option B:
   Render Auto-Deploy   GitHub Actions
   (Recommended)        triggers deploy hook
              │                 │
              └────────┬────────┘
                       ▼
         ┌─────────────────────────────┐
         │  Render deploys services    │
         │  • Backend (API)            │
         │  • Frontend (Static)        │
         └─────────────┬───────────────┘
                       │
                       ▼
              ✅ Deployment Complete
              Users see new version
```

---

## Monitoring Deployments

### GitHub Actions
- Repository → **Actions** tab
- See test results and deployment triggers
- Each workflow shows: ✅ Success or ❌ Failure

### Render Dashboard
- **Events** tab: Shows deployment history
- **Logs** tab: Shows build and runtime logs
- **Metrics** tab: Shows performance metrics

---

## Troubleshooting

### Tests Pass Locally but Fail in CI

**Common causes:**
1. **Missing environment variables**: Check `.github/workflows/ci.yml` has all required env vars
2. **Database differences**: CI uses PostgreSQL, local might use SQLite
3. **Dependencies**: Ensure `requirements.txt` and `package.json` are up to date

**Solution:**
```bash
# Test locally with PostgreSQL (same as CI)
docker-compose up -d db
export DATABASE_URL=postgresql://r2ce:r2ce_password@localhost:5432/r2ce
pytest backend/tests/
```

### Deployment Fails

**Check Render Logs:**
1. Go to Render Dashboard → Your Service
2. Click **Logs** tab
3. Look for error messages

**Common issues:**
- Missing environment variables (DATABASE_URL, LLM_PROVIDER, API keys)
- Database migration failed (run `alembic upgrade head` in Render shell)
- Build timeout (increase instance size or optimize build)

### Deployment Succeeds but App Doesn't Work

**Verify:**
1. ✅ Backend `/health` endpoint: `https://your-backend.onrender.com/health`
2. ✅ Frontend environment variables: Check `VITE_API_URL` points to backend
3. ✅ CORS settings: Verify backend has `FRONTEND_URL` set
4. ✅ Database migrations: Run `alembic current` in Render shell

---

## Cost Optimization

### Free Tier Limits

**Render Free Tier:**
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds (cold start)
- 750 hours/month of runtime per service

**Tips:**
1. **Use a single paid instance** if you need always-on service ($7/month)
2. **Keep free tier for testing** before upgrading
3. **Monitor usage** in Render Dashboard → Billing

### GitHub Actions Limits

**Free Tier:**
- 2,000 minutes/month for private repositories
- Unlimited for public repositories

**Optimization:**
- Tests usually take 2-3 minutes per run
- ~600-1000 test runs per month on free tier
- Enough for most projects

---

**That's it!** Your CI/CD pipeline is now fully automated. 🚀
