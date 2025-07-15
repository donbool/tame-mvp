"""
Decorators for easy TameSDK integration.
"""

import asyncio
import functools
import inspect
import logging
from typing import Callable, Any, Dict, Optional, Union

from .client import Client, AsyncClient
from .config import get_config
from .exceptions import PolicyViolationException, ApprovalRequiredException


logger = logging.getLogger(__name__)


def enforce_policy(
    tool_name: Optional[str] = None,
    client: Optional[Union[Client, AsyncClient]] = None,
    raise_on_deny: Optional[bool] = None,
    raise_on_approve: Optional[bool] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_args: Optional[Callable] = None
):
    """
    Decorator to enforce policy on function calls.
    
    Args:
        tool_name: Name of the tool (defaults to function name)
        client: TameSDK client to use (creates one if not provided)
        raise_on_deny: Whether to raise exception on policy denial
        raise_on_approve: Whether to raise exception when approval required
        metadata: Additional metadata to include
        extract_args: Function to extract tool args from function arguments
        
    Example:
        @enforce_policy
        def read_file(path: str) -> str:
            with open(path) as f:
                return f.read()
        
        @enforce_policy(tool_name="custom_tool", metadata={"sensitive": True})
        def sensitive_operation(data: dict) -> dict:
            return process_data(data)
    """
    
    def decorator(func: Callable) -> Callable:
        func_name = tool_name or func.__name__
        is_async = asyncio.iscoroutinefunction(func)
        
        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Extract tool arguments
                if extract_args:
                    tool_args = extract_args(*args, **kwargs)
                else:
                    # Use function signature to map arguments
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    tool_args = dict(bound_args.arguments)
                
                # Use provided client or create a new one
                if client:
                    tame_client = client
                    should_close = False
                else:
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
                if extract_args:
                    tool_args = extract_args(*args, **kwargs)
                else:
                    # Use function signature to map arguments
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
    client: Optional[Union[Client, AsyncClient]] = None,
    approval_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator to require approval for function calls.
    
    This is a convenience decorator that sets raise_on_approve=True.
    
    Args:
        tool_name: Name of the tool (defaults to function name)
        client: TameSDK client to use
        approval_message: Custom message for approval request
        metadata: Additional metadata to include
        
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
    client: Optional[Union[Client, AsyncClient]] = None,
    level: str = "INFO",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator to log function calls without policy enforcement.
    
    This decorator only logs the action and doesn't enforce policies.
    
    Args:
        tool_name: Name of the tool (defaults to function name)
        client: TameSDK client to use
        level: Log level for the action
        metadata: Additional metadata to include
        
    Example:
        @log_action(level="DEBUG")
        def helper_function(data: dict) -> dict:
            return transform_data(data)
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
                    tame_client = AsyncClient()
                    should_close = True
                
                try:
                    # Force bypass mode for logging-only
                    original_bypass = tame_client.config.bypass_mode
                    tame_client.config.bypass_mode = True
                    
                    # "Enforce" (which will bypass and just log)
                    decision = await tame_client.enforce(
                        tool_name=func_name,
                        tool_args=tool_args,
                        metadata={**(metadata or {}), "log_level": level, "log_only": True},
                        raise_on_deny=False,
                        raise_on_approve=False
                    )
                    
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
                
                finally:
                    if should_close:
                        await tame_client.close()
                    else:
                        # Restore original bypass mode
                        tame_client.config.bypass_mode = original_bypass
            
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
                    # Force bypass mode for logging-only
                    original_bypass = tame_client.config.bypass_mode
                    tame_client.config.bypass_mode = True
                    
                    # "Enforce" (which will bypass and just log)
                    decision = tame_client.enforce(
                        tool_name=func_name,
                        tool_args=tool_args,
                        metadata={**(metadata or {}), "log_level": level, "log_only": True},
                        raise_on_deny=False,
                        raise_on_approve=False
                    )
                    
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
                
                finally:
                    if should_close:
                        tame_client.close()
                    else:
                        # Restore original bypass mode
                        tame_client.config.bypass_mode = original_bypass
            
            return sync_wrapper
    
    return decorator


class PolicyEnforcer:
    """
    Context manager for policy enforcement with fine-grained control.
    
    Example:
        with PolicyEnforcer() as enforcer:
            enforcer.check("read_file", {"path": "/tmp/file.txt"})
            result = read_file("/tmp/file.txt")
            enforcer.log_result(result)
    """
    
    def __init__(
        self,
        client: Optional[Union[Client, AsyncClient]] = None,
        session_id: Optional[str] = None
    ):
        self.client = client
        self.session_id = session_id
        self._decisions = []
        self._should_close = False
    
    def __enter__(self):
        if self.client is None:
            self.client = Client(session_id=self.session_id)
            self._should_close = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._should_close and self.client:
            self.client.close()
    
    async def __aenter__(self):
        if self.client is None:
            self.client = AsyncClient(session_id=self.session_id)
            self._should_close = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._should_close and self.client:
            await self.client.close()
    
    def check(self, tool_name: str, tool_args: Dict[str, Any], **kwargs):
        """Check policy for a tool call."""
        if isinstance(self.client, AsyncClient):
            raise RuntimeError("Use async_check() with AsyncClient")
        
        decision = self.client.enforce(tool_name, tool_args, **kwargs)
        self._decisions.append(decision)
        return decision
    
    async def async_check(self, tool_name: str, tool_args: Dict[str, Any], **kwargs):
        """Async version of check method."""
        if not isinstance(self.client, AsyncClient):
            raise RuntimeError("Use check() with sync Client")
        
        decision = await self.client.enforce(tool_name, tool_args, **kwargs)
        self._decisions.append(decision)
        return decision
    
    def log_result(self, result: Any, decision_index: int = -1):
        """Log the result of the last (or specified) tool call."""
        if isinstance(self.client, AsyncClient):
            raise RuntimeError("Use async_log_result() with AsyncClient")
        
        if not self._decisions:
            raise ValueError("No policy decisions to log result for")
        
        decision = self._decisions[decision_index]
        return self.client.update_result(
            decision.session_id,
            decision.log_id,
            {"status": "success", "result": result}
        )
    
    async def async_log_result(self, result: Any, decision_index: int = -1):
        """Async version of log_result method."""
        if not isinstance(self.client, AsyncClient):
            raise RuntimeError("Use log_result() with sync Client")
        
        if not self._decisions:
            raise ValueError("No policy decisions to log result for")
        
        decision = self._decisions[decision_index]
        return await self.client.update_result(
            decision.session_id,
            decision.log_id,
            {"status": "success", "result": result}
        )