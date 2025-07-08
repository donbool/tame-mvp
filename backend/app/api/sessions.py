from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
import structlog

from app.core.database import get_db
from app.models.session_log import SessionLog

logger = structlog.get_logger()
router = APIRouter()

class SessionLogResponse(BaseModel):
    """Response model for session log entries."""
    id: str
    session_id: str
    timestamp: datetime
    tool_name: str
    tool_args: Dict[str, Any]
    tool_result: Optional[Dict[str, Any]]
    policy_version: str
    policy_decision: str
    policy_rule: Optional[str]
    execution_status: Optional[str]
    execution_duration_ms: Optional[str]
    error_message: Optional[str]
    agent_id: Optional[str]
    user_id: Optional[str]

class SessionSummary(BaseModel):
    """Summary information for a session."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_calls: int
    allowed_calls: int
    denied_calls: int
    approved_calls: int
    agent_id: Optional[str]
    user_id: Optional[str]

class SessionListResponse(BaseModel):
    """Response model for session listing."""
    sessions: List[SessionSummary]
    total_count: int
    page: int
    page_size: int

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: AsyncSession = Depends(get_db)
):
    """List all sessions with summary information."""
    
    try:
        # Build base query
        base_query = select(SessionLog)
        
        # Apply filters
        if agent_id:
            base_query = base_query.where(SessionLog.agent_id == agent_id)
        if user_id:
            base_query = base_query.where(SessionLog.user_id == user_id)
        
        # Get unique sessions with aggregated data
        # This is a simplified approach - in production you might want to use
        # a separate sessions table or more complex aggregation
        
        offset = (page - 1) * page_size
        
        # Get all logs and group by session_id in Python
        # In production, this should be done with SQL aggregation
        all_logs_query = base_query.order_by(desc(SessionLog.timestamp))
        result = await db.execute(all_logs_query)
        all_logs = result.scalars().all()
        
        # Group by session_id
        sessions_dict = {}
        for log in all_logs:
            if log.session_id not in sessions_dict:
                sessions_dict[log.session_id] = {
                    "session_id": log.session_id,
                    "start_time": log.timestamp,
                    "end_time": log.timestamp,
                    "logs": [],
                    "agent_id": log.agent_id,
                    "user_id": log.user_id
                }
            
            session_data = sessions_dict[log.session_id]
            session_data["logs"].append(log)
            
            # Update time range
            if log.timestamp < session_data["start_time"]:
                session_data["start_time"] = log.timestamp
            if log.timestamp > session_data["end_time"]:
                session_data["end_time"] = log.timestamp
        
        # Create session summaries
        session_summaries = []
        for session_data in sessions_dict.values():
            logs = session_data["logs"]
            
            allowed_count = sum(1 for log in logs if log.policy_decision == "allow")
            denied_count = sum(1 for log in logs if log.policy_decision == "deny")
            approved_count = sum(1 for log in logs if log.policy_decision == "approve")
            
            summary = SessionSummary(
                session_id=session_data["session_id"],
                start_time=session_data["start_time"],
                end_time=session_data["end_time"] if session_data["end_time"] != session_data["start_time"] else None,
                total_calls=len(logs),
                allowed_calls=allowed_count,
                denied_calls=denied_count,
                approved_calls=approved_count,
                agent_id=session_data["agent_id"],
                user_id=session_data["user_id"]
            )
            session_summaries.append(summary)
        
        # Sort by start time (newest first)
        session_summaries.sort(key=lambda x: x.start_time, reverse=True)
        
        # Apply pagination
        total_count = len(session_summaries)
        paginated_sessions = session_summaries[offset:offset + page_size]
        
        return SessionListResponse(
            sessions=paginated_sessions,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error("Failed to list sessions", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions/{session_id}", response_model=List[SessionLogResponse])
async def get_session_logs(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all logs for a specific session."""
    
    try:
        query = select(SessionLog).where(
            SessionLog.session_id == session_id
        ).order_by(SessionLog.timestamp)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return [
            SessionLogResponse(
                id=str(log.id),
                session_id=log.session_id,
                timestamp=log.timestamp,
                tool_name=log.tool_name,
                tool_args=log.tool_args,
                tool_result=log.tool_result,
                policy_version=log.policy_version,
                policy_decision=log.policy_decision,
                policy_rule=log.policy_rule,
                execution_status=log.execution_status,
                execution_duration_ms=log.execution_duration_ms,
                error_message=log.error_message,
                agent_id=log.agent_id,
                user_id=log.user_id
            )
            for log in logs
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get session logs", 
                    session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions/{session_id}/summary", response_model=SessionSummary)
async def get_session_summary(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get summary information for a specific session."""
    
    try:
        query = select(SessionLog).where(
            SessionLog.session_id == session_id
        ).order_by(SessionLog.timestamp)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Calculate summary stats
        start_time = min(log.timestamp for log in logs)
        end_time = max(log.timestamp for log in logs)
        
        allowed_count = sum(1 for log in logs if log.policy_decision == "allow")
        denied_count = sum(1 for log in logs if log.policy_decision == "deny") 
        approved_count = sum(1 for log in logs if log.policy_decision == "approve")
        
        return SessionSummary(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time if end_time != start_time else None,
            total_calls=len(logs),
            allowed_calls=allowed_count,
            denied_calls=denied_count,
            approved_calls=approved_count,
            agent_id=logs[0].agent_id,
            user_id=logs[0].user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get session summary", 
                    session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete all logs for a session (use with caution)."""
    
    try:
        # Check if session exists
        query = select(SessionLog).where(SessionLog.session_id == session_id)
        result = await db.execute(query)
        logs = result.scalars().all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete all logs for the session
        for log in logs:
            await db.delete(log)
        
        await db.commit()
        
        logger.info("Session deleted", session_id=session_id, logs_deleted=len(logs))
        
        return {"status": "deleted", "session_id": session_id, "logs_deleted": len(logs)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete session", 
                    session_id=session_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error") 