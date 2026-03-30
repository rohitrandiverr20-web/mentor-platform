from fastapi import FastAPI, Depends
from app.core.database import engine, Base
from app.api.dependencies import get_current_user
from app.models.user import User
from app.api import sessions
from app.api import sessions, websocket
from app.models.message import Message

app = FastAPI(title="Mentor-Student Platform API")


# Ensure tables are created
Base.metadata.create_all(bind=engine)

app.include_router(sessions.router)
app.include_router(websocket.router)

@app.get("/")
def read_root():
    return {"message": "API is live!"}

@app.get("/")
def read_root():
    return {"message": "API is live! This route is public."}

# 👉 THIS IS YOUR PROTECTED ROUTE
@app.get("/api/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Because of 'Depends(get_current_user)', FastAPI will automatically 
    reject anyone without a valid Supabase token.
    """
    return {
        "message": "You are authenticated!",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }
    