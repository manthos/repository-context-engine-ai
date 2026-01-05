# Docker Deployment Guide

## Architecture

R2CE uses a **secure Docker deployment** with no external API access:

```
[User Browser] --> [Frontend:3000] --proxy--> [Backend:8000] --> [Database:5432]
                         ↑                          ↑                    ↑
                    Exposed to host          Internal network      Internal network
```

### Security Model

- **Frontend (port 3000)**: Only port exposed to host. Runs Vite dev server with proxy configuration
- **Backend (no external port)**: Only accessible within Docker network via frontend proxy
- **Database (no external port)**: Only accessible within Docker network
- **API Protection**: Backend API cannot be accessed directly from outside the Docker network

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- `.env` file configured (copy from `.env.example`)

### 2. Build and Run

```bash
# Make the build script executable
chmod +x docker-build.sh

# Build and start all services
./docker-build.sh
```

Or manually:

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Access

Open http://localhost:3000 in your browser

## How It Works

### Frontend Proxy

The Vite dev server proxies all `/api/*` and `/health` requests to the backend service:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://backend:8000',
      changeOrigin: true
    }
  }
}
```

### Docker Network

All services communicate via the `r2ce-network` internal Docker network:

- Frontend makes requests to `http://backend:8000` (Docker DNS)
- Browser makes requests to `http://localhost:3000/api` (frontend proxies to backend)
- Backend is never directly accessible from outside Docker

### Environment Variables

```env
# Required
DEEPSEEK_API_KEY=your_api_key

# Optional
LLM_PROVIDER=deepseek
DATABASE_URL=postgresql://r2ce:r2ce_password@db:5432/r2ce
```

## Production Deployment

For production, you can:

1. **Keep this setup**: Simple and secure, frontend proxies to backend
2. **Add nginx**: For better performance and caching
3. **Use cloud platform**: Deploy to Render, Railway, Fly.io, etc.

The key principle remains: **Backend API is never directly exposed to the internet**.

## Troubleshooting

### Backend not accessible

This is intentional! The backend should only be accessible via the frontend proxy.

### Port 3000 already in use

```bash
# Change port in docker-compose.yml
ports:
  - "8080:3000"  # Use port 8080 instead
```

### View backend logs

```bash
docker-compose logs -f backend
```

### Reset everything

```bash
docker-compose down -v  # Remove volumes
docker-compose build --no-cache
docker-compose up -d
```

## Testing Security

**Test from your host machine** that backend is not directly accessible:

```bash
# 1. Try to access backend directly (should fail - port not exposed to host)
curl http://localhost:8000/health
# Expected: curl: (7) Failed to connect to localhost port 8000: Connection refused ✓
# This is GOOD - backend is not exposed!

# 2. Access via frontend proxy (should work)
curl http://localhost:3000/health
# Expected: {"status":"healthy"} ✓
# This works because frontend proxies to backend internally
```

**Why this test matters:**
- We intentionally don't expose backend port 8000 to the host machine
- The backend is only accessible via `backend:8000` inside the Docker network
- The frontend (port 3000) is the only entry point
- All API requests go through frontend's Vite proxy

## Development vs Production

### Development (current setup)
- Frontend: Vite dev server with HMR
- Backend: Uvicorn with auto-reload
- Volumes mounted for live code changes

### Production (recommendations)
- Frontend: Build static files, serve with nginx or CDN
- Backend: Gunicorn with multiple workers
- No volumes, baked into image
- HTTPS with Let's Encrypt
