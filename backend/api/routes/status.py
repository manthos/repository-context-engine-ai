"""Status endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.task import TaskStatus
from backend.db.base import get_db
from backend.models.task import Task

router = APIRouter()


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str, db: Session = Depends(get_db)):
    """Get analysis progress."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatus(
        status=task.status,
        progress=task.progress,
        status_message=task.status_message,
        result_id=task.result_id,
    )

