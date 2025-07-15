"""
Decorators for easy TameSDK integration.
"""

import asyncio
import functools
import inspect
import logging
from typing import Callable, Any, Dict, Optional

from .client import Client, AsyncClient
from .exceptions import PolicyViolationException, ApprovalRequiredException


logger = logging.getLogger(__name__)


def enforce_policy(
    tool_name: Optional[str] = None,
    client: Optional[Client] = None,
    raise_on_deny: Optional[bool] = None,
    raise_on_approve: Optional[bool] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator to enforce policy on function calls.
    
    Example:
        @enforce_policy
        def read_file(path: str) -> str:
            with open(path) as f:
                return f.read()
    """
    
    def decorator(func: Callable) -> Callable:
        func_name = tool_name or func.__name__
        is_async = asyncio.iscoroutinefunction(func)
        
        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Extract tool arguments
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                tool_args = dict(bound_args.arguments)
                
                # Use provided client or create a new one
                if client:
                    tame_client = client
                    should_close = False
                else:
                    from .client import AsyncClient
                    tame_client = AsyncClient()
                    should_close = True
                
                try:
                    # Enforce policy
                    decision = await tame_client.enforce(
                        tool_name=func_name,
                        tool_args=tool_args,
                        metadata=metadata,
                        raise_on_deny=raise_on_deny,
                        raise_on_approve=raise_on_approve
                    )
                    
                    if decision.is_allowed:
                        # Execute the original function
                        result = await func(*args, **kwargs)
                        
                        # Log the result
                        try:
                            await tame_client.update_result(
                                decision.session_id,
                                decision.log_id,
                                {"status": "success", "result": result}
                            )
                        except Exception as e:
                            logger.warning(f"Failed to log result: {e}")
                        
                        return result
                    else:
                        # This shouldn't happen if raise_on_deny/approve is True
                        raise PolicyViolationException(decision)
                
                finally:
                    if should_close:
                        await tame_client.close()
            
            return async_wrapper
        
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Extract tool arguments
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                tool_args = dict(bound_args.arguments)
                
                # Use provided client or create a new one
                if client:
                    tame_client = client
                    should_close = False
                else:
                    tame_client = Client()
                    should_close = True
                
                try:
                    # Enforce policy
                    decision = tame_client.enforce(
                        tool_name=func_name,
                        tool_args=tool_args,
                        metadata=metadata,
                        raise_on_deny=raise_on_deny,
                        raise_on_approve=raise_on_approve
                    )
                    
                    if decision.is_allowed:
                        # Execute the original function
                        result = func(*args, **kwargs)
                        
                        # Log the result
                        try:
                            tame_client.update_result(
                                decision.session_id,
                                decision.log_id,
                                {"status": "success", "result": result}
                            )
                        except Exception as e:
                            logger.warning(f"Failed to log result: {e}")
                        
                        return result
                    else:
                        # This shouldn't happen if raise_on_deny/approve is True
                        raise PolicyViolationException(decision)
                
                finally:
                    if should_close:
                        tame_client.close()
            
            return sync_wrapper
    
    return decorator


def with_approval(
    tool_name: Optional[str] = None,
    client: Optional[Client] = None,
    approval_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator to require approval for function calls.
    
    Example:
        @with_approval(approval_message="This operation modifies system files")
        def write_system_file(path: str, content: str) -> None:
            with open(path, 'w') as f:
                f.write(content)
    """
    
    # Add approval message to metadata
    meta = metadata or {}
    if approval_message:
        meta["approval_message"] = approval_message
    
    return enforce_policy(
        tool_name=tool_name,
        client=client,
        raise_on_deny=True,
        raise_on_approve=True,
        metadata=meta
    )


def log_action(
    tool_name: Optional[str] = None,
    client: Optional[Client] = None,
    level: str = "INFO",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator to log function calls without policy enforcement.
    
    Example:
        @log_action(level="DEBUG")
        def helper_function(data: dict) -> dict:
            return transform_data(data)
    """
    
    def decorator(func: Callable) -> Callable:
        func_name = tool_name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Just execute the function and log it
            logger.log(getattr(logging, level, logging.INFO), f"Executing {func_name}")
            result = func(*args, **kwargs)
            logger.log(getattr(logging, level, logging.INFO), f"Completed {func_name}")
            return result
        
        return wrapper
    
    return decorator