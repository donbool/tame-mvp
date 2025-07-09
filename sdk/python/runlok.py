"""
Runlok Python SDK - Middleware for enforcing and logging AI agent tool use.

Usage:
    import runlok
    
    # Initialize client
    client = runlok.Client(api_url="http://localhost:8000")
    
    # Enforce a tool call
    decision = client.enforce(
        tool_name="search_web",
        tool_args={"query": "python tutorials"},
        session_id="my-session-123"
    )
    
    if decision.action == "allow":
        # Execute the tool
        result = execute_tool(decision.tool_name, decision.tool_args)
        
        # Report the result back
        client.update_result(decision.session_id, decision.log_id, result)
"""

import httpx
import json
import uuid
import time
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EnforcementDecision:
    """Result of a policy enforcement decision."""
    session_id: str
    action: str  # allow, deny, approve
    rule_name: Optional[str]
    reason: str
    policy_version: str
    log_id: str
    timestamp: datetime
    tool_name: str
    tool_args: Dict[str, Any]


class RunlokException(Exception):
    """Base exception for Runlok SDK errors."""
    pass


class PolicyViolationException(RunlokException):
    """Raised when a tool call is denied by policy."""
    
    def __init__(self, decision: EnforcementDecision):
        self.decision = decision
        super().__init__(f"Tool call denied: {decision.reason}")


class ApprovalRequiredException(RunlokException):
    """Raised when a tool call requires approval."""
    
    def __init__(self, decision: EnforcementDecision):
        self.decision = decision
        super().__init__(f"Tool call requires approval: {decision.reason}")


class Client:
    """Runlok client for policy enforcement and logging."""
    
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Initialize Runlok client.
        
        Args:
            api_url: Base URL of the Runlok API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            session_id: Default session ID (will auto-generate if not provided)
            agent_id: Optional agent identifier
            user_id: Optional user identifier
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session_id = session_id or str(uuid.uuid4())
        self.agent_id = agent_id
        self.user_id = user_id
        
        # HTTP client configuration
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "runlok-python-sdk/0.1.0"
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        self.client = httpx.Client(
            base_url=self.api_url,
            headers=headers,
            timeout=timeout
        )
    
    def enforce(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        raise_on_deny: bool = True,
        raise_on_approve: bool = True
    ) -> EnforcementDecision:
        """
        Enforce policy on a tool call.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            session_id: Session identifier (uses default if not provided)
            agent_id: Agent identifier (uses default if not provided)  
            user_id: User identifier (uses default if not provided)
            metadata: Additional metadata to log
            raise_on_deny: Raise PolicyViolationException if denied
            raise_on_approve: Raise ApprovalRequiredException if approval needed
            
        Returns:
            EnforcementDecision with the policy decision
            
        Raises:
            PolicyViolationException: If tool call is denied and raise_on_deny=True
            ApprovalRequiredException: If approval required and raise_on_approve=True
            RunlokException: If API call fails
        """
        
        request_data = {
            "tool_name": tool_name,
            "tool_args": tool_args,
            "session_id": session_id or self.session_id,
            "agent_id": agent_id or self.agent_id,
            "user_id": user_id or self.user_id,
            "metadata": metadata
        }
        
        try:
            response = self.client.post("/api/v1/enforce", json=request_data)
            response.raise_for_status()
            
            data = response.json()
            
            decision = EnforcementDecision(
                session_id=data["session_id"],
                action=data["decision"],
                rule_name=data["rule_name"],
                reason=data["reason"],
                policy_version=data["policy_version"],
                log_id=data["log_id"],
                timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
                tool_name=tool_name,
                tool_args=tool_args
            )
            
            # Handle policy decisions
            if decision.action == "deny" and raise_on_deny:
                raise PolicyViolationException(decision)
            elif decision.action == "approve" and raise_on_approve:
                raise ApprovalRequiredException(decision)
            
            return decision
            
        except httpx.RequestError as e:
            raise RunlokException(f"Failed to connect to Runlok API: {e}")
        except httpx.HTTPStatusError as e:
            raise RunlokException(f"Runlok API error {e.response.status_code}: {e.response.text}")
    
    def update_result(
        self,
        session_id: str,
        log_id: str,
        result: Dict[str, Any],
        execution_time_ms: Optional[float] = None
    ) -> bool:
        """
        Update the result of a tool call after execution.
        
        Args:
            session_id: Session identifier
            log_id: Log entry identifier from enforcement decision
            result: Tool execution result
            execution_time_ms: Optional execution time in milliseconds
            
        Returns:
            True if update successful
            
        Raises:
            RunlokException: If API call fails
        """
        
        # Add execution metadata
        result_data = dict(result)
        if execution_time_ms is not None:
            result_data["duration_ms"] = execution_time_ms
        
        try:
            response = self.client.post(
                f"/api/v1/enforce/{session_id}/result",
                params={"log_id": log_id},
                json=result_data
            )
            response.raise_for_status()
            return True
            
        except httpx.RequestError as e:
            raise RunlokException(f"Failed to connect to Runlok API: {e}")
        except httpx.HTTPStatusError as e:
            raise RunlokException(f"Runlok API error {e.response.status_code}: {e.response.text}")
    
    def get_session_logs(self, session_id: Optional[str] = None) -> list:
        """
        Get all logs for a session.
        
        Args:
            session_id: Session identifier (uses default if not provided)
            
        Returns:
            List of session log entries
            
        Raises:
            RunlokException: If API call fails
        """
        
        session_id = session_id or self.session_id
        
        try:
            response = self.client.get(f"/api/v1/sessions/{session_id}")
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            raise RunlokException(f"Failed to connect to Runlok API: {e}")
        except httpx.HTTPStatusError as e:
            raise RunlokException(f"Runlok API error {e.response.status_code}: {e.response.text}")
    
    def get_policy_info(self) -> Dict[str, Any]:
        """
        Get current policy information.
        
        Returns:
            Dictionary with policy information
            
        Raises:
            RunlokException: If API call fails
        """
        
        try:
            response = self.client.get("/api/v1/policy/current")
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            raise RunlokException(f"Failed to connect to Runlok API: {e}")
        except httpx.HTTPStatusError as e:
            raise RunlokException(f"Runlok API error {e.response.status_code}: {e.response.text}")
    
    def test_policy(
        self,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test a tool call against the current policy without executing it.
        
        Args:
            tool_name: Name of the tool to test
            tool_args: Arguments for the tool (optional)
            session_context: Session context for testing (optional)
            
        Returns:
            Dict with policy test results
            
        Raises:
            RunlokException: If API call fails
        """
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
            raise RunlokException(f"Failed to connect to Runlok API: {e}")
        except httpx.HTTPStatusError as e:
            raise RunlokException(f"Runlok API error {e.response.status_code}: {e.response.text}")

    def validate_policy(
        self,
        policy_content: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a policy YAML configuration without deploying it.
        
        Args:
            policy_content: YAML policy content as string
            description: Optional description for the policy
            
        Returns:
            Dict with validation results including:
            - is_valid: bool
            - errors: List[str]
            - rules_count: int
            - version: Optional[str]
            
        Raises:
            RunlokException: If API call fails
        """
        request_data = {
            "policy_content": policy_content,
            "description": description
        }
        
        try:
            response = self.client.post("/api/v1/policy/validate", json=request_data)
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            raise RunlokException(f"Failed to connect to Runlok API: {e}")
        except httpx.HTTPStatusError as e:
            raise RunlokException(f"Runlok API error {e.response.status_code}: {e.response.text}")

    def create_policy(
        self,
        policy_content: str,
        version: str,
        description: Optional[str] = None,
        activate: bool = True
    ) -> Dict[str, Any]:
        """
        Create and optionally deploy a new policy.
        
        Args:
            policy_content: YAML policy content as string
            version: Version identifier for the policy
            description: Optional description for the policy
            activate: Whether to activate the policy immediately
            
        Returns:
            Dict with creation results including:
            - success: bool
            - policy_id: str
            - version: str
            - message: str
            - validation_errors: List[str]
            
        Raises:
            RunlokException: If API call fails
        """
        request_data = {
            "policy_content": policy_content,
            "version": version,
            "description": description,
            "activate": activate
        }
        
        try:
            response = self.client.post("/api/v1/policy/create", json=request_data)
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            raise RunlokException(f"Failed to connect to Runlok API: {e}")
        except httpx.HTTPStatusError as e:
            raise RunlokException(f"Runlok API error {e.response.status_code}: {e.response.text}")

    def reload_policy(self) -> Dict[str, Any]:
        """
        Reload the policy from the configuration file.
        
        Returns:
            Dict with reload results including:
            - status: str
            - old_version: str
            - new_version: str
            - rules_count: int
            
        Raises:
            RunlokException: If API call fails
        """
        try:
            response = self.client.post("/api/v1/policy/reload")
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            raise RunlokException(f"Failed to connect to Runlok API: {e}")
        except httpx.HTTPStatusError as e:
            raise RunlokException(f"Runlok API error {e.response.status_code}: {e.response.text}")
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions for quick usage
def enforce(
    tool_name: str,
    tool_args: Dict[str, Any],
    api_url: str = "http://localhost:8000",
    session_id: Optional[str] = None,
    **kwargs
) -> EnforcementDecision:
    """
    Convenience function for one-off policy enforcement.
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        api_url: Runlok API URL
        session_id: Session identifier
        **kwargs: Additional arguments passed to Client.enforce()
        
    Returns:
        EnforcementDecision with the policy decision
    """
    
    with Client(api_url=api_url, session_id=session_id) as client:
        return client.enforce(tool_name, tool_args, **kwargs)


def execute_with_enforcement(
    tool_name: str,
    tool_args: Dict[str, Any],
    executor_func: callable,
    api_url: str = "http://localhost:8000",
    session_id: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Execute a tool with automatic enforcement and result logging.
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        executor_func: Function that executes the tool (receives tool_name, tool_args)
        api_url: Runlok API URL
        session_id: Session identifier
        **kwargs: Additional arguments passed to Client.enforce()
        
    Returns:
        Result from executor_func
        
    Raises:
        PolicyViolationException: If tool call is denied
        ApprovalRequiredException: If approval is required
    """
    
    with Client(api_url=api_url, session_id=session_id) as client:
        # Enforce policy
        start_time = time.time()
        decision = client.enforce(tool_name, tool_args, **kwargs)
        
        try:
            # Execute the tool
            result = executor_func(tool_name, tool_args)
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Log successful result
            client.update_result(
                decision.session_id,
                decision.log_id,
                {"status": "success", "result": result},
                execution_time
            )
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Log error result
            client.update_result(
                decision.session_id,
                decision.log_id,
                {
                    "status": "error",
                    "error_message": str(e),
                    "error_type": type(e).__name__
                },
                execution_time
            )
            
            # Re-raise the original exception
            raise 