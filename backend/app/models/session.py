import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class SessionStatus(str, enum.Enum):
    scheduled = "scheduled"
    active = "active"
    ended = "ended"

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # The mentor who created the session
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # The student who joins (nullable initially because a mentor might create it before a student joins)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    status = Column(Enum(SessionStatus), default=SessionStatus.scheduled)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships to easily fetch the full user profile if needed
    mentor = relationship("User", foreign_keys=[mentor_id])
    student = relationship("User", foreign_keys=[student_id])