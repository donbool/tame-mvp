"""
Core client implementation for TameSDK.
"""

import asyncio
import httpx
import json
import uuid
import time
import logging
from typing import Dict, Any, Optional, Union, List, Callable
from datetime import datetime

from .config import get_config, TameConfig
from .models import EnforcementDecision, PolicyInfo, SessionLog, ToolResult, ActionType
from .exceptions import (
    TameSDKException, PolicyViolationException, ApprovalRequiredException,
    ConnectionException, AuthenticationException, RateLimitException,
    ValidationException, TimeoutException
)
from .utils import validate_tool_call, format_policy_error


logger = logging.getLogger(__name__)


class BaseClient:
    """Base client with common functionality."""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        config: Optional[TameConfig] = None
    ):
        """
        Initialize the client.
        
        Args:
            api_url: Base URL of the Tame API
            api_key: API key for authentication
            timeout: Request timeout in seconds
            session_id: Session identifier
            agent_id: Agent identifier
            user_id: User identifier
            config: Configuration object (overrides other params)
        """
        # Use provided config or global config
        self.config = config or get_config()
        
        # Override config with explicit parameters
        self.api_url = (api_url or self.config.api_url).rstrip("/")
        self.api_key = api_key or self.config.api_key
        self.timeout = timeout or self.config.timeout
        self.session_id = session_id or self.config.session_id or str(uuid.uuid4())
        self.agent_id = agent_id or self.config.agent_id
        self.user_id = user_id or self.config.user_id
        
        # Prepare headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": f"tamesdk/1.0.0 python/{httpx.__version__}",
            **self.config.extra_headers
        }
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"Initialized TameSDK client for session {self.session_id}")
    
    def _handle_http_error(self, response: httpx.Response) -> None:
        """Handle HTTP errors and convert to appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationException("Authentication failed - check API key")
        elif response.status_code == 403:
            raise AuthenticationException("Access forbidden - insufficient permissions")
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitException(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None
            )
        elif response.status_code >= 500:
            raise ConnectionException(f"Server error {response.status_code}: {response.text}")
        else:
            raise TameSDKException(f"API error {response.status_code}: {response.text}")
    
    def _parse_enforcement_decision(self, data: Dict[str, Any], tool_name: str, tool_args: Dict[str, Any]) -> EnforcementDecision:
        """Parse API response into EnforcementDecision object."""
        return EnforcementDecision(
            session_id=data["session_id"],
            action=ActionType(data["decision"]),
            rule_name=data.get("rule_name"),
            reason=data["reason"],
            policy_version=data["policy_version"],
            log_id=data["log_id"],
            timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
            tool_name=tool_name,
            tool_args=tool_args,
            metadata=data.get("metadata", {})
        )


class Client(BaseClient):
    """Synchronous TameSDK client."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = httpx.Client(
            base_url=self.api_url,
            headers=self.headers,
            timeout=self.timeout
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def enforce(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        raise_on_deny: Optional[bool] = None,
        raise_on_approve: Optional[bool] = None
    ) -> EnforcementDecision:
        """
        Enforce policy on a tool call.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            session_id: Session identifier (uses default if not provided)
            metadata: Additional metadata to log
            raise_on_deny: Raise PolicyViolationException if denied
            raise_on_approve: Raise ApprovalRequiredException if approval needed
            
        Returns:
            EnforcementDecision with the policy decision
        """
        # Use config defaults if not specified
        if raise_on_deny is None:
            raise_on_deny = self.config.raise_on_deny
        if raise_on_approve is None:
            raise_on_approve = self.config.raise_on_approve
        
        # Validate inputs
        validate_tool_call(tool_name, tool_args)
        
        # Check bypass mode
        if self.config.bypass_mode:
            logger.warning("Bypass mode enabled - skipping policy enforcement")
            return EnforcementDecision(
                session_id=session_id or self.session_id,
                action=ActionType.ALLOW,
                rule_name="bypass_mode",
                reason="Policy enforcement bypassed",
                policy_version="bypass",
                log_id=f"bypass-{int(time.time() * 1000)}",
                timestamp=datetime.now(),
                tool_name=tool_name,
                tool_args=tool_args
            )
        
        request_data = {
            "tool_name": tool_name,
            "tool_args": tool_args,
            "session_id": session_id or self.session_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "metadata": metadata or {}
        }
        
        try:
            response = self.client.post("/api/v1/enforce", json=request_data)
            response.raise_for_status()
            
            data = response.json()
            decision = self._parse_enforcement_decision(data, tool_name, tool_args)
            
            # Handle policy decisions
            if decision.action == ActionType.DENY and raise_on_deny:
                raise PolicyViolationException(decision)
            elif decision.action == ActionType.APPROVE and raise_on_approve:
                raise ApprovalRequiredException(decision)
            
            return decision
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)
    
    def execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        executor: Optional[Callable] = None,
        **kwargs
    ) -> ToolResult:
        """
        Execute a tool with automatic policy enforcement.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            executor: Function to execute the tool (receives tool_name, tool_args)
            **kwargs: Additional arguments passed to enforce()
            
        Returns:
            ToolResult with execution details
        """
        start_time = time.time()
        
        try:
            # Enforce policy
            decision = self.enforce(tool_name, tool_args, **kwargs)
            
            # Execute the tool if allowed
            if decision.is_allowed:
                if executor:
                    result = executor(tool_name, tool_args)
                else:
                    # Default behavior - just return the decision
                    result = {"decision": decision}
                
                execution_time = (time.time() - start_time) * 1000
                
                # Log successful result
                tool_result = ToolResult(
                    success=True,
                    result=result,
                    execution_time_ms=execution_time
                )
                
                try:
                    self.update_result(decision.session_id, decision.log_id, {
                        "status": "success",
                        "result": result,
                        "execution_time_ms": execution_time
                    })
                except Exception as log_error:
                    logger.warning(f"Failed to log result: {log_error}")
                
                return tool_result
            else:
                # Should not reach here if raise_on_deny/approve is True
                return ToolResult(
                    success=False,
                    error=f"Tool call not allowed: {decision.reason}"
                )
                
        except (PolicyViolationException, ApprovalRequiredException) as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Log the blocked call
            try:
                self.update_result(e.decision.session_id, e.decision.log_id, {
                    "status": "blocked",
                    "error": str(e),
                    "execution_time_ms": execution_time
                })
            except Exception as log_error:
                logger.warning(f"Failed to log blocked call: {log_error}")
            
            raise
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    def update_result(
        self,
        session_id: str,
        log_id: str,
        result: Dict[str, Any],
        execution_time_ms: Optional[float] = None
    ) -> bool:
        """Update the result of a tool call after execution."""
        if execution_time_ms is not None:
            result = dict(result)
            result["execution_time_ms"] = execution_time_ms
        
        try:
            response = self.client.post(
                f"/api/v1/enforce/{session_id}/result",
                params={"log_id": log_id},
                json=result
            )
            response.raise_for_status()
            return True
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)
    
    def get_session_logs(self, session_id: Optional[str] = None) -> List[SessionLog]:
        """Get all logs for a session."""
        session_id = session_id or self.session_id
        
        try:
            response = self.client.get(f"/api/v1/sessions/{session_id}")
            response.raise_for_status()
            
            data = response.json()
            return [SessionLog(**log) for log in data]
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)
    
    def get_policy_info(self) -> PolicyInfo:
        """Get current policy information."""
        try:
            response = self.client.get("/api/v1/policy/current")
            response.raise_for_status()
            
            data = response.json()
            return PolicyInfo(
                version=data["version"],
                description=data.get("description"),
                rules_count=data["rules_count"],
                last_updated=datetime.fromisoformat(data["last_updated"]),
                hash=data["hash"],
                active=data.get("active", True)
            )
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)
    
    def test_policy(
        self,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test a tool call against the current policy without executing it."""
        params = {"tool_name": tool_name}
        
        if tool_args:
            params["tool_args"] = json.dumps(tool_args)
        
        if session_context:
            params["session_context"] = json.dumps(session_context)
        
        try:
            response = self.client.get("/api/v1/policy/test", params=params)
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)


class AsyncClient(BaseClient):
    """Asynchronous TameSDK client."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers=self.headers,
            timeout=self.timeout
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def enforce(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        raise_on_deny: Optional[bool] = None,
        raise_on_approve: Optional[bool] = None
    ) -> EnforcementDecision:
        """Async version of enforce method."""
        # Use config defaults if not specified
        if raise_on_deny is None:
            raise_on_deny = self.config.raise_on_deny
        if raise_on_approve is None:
            raise_on_approve = self.config.raise_on_approve
        
        # Validate inputs
        validate_tool_call(tool_name, tool_args)
        
        # Check bypass mode
        if self.config.bypass_mode:
            logger.warning("Bypass mode enabled - skipping policy enforcement")
            return EnforcementDecision(
                session_id=session_id or self.session_id,
                action=ActionType.ALLOW,
                rule_name="bypass_mode",
                reason="Policy enforcement bypassed",
                policy_version="bypass",
                log_id=f"bypass-{int(time.time() * 1000)}",
                timestamp=datetime.now(),
                tool_name=tool_name,
                tool_args=tool_args
            )
        
        request_data = {
            "tool_name": tool_name,
            "tool_args": tool_args,
            "session_id": session_id or self.session_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "metadata": metadata or {}
        }
        
        try:
            response = await self.client.post("/api/v1/enforce", json=request_data)
            response.raise_for_status()
            
            data = response.json()
            decision = self._parse_enforcement_decision(data, tool_name, tool_args)
            
            # Handle policy decisions
            if decision.action == ActionType.DENY and raise_on_deny:
                raise PolicyViolationException(decision)
            elif decision.action == ActionType.APPROVE and raise_on_approve:
                raise ApprovalRequiredException(decision)
            
            return decision
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)
    
    async def execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        executor: Optional[Callable] = None,
        **kwargs
    ) -> ToolResult:
        """Async version of execute_tool method."""
        start_time = time.time()
        
        try:
            # Enforce policy
            decision = await self.enforce(tool_name, tool_args, **kwargs)
            
            # Execute the tool if allowed
            if decision.is_allowed:
                if executor:
                    if asyncio.iscoroutinefunction(executor):
                        result = await executor(tool_name, tool_args)
                    else:
                        result = executor(tool_name, tool_args)
                else:
                    # Default behavior - just return the decision
                    result = {"decision": decision}
                
                execution_time = (time.time() - start_time) * 1000
                
                # Log successful result
                tool_result = ToolResult(
                    success=True,
                    result=result,
                    execution_time_ms=execution_time
                )
                
                try:
                    await self.update_result(decision.session_id, decision.log_id, {
                        "status": "success",
                        "result": result,
                        "execution_time_ms": execution_time
                    })
                except Exception as log_error:
                    logger.warning(f"Failed to log result: {log_error}")
                
                return tool_result
            else:
                # Should not reach here if raise_on_deny/approve is True
                return ToolResult(
                    success=False,
                    error=f"Tool call not allowed: {decision.reason}"
                )
                
        except (PolicyViolationException, ApprovalRequiredException) as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Log the blocked call
            try:
                await self.update_result(e.decision.session_id, e.decision.log_id, {
                    "status": "blocked",
                    "error": str(e),
                    "execution_time_ms": execution_time
                })
            except Exception as log_error:
                logger.warning(f"Failed to log blocked call: {log_error}")
            
            raise
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def update_result(
        self,
        session_id: str,
        log_id: str,
        result: Dict[str, Any],
        execution_time_ms: Optional[float] = None
    ) -> bool:
        """Async version of update_result method."""
        if execution_time_ms is not None:
            result = dict(result)
            result["execution_time_ms"] = execution_time_ms
        
        try:
            response = await self.client.post(
                f"/api/v1/enforce/{session_id}/result",
                params={"log_id": log_id},
                json=result
            )
            response.raise_for_status()
            return True
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)
    
    async def get_session_logs(self, session_id: Optional[str] = None) -> List[SessionLog]:
        """Async version of get_session_logs method."""
        session_id = session_id or self.session_id
        
        try:
            response = await self.client.get(f"/api/v1/sessions/{session_id}")
            response.raise_for_status()
            
            data = response.json()
            return [SessionLog(**log) for log in data]
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)
    
    async def get_policy_info(self) -> PolicyInfo:
        """Async version of get_policy_info method."""
        try:
            response = await self.client.get("/api/v1/policy/current")
            response.raise_for_status()
            
            data = response.json()
            return PolicyInfo(
                version=data["version"],
                description=data.get("description"),
                rules_count=data["rules_count"],
                last_updated=datetime.fromisoformat(data["last_updated"]),
                hash=data["hash"],
                active=data.get("active", True)
            )
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)
    
    async def test_policy(
        self,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Async version of test_policy method."""
        params = {"tool_name": tool_name}
        
        if tool_args:
            params["tool_args"] = json.dumps(tool_args)
        
        if session_context:
            params["session_context"] = json.dumps(session_context)
        
        try:
            response = await self.client.get("/api/v1/policy/test", params=params)
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            raise ConnectionException(f"Failed to connect to Tame API: {e}")
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e.response)