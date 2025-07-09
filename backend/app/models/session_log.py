from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, Index
from datetime import datetime
import uuid
import structlog

from app.core.database import Base

logger = structlog.get_logger()

class SessionLog(Base):
    """Model for storing session logs with tool call enforcement records."""
    
    __tablename__ = "session_logs"
    
    # Primary fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Tool call details
    tool_name = Column(String(255), nullable=False)
    tool_args = Column(JSON, nullable=False)
    tool_result = Column(JSON, nullable=True)
    
    # Policy enforcement
    policy_version = Column(String(100), nullable=False)
    policy_decision = Column(String(50), nullable=False)  # allow, deny, approve
    policy_rule = Column(String(255), nullable=True)  # Which rule matched
    
    # Security and traceability
    log_signature = Column(String(512), nullable=False)  # HMAC signature
    agent_id = Column(String(255), nullable=True)  # Optional agent identifier
    user_id = Column(String(255), nullable=True)   # Optional user identifier
    
    # Execution details
    execution_status = Column(String(50), nullable=True)  # success, error, pending
    execution_duration_ms = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Approval workflow (for future use)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Additional metadata
    metadata_fields = Column(JSON, nullable=True)

    # Archive and retention fields for compliance
    is_archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime, nullable=True)
    archived_by = Column(String(255), nullable=True)
    retention_until = Column(DateTime, nullable=True)  # When this can be deleted
    data_category = Column(String(100), nullable=True)  # For compliance classification
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_tool_name', 'tool_name'),
        Index('idx_policy_decision', 'policy_decision'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_archived', 'is_archived'),
        Index('idx_retention', 'retention_until'),
    )
    
    def __repr__(self):
        return f"<SessionLog(session_id='{self.session_id}', tool_name='{self.tool_name}', decision='{self.policy_decision}')>" 