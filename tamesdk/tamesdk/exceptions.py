"""
Exception classes for TameSDK.
"""

from typing import Optional, Dict, Any


class TameSDKException(Exception):
    """Base exception for all TameSDK errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PolicyViolationException(TameSDKException):
    """Raised when a tool call is denied by policy."""
    
    def __init__(self, decision):
        self.decision = decision
        super().__init__(
            f"Tool call '{decision.tool_name}' denied by policy: {decision.reason}",
            details={
                "tool_name": decision.tool_name,
                "tool_args": decision.tool_args,
                "rule_name": decision.rule_name,
                "policy_version": decision.policy_version,
                "session_id": decision.session_id,
                "log_id": decision.log_id
            }
        )


class ApprovalRequiredException(TameSDKException):
    """Raised when a tool call requires manual approval."""
    
    def __init__(self, decision):
        self.decision = decision
        super().__init__(
            f"Tool call '{decision.tool_name}' requires approval: {decision.reason}",
            details={
                "tool_name": decision.tool_name,
                "tool_args": decision.tool_args,
                "rule_name": decision.rule_name,
                "policy_version": decision.policy_version,
                "session_id": decision.session_id,
                "log_id": decision.log_id
            }
        )


class ConfigurationException(TameSDKException):
    """Raised when there's a configuration error."""
    pass


class ConnectionException(TameSDKException):
    """Raised when unable to connect to Tame API."""
    pass


class AuthenticationException(TameSDKException):
    """Raised when authentication fails."""
    pass