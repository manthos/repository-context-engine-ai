"""Configuration management for R2CE."""
from pydantic_settings import BaseSettings
from typing import Literal
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:///r2ce.db"
    
    # LLM Provider
    llm_provider: Literal["openai", "ollama", "deepseek"] = "deepseek"
    
    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-3.5-turbo"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    
    # DeepSeek
    deepseek_api_key: str | None = None
    deepseek_api_base: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-coder"  # Code-specific model
    
    # Application
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"
    
    # File processing
    max_file_size: int = 1_000_000  # 1MB
    temp_dir: str = "/tmp/r2ce"
    cache_dir: str = "cache"  # Permanent cache directory for repositories
    
    # Repository size limit (in KB)
    max_git_size_kb: int = 10  # Default 10KB for demo version
    
    # Access control
    class_repo_name: str = "ai-dev-tools-zoomcamp"  # Class repository name for passphrases
    admin_passphrase: str = "manthos-owner"  # Admin passphrase (unlimited access)
    
    class Config:
        # Look for .env in project root (parent of backend directory)
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars (like VITE_API_URL, R2CE_API_URL used by frontend/MCP)


settings = Settings()

