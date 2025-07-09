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

@router.post("/sessions/{session_id}/archive")
async def archive_session(
    session_id: str,
    archived_by: Optional[str] = None,
    retention_days: Optional[int] = 2555,  # ~7 years default for EU AI Act
    db: AsyncSession = Depends(get_db)
):
    """Archive a session instead of deleting it for compliance."""
    
    try:
        from datetime import timedelta
        
        # Check if session exists
        query = select(SessionLog).where(SessionLog.session_id == session_id)
        result = await db.execute(query)
        logs = result.scalars().all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Archive all logs for the session
        archive_time = datetime.utcnow()
        retention_until = archive_time + timedelta(days=retention_days)
        
        for log in logs:
            log.is_archived = True
            log.archived_at = archive_time
            log.archived_by = archived_by
            log.retention_until = retention_until
        
        await db.commit()
        
        logger.info("Session archived", 
                   session_id=session_id, 
                   logs_archived=len(logs),
                   retention_until=retention_until,
                   archived_by=archived_by)
        
        return {
            "status": "archived", 
            "session_id": session_id, 
            "logs_archived": len(logs),
            "retention_until": retention_until.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to archive session", 
                    session_id=session_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sessions/bulk/archive")
async def bulk_archive_sessions(
    session_ids: List[str],
    archived_by: Optional[str] = None,
    retention_days: Optional[int] = 2555,
    db: AsyncSession = Depends(get_db)
):
    """Archive multiple sessions at once."""
    
    try:
        from datetime import timedelta
        
        archive_time = datetime.utcnow()
        retention_until = archive_time + timedelta(days=retention_days)
        archived_count = 0
        
        for session_id in session_ids:
            query = select(SessionLog).where(SessionLog.session_id == session_id)
            result = await db.execute(query)
            logs = result.scalars().all()
            
            for log in logs:
                log.is_archived = True
                log.archived_at = archive_time
                log.archived_by = archived_by
                log.retention_until = retention_until
                archived_count += 1
        
        await db.commit()
        
        logger.info("Bulk archive completed", 
                   sessions_requested=len(session_ids),
                   logs_archived=archived_count,
                   archived_by=archived_by)
        
        return {
            "status": "bulk_archived",
            "sessions_processed": len(session_ids),
            "logs_archived": archived_count,
            "retention_until": retention_until.isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to bulk archive sessions", error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions/export")
async def export_sessions(
    format: str = Query("json", regex="^(json|csv)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    agent_id: Optional[str] = None,
    include_archived: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Export session data for compliance auditing."""
    
    try:
        from fastapi.responses import StreamingResponse
        import io
        import csv
        
        # Build query
        query = select(SessionLog).order_by(SessionLog.timestamp)
        
        if start_date:
            query = query.where(SessionLog.timestamp >= start_date)
        if end_date:
            query = query.where(SessionLog.timestamp <= end_date)
        if agent_id:
            query = query.where(SessionLog.agent_id == agent_id)
        if not include_archived:
            query = query.where(SessionLog.is_archived == False)
            
        result = await db.execute(query)
        logs = result.scalars().all()
        
        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "session_id", "timestamp", "tool_name", "policy_decision", 
                "policy_rule", "agent_id", "user_id", "execution_status",
                "is_archived", "archived_at"
            ])
            
            # Write data
            for log in logs:
                writer.writerow([
                    log.session_id, log.timestamp.isoformat(), log.tool_name,
                    log.policy_decision, log.policy_rule, log.agent_id,
                    log.user_id, log.execution_status, log.is_archived,
                    log.archived_at.isoformat() if log.archived_at else None
                ])
            
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=sessions_export.csv"}
            )
        
        else:  # JSON format
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_records": len(logs),
                "filters": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "agent_id": agent_id,
                    "include_archived": include_archived
                },
                "sessions": []
            }
            
            for log in logs:
                export_data["sessions"].append({
                    "id": str(log.id),
                    "session_id": log.session_id,
                    "timestamp": log.timestamp.isoformat(),
                    "tool_name": log.tool_name,
                    "tool_args": log.tool_args,
                    "tool_result": log.tool_result,
                    "policy_decision": log.policy_decision,
                    "policy_rule": log.policy_rule,
                    "policy_version": log.policy_version,
                    "agent_id": log.agent_id,
                    "user_id": log.user_id,
                    "execution_status": log.execution_status,
                    "log_signature": log.log_signature,
                    "is_archived": log.is_archived,
                    "archived_at": log.archived_at.isoformat() if log.archived_at else None
                })
            
            return export_data
            
    except Exception as e:
        logger.error("Failed to export sessions", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") 