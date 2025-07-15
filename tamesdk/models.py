"""
Data models and types for TameSDK.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum


class ActionType(Enum):
    """Possible policy enforcement actions."""
    ALLOW = "allow"
    DENY = "deny" 
    APPROVE = "approve"


class LogLevel(Enum):
    """Log levels for action logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class EnforcementDecision:
    """Result of a policy enforcement decision."""
    session_id: str
    action: ActionType
    rule_name: Optional[str]
    reason: str
    policy_version: str
    log_id: str
    timestamp: datetime
    tool_name: str
    tool_args: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_allowed(self) -> bool:
        """Check if the action is allowed."""
        return self.action == ActionType.ALLOW
    
    @property
    def is_denied(self) -> bool:
        """Check if the action is denied."""
        return self.action == ActionType.DENY
        
    @property
    def requires_approval(self) -> bool:
        """Check if the action requires approval."""
        return self.action == ActionType.APPROVE


@dataclass
class PolicyInfo:
    """Information about the current policy."""
    version: str
    description: Optional[str]
    rules_count: int
    last_updated: datetime
    hash: str
    active: bool = True


@dataclass
class SessionLog:
    """A single log entry for a session."""
    log_id: str
    session_id: str
    timestamp: datetime
    tool_name: str
    tool_args: Dict[str, Any]
    decision: EnforcementDecision
    execution_result: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None
    

@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionInfo:
    """Information about a session."""
    session_id: str
    agent_id: Optional[str]
    user_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    total_actions: int
    allowed_actions: int
    denied_actions: int
    pending_approvals: int


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    policy_version: Optional[str] = None
    enabled: bool = True
    rate_limit: Optional[int] = None
    allowed_tools: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalRequest:
    """A request for manual approval."""
    approval_id: str
    session_id: str
    tool_name: str
    tool_args: Dict[str, Any]
    reason: str
    requested_at: datetime
    status: str = "pending"  # pending, approved, denied
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_comment: Optional[str] = None