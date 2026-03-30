from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession
from uuid import UUID

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.session import Session, SessionStatus
from app.schemas.session import SessionResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

@router.post("/create", response_model=SessionResponse)
def create_session(
    db: DbSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Mentors can create a new session."""
    if current_user.role != UserRole.mentor:
        raise HTTPException(status_code=403, detail="Only mentors can create sessions.")
    
    new_session = Session(mentor_id=current_user.id, status=SessionStatus.scheduled)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.post("/{session_id}/join", response_model=SessionResponse)
def join_session(
    session_id: UUID,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Students can join a scheduled session."""
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    if current_user.role == UserRole.student:
        if session.student_id and session.student_id != current_user.id:
            raise HTTPException(status_code=400, detail="Another student has already joined this session.")
        
        # Assign the student and set status to active
        session.student_id = current_user.id
        session.status = SessionStatus.active
        db.commit()
        db.refresh(session)
        
    return session

@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(
    session_id: UUID,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mentors (or students) can end an active session."""
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    # Security check: Ensure the user is actually part of this session
    if current_user.id not in [session.mentor_id, session.student_id]:
        raise HTTPException(status_code=403, detail="You do not have permission to end this session.")

    session.status = SessionStatus.ended
    db.commit()
    db.refresh(session)
    return session

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: UUID,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch details of a specific session."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session