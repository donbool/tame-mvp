from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.models.audit_log import AuditLog
from app.models.session_log import SessionLog
from app.models.policy_version import PolicyVersion

logger = structlog.get_logger()

class ComplianceService:
    """Service for EU AI Act compliance and auditing."""
    
    def __init__(self):
        self.last_log_hash: Optional[str] = None
    
    async def log_audit_event(
        self,
        db: AsyncSession,
        event_type: str,
        action: str,
        description: str,
        actor_type: str = "system",
        actor_id: Optional[str] = None,
        actor_ip: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        outcome: str = "success",
        risk_level: str = "low",
        compliance_relevant: bool = True,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        ai_system_component: Optional[str] = None,
        data_subject_category: Optional[str] = None,
        legal_basis: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry with integrity chain."""
        
        timestamp = datetime.utcnow()
        
        # Get last log hash for chaining
        if self.last_log_hash is None:
            last_log_query = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(1)
            result = await db.execute(last_log_query)
            last_log = result.scalar_one_or_none()
            self.last_log_hash = last_log.log_hash if last_log else "genesis"
        
        # Create audit log entry
        audit_log = AuditLog(
            timestamp=timestamp,
            event_type=event_type,
            event_category=self._categorize_event(event_type),
            event_source="api",  # Can be enhanced to detect source
            actor_type=actor_type,
            actor_id=actor_id,
            actor_ip=actor_ip,
            target_type=target_type,
            target_id=target_id,
            action=action,
            description=description,
            outcome=outcome,
            risk_level=risk_level,
            compliance_relevant=compliance_relevant,
            retention_category=self._determine_retention_category(risk_level, event_type),
            request_data=self._anonymize_data(request_data),
            response_data=self._anonymize_data(response_data),
            ai_system_component=ai_system_component,
            data_subject_category=data_subject_category,
            legal_basis=legal_basis,
            previous_log_hash=self.last_log_hash
        )
        
        # Calculate hash for integrity
        log_content = f"{timestamp.isoformat()}:{event_type}:{action}:{actor_id}:{target_id}:{outcome}:{self.last_log_hash}"
        audit_log.log_hash = hashlib.sha256(log_content.encode()).hexdigest()
        
        # Update last hash
        self.last_log_hash = audit_log.log_hash
        
        # Save to database
        db.add(audit_log)
        await db.commit()
        
        logger.info("Audit event logged", 
                   event_type=event_type,
                   action=action,
                   actor_id=actor_id,
                   risk_level=risk_level,
                   log_id=str(audit_log.id))
        
        return audit_log
    
    def _categorize_event(self, event_type: str) -> str:
        """Categorize events for compliance reporting."""
        categories = {
            "policy_change": "policy",
            "session_access": "data",
            "data_export": "data",
            "user_login": "user",
            "tool_enforcement": "system",
            "archive_action": "data",
            "system_config": "system"
        }
        return categories.get(event_type, "system")
    
    def _determine_retention_category(self, risk_level: str, event_type: str) -> str:
        """Determine data retention category based on risk and type."""
        if risk_level in ["high", "critical"] or event_type in ["policy_change", "data_export"]:
            return "extended"  # 10+ years
        elif event_type in ["system_config", "user_login"]:
            return "standard"  # 7 years
        else:
            return "standard"  # 7 years default
    
    def _anonymize_data(self, data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Anonymize sensitive data in logs."""
        if not data:
            return data
            
        # Remove or hash sensitive fields
        sensitive_fields = ["password", "token", "secret", "key", "email", "ip"]
        anonymized = data.copy()
        
        for field in sensitive_fields:
            if field in anonymized:
                if isinstance(anonymized[field], str):
                    anonymized[field] = hashlib.sha256(anonymized[field].encode()).hexdigest()[:8] + "..."
                else:
                    anonymized[field] = "[REDACTED]"
        
        return anonymized
    
    async def generate_compliance_report(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "full"
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report for EU AI Act."""
        
        # Query audit logs for period
        audit_query = select(AuditLog).where(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date,
                AuditLog.compliance_relevant == True
            )
        ).order_by(AuditLog.timestamp)
        
        audit_result = await db.execute(audit_query)
        audit_logs = audit_result.scalars().all()
        
        # Query session logs for period  
        session_query = select(SessionLog).where(
            and_(
                SessionLog.timestamp >= start_date,
                SessionLog.timestamp <= end_date
            )
        )
        
        session_result = await db.execute(session_query)
        session_logs = session_result.scalars().all()
        
        # Compile statistics
        report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "report_type": report_type,
                "total_audit_events": len(audit_logs),
                "total_ai_decisions": len(session_logs)
            },
            "ai_system_usage": {
                "total_tool_calls": len(session_logs),
                "allowed_calls": len([l for l in session_logs if l.policy_decision == "allow"]),
                "denied_calls": len([l for l in session_logs if l.policy_decision == "deny"]),
                "approval_required": len([l for l in session_logs if l.policy_decision == "approve"]),
                "unique_agents": len(set(l.agent_id for l in session_logs if l.agent_id)),
                "unique_users": len(set(l.user_id for l in session_logs if l.user_id))
            },
            "risk_assessment": {
                "high_risk_events": len([l for l in audit_logs if l.risk_level in ["high", "critical"]]),
                "policy_violations": len([l for l in session_logs if l.policy_decision == "deny"]),
                "data_exports": len([l for l in audit_logs if l.event_type == "data_export"]),
                "unauthorized_access_attempts": len([l for l in audit_logs if l.outcome == "failure" and l.event_type == "session_access"])
            },
            "data_governance": {
                "archived_sessions": len([l for l in session_logs if l.is_archived]),
                "retention_compliance": await self._check_retention_compliance(db),
                "data_integrity_status": await self._verify_audit_chain_integrity(db, start_date, end_date)
            },
            "human_oversight": {
                "manual_interventions": len([l for l in audit_logs if l.actor_type == "user" and l.event_type == "policy_change"]),
                "approval_workflows": len([l for l in session_logs if l.requires_approval])
            }
        }
        
        if report_type == "detailed":
            report["detailed_events"] = [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "event_type": log.event_type,
                    "action": log.action,
                    "outcome": log.outcome,
                    "risk_level": log.risk_level,
                    "actor": log.actor_id,
                    "description": log.description
                }
                for log in audit_logs
            ]
        
        return report
    
    async def _check_retention_compliance(self, db: AsyncSession) -> Dict[str, Any]:
        """Check compliance with data retention policies."""
        now = datetime.utcnow()
        
        # Check for logs that should be deleted
        overdue_query = select(SessionLog).where(
            and_(
                SessionLog.retention_until.isnot(None),
                SessionLog.retention_until < now
            )
        )
        
        result = await db.execute(overdue_query)
        overdue_logs = result.scalars().all()
        
        return {
            "overdue_deletions": len(overdue_logs),
            "next_review_date": (now + timedelta(days=30)).isoformat(),
            "retention_policy_compliant": len(overdue_logs) == 0
        }
    
    async def _verify_audit_chain_integrity(
        self, 
        db: AsyncSession, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Verify the integrity of the audit log chain."""
        
        query = select(AuditLog).where(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date
            )
        ).order_by(AuditLog.timestamp)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        integrity_violations = 0
        verified_entries = 0
        
        for i, log in enumerate(logs):
            if i > 0:
                previous_log = logs[i-1]
                if log.previous_log_hash != previous_log.log_hash:
                    integrity_violations += 1
            verified_entries += 1
        
        return {
            "total_entries_verified": verified_entries,
            "integrity_violations": integrity_violations,
            "chain_intact": integrity_violations == 0,
            "verification_timestamp": datetime.utcnow().isoformat()
        }

# Global compliance service instance
compliance_service = ComplianceService() 