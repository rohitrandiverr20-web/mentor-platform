from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import Column, String, UUID


SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
load_dotenv()

DATABASE_URL = os.getenv("postgresql://postgres:[Mentor–Student Platform]@db.ixiwoozgkanoszsbguoq.supabase.co:5432/postgres", "sqlite:///./sql_app.db")

# Create the engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for models
Base = declarative_base()
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True) # Matches Supabase User ID
    email = Column(String, unique=True, index=True) 
    role = Column(String)