"""Q&A service for answering questions about repositories."""
from sqlalchemy.orm import Session
from backend.models.node import Node
from backend.services.llm_service import get_llm_service
from backend.services.embedding_service import search_summaries
from typing import Dict, List


async def answer_question(db: Session, repo_id: str, question: str) -> Dict[str, List[str] | str]:
    """
    Answer a question about a repository using context from summaries.
    
    Args:
        db: Database session
        repo_id: Repository ID
        question: User's question
        
    Returns:
        Dictionary with 'answer' and 'sources' (list of file paths)
    """
    # Search for relevant summaries within this repository
    search_results = search_summaries(db, question, limit=10, repo_id=repo_id)
    
    # Get top relevant summaries with file paths
    relevant_summaries = []
    sources = []
    
    for result in search_results[:5]:  # Top 5 results
        node = db.query(Node).filter(
            Node.repo_id == repo_id,
            Node.path == result["path"]
        ).first()
        if node and node.summary:
            # Include file path in context for better answers
            relevant_summaries.append(f"## File: {node.path}\n{node.summary}")
            sources.append(node.path)
    
    # If no search results, use root summary as fallback
    if not relevant_summaries:
        root_node = db.query(Node).filter(
            Node.repo_id == repo_id,
            Node.path == "",
            Node.parent_id.is_(None)
        ).first()
        if root_node and root_node.summary:
            relevant_summaries.append(f"## Repository Overview\n{root_node.summary}")
            sources.append(root_node.path or "root")
    
    # Build context from relevant summaries
    context = "\n\n".join(relevant_summaries)
    
    # Generate answer using LLM's Q&A method (not summary method)
    llm_service = get_llm_service()
    
    # Use the answer_question method which has proper Q&A prompt
    answer = await llm_service.answer_question(question, context)
    
    return {
        "answer": answer,
        "sources": sources,
    }

