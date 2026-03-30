from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum
import uuid

class UserRole(str, enum.Enum):
    mentor = "mentor"
    student = "student"

class User(Base):
    __tablename__ = "users"

    # The ID will come directly from Supabase Auth
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)