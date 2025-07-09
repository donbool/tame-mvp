from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.services.compliance_service import compliance_service
from app.models.audit_log import AuditLog
from app.models.session_log import SessionLog

logger = structlog.get_logger()
router = APIRouter()

class ComplianceReportRequest(BaseModel):
    """Request model for compliance reports."""
    start_date: datetime
    end_date: datetime
    report_type: str = "summary"  # summary, detailed, full
    include_personal_data: bool = False

class AuditEventRequest(BaseModel):
    """Request model for creating audit events."""
    event_type: str
    action: str
    description: str
    actor_type: str = "user"
    actor_id: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    risk_level: str = "low"
    metadata: Optional[Dict[str, Any]] = None

@router.post("/compliance/audit/event")
async def create_audit_event(
    request: AuditEventRequest,
    actor_ip: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a new audit event for compliance tracking."""
    
    try:
        audit_log = await compliance_service.log_audit_event(
            db=db,
            event_type=request.event_type,
            action=request.action,
            description=request.description,
            actor_type=request.actor_type,
            actor_id=request.actor_id,
            actor_ip=actor_ip,
            target_type=request.target_type,
            target_id=request.target_id,
            risk_level=request.risk_level,
            request_data=request.metadata
        )
        
        return {
            "status": "audit_event_created",
            "audit_id": str(audit_log.id),
            "timestamp": audit_log.timestamp.isoformat(),
            "log_hash": audit_log.log_hash
        }
        
    except Exception as e:
        logger.error("Failed to create audit event", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create audit event")

@router.post("/compliance/report/generate")
async def generate_compliance_report(
    request: ComplianceReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a comprehensive compliance report for EU AI Act."""
    
    try:
        # Log the report generation
        await compliance_service.log_audit_event(
            db=db,
            event_type="compliance_report",
            action="generate",
            description=f"Generated {request.report_type} compliance report for period {request.start_date} to {request.end_date}",
            actor_type="system",
            risk_level="medium",
            target_type="compliance_data",
            request_data={
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "report_type": request.report_type
            }
        )
        
        # Generate the report
        report = await compliance_service.generate_compliance_report(
            db=db,
            start_date=request.start_date,
            end_date=request.end_date,
            report_type=request.report_type
        )
        
        # Add compliance metadata
        report["eu_ai_act_compliance"] = {
            "assessment_date": datetime.utcnow().isoformat(),
            "regulation_version": "EU AI Act 2024",
            "system_classification": "limited_risk",  # Should be configurable
            "compliance_status": "compliant",
            "next_review_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
            "responsible_person": "AI Governance Officer",
            "documentation_complete": True,
            "audit_trail_verified": report.get("data_governance", {}).get("data_integrity_status", {}).get("chain_intact", False)
        }
        
        return report
        
    except Exception as e:
        logger.error("Failed to generate compliance report", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate compliance report")

@router.get("/compliance/retention/status")
async def get_retention_status(
    db: AsyncSession = Depends(get_db)
):
    """Get data retention compliance status."""
    
    try:
        from sqlalchemy import select, and_
        
        now = datetime.utcnow()
        
        # Check upcoming deletions (next 30 days)
        upcoming_query = select(SessionLog).where(
            and_(
                SessionLog.retention_until.isnot(None),
                SessionLog.retention_until <= now + timedelta(days=30),
                SessionLog.retention_until > now
            )
        )
        
        upcoming_result = await db.execute(upcoming_query)
        upcoming_deletions = upcoming_result.scalars().all()
        
        # Check overdue deletions
        overdue_query = select(SessionLog).where(
            and_(
                SessionLog.retention_until.isnot(None),
                SessionLog.retention_until < now
            )
        )
        
        overdue_result = await db.execute(overdue_query)
        overdue_deletions = overdue_result.scalars().all()
        
        # Get archive statistics
        archived_query = select(SessionLog).where(SessionLog.is_archived == True)
        archived_result = await db.execute(archived_query)
        archived_sessions = archived_result.scalars().all()
        
        return {
            "retention_compliance": {
                "upcoming_deletions": len(upcoming_deletions),
                "overdue_deletions": len(overdue_deletions),
                "archived_sessions": len(archived_sessions),
                "compliance_status": "compliant" if len(overdue_deletions) == 0 else "non_compliant",
                "next_review_date": (now + timedelta(days=7)).isoformat()
            },
            "upcoming_actions": [
                {
                    "session_id": log.session_id,
                    "retention_until": log.retention_until.isoformat(),
                    "days_remaining": (log.retention_until - now).days,
                    "agent_id": log.agent_id
                }
                for log in upcoming_deletions[:10]  # Limit to first 10
            ],
            "overdue_actions": [
                {
                    "session_id": log.session_id,
                    "retention_until": log.retention_until.isoformat(),
                    "days_overdue": (now - log.retention_until).days,
                    "agent_id": log.agent_id
                }
                for log in overdue_deletions[:10]  # Limit to first 10
            ]
        }
        
    except Exception as e:
        logger.error("Failed to get retention status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get retention status")

@router.get("/compliance/integrity/verify")
async def verify_audit_integrity(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Verify the integrity of audit logs."""
    
    try:
        # Default to last 30 days if not specified
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Log the integrity check
        await compliance_service.log_audit_event(
            db=db,
            event_type="integrity_check",
            action="verify",
            description=f"Verified audit log integrity for period {start_date} to {end_date}",
            actor_type="system",
            risk_level="low",
            target_type="audit_logs"
        )
        
        # Verify integrity
        integrity_status = await compliance_service._verify_audit_chain_integrity(
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "integrity_verification": integrity_status,
            "verification_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "compliance_impact": {
                "meets_eu_ai_act": integrity_status.get("chain_intact", False),
                "audit_quality": "high" if integrity_status.get("integrity_violations", 0) == 0 else "compromised"
            }
        }
        
    except Exception as e:
        logger.error("Failed to verify audit integrity", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to verify audit integrity")

@router.post("/compliance/retention/cleanup")
async def cleanup_expired_data(
    dry_run: bool = Query(True, description="If true, only return what would be deleted"),
    db: AsyncSession = Depends(get_db)
):
    """Clean up expired data according to retention policies."""
    
    try:
        from sqlalchemy import select, and_
        
        now = datetime.utcnow()
        
        # Find expired logs
        expired_query = select(SessionLog).where(
            and_(
                SessionLog.retention_until.isnot(None),
                SessionLog.retention_until < now
            )
        )
        
        result = await db.execute(expired_query)
        expired_logs = result.scalars().all()
        
        if dry_run:
            return {
                "dry_run": True,
                "would_delete": len(expired_logs),
                "expired_sessions": [
                    {
                        "session_id": log.session_id,
                        "expired_since": (now - log.retention_until).days,
                        "agent_id": log.agent_id
                    }
                    for log in expired_logs[:20]  # Limit preview
                ]
            }
        
        # Actually delete expired logs
        deleted_count = 0
        for log in expired_logs:
            await db.delete(log)
            deleted_count += 1
        
        await db.commit()
        
        # Log the cleanup action
        await compliance_service.log_audit_event(
            db=db,
            event_type="data_cleanup",
            action="delete",
            description=f"Cleaned up {deleted_count} expired session logs per retention policy",
            actor_type="system",
            risk_level="medium",
            target_type="session_logs",
            response_data={"deleted_count": deleted_count}
        )
        
        return {
            "dry_run": False,
            "deleted_count": deleted_count,
            "cleanup_completed": True,
            "next_cleanup_recommended": (now + timedelta(days=7)).isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to cleanup expired data", error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to cleanup expired data") 