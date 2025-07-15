"""
Configuration management for TameSDK.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TameConfig:
    """Configuration settings for TameSDK."""
    
    # API connection settings
    api_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    timeout: float = 30.0
    
    # Session settings
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Behavior settings
    raise_on_deny: bool = True
    raise_on_approve: bool = True
    bypass_mode: bool = False
    
    # Advanced settings
    extra_headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# Global configuration instance
_global_config: Optional[TameConfig] = None


def configure(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    session_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    user_id: Optional[str] = None,
    timeout: Optional[float] = None,
    raise_on_deny: Optional[bool] = None,
    raise_on_approve: Optional[bool] = None,
    bypass_mode: Optional[bool] = None,
    **kwargs
) -> TameConfig:
    """Configure global TameSDK settings."""
    global _global_config
    
    if _global_config is None:
        _global_config = TameConfig()
    
    # Update configuration with provided values
    if api_url is not None:
        _global_config.api_url = api_url
    if api_key is not None:
        _global_config.api_key = api_key
    if session_id is not None:
        _global_config.session_id = session_id
    if agent_id is not None:
        _global_config.agent_id = agent_id
    if user_id is not None:
        _global_config.user_id = user_id
    if timeout is not None:
        _global_config.timeout = timeout
    if raise_on_deny is not None:
        _global_config.raise_on_deny = raise_on_deny
    if raise_on_approve is not None:
        _global_config.raise_on_approve = raise_on_approve
    if bypass_mode is not None:
        _global_config.bypass_mode = bypass_mode
    
    return _global_config


def get_config() -> TameConfig:
    """Get the current global configuration."""
    global _global_config
    
    if _global_config is None:
        # Initialize with defaults and environment variables
        _global_config = TameConfig()
        
        # Load from environment variables
        if os.getenv('TAME_API_URL'):
            _global_config.api_url = os.getenv('TAME_API_URL')
        if os.getenv('TAME_API_KEY'):
            _global_config.api_key = os.getenv('TAME_API_KEY')
        if os.getenv('TAME_SESSION_ID'):
            _global_config.session_id = os.getenv('TAME_SESSION_ID')
        if os.getenv('TAME_AGENT_ID'):
            _global_config.agent_id = os.getenv('TAME_AGENT_ID')
        if os.getenv('TAME_USER_ID'):
            _global_config.user_id = os.getenv('TAME_USER_ID')
        if os.getenv('TAME_BYPASS_MODE'):
            _global_config.bypass_mode = os.getenv('TAME_BYPASS_MODE').lower() in ['true', '1', 'yes']
    
    return _global_config