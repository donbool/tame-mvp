"""
TameSDK - Runtime Control for AI Agents

A comprehensive Python SDK for enforcing policies, logging actions, and controlling
AI agent behavior in real-time.

Usage:
    import tamesdk

    # Simple usage with decorator
    @tamesdk.enforce_policy
    def my_tool(path: str) -> str:
        return f"Reading {path}"

    # Advanced usage with client
    with tamesdk.Client() as client:
        result = client.execute_tool("read_file", {"path": "/tmp/file.txt"})

    # Async support
    async with tamesdk.AsyncClient() as client:
        result = await client.execute_tool("write_file", {"path": "/tmp/out.txt", "content": "Hello"})
"""

from .client import Client, AsyncClient
from .decorators import enforce_policy, with_approval, log_action
from .exceptions import (
    TameSDKException,
    PolicyViolationException, 
    ApprovalRequiredException,
    ConfigurationException
)
from .models import EnforcementDecision, PolicyInfo, SessionLog
from .config import configure, get_config
from .utils import validate_tool_call, format_policy_error

__version__ = "1.0.0"
__author__ = "Tame Team"
__email__ = "team@tame.dev"

__all__ = [
    # Core client classes
    "Client",
    "AsyncClient",
    
    # Decorators for easy integration
    "enforce_policy", 
    "with_approval",
    "log_action",
    
    # Exceptions
    "TameSDKException",
    "PolicyViolationException",
    "ApprovalRequiredException", 
    "ConfigurationException",
    
    # Data models
    "EnforcementDecision",
    "PolicyInfo", 
    "SessionLog",
    
    # Configuration
    "configure",
    "get_config",
    
    # Utilities
    "validate_tool_call",
    "format_policy_error",
]