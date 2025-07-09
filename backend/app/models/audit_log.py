from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, Index
from datetime import datetime
import uuid
import structlog

from app.core.database import Base

logger = structlog.get_logger()

class AuditLog(Base):
    """Model for storing comprehensive audit logs for EU AI Act compliance."""
    
    __tablename__ = "audit_logs"
    
    # Primary fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Event identification
    event_type = Column(String(100), nullable=False)  # policy_change, session_access, data_export, etc.
    event_category = Column(String(50), nullable=False)  # system, user, policy, data
    event_source = Column(String(100), nullable=False)  # api, ui, cli, system
    
    # Actor information
    actor_type = Column(String(50), nullable=False)  # user, admin, system, agent
    actor_id = Column(String(255), nullable=True)
    actor_ip = Column(String(45), nullable=True)  # IPv4/IPv6
    
    # Target information
    target_type = Column(String(100), nullable=True)  # session, policy, user, etc.
    target_id = Column(String(255), nullable=True)
    
    # Event details
    action = Column(String(100), nullable=False)  # create, read, update, delete, export, archive
    description = Column(Text, nullable=False)
    outcome = Column(String(50), nullable=False)  # success, failure, partial
    
    # Risk and compliance
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    compliance_relevant = Column(Boolean, default=True, nullable=False)
    retention_category = Column(String(50), nullable=False)  # standard, extended, permanent
    
    # Context and metadata
    request_data = Column(JSON, nullable=True)  # Input parameters (anonymized)
    response_data = Column(JSON, nullable=True)  # Output summary (anonymized)
    system_context = Column(JSON, nullable=True)  # System state, versions, etc.
    user_context = Column(JSON, nullable=True)  # User role, permissions, etc.
    
    # Integrity and security
    log_hash = Column(String(64), nullable=False)  # SHA-256 of log content
    previous_log_hash = Column(String(64), nullable=True)  # Chain integrity
    digital_signature = Column(Text, nullable=True)  # For high-risk events
    
    # EU AI Act specific fields
    ai_system_component = Column(String(100), nullable=True)  # Which AI component
    data_subject_category = Column(String(100), nullable=True)  # personal, sensitive, etc.
    legal_basis = Column(String(100), nullable=True)  # GDPR/AI Act legal basis
    impact_assessment_id = Column(String(100), nullable=True)  # Reference to impact assessment
    
    # Performance indexes
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_event_type', 'event_type'),
        Index('idx_audit_actor', 'actor_type', 'actor_id'),
        Index('idx_audit_target', 'target_type', 'target_id'),
        Index('idx_audit_compliance', 'compliance_relevant'),
        Index('idx_audit_risk', 'risk_level'),
        Index('idx_audit_chain', 'previous_log_hash'),
    )
    
    def __repr__(self):
        return f"<AuditLog(event_type='{self.event_type}', actor='{self.actor_id}', outcome='{self.outcome}')>" 