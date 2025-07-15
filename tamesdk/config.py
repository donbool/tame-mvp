"""
Configuration management for TameSDK.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml


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
    auto_retry: bool = True
    max_retries: int = 3
    raise_on_deny: bool = True
    raise_on_approve: bool = True
    
    # Logging settings
    enable_logging: bool = True
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Development settings
    bypass_mode: bool = False
    mock_responses: bool = False
    
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
    """
    Configure global TameSDK settings.
    
    Args:
        api_url: Base URL of the Tame API
        api_key: API key for authentication
        session_id: Default session ID
        agent_id: Default agent ID
        user_id: Default user ID
        timeout: Request timeout in seconds
        raise_on_deny: Whether to raise exception on policy denial
        raise_on_approve: Whether to raise exception when approval required
        bypass_mode: Whether to bypass policy enforcement (dev mode)
        **kwargs: Additional configuration options
        
    Returns:
        Updated configuration object
    """
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
    
    # Update any additional settings
    for key, value in kwargs.items():
        if hasattr(_global_config, key):
            setattr(_global_config, key, value)
    
    return _global_config


def get_config() -> TameConfig:
    """
    Get the current global configuration.
    
    Returns:
        Current configuration object
    """
    global _global_config
    
    if _global_config is None:
        # Initialize with defaults and environment variables
        _global_config = load_config()
    
    return _global_config


def load_config(config_file: Optional[str] = None) -> TameConfig:
    """
    Load configuration from file and environment variables.
    
    Args:
        config_file: Path to configuration file (JSON or YAML)
        
    Returns:
        Loaded configuration object
    """
    config = TameConfig()
    
    # Load from file if specified
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                with open(config_path) as f:
                    file_config = yaml.safe_load(f)
            else:
                with open(config_path) as f:
                    file_config = json.load(f)
            
            # Update config with file values
            for key, value in file_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    # Override with environment variables
    env_mappings = {
        'TAME_API_URL': 'api_url',
        'TAME_API_KEY': 'api_key', 
        'TAME_SESSION_ID': 'session_id',
        'TAME_AGENT_ID': 'agent_id',
        'TAME_USER_ID': 'user_id',
        'TAME_TIMEOUT': 'timeout',
        'TAME_BYPASS_MODE': 'bypass_mode',
        'TAME_RAISE_ON_DENY': 'raise_on_deny',
        'TAME_RAISE_ON_APPROVE': 'raise_on_approve',
        'TAME_LOG_LEVEL': 'log_level',
        'TAME_LOG_FILE': 'log_file',
    }
    
    for env_var, config_attr in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            # Convert string values to appropriate types
            if config_attr in ['timeout']:
                env_value = float(env_value)
            elif config_attr in ['bypass_mode', 'raise_on_deny', 'raise_on_approve']:
                env_value = env_value.lower() in ['true', '1', 'yes', 'on']
            
            setattr(config, config_attr, env_value)
    
    return config


def save_config(config: TameConfig, config_file: str) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration object to save
        config_file: Path to save configuration file
    """
    config_path = Path(config_file)
    config_dict = {
        field.name: getattr(config, field.name)
        for field in config.__dataclass_fields__.values()
    }
    
    if config_path.suffix.lower() in ['.yml', '.yaml']:
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    else:
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _global_config
    _global_config = None