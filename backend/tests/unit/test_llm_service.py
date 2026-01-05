"""Unit tests for LLM service."""
import pytest
from unittest.mock import Mock, patch
from backend.services.llm_service import get_llm_service, OpenAIService, OllamaService, DeepSeekService
from backend.config import settings


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('backend.services.llm_service.openai.OpenAI') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test summary"))]
        )
        yield mock_instance


def test_openai_service(mock_openai_client):
    """Test OpenAI service."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key', 'LLM_PROVIDER': 'openai'}):
        service = OpenAIService()
        assert service.model == settings.openai_model


def test_ollama_service():
    """Test Ollama service initialization."""
    with patch.dict('os.environ', {'LLM_PROVIDER': 'ollama'}):
        service = OllamaService()
        assert service.base_url == settings.ollama_base_url
        assert service.model == settings.ollama_model


def test_deepseek_service():
    """Test DeepSeek service initialization."""
    with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test_key', 'LLM_PROVIDER': 'deepseek'}):
        with patch('backend.services.llm_service.openai.OpenAI') as mock:
            service = DeepSeekService()
            assert service.model == settings.deepseek_model

