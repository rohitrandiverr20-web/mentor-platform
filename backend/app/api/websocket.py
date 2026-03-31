from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
from uuid import UUID
import json
from app.models.message import Message
from uuid import UUID
from app.core.database import get_db
from sqlalchemy.orm import Session as DbSession

router = APIRouter(tags=["WebSockets"])

class ConnectionManager:
    def __init__(self):
        # Maps a session_id to a list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            # Clean up the room if it's empty
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, message: str, session_id: str, sender: WebSocket):
        """Sends the message to everyone in the session EXCEPT the sender."""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                if connection != sender:
                    await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/session/{session_id}")

async def websocket_endpoint( 
    websocket: WebSocket, 
    session_id: UUID, 
    user_id: UUID, 
    db: DbSession = Depends(get_db)
    
):
    """
    Real-time code collaboration endpoint.
    Frontend connection URL: ws://localhost:8000/ws/session/{id}?token={jwt_token}
    """
    
    session_str = str(session_id)
    await manager.connect(websocket, session_str)
    
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            # 1. Handle Chat Messages
            if event_type == "chat":
                chat_text = data.get("message")
                
                # Save to database
                new_msg = Message(
                    session_id=session_id,
                    sender_id=user_id,
                    message=chat_text
                )
                db.add(new_msg)
                db.commit()
                db.refresh(new_msg)

                # Broadcast to the other user
                broadcast_payload = {
                    "type": "chat",
                    "sender_id": str(user_id),
                    "message": chat_text,
                    "timestamp": new_msg.timestamp.isoformat()
                }
                await manager.broadcast(json.dumps(broadcast_payload), session_str, sender=websocket)

            # 2. Handle Code Updates
            elif event_type == "code":
                await manager.broadcast(json.dumps(data), session_str, sender=websocket)

            # 3. Handle WebRTC Signaling (Video/Audio)
            elif event_type in ["offer", "answer", "ice-candidate"]:
                # The backend blindly forwards these WebRTC signals so the browsers can connect
                await manager.broadcast(json.dumps(data), session_str, sender=websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_str)