"""
Data models for TameSDK.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class ActionType(Enum):
    """Possible policy enforcement actions."""
    ALLOW = "allow"
    DENY = "deny" 
    APPROVE = "approve"


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
class ToolResult:
    """Result of a tool execution."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)