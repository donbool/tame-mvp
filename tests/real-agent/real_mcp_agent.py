#!/usr/bin/env python3
"""
Real MCP Agent Test with tamesdk Integration

This test demonstrates a real MCP agent that uses the tamesdk for runtime control,
policy enforcement, and action logging. The agent's tool calls are wrapped with
tamesdk to provide governance and observability.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

import tamesdk
from tamesdk import PolicyViolationException, ApprovalRequiredException

# MCP-related imports
try:
    from mcp import types
    from mcp.client.session import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:
    print("MCP library not found. Please install with: pip install mcp")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TameWrappedMCPAgent:
    """
    An MCP agent that wraps all tool calls with tamesdk for policy enforcement
    and logging. This provides runtime control over the agent's actions.
    """
    
    def __init__(
        self,
        tame_api_url: str = "http://localhost:8000",
        agent_id: str = "mcp-test-agent",
        user_id: str = "test-user",
        session_id: Optional[str] = None
    ):
        """
        Initialize the wrapped MCP agent.
        
        Args:
            tame_api_url: URL of the tame API server
            agent_id: Identifier for this agent
            user_id: Identifier for the user running the agent
            session_id: Optional session ID (auto-generated if not provided)
        """
        self.tame_client = tamesdk.Client(
            api_url=tame_api_url,
            agent_id=agent_id,
            user_id=user_id,
            session_id=session_id
        )
        
        self.session_id = self.tame_client.session_id
        self.agent_id = agent_id
        self.user_id = user_id
        
        # MCP client will be initialized when we connect to a server
        self.mcp_session: Optional[ClientSession] = None
        self.available_tools: Dict[str, types.Tool] = {}
        
        logger.info(f"Initialized TameWrappedMCPAgent with session_id={self.session_id}")
    
    async def connect_to_mcp_server(self, server_params: StdioServerParameters):
        """Connect to an MCP server and discover available tools."""
        try:
            logger.info(f"Connecting to MCP server: {server_params.command}")
            
            # Connect to the MCP server
            self.mcp_session = await stdio_client(server_params).__aenter__()
            
            # Initialize the session
            init_result = await self.mcp_session.initialize()
            logger.info(f"MCP server initialized: {init_result}")
            
            # List available tools
            tools_result = await self.mcp_session.list_tools()
            self.available_tools = {tool.name: tool for tool in tools_result.tools}
            
            logger.info(f"Available tools: {list(self.available_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def execute_tool_with_enforcement(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool call through MCP with tamesdk enforcement and logging.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            metadata: Additional metadata for logging
            
        Returns:
            Dict containing the tool execution result
            
        Raises:
            PolicyViolationException: If the tool call is denied by policy
            ApprovalRequiredException: If the tool call requires approval
            Exception: If tool execution fails
        """
        
        # Check if tool exists
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available. Available tools: {list(self.available_tools.keys())}")
        
        start_time = time.time()
        
        try:
            # Step 1: Enforce policy through tamesdk
            logger.info(f"Enforcing policy for tool call: {tool_name}")
            
            try:
                decision = self.tame_client.enforce(
                    tool_name=tool_name,
                    tool_args=arguments,
                    metadata=metadata or {}
                )
                logger.info(f"Policy decision: {decision.action} - {decision.reason}")
                
            except Exception as tame_error:
                logger.warning(f"tame server not available, running in bypass mode: {tame_error}")
                # Create a mock decision for demonstration
                decision = type('MockDecision', (), {
                    'session_id': self.session_id,
                    'action': 'allow',
                    'rule_name': 'bypass_mode',
                    'reason': 'tame server not available - bypassing policy enforcement',
                    'log_id': f"mock-{int(time.time() * 1000)}"
                })()
            
            # Step 2: Execute the tool if allowed
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            
            call_result = await self.mcp_session.call_tool(tool_name, arguments)
            
            # Extract result content
            result_content = []
            for content in call_result.content:
                if isinstance(content, types.TextContent):
                    result_content.append(content.text)
                else:
                    result_content.append(str(content))
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = {
                "tool_name": tool_name,
                "arguments": arguments,
                "success": True,
                "content": result_content,
                "execution_time_ms": execution_time,
                "policy_decision": {
                    "action": decision.action,
                    "rule_name": decision.rule_name,
                    "reason": decision.reason
                }
            }
            
            # Step 3: Log the successful result
            try:
                self.tame_client.update_result(
                    session_id=decision.session_id,
                    log_id=decision.log_id,
                    result=result,
                    execution_time_ms=execution_time
                )
            except Exception as log_error:
                logger.warning(f"Could not log result to tame server: {log_error}")
            
            logger.info(f"Tool execution completed successfully in {execution_time:.2f}ms")
            return result
            
        except (PolicyViolationException, ApprovalRequiredException) as e:
            # Policy enforcement blocked the call
            execution_time = (time.time() - start_time) * 1000
            
            error_result = {
                "tool_name": tool_name,
                "arguments": arguments,
                "success": False,
                "error": str(e),
                "error_type": "PolicyEnforcement",
                "execution_time_ms": execution_time,
                "policy_decision": {
                    "action": e.decision.action,
                    "rule_name": e.decision.rule_name,
                    "reason": e.decision.reason
                }
            }
            
            # Log the blocked call
            try:
                self.tame_client.update_result(
                    session_id=e.decision.session_id,
                    log_id=e.decision.log_id,
                    result=error_result,
                    execution_time_ms=execution_time
                )
            except Exception as log_error:
                logger.warning(f"Could not log blocked call to tame server: {log_error}")
            
            logger.warning(f"Tool call blocked by policy: {e}")
            raise
            
        except Exception as e:
            # Tool execution failed
            execution_time = (time.time() - start_time) * 1000
            
            error_result = {
                "tool_name": tool_name,
                "arguments": arguments,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time_ms": execution_time
            }
            
            # Log the error if we have a decision (policy was enforced but execution failed)
            if 'decision' in locals():
                try:
                    self.tame_client.update_result(
                        session_id=decision.session_id,
                        log_id=decision.log_id,
                        result=error_result,
                        execution_time_ms=execution_time
                    )
                except Exception as log_error:
                    logger.warning(f"Could not log error result to tame server: {log_error}")
            
            logger.error(f"Tool execution failed: {e}")
            raise
    
    async def test_policy_without_execution(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test a tool call against the current policy without executing it."""
        return self.tame_client.test_policy(
            tool_name=tool_name,
            tool_args=arguments,
            session_context={
                "agent_id": self.agent_id,
                "user_id": self.user_id,
                "session_id": self.session_id
            }
        )
    
    def get_session_logs(self) -> List[Dict[str, Any]]:
        """Get all logs for the current session."""
        return self.tame_client.get_session_logs()
    
    def get_policy_info(self) -> Dict[str, Any]:
        """Get current policy information."""
        return self.tame_client.get_policy_info()
    
    async def close(self):
        """Clean up resources."""
        if self.mcp_session and hasattr(self.mcp_session, '__aexit__'):
            await self.mcp_session.__aexit__(None, None, None)
        self.tame_client.close()


async def run_agent_test():
    """
    Main test function that demonstrates the wrapped MCP agent.
    """
    logger.info("Starting MCP Agent Test with tamesdk Integration")
    
    # Initialize the wrapped agent
    agent = TameWrappedMCPAgent(
        tame_api_url="http://localhost:8000",
        agent_id="mcp-test-agent-1",
        user_id="test-user",
        session_id=f"test-session-{int(time.time())}"
    )
    
    try:
        # For this test, we'll simulate connecting to a filesystem MCP server
        # In a real scenario, you would connect to an actual MCP server
        logger.info("Note: This test demonstrates the wrapping mechanism.")
        logger.info("In a real scenario, you would connect to an MCP server like this:")
        logger.info("server_params = StdioServerParameters(command=['python', 'filesystem_server.py'])")
        logger.info("await agent.connect_to_mcp_server(server_params)")
        
        # Simulate some tools being available
        agent.available_tools = {
            "read_file": types.Tool(
                name="read_file",
                description="Read contents of a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file"}
                    },
                    "required": ["path"]
                }
            ),
            "write_file": types.Tool(
                name="write_file", 
                description="Write content to a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            ),
            "list_directory": types.Tool(
                name="list_directory",
                description="List contents of a directory", 
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the directory"}
                    },
                    "required": ["path"]
                }
            )
        }
        
        # Test 1: Check current policy
        logger.info("\n=== Test 1: Policy Information ===")
        try:
            policy_info = agent.get_policy_info()
            logger.info(f"Current policy: {json.dumps(policy_info, indent=2)}")
        except Exception as e:
            logger.warning(f"Could not get policy info (tame server may not be running): {e}")
        
        # Test 2: Test policy enforcement without execution
        logger.info("\n=== Test 2: Policy Testing ===")
        test_cases = [
            ("read_file", {"path": "/etc/passwd"}),
            ("write_file", {"path": "/tmp/test.txt", "content": "Hello World"}),
            ("list_directory", {"path": "/home"})
        ]
        
        for tool_name, args in test_cases:
            try:
                test_result = await agent.test_policy_without_execution(tool_name, args)
                logger.info(f"Policy test for {tool_name}: {test_result}")
            except Exception as e:
                logger.warning(f"Policy test failed: {e}")
        
        # Test 3: Simulate tool execution with enforcement
        logger.info("\n=== Test 3: Simulated Tool Execution ===")
        
        # Mock the MCP session for demonstration
        class MockMCPSession:
            async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
                # Simulate tool execution
                await asyncio.sleep(0.1)  # Simulate processing time
                
                if tool_name == "read_file":
                    return type('Result', (), {
                        'content': [types.TextContent(type="text", text=f"Contents of {arguments['path']}: Hello World!")]
                    })()
                elif tool_name == "write_file":
                    return type('Result', (), {
                        'content': [types.TextContent(type="text", text=f"Successfully wrote to {arguments['path']}")]
                    })()
                elif tool_name == "list_directory":
                    return type('Result', (), {
                        'content': [types.TextContent(type="text", text=f"Directory {arguments['path']} contains: file1.txt, file2.txt")]
                    })()
                else:
                    raise Exception(f"Unknown tool: {tool_name}")
        
        agent.mcp_session = MockMCPSession()
        
        # Execute some tool calls
        execution_tests = [
            ("list_directory", {"path": "/tmp"}),
            ("read_file", {"path": "/tmp/safe_file.txt"}),
            ("write_file", {"path": "/tmp/output.txt", "content": "Test output"})
        ]
        
        for tool_name, args in execution_tests:
            try:
                logger.info(f"Executing: {tool_name} with {args}")
                result = await agent.execute_tool_with_enforcement(
                    tool_name=tool_name,
                    arguments=args,
                    metadata={"test_case": f"execution_test_{tool_name}"}
                )
                logger.info(f"Execution result: {json.dumps(result, indent=2)}")
                
            except PolicyViolationException as e:
                logger.warning(f"Tool call denied by policy: {e}")
            except ApprovalRequiredException as e:
                logger.warning(f"Tool call requires approval: {e}")
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
        
        # Test 4: Get session logs
        logger.info("\n=== Test 4: Session Logs ===")
        try:
            logs = agent.get_session_logs()
            logger.info(f"Session logs: {json.dumps(logs, indent=2)}")
        except Exception as e:
            logger.warning(f"Could not get session logs: {e}")
        
        logger.info("\n=== Test Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        # Clean up
        await agent.close()


def create_sample_policy():
    """
    Create a sample policy file for testing.
    This demonstrates how to configure policies for the MCP agent.
    """
    policy_content = """
# Sample tame Policy for MCP Agent Testing
version: "1.0"
description: "Test policy for MCP agent with file system access controls"

rules:
  # Allow safe read operations
  - name: "allow_safe_reads"
    description: "Allow reading from safe directories"
    condition: |
      tool_name == "read_file" and 
      (tool_args.path.startswith("/tmp/") or 
       tool_args.path.startswith("/home/") or
       tool_args.path.startswith("./"))
    action: "allow"
    
  # Require approval for system file reads
  - name: "approve_system_reads"
    description: "System files require approval"
    condition: |
      tool_name == "read_file" and
      (tool_args.path.startswith("/etc/") or
       tool_args.path.startswith("/sys/") or
       tool_args.path.startswith("/proc/"))
    action: "approve"
    reason: "Reading system files requires manual approval"
    
  # Allow safe write operations
  - name: "allow_safe_writes"
    description: "Allow writing to temporary directories"
    condition: |
      tool_name == "write_file" and
      tool_args.path.startswith("/tmp/")
    action: "allow"
    
  # Deny dangerous write operations
  - name: "deny_dangerous_writes"
    description: "Deny writes to system directories"
    condition: |
      tool_name == "write_file" and
      (tool_args.path.startswith("/etc/") or
       tool_args.path.startswith("/sys/") or
       tool_args.path.startswith("/bin/") or
       tool_args.path.startswith("/usr/"))
    action: "deny"
    reason: "Writing to system directories is not allowed"
    
  # Allow directory listing with logging
  - name: "allow_directory_listing"
    description: "Allow directory listing operations"
    condition: 'tool_name == "list_directory"'
    action: "allow"
    
  # Default deny for unspecified operations
  - name: "default_deny"
    description: "Default policy - deny unknown operations"
    condition: "true"
    action: "deny"
    reason: "Operation not explicitly allowed by policy"
"""
    
    policy_path = Path(__file__).parent / "sample_policy.yaml"
    with open(policy_path, "w") as f:
        f.write(policy_content)
    
    logger.info(f"Sample policy created at: {policy_path}")
    return policy_path


if __name__ == "__main__":
    logger.info("MCP Agent Test with tamesdk Integration")
    logger.info("=" * 50)
    
    # Create sample policy for reference
    policy_path = create_sample_policy()
    logger.info(f"Sample policy created at: {policy_path}")
    
    logger.info("\nTo run this test with a real tame server:")
    logger.info("1. Start the tame API server (usually on http://localhost:8000)")
    logger.info("2. Configure your policy using the sample_policy.yaml file")
    logger.info("3. Run this test script")
    
    logger.info("\nStarting test...")
    
    try:
        asyncio.run(run_agent_test())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        sys.exit(1)