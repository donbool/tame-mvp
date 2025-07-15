"""
Utility functions for TameSDK.
"""

import re
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from .exceptions import ValidationException, TameSDKException


def validate_tool_call(tool_name: str, tool_args: Dict[str, Any]) -> None:
    """
    Validate a tool call for basic requirements.
    
    Args:
        tool_name: Name of the tool
        tool_args: Arguments for the tool
        
    Raises:
        ValidationException: If validation fails
    """
    if not tool_name or not isinstance(tool_name, str):
        raise ValidationException("Tool name must be a non-empty string")
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', tool_name):
        raise ValidationException(
            "Tool name must start with a letter and contain only letters, numbers, and underscores"
        )
    
    if not isinstance(tool_args, dict):
        raise ValidationException("Tool arguments must be a dictionary")
    
    # Check for potentially dangerous argument names
    dangerous_keys = ['__', 'eval', 'exec', 'compile']
    for key in tool_args.keys():
        if any(dangerous in str(key).lower() for dangerous in dangerous_keys):
            raise ValidationException(f"Potentially dangerous argument name: {key}")
    
    # Validate that arguments are JSON serializable
    try:
        json.dumps(tool_args, default=str)
    except (TypeError, ValueError) as e:
        raise ValidationException(f"Tool arguments must be JSON serializable: {e}")


def format_policy_error(error: Union[Exception, str], include_traceback: bool = False) -> str:
    """
    Format a policy error for user-friendly display.
    
    Args:
        error: The error to format
        include_traceback: Whether to include traceback information
        
    Returns:
        Formatted error string
    """
    if isinstance(error, Exception):
        error_type = type(error).__name__
        error_msg = str(error)
        
        if hasattr(error, 'decision'):
            # Policy-related error
            decision = error.decision
            formatted = f"""
Policy Violation: {error_msg}

Details:
  Tool: {decision.tool_name}
  Rule: {decision.rule_name or 'Unknown'}
  Reason: {decision.reason}
  Policy Version: {decision.policy_version}
  Session: {decision.session_id}
  Timestamp: {decision.timestamp.isoformat()}
"""
            if decision.tool_args:
                formatted += f"  Arguments: {json.dumps(decision.tool_args, indent=2)}\n"
            
            return formatted.strip()
        else:
            # Generic error
            formatted = f"{error_type}: {error_msg}"
            
            if include_traceback:
                import traceback
                formatted += f"\n\nTraceback:\n{traceback.format_exc()}"
            
            return formatted
    else:
        return str(error)


def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize metadata to ensure it's safe for logging.
    
    Args:
        metadata: Raw metadata dictionary
        
    Returns:
        Sanitized metadata dictionary
    """
    if not isinstance(metadata, dict):
        return {}
    
    sanitized = {}
    sensitive_keys = [
        'password', 'token', 'key', 'secret', 'auth', 'credential',
        'private', 'confidential', 'sensitive'
    ]
    
    for key, value in metadata.items():
        # Check if key might contain sensitive information
        key_lower = str(key).lower()
        is_sensitive = any(sensitive in key_lower for sensitive in sensitive_keys)
        
        if is_sensitive:
            # Mask sensitive values
            if isinstance(value, str) and len(value) > 4:
                sanitized[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
            else:
                sanitized[key] = '***'
        else:
            # Keep non-sensitive values, but ensure they're serializable
            try:
                json.dumps(value, default=str)
                sanitized[key] = value
            except (TypeError, ValueError):
                sanitized[key] = str(value)
    
    return sanitized


def extract_tool_signature(func) -> Dict[str, Any]:
    """
    Extract tool signature information from a function.
    
    Args:
        func: Function to analyze
        
    Returns:
        Dictionary with signature information
    """
    import inspect
    
    try:
        sig = inspect.signature(func)
        
        parameters = {}
        for name, param in sig.parameters.items():
            param_info = {
                'name': name,
                'kind': param.kind.name,
                'required': param.default == inspect.Parameter.empty
            }
            
            if param.annotation != inspect.Parameter.empty:
                param_info['type'] = str(param.annotation)
            
            if param.default != inspect.Parameter.empty:
                param_info['default'] = param.default
            
            parameters[name] = param_info
        
        return {
            'name': func.__name__,
            'module': func.__module__,
            'doc': inspect.getdoc(func),
            'parameters': parameters,
            'return_annotation': str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else None
        }
    except Exception as e:
        return {
            'name': getattr(func, '__name__', 'unknown'),
            'error': f"Could not extract signature: {e}"
        }


def create_session_summary(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a summary of session activity.
    
    Args:
        logs: List of session log entries
        
    Returns:
        Session summary dictionary
    """
    if not logs:
        return {
            'total_actions': 0,
            'allowed_actions': 0,
            'denied_actions': 0,
            'approval_requests': 0,
            'unique_tools': [],
            'session_duration': None,
            'error_rate': 0.0
        }
    
    total_actions = len(logs)
    allowed_actions = 0
    denied_actions = 0
    approval_requests = 0
    errors = 0
    tools_used = set()
    
    start_time = None
    end_time = None
    
    for log in logs:
        # Count by decision type
        decision = log.get('decision', {})
        action = decision.get('action')
        
        if action == 'allow':
            allowed_actions += 1
        elif action == 'deny':
            denied_actions += 1
        elif action == 'approve':
            approval_requests += 1
        
        # Track tools used
        tool_name = log.get('tool_name')
        if tool_name:
            tools_used.add(tool_name)
        
        # Track errors
        if log.get('error'):
            errors += 1
        
        # Track time range
        timestamp_str = log.get('timestamp')
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if start_time is None or timestamp < start_time:
                    start_time = timestamp
                if end_time is None or timestamp > end_time:
                    end_time = timestamp
            except ValueError:
                pass
    
    # Calculate session duration
    session_duration = None
    if start_time and end_time:
        duration = end_time - start_time
        session_duration = duration.total_seconds()
    
    # Calculate error rate
    error_rate = (errors / total_actions) if total_actions > 0 else 0.0
    
    return {
        'total_actions': total_actions,
        'allowed_actions': allowed_actions,
        'denied_actions': denied_actions,
        'approval_requests': approval_requests,
        'unique_tools': sorted(list(tools_used)),
        'session_duration': session_duration,
        'error_rate': error_rate,
        'start_time': start_time.isoformat() if start_time else None,
        'end_time': end_time.isoformat() if end_time else None
    }


def generate_policy_test_cases(tool_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate test cases for policy validation.
    
    Args:
        tool_configs: List of tool configuration dictionaries
        
    Returns:
        List of test case dictionaries
    """
    test_cases = []
    
    for tool_config in tool_configs:
        tool_name = tool_config.get('name')
        if not tool_name:
            continue
        
        # Generate basic test case
        test_cases.append({
            'name': f"test_{tool_name}_basic",
            'tool_name': tool_name,
            'tool_args': tool_config.get('sample_args', {}),
            'expected_action': 'allow',
            'description': f"Basic test for {tool_name}"
        })
        
        # Generate edge cases based on tool configuration
        sensitive_args = tool_config.get('sensitive_args', [])
        for arg_name in sensitive_args:
            test_cases.append({
                'name': f"test_{tool_name}_sensitive_{arg_name}",
                'tool_name': tool_name,
                'tool_args': {arg_name: "/etc/passwd"},
                'expected_action': 'deny',
                'description': f"Test {tool_name} with sensitive {arg_name}"
            })
        
        # Generate approval test cases
        if tool_config.get('requires_approval'):
            test_cases.append({
                'name': f"test_{tool_name}_approval",
                'tool_name': tool_name,
                'tool_args': tool_config.get('approval_args', {}),
                'expected_action': 'approve',
                'description': f"Test {tool_name} requiring approval"
            })
    
    return test_cases


def mask_sensitive_data(data: Any, mask_char: str = '*') -> Any:
    """
    Recursively mask sensitive data in nested structures.
    
    Args:
        data: Data structure to mask
        mask_char: Character to use for masking
        
    Returns:
        Data structure with sensitive values masked
    """
    sensitive_patterns = [
        r'password', r'token', r'key', r'secret', r'auth',
        r'credential', r'private', r'confidential'
    ]
    
    def is_sensitive_key(key: str) -> bool:
        key_lower = str(key).lower()
        return any(re.search(pattern, key_lower) for pattern in sensitive_patterns)
    
    def mask_value(value: str) -> str:
        if len(value) <= 4:
            return mask_char * len(value)
        return value[:2] + mask_char * (len(value) - 4) + value[-2:]
    
    def mask_recursive(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                key: mask_value(str(value)) if is_sensitive_key(key) and isinstance(value, (str, int, float))
                else mask_recursive(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [mask_recursive(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(mask_recursive(item) for item in obj)
        else:
            return obj
    
    return mask_recursive(data)


def validate_api_response(response_data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that an API response contains required fields.
    
    Args:
        response_data: Response data to validate
        required_fields: List of required field names
        
    Raises:
        ValidationException: If validation fails
    """
    if not isinstance(response_data, dict):
        raise ValidationException("API response must be a dictionary")
    
    missing_fields = []
    for field in required_fields:
        if field not in response_data:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationException(f"API response missing required fields: {missing_fields}")


def build_tool_registry(functions: List[callable]) -> Dict[str, Dict[str, Any]]:
    """
    Build a registry of tools from a list of functions.
    
    Args:
        functions: List of functions to register as tools
        
    Returns:
        Dictionary mapping tool names to tool information
    """
    registry = {}
    
    for func in functions:
        tool_info = extract_tool_signature(func)
        tool_name = tool_info['name']
        
        registry[tool_name] = {
            'function': func,
            'signature': tool_info,
            'metadata': {
                'registered_at': datetime.now().isoformat(),
                'module': tool_info.get('module'),
                'doc': tool_info.get('doc')
            }
        }
    
    return registry