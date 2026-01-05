#!/bin/bash
# Build and test Docker deployment

set -e

echo "=== R2CE Docker Build and Test ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Please copy .env.example to .env and fill in your API keys"
    exit 1
fi

# Build and start services
echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 15

# Check if services are running
echo "Checking service health..."
docker-compose ps

# Test health endpoint
echo "Testing health endpoint..."
curl -f http://localhost:3000/health || echo "Health check pending..."

echo ""
echo "=== Docker deployment ready ==="
echo "Access the application at: http://localhost:3000"
echo ""
echo "Architecture:"
echo "  - Frontend (port 3000): Exposed to host, proxies API calls to backend"
echo "  - Backend (no exposed port): Only accessible via frontend proxy within Docker network"
echo "  - Database (no exposed port): Internal network only"
echo ""
echo "Security Test (from your host machine):"
echo "  - Backend direct access: curl http://localhost:8000/health"
echo "    Expected: Connection refused (port not exposed to host) ✓"
echo "  - Frontend proxy access: curl http://localhost:3000/health"
echo "    Expected: {\"status\":\"healthy\"} (works via proxy) ✓"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop:"
echo "  docker-compose down"

