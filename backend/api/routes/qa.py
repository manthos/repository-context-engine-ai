"""Q&A endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.qa import QARequest, QAResponse
from backend.db.base import get_db
from backend.models.repository import Repository
from backend.services.qa_service import answer_question
from backend.services.passphrase_service import can_ask_question, record_question_asked

router = APIRouter()


@router.post("/qa", response_model=QAResponse)
async def ask_question(request: QARequest, db: Session = Depends(get_db)):
    """Answer questions about a repository."""
    # Check passphrase and access limits
    can_ask, error_msg = can_ask_question(db, request.passphrase)
    if not can_ask:
        raise HTTPException(status_code=403, detail=error_msg)
    
    # Check if repository exists
    repo = db.query(Repository).filter(Repository.id == request.repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Answer question
    result = await answer_question(db, request.repo_id, request.question)
    
    # Record question usage
    record_question_asked(db, request.passphrase)
    
    return QAResponse(
        answer=result["answer"],
        sources=result["sources"],
    )

