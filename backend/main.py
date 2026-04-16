from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
models.Base.metadata.create_all(bind=engine)
from supabase import create_client
from models import Profile, SessionModel
import uuid
from fastapi import WebSocket, WebSocketDisconnect
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Your Next.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "Backend running successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the Mentor-Student Platform API!"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/user/setup-role")
async def setup_user_role(
    user_id: str, 
    email: str, 
    role: str, 
    db: Session = Depends(get_db)
):
    if role not in ["mentor", "student"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    existing_user = db.query(models.Profile).filter(models.Profile.id == user_id).first()
    if existing_user:
        return {"message": "User already configured"}
    
    new_profile = models.Profile(id=user_id, email=email, role=role)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {"status": "success", "role": new_profile.role}

supabase = create_client("https://ixiwoozgkanoszsbguoq.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4aXdvb3pna2Fub3N6c2JndW9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxMDI1MjIsImV4cCI6MjA5MDY3ODUyMn0.JhRMNiqQyZeWsqnEgPGFTAfJmDYCUbAyt3GmX4ycrlE")

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Token")
    
    # Remove "Bearer " prefix if present
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify token with Supabase Auth 
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token")

@app.post("/api/sessions/create")
async def create_session(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # Check if the user's role in our DB is 'mentor' [cite: 58, 62]
    user_profile = db.query(Profile).filter(Profile.id == user.id).first()
    
    if user_profile.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can create sessions")
    
    # Logic to create session goes here... [cite: 67, 72]
    return {"message": "Session created successfully"}
async def verify_user_role(request: Request):
    # 1. Get token from header 
    auth_header = request.headers.get("Authorization")
    
    # 2. Verify with Supabase 
    user = supabase.auth.get_user(auth_header)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Token") 
    
    return user

@app.post("/sessions/create")
async def create_session(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # 1. Check if the user is a mentor [cite: 58, 64]
    user_profile = db.query(Profile).filter(Profile.id == user.id).first()
    if user_profile.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can create sessions")
    return {"session_id": str(uuid.uuid4())}

    # 2. Create the session entry [cite: 72, 85]
    new_session = SessionModel(id=str(uuid.uuid4()), mentor_id=user.id, status="active")
    db.add(new_session)
    db.commit()
    return {"session_id": new_session.id}

@app.post("/sessions/join")
async def join_session(session_id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.student_id = user.id # Update the student_id field [cite: 81, 85]
    db.commit()
    return {"message": "Joined successfully", "session_id": session_id}

@app.post("/sessions/end")
async def end_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    session.status = "ended" # Change status to ended [cite: 82]
    db.commit()
    return {"status": "Session closed"}

class ConnectionManager:
    def __init__(self):
        # Dictionary to store active connections: {session_id: [list_of_websockets]}
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept() 
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        self.active_connections[session_id].remove(websocket)

    async def broadcast(self, session_id: str, message: str):
        # Send the code update to everyone in THIS specific session [cite: 102]
        for connection in self.active_connections.get(session_id, []):
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/session/{session_id}") 
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            # Receive code updates from the frontend [cite: 101]
            data = await websocket.receive_text() 
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat":
                new_msg = models.Message(
                    session_id=session_id,
                    message=message_data["message"],
                    sender_id=message_data.get("sender_id") # [cite: 118, 119]
                )
                # Save to Database for Persistence 
                save_message_to_db(session_id, message_data["message"])
            # Broadcast updates to the other person in the room [cite: 102]
            await manager.broadcast(session_id, data) 
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
        
        
        
def save_message_to_db(session_id: str, message: str):
    db = SessionLocal()
    try:
        new_message = models.ChatMessage(
            session_id=session_id, 
            content=message
        )
        db.add(new_message)
        db.commit()
    finally:
        db.close()
        
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mentor-student-platform.vercel.app"], # Your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)