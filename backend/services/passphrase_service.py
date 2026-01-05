"""Passphrase validation and usage tracking service."""
from sqlalchemy.orm import Session
from backend.config import settings
from backend.models.passphrase_usage import PassphraseUsage
import uuid


def is_valid_passphrase(passphrase: str) -> bool:
    """
    Check if passphrase is valid.
    
    Valid passphrases:
    - Admin passphrase (unlimited access)
    - Class repo name + 1, 2, or 3 (evaluator passphrases)
    
    Args:
        passphrase: Passphrase to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not passphrase:
        return False
    
    # Check admin passphrase
    if passphrase == settings.admin_passphrase:
        return True
    
    # Check evaluator passphrases (class_repo_name + 1, 2, or 3)
    expected_passphrases = [
        f"{settings.class_repo_name}1",
        f"{settings.class_repo_name}2",
        f"{settings.class_repo_name}3",
    ]
    
    return passphrase in expected_passphrases


def is_admin_passphrase(passphrase: str) -> bool:
    """Check if passphrase is admin passphrase."""
    return passphrase == settings.admin_passphrase


def get_or_create_passphrase_usage(db: Session, passphrase: str) -> PassphraseUsage:
    """
    Get or create passphrase usage record.
    
    Args:
        db: Database session
        passphrase: Passphrase
        
    Returns:
        PassphraseUsage record
    """
    usage = db.query(PassphraseUsage).filter(
        PassphraseUsage.passphrase == passphrase
    ).first()
    
    if not usage:
        usage = PassphraseUsage(
            id=str(uuid.uuid4()),
            passphrase=passphrase,
            questions_asked=0,
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
    
    return usage


def can_crawl_repository(db: Session, passphrase: str) -> tuple[bool, str]:
    """
    Check if passphrase can crawl a repository.
    
    Rules:
    - Admin: unlimited
    - Evaluators: 1 repository max
    
    Args:
        db: Database session
        passphrase: Passphrase to check
        
    Returns:
        Tuple of (can_crawl, error_message)
    """
    if not is_valid_passphrase(passphrase):
        return (False, "Invalid passphrase. Please use your assigned evaluator passphrase.")
    
    # Admin has unlimited access
    if is_admin_passphrase(passphrase):
        return (True, "")
    
    # Check evaluator limits
    usage = get_or_create_passphrase_usage(db, passphrase)
    
    # Count how many repositories this passphrase has crawled
    crawled_count = db.query(PassphraseUsage).filter(
        PassphraseUsage.passphrase == passphrase,
        PassphraseUsage.repo_id.isnot(None)
    ).count()
    
    if crawled_count >= 1:
        return (False, f"You have already crawled 1 repository. Each evaluator can crawl only 1 repository.")
    
    return (True, "")


def can_ask_question(db: Session, passphrase: str) -> tuple[bool, str]:
    """
    Check if passphrase can ask a question.
    
    Rules:
    - Admin: unlimited
    - Evaluators: 2 questions max
    
    Args:
        db: Database session
        passphrase: Passphrase to check
        
    Returns:
        Tuple of (can_ask, error_message)
    """
    if not is_valid_passphrase(passphrase):
        return (False, "Invalid passphrase. Please use your assigned evaluator passphrase.")
    
    # Admin has unlimited access
    if is_admin_passphrase(passphrase):
        return (True, "")
    
    # Check evaluator limits
    usage = get_or_create_passphrase_usage(db, passphrase)
    
    if usage.questions_asked >= 2:
        return (False, f"You have already asked 2 questions. Each evaluator can ask only 2 questions.")
    
    return (True, "")


def record_repository_crawl(db: Session, passphrase: str, repo_id: str):
    """
    Record that a passphrase has crawled a repository.
    
    Args:
        db: Database session
        passphrase: Passphrase used
        repo_id: Repository ID that was crawled
    """
    if is_admin_passphrase(passphrase):
        # Admin doesn't need tracking
        return
    
    usage = PassphraseUsage(
        id=str(uuid.uuid4()),
        passphrase=passphrase,
        repo_id=repo_id,
        questions_asked=0,
    )
    db.add(usage)
    db.commit()


def record_question_asked(db: Session, passphrase: str):
    """
    Record that a passphrase has asked a question.
    
    Args:
        db: Database session
        passphrase: Passphrase used
    """
    if is_admin_passphrase(passphrase):
        # Admin doesn't need tracking
        return
    
    usage = get_or_create_passphrase_usage(db, passphrase)
    usage.questions_asked += 1
    db.commit()

