"""LLM service abstraction supporting multiple providers."""
from abc import ABC, abstractmethod
from typing import Optional
from backend.config import settings
from backend.services.llm_logger import log_llm_call
import openai
import httpx
import logging

logger = logging.getLogger(__name__)


class LLMService(ABC):
    """Abstract LLM service interface."""
    
    @abstractmethod
    async def generate_summary(self, content: str, context: Optional[str] = None, item_type: str = "file") -> str:
        """Generate a summary of the given content."""
        pass
    
    async def answer_question(self, question: str, context: str) -> str:
        """Answer a question based on provided context. Default implementation uses generate_summary."""
        # Default implementation - can be overridden by subclasses
        prompt = f"""You are a code assistant helping a developer understand and modify a codebase. Answer the following question with specific, actionable information.

Question: {question}

Repository Context:
{context}

Instructions:
1. Provide a specific, direct answer to the question
2. If the question asks about where something is defined or how to change it, specify the exact file path(s) and relevant code sections
3. If code changes are needed, provide specific examples showing what to change
4. Reference the file paths from the context above
5. Be concise but complete - focus on answering the question directly

Answer:"""
        return await self.generate_summary(prompt, item_type="file")


class OpenAIService(LLMService):
    """OpenAI LLM service."""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def answer_question(self, question: str, context: str) -> str:
        """Answer a question using OpenAI."""
        prompt = f"""You are a code assistant helping a developer understand and modify a codebase. Answer the following question with specific, actionable information.

Question: {question}

Repository Context:
{context}

Instructions:
1. Provide a specific, direct answer to the question
2. If the question asks about where something is defined or how to change it, specify the exact file path(s) and relevant code sections
3. If code changes are needed, provide specific examples showing what to change
4. Reference the file paths from the context above
5. Be concise but complete - focus on answering the question directly

Answer:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
        
        result = response.choices[0].message.content.strip()
        
        # Log the LLM call
        log_llm_call("openai", self.model, prompt, result, "qa", context)
        
        return result
    
    async def generate_summary(self, content: str, context: Optional[str] = None, item_type: str = "file") -> str:
        """Generate summary using OpenAI."""
        logger.info(f"OpenAI: Generating {item_type} summary, content length: {len(content)}")
        prompt = self._build_prompt(content, context, item_type)
        
        logger.info(f"OpenAI: Calling API with model {self.model}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,  # Increased for comprehensive summaries
        )
        
        result = response.choices[0].message.content.strip()
        logger.info(f"OpenAI: Received response, length: {len(result)}")
        
        # Log the LLM call
        log_llm_call("openai", self.model, prompt, result, item_type, context)
        
        return result
    
    def _build_prompt(self, content: str, context: Optional[str] = None, item_type: str = "file") -> str:
        """Build prompt for summarization optimized for AI agents."""
        if item_type == "file":
            prompt = f"""Analyze this code file and provide a comprehensive summary that would help an AI agent understand how to modify it:

1. **Purpose**: What does this file do? What is its main responsibility?
2. **Key Functions/Classes**: List all important functions, classes, methods, and their purposes
3. **Dependencies**: What other files/modules does this depend on?
4. **Configuration**: What configuration options, environment variables, or parameters does it use?
5. **Data Flow**: How does data flow through this file? What are the inputs and outputs?
6. **Modification Guide**: How would an AI agent modify this file to add new features or change behavior?
7. **Important Patterns**: What coding patterns, conventions, or architectural decisions are used?

File Content:
{content}

Provide a detailed summary that enables an AI agent to programmatically modify this file:"""
        else:  # folder
            prompt = f"""Analyze this folder/directory structure and provide a comprehensive summary:

The folder structure and contents are provided below. Use this information to generate a detailed summary.

{content}

1. **Purpose**: What is the purpose of this folder? What role does it play in the project?
2. **Structure**: What files and subdirectories does it contain? (Use the structure provided above)
3. **Relationships**: How do the files in this folder relate to each other?
4. **Dependencies**: What dependencies does this folder have on other parts of the project?
5. **Modification Guide**: How would an AI agent add new files or modify existing ones in this folder?

Provide a detailed summary that enables an AI agent to understand and modify this folder structure:"""
        
        return prompt


class OllamaService(LLMService):
    """Ollama LLM service."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
    
    async def answer_question(self, question: str, context: str) -> str:
        """Answer a question using Ollama."""
        prompt = f"""You are a code assistant helping a developer understand and modify a codebase. Answer the following question with specific, actionable information.

Question: {question}

Repository Context:
{context}

Instructions:
1. Provide a specific, direct answer to the question
2. If the question asks about where something is defined or how to change it, specify the exact file path(s) and relevant code sections
3. If code changes are needed, provide specific examples showing what to change
4. Reference the file paths from the context above
5. Be concise but complete - focus on answering the question directly

Answer:"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
            answer = result.get("response", "").strip()
            
            # Log the LLM call
            log_llm_call("ollama", self.model, prompt, answer, "qa", context)
            
            return answer
    
    async def generate_summary(self, content: str, context: Optional[str] = None, item_type: str = "file") -> str:
        """Generate summary using Ollama."""
        prompt = self._build_prompt(content, context, item_type)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
            summary = result.get("response", "").strip()
            
            # Log the LLM call
            log_llm_call("ollama", self.model, prompt, summary, item_type, context)
            
            return summary
    
    def _build_prompt(self, content: str, context: Optional[str] = None, item_type: str = "file") -> str:
        """Build prompt for summarization optimized for AI agents."""
        if item_type == "file":
            prompt = f"""Analyze this code file and provide a comprehensive summary that would help an AI agent understand how to modify it:

1. **Purpose**: What does this file do? What is its main responsibility?
2. **Key Functions/Classes**: List all important functions, classes, methods, and their purposes
3. **Dependencies**: What other files/modules does this depend on?
4. **Configuration**: What configuration options, environment variables, or parameters does it use?
5. **Data Flow**: How does data flow through this file? What are the inputs and outputs?
6. **Modification Guide**: How would an AI agent modify this file to add new features or change behavior?
7. **Important Patterns**: What coding patterns, conventions, or architectural decisions are used?

File Content:
{content}

Provide a detailed summary that enables an AI agent to programmatically modify this file:"""
        else:  # folder
            prompt = f"""Analyze this folder/directory structure and provide a comprehensive summary:

The folder structure and contents are provided below. Use this information to generate a detailed summary.

{content}

1. **Purpose**: What is the purpose of this folder? What role does it play in the project?
2. **Structure**: What files and subdirectories does it contain? (Use the structure provided above)
3. **Relationships**: How do the files in this folder relate to each other?
4. **Dependencies**: What dependencies does this folder have on other parts of the project?
5. **Modification Guide**: How would an AI agent add new files or modify existing ones in this folder?

Provide a detailed summary that enables an AI agent to understand and modify this folder structure:"""
        
        return prompt


class DeepSeekService(LLMService):
    """DeepSeek Coding LLM service."""
    
    def __init__(self):
        if not settings.deepseek_api_key:
            raise ValueError("DeepSeek API key not configured")
        self.client = openai.OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base,
        )
        # Ensure we're using the coder model, not chat
        self.model = settings.deepseek_model
        if self.model == "deepseek-chat":
            # Auto-upgrade to coder if chat is configured
            self.model = "deepseek-coder"
    
    async def generate_summary(self, content: str, context: Optional[str] = None, item_type: str = "file") -> str:
        """Generate summary using DeepSeek."""
        prompt = self._build_prompt(content, context, item_type)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,  # Increased for comprehensive summaries
        )
        
        result = response.choices[0].message.content.strip()
        
        # Log the LLM call
        log_llm_call("deepseek", self.model, prompt, result, item_type, context)
        
        return result
    
    async def answer_question(self, question: str, context: str) -> str:
        """Answer a question using DeepSeek Coder with Q&A-specific prompt."""
        prompt = f"""You are a code assistant helping a developer understand and modify a codebase. Answer the following question with specific, actionable information.

Question: {question}

Repository Context:
{context}

Instructions:
1. Provide a specific, direct answer to the question
2. If the question asks about where something is defined or how to change it, specify the exact file path(s) and relevant code sections
3. If code changes are needed, provide specific examples showing what to change
4. Reference the file paths from the context above
5. Be concise but complete - focus on answering the question directly

Answer:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
        
        result = response.choices[0].message.content.strip()
        
        # Log the LLM call with "qa" as item_type
        log_llm_call("deepseek", self.model, prompt, result, "qa", context)
        
        return result
    
    def _build_prompt(self, content: str, context: Optional[str] = None, item_type: str = "file") -> str:
        """
        Build prompt for summarization optimized for AI agents.
        
        Args:
            content: The content to summarize
            context: Optional context (for folders, this is child summaries)
            item_type: "file" or "folder"
        """
        if item_type == "file":
            prompt = f"""Analyze this code file and provide a comprehensive summary that would help an AI agent understand how to modify it:

1. **Purpose**: What does this file do? What is its main responsibility?
2. **Key Functions/Classes**: List all important functions, classes, methods, and their purposes
3. **Dependencies**: What other files/modules does this depend on?
4. **Configuration**: What configuration options, environment variables, or parameters does it use?
5. **Data Flow**: How does data flow through this file? What are the inputs and outputs?
6. **Modification Guide**: How would an AI agent modify this file to add new features or change behavior?
7. **Important Patterns**: What coding patterns, conventions, or architectural decisions are used?

File Content:
{content}

Provide a detailed summary that enables an AI agent to programmatically modify this file:"""
        else:  # folder
            prompt = f"""Analyze this folder/directory structure and provide a comprehensive summary:

The folder structure and contents are provided below. Use this information to generate a detailed summary.

{content}

1. **Purpose**: What is the purpose of this folder? What role does it play in the project?
2. **Structure**: What files and subdirectories does it contain? (Use the structure provided above)
3. **Relationships**: How do the files in this folder relate to each other?
4. **Dependencies**: What dependencies does this folder have on other parts of the project?
5. **Modification Guide**: How would an AI agent add new files or modify existing ones in this folder?

Provide a detailed summary that enables an AI agent to understand and modify this folder structure:"""
        
        return prompt


def get_llm_service() -> LLMService:
    """Get the configured LLM service."""
    provider = settings.llm_provider
    
    if provider == "openai":
        return OpenAIService()
    elif provider == "ollama":
        return OllamaService()
    elif provider == "deepseek":
        return DeepSeekService()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

