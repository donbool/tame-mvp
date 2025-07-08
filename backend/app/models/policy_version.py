from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base

class PolicyVersion(Base):
    """Model for tracking policy versions and changes."""
    
    __tablename__ = "policy_versions"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Policy content
    policy_content = Column(Text, nullable=False)  # YAML content as text
    policy_hash = Column(String(64), nullable=False)  # SHA-256 hash
    
    # Metadata
    description = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Validation
    is_valid = Column(Boolean, default=True, nullable=False)
    validation_errors = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<PolicyVersion(version='{self.version}', active={self.is_active})>" 