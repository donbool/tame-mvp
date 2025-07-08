from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import structlog
import hashlib
import hmac

from app.core.config import settings
from app.core.database import get_db
from app.services.policy_engine import policy_engine
from app.services.websocket_manager import WebSocketManager
from app.models.session_log import SessionLog
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()
router = APIRouter()

class ToolCallRequest(BaseModel):
    """Request model for tool call enforcement."""
    tool_name: str
    tool_args: Dict[str, Any]
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ToolCallResponse(BaseModel):
    """Response model for tool call enforcement."""
    session_id: str
    decision: str  # allow, deny, approve
    rule_name: Optional[str]
    reason: str
    policy_version: str
    log_id: str
    timestamp: datetime

# WebSocket manager (imported from main)
websocket_manager = WebSocketManager()

def generate_log_signature(log_data: Dict[str, Any]) -> str:
    """Generate HMAC signature for log entry."""
    # Create canonical string representation
    canonical_data = f"{log_data['session_id']}:{log_data['tool_name']}:{log_data['timestamp'].isoformat()}"
    
    # Generate HMAC signature
    signature = hmac.new(
        settings.HMAC_SECRET.encode(),
        canonical_data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature

@router.post("/enforce", response_model=ToolCallResponse)
async def enforce_tool_call(
    request: ToolCallRequest,
    db: AsyncSession = Depends(get_db)
):
    """Enforce policy on a tool call and log the decision."""
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    timestamp = datetime.utcnow()
    
    logger.info("Tool call enforcement requested", 
               tool_name=request.tool_name,
               session_id=session_id,
               agent_id=request.agent_id)
    
    try:
        # Evaluate against policy
        session_context = {
            "session_id": session_id,
            "agent_id": request.agent_id,
            "user_id": request.user_id,
            **(request.metadata or {})
        }
        
        decision = policy_engine.evaluate(
            tool_name=request.tool_name,
            tool_args=request.tool_args,
            session_context=session_context
        )
        
        # Create log entry
        log_data = {
            "session_id": session_id,
            "tool_name": request.tool_name,
            "timestamp": timestamp,
            "policy_version": decision.policy_version,
            "policy_decision": decision.action,
            "policy_rule": decision.rule_name
        }
        
        # Generate signature
        log_signature = generate_log_signature(log_data)
        
        # Save to database
        session_log = SessionLog(
            session_id=session_id,
            timestamp=timestamp,
            tool_name=request.tool_name,
            tool_args=request.tool_args,
            policy_version=decision.policy_version,
            policy_decision=decision.action,
            policy_rule=decision.rule_name,
            log_signature=log_signature,
            agent_id=request.agent_id,
            user_id=request.user_id,
            metadata_fields=request.metadata
        )
        
        db.add(session_log)
        await db.commit()
        await db.refresh(session_log)
        
        # Send real-time update via WebSocket
        websocket_message = {
            "type": "tool_call_decision",
            "session_id": session_id,
            "log_id": str(session_log.id),
            "tool_name": request.tool_name,
            "decision": decision.action,
            "rule_name": decision.rule_name,
            "reason": decision.reason,
            "timestamp": timestamp.isoformat(),
            "policy_version": decision.policy_version
        }
        
        await websocket_manager.send_personal_message(websocket_message, session_id)
        
        # Log the decision
        logger.info("Tool call decision made",
                   session_id=session_id,
                   tool_name=request.tool_name,
                   decision=decision.action,
                   rule_name=decision.rule_name,
                   log_id=str(session_log.id))
        
        return ToolCallResponse(
            session_id=session_id,
            decision=decision.action,
            rule_name=decision.rule_name,
            reason=decision.reason,
            policy_version=decision.policy_version,
            log_id=str(session_log.id),
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error("Failed to enforce tool call", 
                    session_id=session_id,
                    tool_name=request.tool_name,
                    error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during enforcement")

@router.post("/enforce/{session_id}/result")
async def update_tool_result(
    session_id: str,
    log_id: str,
    result: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Update the result of a tool call after execution."""
    
    try:
        # Find the log entry
        log_entry = await db.get(SessionLog, log_id)
        if not log_entry:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        if log_entry.session_id != session_id:
            raise HTTPException(status_code=403, detail="Session ID mismatch")
        
        # Update the result
        log_entry.tool_result = result
        log_entry.execution_status = result.get("status", "success")
        log_entry.execution_duration_ms = result.get("duration_ms")
        log_entry.error_message = result.get("error_message")
        
        await db.commit()
        
        # Send real-time update
        websocket_message = {
            "type": "tool_call_result",
            "session_id": session_id,
            "log_id": log_id,
            "result": result,
            "execution_status": log_entry.execution_status
        }
        
        await websocket_manager.send_personal_message(websocket_message, session_id)
        
        logger.info("Tool call result updated",
                   session_id=session_id,
                   log_id=log_id,
                   status=log_entry.execution_status)
        
        return {"status": "updated", "log_id": log_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update tool result",
                    session_id=session_id,
                    log_id=log_id,
                    error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error") 