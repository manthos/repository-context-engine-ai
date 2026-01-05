# Deployment & Security Workflow

## 🔐 Understanding Environment Variables & Secrets

### Key Concepts

**✅ SAFE (Never in Git):**
- `.env` file (local development)
- Render environment variables (cloud deployment)
- API keys, database passwords, secrets

**✅ SAFE (In Git):**
- `.env.example` (template without real values)
- `docker-compose.yml` (uses environment variables from `.env`)
- Application code (never hardcode secrets!)

---

## 📋 Complete Workflow Explanation

### 1. Your Local Development

**What you do:**
```bash
# Clone your repo
git clone https://github.com/yourusername/r2ce.git
cd r2ce

# Create .env with YOUR keys
cp .env.example .env
nano .env  # Add YOUR DeepSeek/OpenAI API key

# Run locally
docker-compose up
```

**Your `.env` file (NOT in Git):**
```bash
DEEPSEEK_API_KEY=sk-your-secret-key-12345  # Your key
LLM_PROVIDER=deepseek
# ... other settings
```

**Important:** `.env` is in `.gitignore` → Never committed to Git ✅

---

### 2. Your Deployment to Render

**What you do:**

1. **Deploy to Render** (following DEPLOYMENT.md)
2. **Set environment variables in Render Dashboard** (not in code):
   ```
   Render Dashboard → Your Service → Environment
   Add: DEEPSEEK_API_KEY=sk-your-secret-key-12345
   ```

**Where secrets live:**
- ❌ NOT in Git repository
- ❌ NOT in docker-compose.yml
- ✅ In Render's secure environment variable storage
- ✅ In your local `.env` file (never committed)

**Your Render deployment:**
- Connected to YOUR Render account
- Uses YOUR environment variables
- Deploys to YOUR Render URL: `https://your-app.onrender.com`

---

### 3. Someone Else Clones Your Repo

**What they do:**
```bash
# Clone your public repo
git clone https://github.com/yourusername/r2ce.git
cd r2ce

# Create THEIR OWN .env
cp .env.example .env
nano .env  # Add THEIR OWN API key

# Run with THEIR keys
docker-compose up
```

**Their `.env` file:**
```bash
DEEPSEEK_API_KEY=sk-their-different-key-67890  # Their key
LLM_PROVIDER=deepseek
# ... their settings
```

**What they see in Git:**
- ✅ Your code
- ✅ `.env.example` (template)
- ✅ `docker-compose.yml`
- ❌ NO secrets (your `.env` never committed)
- ❌ NO API keys
- ❌ NO passwords

**If they want to deploy:**
- They deploy to THEIR OWN Render account
- They use THEIR OWN API keys
- They get THEIR OWN URL: `https://their-app.onrender.com`

---

### 4. Pull Request Workflow (The Key Question!)

**Scenario: Someone submits a PR to your repo**

#### Step 1: Developer Creates PR
```bash
# Developer forks your repo
git clone https://github.com/developer/r2ce.git  # Their fork
cd r2ce

# They make changes (e.g., fix a bug)
git checkout -b fix-bug
# ... make code changes ...
git commit -am "fix: Fixed search bug"
git push origin fix-bug

# They create PR to YOUR repo
# From: developer:fix-bug → To: yourusername:main
```

**Important:** They CANNOT see or access your `.env` or Render secrets!

#### Step 2: GitHub Actions Tests (On PR)
```
PR Created → GitHub Actions Runs
├─ Uses GitHub's test environment
├─ Uses test database (temporary PostgreSQL)
├─ Does NOT use your production keys
├─ Uses minimal test credentials (safe to expose in workflow)
└─ ✅ Pass or ❌ Fail
```

**From `.github/workflows/ci.yml`:**
```yaml
env:
  DATABASE_URL: postgresql://r2ce:r2ce_password@localhost:5432/r2ce
  LLM_PROVIDER: deepseek
  # Note: No real API keys needed for tests (mocked)
```

Tests use **mocked** LLM calls → No real API keys needed!

#### Step 3: You Review and Merge
```bash
# You review the PR on GitHub
# Check code changes
# See test results (✅ all pass)

# You merge PR
Click "Merge Pull Request" button
```

#### Step 4: Automatic Deployment (To YOUR Render)
```
PR Merged to main → Triggers Deploy
├─ GitHub Actions runs tests again (on main branch)
├─ ✅ Tests pass
├─ Render detects push to main
├─ Render pulls latest code from YOUR repo
├─ Render builds with YOUR environment variables
│   └─ Uses YOUR DEEPSEEK_API_KEY (already set in Render)
├─ Deploys to YOUR Render URL
└─ Your app updates with new code
```

**Critical Security Points:**
- ✅ Deploy happens on YOUR Render account
- ✅ Uses YOUR environment variables (in Render dashboard)
- ✅ Developer NEVER sees your Render credentials
- ✅ Developer NEVER sees your API keys
- ✅ Code is public, secrets are separate

---

## 🔒 Security Architecture

### What's Public (Safe in Git)

```
r2ce/
├── .env.example          ✅ Template (no real values)
├── .gitignore            ✅ Prevents .env from being committed
├── docker-compose.yml    ✅ References ${ENV_VARS}, no hardcoded secrets
├── backend/
│   ├── config.py         ✅ Reads from environment variables
│   └── main.py           ✅ No hardcoded secrets
├── frontend/
│   └── src/              ✅ Public code (backend URL only)
└── .github/
    └── workflows/ci.yml  ✅ Uses safe test credentials
```

### What's Private (NEVER in Git)

```
Your Computer:
├── .env                  ❌ Local secrets (in .gitignore)

Your Render Account:
├── Environment Variables ❌ Render dashboard (encrypted)
│   ├── DEEPSEEK_API_KEY
│   ├── DATABASE_URL
│   └── Other secrets

GitHub Secrets (Optional):
└── Repository Settings → Secrets  ❌ For CI/CD (encrypted)
    └── RENDER_DEPLOY_HOOK (if using deploy hooks)
```

---

## 🎯 Real-World Example

### Scenario: Alice owns the repo, Bob contributes

**Alice (Repo Owner):**
```bash
# Alice's .env (never committed)
DEEPSEEK_API_KEY=sk-alice-secret-abc123

# Alice's Render Dashboard:
Environment Variables:
  DEEPSEEK_API_KEY=sk-alice-secret-abc123
  DATABASE_URL=postgresql://...alice-render-db...
  FRONTEND_URL=https://alice-app.onrender.com

# Alice's Render URL:
https://alice-r2ce.onrender.com
```

**Bob (Contributor):**
```bash
# Bob clones Alice's repo
git clone https://github.com/alice/r2ce.git

# Bob creates HIS OWN .env
DEEPSEEK_API_KEY=sk-bob-different-xyz789

# Bob tests locally with HIS keys
docker-compose up

# Bob makes a change and submits PR
git checkout -b improve-search
# ... code changes ...
git push origin improve-search
# Create PR to alice/r2ce
```

**What Bob Can See:**
- ✅ Alice's code
- ✅ `.env.example` template
- ❌ Alice's `.env` (not in Git)
- ❌ Alice's API keys
- ❌ Alice's Render dashboard
- ❌ Alice's database

**Alice Merges Bob's PR:**
1. Alice reviews PR
2. Tests pass (using mocked LLM calls)
3. Alice clicks "Merge"
4. **Render auto-deploys to Alice's account**
5. Uses Alice's API keys (from Render dashboard)
6. Deploys to Alice's URL
7. Bob's code is now live on Alice's app

**Bob Never Gets:**
- Alice's API keys
- Alice's Render access
- Alice's database credentials
- Access to Alice's deployment

---

## ✅ Pre-Deployment Checklist

### Before You Deploy (First Time)

- [ ] Verify `.env` is in `.gitignore`
- [ ] Create `.env` locally with YOUR API keys
- [ ] Test locally: `docker-compose up`
- [ ] Commit code (`.env` will be ignored)
- [ ] Push to GitHub: `git push origin main`

### When Deploying to Render

- [ ] Create Render account
- [ ] Deploy database (note connection string)
- [ ] Deploy backend (set environment variables in dashboard)
- [ ] Deploy frontend (set VITE_API_URL in dashboard)
- [ ] Run migrations: `alembic upgrade head`
- [ ] Test deployment

### After Deployment

- [ ] Verify app works at Render URL
- [ ] Check no secrets visible in public repo
- [ ] Test PR workflow with a test branch
- [ ] Verify auto-deploy works

---

## 🚨 Common Security Mistakes (DON'T DO THIS)

### ❌ Hardcoding Secrets in Code
```python
# backend/config.py - WRONG!
DEEPSEEK_API_KEY = "sk-your-secret-key-abc123"  # ❌ Never do this!
```

### ✅ Correct Way
```python
# backend/config.py - RIGHT!
import os
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # ✅ From environment
```

### ❌ Committing .env to Git
```bash
git add .env  # ❌ Never do this!
```

### ✅ Correct Way
```bash
# .gitignore already has:
.env  # ✅ .env is ignored
```

### ❌ Putting Secrets in docker-compose.yml
```yaml
# docker-compose.yml - WRONG!
environment:
  DEEPSEEK_API_KEY: "sk-your-secret-key-abc123"  # ❌ Don't do this!
```

### ✅ Correct Way
```yaml
# docker-compose.yml - RIGHT!
environment:
  DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}  # ✅ From .env file
```

---

## 📝 Summary: Who Has Access to What

| Resource | You (Owner) | Contributors | Public |
|----------|-------------|--------------|--------|
| Source Code | ✅ Full Access | ✅ Can Fork/PR | ✅ Can View |
| `.env.example` | ✅ Template | ✅ Template | ✅ Template |
| Your `.env` | ✅ Your Keys | ❌ No Access | ❌ No Access |
| Your Render Account | ✅ Full Access | ❌ No Access | ❌ No Access |
| Your API Keys | ✅ Your Keys | ❌ No Access | ❌ No Access |
| Your Database | ✅ Full Access | ❌ No Access | ❌ No Access |
| Your Deployment URL | ✅ Admin | ❌ No Access | ✅ Can Visit |

**Bottom Line:**
- Code is public ✅
- Secrets stay private ✅
- Contributors can run their own instance ✅
- Contributors CANNOT access your deployment ✅
- PRs deploy to YOUR Render automatically ✅

---

## 🎓 Next Steps

1. **Test Security Locally:**
   ```bash
   # Verify .env is ignored
   git status  # Should NOT show .env
   
   # Check .gitignore
   cat .gitignore | grep .env  # Should see .env listed
   ```

2. **Deploy to Render:**
   - Follow [DEPLOYMENT.md](DEPLOYMENT.md)
   - Set environment variables in Render dashboard (not in code)
   - Verify app works

3. **Test PR Workflow:**
   ```bash
   # Create test branch
   git checkout -b test-security
   echo "# Test" >> README.md
   git commit -am "test: Security workflow"
   git push origin test-security
   
   # Create PR on GitHub
   # Merge PR
   # Watch Render auto-deploy to YOUR instance
   ```

4. **Verify Security:**
   - Check GitHub repo → No `.env` file visible
   - Check Render dashboard → Environment variables encrypted
   - Test with a friend: They clone, can't see your keys

---

**You're secure! Deploy with confidence.** 🔒✅
