from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import uvicorn

from app.core.config import settings
from app.core.database import init_db
from app.api import enforcement, sessions, policies, compliance
from app.services.websocket_manager import WebSocketManager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# WebSocket manager for real-time updates
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application on startup and cleanup on shutdown."""
    # Startup
    logger.info("Starting Runlok API server", version="0.1.0")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Runlok API server")

app = FastAPI(
    title="Runlok API",
    description="Middleware for enforcing and logging AI agent tool use",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(enforcement.router, prefix="/api/v1", tags=["enforcement"])
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(policies.router, prefix="/api/v1", tags=["policies"])
app.include_router(compliance.router, prefix="/api/v1", tags=["compliance"])

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Runlok API is running", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": "connected",  # TODO: Add actual DB health check
        "redis": "connected"      # TODO: Add actual Redis health check
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates."""
    await websocket_manager.connect(websocket, session_id)
    logger.info("WebSocket connected", session_id=session_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages if needed
            data = await websocket.receive_text()
            logger.debug("WebSocket message received", session_id=session_id, data=data)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, session_id)
        logger.info("WebSocket disconnected", session_id=session_id)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    ) 