from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.session import SessionStatus

# What we return to the frontend
class SessionResponse(BaseModel):
    id: UUID
    mentor_id: UUID
    student_id: UUID | None = None
    status: SessionStatus
    start_time: datetime

    class Config:
        from_attributes = True