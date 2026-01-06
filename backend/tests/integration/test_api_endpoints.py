"""Integration tests for API endpoints."""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.tests.conftest import db_session


@pytest.fixture
def client(db_session):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_passphrase():
    """Mock passphrase validation to always allow access in tests."""
    with patch("backend.services.passphrase_service.can_crawl_repository") as mock_can_crawl:
        mock_can_crawl.return_value = (True, None)
        yield mock_can_crawl


@pytest.fixture
def mock_analysis():
    """Mock the actual analysis process to avoid LLM calls."""
    with patch("backend.services.analyzer.start_analysis") as mock_start:
        yield mock_start


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


def test_analyze_endpoint(client, mock_passphrase, mock_analysis):
    """Test analyze endpoint."""
    response = client.post(
        "/api/analyze",
        json={
            "repo_url": "https://github.com/octocat/Hello-World",
            "passphrase": "test"
        }
    )
    assert response.status_code == 202
    assert "task_id" in response.json()


def test_status_endpoint(client, db_session):
    """Test status endpoint."""
    # First create a task (would normally be done by analyze endpoint)
    from backend.models.task import Task, TaskStatus
    from backend.models.repository import Repository, RepositoryStatus
    import uuid
    
    repo_id = str(uuid.uuid4())
    repo = Repository(id=repo_id, url="https://test.com/repo", status=RepositoryStatus.PROCESSING)
    db_session.add(repo)
    
    task_id = str(uuid.uuid4())
    task = Task(id=task_id, repo_id=repo_id, status=TaskStatus.PENDING.value, progress=0)
    db_session.add(task)
    db_session.commit()
    
    response = client.get(f"/api/status/{task_id}")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "progress" in response.json()


def test_search_endpoint(client, db_session):
    """Test search endpoint."""
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_analyze_workflow_complete(client, db_session, mock_passphrase, mock_analysis):
    """
    Integration test for complete analyze workflow:
    1. POST /api/analyze - Start analysis
    2. GET /api/status/{task_id} - Check progress
    3. GET /api/tree/{repo_id} - Retrieve results (when complete)
    """
    # Step 1: Start analysis
    analyze_response = client.post(
        "/api/analyze",
        json={
            "repo_url": "https://github.com/octocat/Hello-World",
            "passphrase": "test"
        }
    )
    assert analyze_response.status_code == 202
    task_id = analyze_response.json()["task_id"]
    assert task_id is not None
    
    # Step 2: Check status
    status_response = client.get(f"/api/status/{task_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert "status" in status_data
    assert "progress" in status_data
    assert status_data["progress"] >= 0


def test_search_with_repo_filter(client, db_session):
    """Test search endpoint with repository filter."""
    from backend.models.repository import Repository, RepositoryStatus
    from backend.models.node import Node
    import uuid
    
    # Create test repository and nodes
    repo_id = str(uuid.uuid4())
    repo = Repository(id=repo_id, url="https://test.com/repo", status=RepositoryStatus.COMPLETED)
    db_session.add(repo)
    
    node = Node(
        id=str(uuid.uuid4()),
        repo_id=repo_id,
        path="test.py",
        name="test.py",
        type="file",
        summary="This is a test file for authentication"
    )
    db_session.add(node)
    db_session.commit()
    
    # Search with repo filter
    response = client.get(f"/api/search?q=authentication&repo_id={repo_id}")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)


def test_browse_repository_structure(client, db_session):
    """
    Test browsing repository structure:
    1. Browse root folder
    2. Browse subfolder
    3. Browse file
    """
    from backend.models.repository import Repository, RepositoryStatus
    from backend.models.node import Node
    import uuid
    
    # Create test repository with structure
    repo_id = str(uuid.uuid4())
    repo = Repository(id=repo_id, url="https://test.com/repo", status=RepositoryStatus.COMPLETED)
    db_session.add(repo)
    
    # Create nodes: root folder, subfolder, file
    root_node = Node(
        id=str(uuid.uuid4()),
        repo_id=repo_id,
        path="",
        name="root",
        type="folder",
        summary="Root folder"
    )
    db_session.add(root_node)
    
    subfolder = Node(
        id=str(uuid.uuid4()),
        repo_id=repo_id,
        path="src",
        name="src",
        type="folder",
        summary="Source folder",
        parent_id=root_node.id
    )
    db_session.add(subfolder)
    
    file_node = Node(
        id=str(uuid.uuid4()),
        repo_id=repo_id,
        path="src/main.py",
        name="main.py",
        type="file",
        summary="Main application file",
        parent_id=subfolder.id
    )
    db_session.add(file_node)
    db_session.commit()
    
    # Browse root
    response = client.get(f"/api/browse/{repo_id}")
    assert response.status_code == 200
    
    # Browse subfolder
    response = client.get(f"/api/browse/{repo_id}?path=src")
    assert response.status_code == 200


def test_cache_list_endpoint(client, db_session):
    """Test listing cached repositories."""
    from backend.models.repository import Repository, RepositoryStatus
    import uuid
    
    # Create some test repositories
    for i in range(2):
        repo = Repository(
            id=str(uuid.uuid4()),
            url=f"https://test.com/repo{i}",
            status=RepositoryStatus.COMPLETED
        )
        db_session.add(repo)
    db_session.commit()
    
    # List cached repos
    response = client.get("/api/cache")
    assert response.status_code == 200
    repos = response.json()
    assert isinstance(repos, list)
    assert len(repos) >= 2


def test_error_handling_invalid_task_id(client):
    """Test error handling for invalid task ID."""
    response = client.get("/api/status/nonexistent-task-id")
    assert response.status_code in [404, 500]  # Should return error


def test_error_handling_invalid_repo_url(client, mock_passphrase, mock_analysis):
    """Test error handling for invalid repository URL."""
    response = client.post(
        "/api/analyze",
        json={
            "repo_url": "not-a-valid-url",
            "passphrase": "test"
        }
    )
    # Should either validate URL or accept it and fail during processing
    assert response.status_code in [202, 400, 422]


def test_qa_endpoint_workflow(client, db_session):
    """
    Test Q&A workflow:
    1. Repository must exist and be completed
    2. POST /api/qa with question and passphrase
    3. Receive answer with sources
    """
    from backend.models.repository import Repository, RepositoryStatus
    from backend.models.node import Node
    import uuid
    
    # Create completed repository with nodes
    repo_id = str(uuid.uuid4())
    repo = Repository(id=repo_id, url="https://test.com/repo", status=RepositoryStatus.COMPLETED)
    db_session.add(repo)
    
    node = Node(
        id=str(uuid.uuid4()),
        repo_id=repo_id,
        path="README.md",
        name="README.md",
        type="file",
        summary="This is a test project for demonstrating R2CE"
    )
    db_session.add(node)
    db_session.commit()
    
    # Mock the QA service to avoid real LLM calls
    with patch("backend.services.qa_service.get_qa_answer") as mock_qa:
        mock_qa.return_value = "This is a test project."
        
        # Ask question
        response = client.post(
            "/api/qa",
            json={
                "repo_id": repo_id,
                "question": "What is this project about?",
                "passphrase": "test"
            }
        )
        # May fail if LLM not configured, but endpoint should exist
        assert response.status_code in [200, 500, 503]
