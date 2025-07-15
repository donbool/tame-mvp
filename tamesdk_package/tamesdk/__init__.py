"""
TameSDK - Runtime Control for AI Agents

Simple, powerful SDK for enforcing policies and logging agent actions.
"""

# Import core functionality
from .client import Client, AsyncClient
from .decorators import enforce_policy, with_approval, log_action
from .exceptions import (
    TameSDKException,
    PolicyViolationException, 
    ApprovalRequiredException,
    ConfigurationException
)
from .models import EnforcementDecision, PolicyInfo
from .config import configure, get_config

__version__ = "1.0.0"

# Simple API exports
__all__ = [
    "Client",
    "AsyncClient", 
    "enforce_policy",
    "with_approval",
    "log_action",
    "TameSDKException",
    "PolicyViolationException",
    "ApprovalRequiredException", 
    "ConfigurationException",
    "EnforcementDecision",
    "PolicyInfo",
    "configure",
    "get_config",
]

# Convenience function for quick setup
def setup(api_url="http://localhost:8000", **kwargs):
    """Quick setup for TameSDK."""
    return configure(api_url=api_url, **kwargs)