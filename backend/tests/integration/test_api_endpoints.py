"""Basic integration tests for CI/CD demonstration."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.tests.conftest import db_session


@pytest.fixture
def client(db_session):
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_search_endpoint(client):
    """Test search endpoint returns a list."""
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_cache_list_endpoint(client):
    """Test cache list endpoint returns a list."""
    response = client.get("/api/cache")
    assert response.status_code == 200
    repos = response.json()
    assert isinstance(repos, list)
