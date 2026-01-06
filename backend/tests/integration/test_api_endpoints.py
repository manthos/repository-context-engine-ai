"""Basic integration tests for CI/CD demonstration."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.tests.conftest import db_session


@pytest.fixture
def client(db_session):
    """Create test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health endpoint responds successfully."""
    response = client.get("/health")
    assert response.status_code == 200
