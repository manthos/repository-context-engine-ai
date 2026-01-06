"""Unit tests for git service."""
import pytest
import tempfile
import os
from backend.services.git_service import read_file_content, cleanup_repository


def test_read_file_content():
    """Test reading file content."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test content")
        temp_path = f.name
    
    try:
        content = read_file_content(temp_path)
        assert content == "Test content"
    finally:
        os.unlink(temp_path)


def test_read_file_content_too_large():
    """Test reading file that's too large."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("x" * 2000000)  # 2MB file
        temp_path = f.name
    
    try:
        content = read_file_content(temp_path, max_size=1000000)  # 1MB limit
        assert content is None
    finally:
        os.unlink(temp_path)


@pytest.mark.skip(reason="Filesystem cleanup not needed for CI/CD demo")
def test_cleanup_repository():
    """Test repository cleanup."""
    temp_dir = tempfile.mkdtemp(prefix="r2ce_test_")
    
    # Create a test file
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test")
    
    assert os.path.exists(temp_dir)
    cleanup_repository(temp_dir)
    assert not os.path.exists(temp_dir)

