from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String) # e.g., "mentor" or "student"
    is_active = Column(Boolean, default=True)

class Profile(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    bio = Column(String)
    
class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True) # Unique Session ID
    mentor_id = Column(String, ForeignKey("profiles.id")) # [cite: 79, 176]
    student_id = Column(String, ForeignKey("profiles.id"), nullable=True) # [cite: 81, 177]
    status = Column(String, default="active") # active, ended [cite: 82, 178]
    start_time = Column(DateTime(timezone=True), server_default=func.now()) # [cite: 83]
    
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True) # [cite: 116]
    session_id = Column(String) # [cite: 117, 181]
    sender_id = Column(String) # [cite: 118, 182]
    message = Column(String) # [cite: 119, 183]
    timestamp = Column(DateTime(timezone=True), server_default=func.now()) # [cite: 120]

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    content = Column(String)