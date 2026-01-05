"""LLM call logging service - logs all LLM input/output to files."""
import os
import json
from datetime import datetime
from pathlib import Path
from backend.config import settings


def get_log_dir() -> Path:
    """Get the log directory path."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir


def log_llm_call(
    provider: str,
    model: str,
    prompt: str,
    response: str,
    item_type: str = "file",
    context: str | None = None,
):
    """
    Log an LLM call to a file.
    
    Args:
        provider: LLM provider name (openai, ollama, deepseek)
        model: Model name
        prompt: Input prompt
        response: LLM response
        item_type: Type of item being summarized (file/folder)
        context: Optional context provided
    """
    log_dir = get_log_dir()
    
    # Create timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"llm_call_{timestamp}.json"
    log_file = log_dir / filename
    
    # Prepare log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "provider": provider,
        "model": model,
        "item_type": item_type,
        "prompt": prompt,
        "response": response,
        "context": context,
        "prompt_length": len(prompt),
        "response_length": len(response),
    }
    
    # Write to file
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
    except Exception as e:
        # Don't fail if logging fails
        print(f"Warning: Failed to log LLM call: {e}")

