#!/usr/bin/env python3
"""
Real-world example: MCP Agent with TameSDK Integration

This example demonstrates how to build a production-ready MCP agent
that uses TameSDK for runtime control and policy enforcement.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from pathlib import Path

try:
    from mcp import types
    from mcp.client.session import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
except ImportError:
    print("Please install mcp: pip install mcp")
    exit(1)

import tamesdk


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass 
class ToolMetadata:
    """Metadata for MCP tools."""
    name: str
    description: str
    category: str
    risk_level: str  # low, medium, high
    requires_approval: bool = False
    rate_limit: Optional[int] = None


class TameMCPAgent:
    """
    Production MCP agent with TameSDK integration.
    
    Features:
    - All tool calls enforced through TameSDK policies
    - Comprehensive logging and monitoring
    - Error handling and recovery
    - Session management
    - Tool categorization and metadata
    """
    
    def __init__(
        self,
        agent_id: str,
        user_id: str,
        tame_api_url: str = "http://localhost:8000",
        tame_api_key: Optional[str] = None
    ):
        # Initialize TameSDK
        self.tame_client = tamesdk.AsyncClient(
            api_url=tame_api_url,
            api_key=tame_api_key,
            agent_id=agent_id,
            user_id=user_id
        )
        
        # MCP session management
        self.mcp_session: Optional[ClientSession] = None
        self.available_tools: Dict[str, types.Tool] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        
        # Runtime state
        self.session_id = self.tame_client.session_id
        self.connected = False
        
        logger.info(f"Initialized TameMCPAgent - Session: {self.session_id}")
    
    async def connect_to_server(self, server_params: StdioServerParameters) -> None:
        """Connect to an MCP server and discover tools."""
        try:
            logger.info(f"Connecting to MCP server: {server_params.command}")
            
            # Connect and initialize
            self.mcp_session = await stdio_client(server_params).__aenter__()
            init_result = await self.mcp_session.initialize()
            
            # Discover available tools
            tools_result = await self.mcp_session.list_tools()
            self.available_tools = {tool.name: tool for tool in tools_result.tools}
            
            # Generate metadata for tools
            self._generate_tool_metadata()
            
            self.connected = True
            logger.info(f"Connected successfully. Available tools: {list(self.available_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    def _generate_tool_metadata(self) -> None:
        """Generate metadata for discovered tools."""
        for tool_name, tool in self.available_tools.items():
            # Categorize tools based on name and description
            category = self._categorize_tool(tool_name, tool.description)
            risk_level = self._assess_risk_level(tool_name, tool.description)
            requires_approval = risk_level == "high"
            
            self.tool_metadata[tool_name] = ToolMetadata(
                name=tool_name,
                description=tool.description,
                category=category,
                risk_level=risk_level,
                requires_approval=requires_approval,
                rate_limit=self._get_rate_limit(category)
            )
    
    def _categorize_tool(self, name: str, description: str) -> str:
        """Categorize tool based on name and description."""
        name_lower = name.lower()
        desc_lower = description.lower() if description else ""
        
        if any(keyword in name_lower for keyword in ["read", "get", "list", "search"]):
            return "read"
        elif any(keyword in name_lower for keyword in ["write", "create", "update", "modify"]):
            return "write"
        elif any(keyword in name_lower for keyword in ["delete", "remove", "destroy"]):
            return "delete"
        elif any(keyword in name_lower for keyword in ["execute", "run", "command"]):
            return "execute"
        elif any(keyword in name_lower for keyword in ["network", "http", "api", "request"]):
            return "network"
        else:
            return "utility"
    
    def _assess_risk_level(self, name: str, description: str) -> str:
        """Assess risk level of a tool."""
        name_lower = name.lower()
        desc_lower = description.lower() if description else ""
        
        # High risk operations
        high_risk_keywords = [
            "delete", "remove", "destroy", "format", "wipe",
            "execute", "run", "command", "shell", "admin",
            "sudo", "root", "system", "install", "uninstall"
        ]
        
        # Medium risk operations
        medium_risk_keywords = [
            "write", "create", "modify", "update", "change",
            "network", "http", "api", "upload", "download"
        ]
        
        if any(keyword in name_lower or keyword in desc_lower for keyword in high_risk_keywords):
            return "high"
        elif any(keyword in name_lower or keyword in desc_lower for keyword in medium_risk_keywords):
            return "medium"
        else:
            return "low"
    
    def _get_rate_limit(self, category: str) -> Optional[int]:
        """Get rate limit for tool category."""
        rate_limits = {
            "read": 100,      # 100 reads per session
            "write": 20,      # 20 writes per session
            "delete": 5,      # 5 deletes per session
            "execute": 10,    # 10 executions per session
            "network": 50,    # 50 network calls per session
            "utility": None   # No limit for utilities
        }
        return rate_limits.get(category)
    
    @tamesdk.enforce_policy(
        tool_name="mcp_tool_call",
        metadata={"source": "mcp_agent", "runtime_controlled": True}
    )
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool with comprehensive TameSDK integration.
        
        This method:
        1. Validates the tool exists
        2. Enforces policies through TameSDK
        3. Executes the tool via MCP
        4. Logs results and metrics
        5. Handles errors gracefully
        """
        
        if not self.connected or not self.mcp_session:
            raise RuntimeError("Not connected to MCP server")
        
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available")
        
        # Get tool metadata
        metadata = self.tool_metadata.get(tool_name, {})
        start_time = time.time()
        
        try:
            # Enhanced arguments with metadata for policy decision
            enhanced_args = {
                **arguments,
                "_tame_metadata": {
                    "tool_category": metadata.category if metadata else "unknown",
                    "risk_level": metadata.risk_level if metadata else "unknown",
                    "mcp_tool": True,
                    "session_id": self.session_id
                }
            }
            
            # Enforce policy through TameSDK
            decision = await self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=enhanced_args,
                metadata={
                    "mcp_agent": True,
                    "tool_category": metadata.category if metadata else "unknown",
                    "risk_level": metadata.risk_level if metadata else "unknown"
                }
            )
            
            logger.info(f"Policy decision for {tool_name}: {decision.action.value}")
            
            # Execute the tool if allowed
            if decision.is_allowed:
                logger.info(f"Executing MCP tool: {tool_name}")
                
                # Call the actual MCP tool
                mcp_result = await self.mcp_session.call_tool(tool_name, arguments)
                
                # Process MCP result
                content_parts = []
                for content in mcp_result.content:
                    if isinstance(content, types.TextContent):
                        content_parts.append(content.text)
                    else:
                        content_parts.append(str(content))
                
                execution_time = (time.time() - start_time) * 1000
                
                # Build comprehensive result
                result = {
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "success": True,
                    "content": content_parts,
                    "execution_time_ms": execution_time,
                    "mcp_session": self.session_id,
                    "policy_decision": {
                        "action": decision.action.value,
                        "rule_name": decision.rule_name,
                        "reason": decision.reason
                    },
                    "tool_metadata": metadata.__dict__ if metadata else {}
                }
                
                # Log successful execution
                try:
                    await self.tame_client.update_result(
                        decision.session_id,
                        decision.log_id,
                        result,
                        execution_time_ms=execution_time
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log result: {log_error}")
                
                logger.info(f"Tool {tool_name} executed successfully in {execution_time:.2f}ms")
                return result
            
            else:
                # This shouldn't happen with raise_on_deny=True (default)
                raise tamesdk.PolicyViolationException(decision)
        
        except (tamesdk.PolicyViolationException, tamesdk.ApprovalRequiredException) as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Log policy enforcement action
            error_result = {
                "tool_name": tool_name,
                "arguments": arguments,
                "success": False,
                "error": str(e),
                "error_type": "PolicyEnforcement",
                "execution_time_ms": execution_time,
                "policy_decision": {
                    "action": e.decision.action.value,
                    "rule_name": e.decision.rule_name,
                    "reason": e.decision.reason
                }
            }
            
            try:
                await self.tame_client.update_result(
                    e.decision.session_id,
                    e.decision.log_id,
                    error_result,
                    execution_time_ms=execution_time
                )
            except Exception as log_error:
                logger.warning(f"Failed to log policy violation: {log_error}")
            
            logger.warning(f"Tool {tool_name} blocked by policy: {e.decision.reason}")
            raise
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Log execution error
            error_result = {
                "tool_name": tool_name,
                "arguments": arguments,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time_ms": execution_time
            }
            
            # Log error if we have a decision
            if 'decision' in locals():
                try:
                    await self.tame_client.update_result(
                        decision.session_id,
                        decision.log_id,
                        error_result,
                        execution_time_ms=execution_time
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log execution error: {log_error}")
            
            logger.error(f"Tool {tool_name} execution failed: {e}")
            raise
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with metadata."""
        tools_info = []
        
        for tool_name, tool in self.available_tools.items():
            metadata = self.tool_metadata.get(tool_name)
            
            tool_info = {
                "name": tool_name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
                "metadata": metadata.__dict__ if metadata else {}
            }
            
            tools_info.append(tool_info)
        
        return tools_info
    
    async def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session activity."""
        try:
            logs = await self.tame_client.get_session_logs()
            
            # Convert to dict format for summary
            log_dicts = []
            for log in logs:
                log_dict = {
                    "tool_name": log.tool_name,
                    "timestamp": log.timestamp.isoformat(),
                    "decision": {
                        "action": log.decision.action.value if log.decision else None
                    },
                    "error": log.error
                }
                log_dicts.append(log_dict)
            
            from tamesdk.utils import create_session_summary
            summary = create_session_summary(log_dicts)
            
            # Add MCP-specific information
            summary.update({
                "mcp_server_connected": self.connected,
                "available_tools_count": len(self.available_tools),
                "tool_categories": self._get_tool_categories_summary()
            })
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get session summary: {e}")
            return {"error": str(e)}
    
    def _get_tool_categories_summary(self) -> Dict[str, int]:
        """Get summary of tools by category."""
        categories = {}
        for metadata in self.tool_metadata.values():
            category = metadata.category
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    async def test_tool_policy(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test a tool against policies without executing."""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available")
        
        metadata = self.tool_metadata.get(tool_name)
        enhanced_args = {
            **arguments,
            "_tame_metadata": {
                "tool_category": metadata.category if metadata else "unknown",
                "risk_level": metadata.risk_level if metadata else "unknown",
                "test_mode": True
            }
        }
        
        return await self.tame_client.test_policy(tool_name, enhanced_args)
    
    async def close(self):
        """Clean up resources."""
        if self.mcp_session and hasattr(self.mcp_session, '__aexit__'):
            await self.mcp_session.__aexit__(None, None, None)
        
        await self.tame_client.close()
        self.connected = False
        logger.info("TameMCPAgent closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def create_mock_mcp_server() -> Dict[str, types.Tool]:
    """Create mock MCP tools for demonstration."""
    return {
        "read_file": types.Tool(
            name="read_file",
            description="Read contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
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
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        ),
        "delete_file": types.Tool(
            name="delete_file",
            description="Delete a file from the filesystem",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to delete"}
                },
                "required": ["path"]
            }
        ),
        "execute_command": types.Tool(
            name="execute_command",
            description="Execute a system command",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute"}
                },
                "required": ["command"]
            }
        ),
        "http_request": types.Tool(
            name="http_request",
            description="Make an HTTP request",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to request"},
                    "method": {"type": "string", "description": "HTTP method"}
                },
                "required": ["url"]
            }
        )
    }


class MockMCPSession:
    """Mock MCP session for demonstration."""
    
    def __init__(self, tools: Dict[str, types.Tool]):
        self.tools = tools
    
    async def initialize(self):
        return {"version": "1.0", "capabilities": {}}
    
    async def list_tools(self):
        return type('ToolsResult', (), {'tools': list(self.tools.values())})()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        # Simulate tool execution
        await asyncio.sleep(0.1)
        
        if tool_name == "read_file":
            content = f"Contents of {arguments['path']}: Mock file content"
        elif tool_name == "write_file":
            content = f"Successfully wrote to {arguments['path']}"
        elif tool_name == "delete_file":
            content = f"Successfully deleted {arguments['path']}"
        elif tool_name == "execute_command":
            content = f"Executed command: {arguments['command']}"
        elif tool_name == "http_request":
            content = f"HTTP {arguments.get('method', 'GET')} to {arguments['url']}: 200 OK"
        else:
            raise Exception(f"Unknown tool: {tool_name}")
        
        return type('Result', (), {
            'content': [types.TextContent(type="text", text=content)]
        })()


async def demonstrate_mcp_agent():
    """Demonstrate the TameMCPAgent with various scenarios."""
    
    print("🚀 TameMCP Agent with TameSDK Integration Demo")
    print("=" * 60)
    
    # Initialize the agent
    agent = TameMCPAgent(
        agent_id="demo-mcp-agent",
        user_id="demo-user",
        tame_api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        tame_api_key=os.getenv("TAME_API_KEY")
    )
    
    try:
        # Mock connection to MCP server
        mock_tools = await create_mock_mcp_server()
        agent.available_tools = mock_tools
        agent.mcp_session = MockMCPSession(mock_tools)
        agent._generate_tool_metadata()
        agent.connected = True
        
        print(f"📡 Connected to mock MCP server")
        print(f"🔧 Available tools: {list(agent.available_tools.keys())}")
        
        # Example 1: List available tools
        print("\n📋 Example 1: Available Tools")
        tools_info = await agent.list_available_tools()
        for tool in tools_info:
            metadata = tool['metadata']
            risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
            print(f"  {risk_emoji.get(metadata.get('risk_level', 'low'), '⚪')} {tool['name']}: {tool['description']}")
        
        # Example 2: Execute safe operations
        print("\n✅ Example 2: Safe Operations")
        safe_operations = [
            ("read_file", {"path": "/tmp/safe_file.txt"}),
            ("http_request", {"url": "https://api.example.com/status", "method": "GET"})
        ]
        
        for tool_name, args in safe_operations:
            try:
                result = await agent.execute_tool(tool_name, args)
                print(f"  ✅ {tool_name}: {result['content'][0][:50]}...")
            except Exception as e:
                print(f"  ❌ {tool_name}: {e}")
        
        # Example 3: Risky operations (may be blocked)
        print("\n⚠️ Example 3: Risky Operations")
        risky_operations = [
            ("delete_file", {"path": "/important/system_file.conf"}),
            ("execute_command", {"command": "rm -rf /"}),
            ("write_file", {"path": "/etc/passwd", "content": "malicious content"})
        ]
        
        for tool_name, args in risky_operations:
            try:
                result = await agent.execute_tool(tool_name, args)
                print(f"  ✅ {tool_name}: {result['content'][0][:50]}...")
            except tamesdk.PolicyViolationException as e:
                print(f"  ❌ {tool_name}: Blocked - {e.decision.reason}")
            except tamesdk.ApprovalRequiredException as e:
                print(f"  ⏳ {tool_name}: Approval required - {e.decision.reason}")
            except Exception as e:
                print(f"  ❌ {tool_name}: Error - {e}")
        
        # Example 4: Policy testing
        print("\n🧪 Example 4: Policy Testing")
        test_cases = [
            ("read_file", {"path": "/home/user/document.txt"}),
            ("write_file", {"path": "/tmp/output.txt", "content": "safe content"}),
            ("delete_file", {"path": "/var/log/old.log"})
        ]
        
        for tool_name, args in test_cases:
            try:
                test_result = await agent.test_tool_policy(tool_name, args)
                decision = test_result.get("decision", "unknown")
                reason = test_result.get("reason", "No reason")
                
                emoji = {"allow": "✅", "deny": "❌", "approve": "⏳"}.get(decision, "❓")
                print(f"  {emoji} {tool_name}: {decision} - {reason}")
            except Exception as e:
                print(f"  ❌ {tool_name}: Test error - {e}")
        
        # Example 5: Session summary
        print("\n📊 Example 5: Session Summary")
        summary = await agent.get_session_summary()
        print(f"  Total actions: {summary.get('total_actions', 0)}")
        print(f"  Allowed: {summary.get('allowed_actions', 0)}")
        print(f"  Denied: {summary.get('denied_actions', 0)}")
        print(f"  Approval requests: {summary.get('approval_requests', 0)}")
        print(f"  Tools by category: {summary.get('tool_categories', {})}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await agent.close()
    
    print("\n✅ Demo completed!")


async def demonstrate_integration_patterns():
    """Demonstrate various integration patterns."""
    
    print("\n🔄 Integration Patterns Demo")
    print("=" * 40)
    
    # Pattern 1: Decorator-based integration
    print("\n🎯 Pattern 1: Decorator Integration")
    
    @tamesdk.enforce_policy(
        tool_name="mcp_file_operation",
        metadata={"integration_pattern": "decorator"}
    )
    async def mcp_file_operation(operation: str, path: str, content: str = None):
        """Example MCP operation with decorator."""
        await asyncio.sleep(0.1)  # Simulate work
        if operation == "read":
            return f"Read content from {path}"
        elif operation == "write":
            return f"Wrote content to {path}"
        else:
            return f"Performed {operation} on {path}"
    
    try:
        result = await mcp_file_operation("read", "/tmp/test.txt")
        print(f"  ✅ Decorator result: {result}")
    except Exception as e:
        print(f"  ❌ Decorator error: {e}")
    
    # Pattern 2: Context manager integration
    print("\n🏗️ Pattern 2: Context Manager Integration")
    
    async with tamesdk.AsyncClient() as client:
        try:
            decision = await client.enforce(
                "mcp_context_operation",
                {"action": "deploy", "target": "production"},
                metadata={"integration_pattern": "context_manager"}
            )
            
            if decision.is_allowed:
                # Simulate MCP operation
                await asyncio.sleep(0.1)
                result = "Deployment successful"
                
                await client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result}
                )
                print(f"  ✅ Context manager result: {result}")
            
        except Exception as e:
            print(f"  ❌ Context manager error: {e}")
    
    # Pattern 3: Batch operations
    print("\n📦 Pattern 3: Batch Operations")
    
    async with tamesdk.AsyncClient() as client:
        batch_operations = [
            ("file_backup", {"path": f"/data/file_{i}.txt"})
            for i in range(5)
        ]
        
        results = []
        for tool_name, args in batch_operations:
            try:
                decision = await client.enforce(tool_name, args)
                if decision.is_allowed:
                    # Simulate operation
                    result = f"Backed up {args['path']}"
                    results.append(result)
                    
                    await client.update_result(
                        decision.session_id, 
                        decision.log_id,
                        {"status": "success", "result": result}
                    )
            except Exception as e:
                results.append(f"Error: {e}")
        
        print(f"  ✅ Batch completed: {len(results)} operations")


if __name__ == "__main__":
    print("🎯 TameSDK MCP Agent Integration Examples")
    print("=" * 55)
    
    try:
        # Main demonstration
        asyncio.run(demonstrate_mcp_agent())
        
        # Integration patterns
        asyncio.run(demonstrate_integration_patterns())
        
        print("\n🎉 All MCP examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()