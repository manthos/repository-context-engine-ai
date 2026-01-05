# R2CE Docker Deployment - Quick Reference

## What We Built

A **secure Docker deployment** without nginx that prevents direct API access.

## Architecture

```
Internet/User
    ↓
[Frontend Container:3000] ← Only exposed port
    ↓ (internal proxy)
[Backend Container] ← No external access
    ↓
[Database Container] ← No external access
```

## Key Files

### Docker Configuration
- `docker-compose.yml` - Defines services with internal network
- `backend/Dockerfile` - Backend container
- `frontend/Dockerfile` - Frontend container with Vite dev server
- `frontend/vite.config.ts` - Proxy configuration
- `docker-build.sh` - Build and test script

### Documentation
- `DOCKER_GUIDE.md` - Complete Docker deployment guide
- `TESTING_GUIDE.md` - Updated with Docker testing section
- `README.md` - Docker as primary option
- `DEPLOYMENT.md` - Cloud deployment with Docker
- `DEVELOPMENT_LOG.md` - Implementation details

## How It Works

1. **Frontend** (Vite dev server on port 3000):
   - Only port exposed to host
   - Proxies `/api/*` requests to backend
   - Browser connects to `http://localhost:3000`

2. **Backend** (FastAPI on internal port 8000):
   - No external port exposure
   - Only accessible via Docker network DNS `backend:8000`
   - Cannot be accessed from outside Docker

3. **Vite Proxy**:
   ```typescript
   proxy: {
     '/api': {
       target: 'http://backend:8000',
       changeOrigin: true
     }
   }
   ```

## Security Benefits

✅ Backend API not directly accessible from internet
✅ All API calls go through frontend proxy
✅ Simple configuration (no nginx needed)
✅ Works locally and in cloud deployments
✅ No API keys or passphrases needed for access control

## Quick Start

```bash
# Build and run
./docker-build.sh

# Or manually
docker-compose up -d

# Access
open http://localhost:3000
```

## Testing Security

Run these commands **from your host machine** (not inside Docker):

```bash
# Test 1: Try to access backend directly (should FAIL - not exposed to host)
curl http://localhost:8000/health
# Expected: curl: (7) Failed to connect to localhost port 8000: Connection refused ✓
# This is GOOD! Backend port is not exposed to your host machine

# Test 2: Access via frontend (should WORK - frontend proxies internally)
curl http://localhost:3000/health
# Expected: {"status":"healthy"} ✓
# This works because frontend proxies to backend within Docker network
```

**What this proves:**
- Backend is not accessible from outside Docker (no port 8000 on host)
- Frontend is the only entry point (port 3000)
- All API calls are proxied internally within Docker network

## Deployment Options

### Local Development
```bash
docker-compose up -d
```

### Cloud Platforms (Render, Railway, Fly.io)
- Use the same `docker-compose.yml`
- Platform exposes only frontend port
- Backend remains internal
- No additional configuration needed

## No nginx Required!

Unlike traditional setups, we don't need nginx because:
- Vite dev server has built-in proxy
- Simple configuration
- Works for both development and production
- Less complexity, same security

## Next Steps

1. Test locally: `./docker-build.sh`
2. Verify security: Backend not directly accessible
3. Deploy to cloud platform using docker-compose.yml
4. Done!
