from typing import Dict, List
from fastapi import WebSocket
import json
import structlog

logger = structlog.get_logger()

class WebSocketManager:
    """Manages WebSocket connections for real-time session updates."""
    
    def __init__(self):
        # Map of session_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a new WebSocket connection for a session."""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        logger.info("WebSocket connected", session_id=session_id, 
                   total_connections=len(self.active_connections[session_id]))
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
                
            # Clean up empty session lists
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                
        logger.info("WebSocket disconnected", session_id=session_id)
    
    async def send_personal_message(self, message: dict, session_id: str):
        """Send a message to all connections for a specific session."""
        if session_id not in self.active_connections:
            return
        
        # Send to all connections for this session
        disconnected_connections = []
        
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.warning("Failed to send WebSocket message", 
                             session_id=session_id, error=str(e))
                disconnected_connections.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection, session_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all active connections."""
        for session_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, session_id)
    
    def get_session_connection_count(self, session_id: str) -> int:
        """Get the number of active connections for a session."""
        return len(self.active_connections.get(session_id, []))
    
    def get_total_connections(self) -> int:
        """Get the total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_active_sessions(self) -> List[str]:
        """Get list of sessions with active connections."""
        return list(self.active_connections.keys()) 