#!/usr/bin/env python3
"""
Real MCP GitHub Agent with TameSDK Policy Enforcement
This uses the actual MCP protocol with GitHub MCP server and TameSDK enforcement.
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

import tamesdk
from openai import OpenAI
from dotenv import load_dotenv

# MCP imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import Tool, TextContent
except ImportError as e:
    print("Error: MCP library not found. Install with: pip install mcp")
    print(f"Import error: {e}")
    sys.exit(1)

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the real MCP GitHub agent."""
    openai_api_key: str
    github_token: str
    tame_api_url: str
    repository: str
    session_id: str
    agent_id: str = "real-mcp-github-agent"
    user_id: str = "mcp-tester"

class RealMCPGitHubAgent:
    """Real MCP GitHub agent with TameSDK policy enforcement."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        
        # Initialize TameSDK client
        self.tame_client = tamesdk.Client(
            api_url=config.tame_api_url,
            session_id=config.session_id,
            agent_id=config.agent_id,
            user_id=config.user_id
        )
        
        # MCP session will be set when connected
        self.mcp_session: Optional[ClientSession] = None
        self.github_tools: List[Tool] = []
        
        self.repo_owner, self.repo_name = config.repository.split('/')
        
        logger.info(f"Initialized real MCP GitHub agent for: {config.repository}")
    
    async def connect_to_github_mcp(self) -> bool:
        """Connect to the real GitHub MCP server."""
        try:
            logger.info("Connecting to GitHub MCP server...")
            
            # GitHub MCP server parameters
            server_params = StdioServerParameters(
                command="npx",
                args=[
                    "-y", "@modelcontextprotocol/server-github"
                ],
                env={
                    "GITHUB_PERSONAL_ACCESS_TOKEN": self.config.github_token
                }
            )
            
            logger.info("Starting MCP server process...")
            
            # Connect to MCP server using proper async context manager
            self.stdio_client = stdio_client(server_params)
            read_stream, write_stream = await self.stdio_client.__aenter__()
            
            # Create MCP session
            self.mcp_session = ClientSession(read_stream, write_stream)
            
            logger.info("Initializing MCP session...")
            
            # Initialize the session
            init_result = await self.mcp_session.initialize()
            logger.info(f"MCP session initialized: {init_result}")
            
            # Get available tools
            logger.info("Listing available GitHub MCP tools...")
            tools_result = await self.mcp_session.list_tools()
            self.github_tools = tools_result.tools
            
            logger.info(f"✅ Connected to GitHub MCP server!")
            logger.info(f"📋 Available tools: {[tool.name for tool in self.github_tools]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to GitHub MCP server: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def call_mcp_tool_with_enforcement(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool with TameSDK policy enforcement.
        This is the key integration point between MCP and TameSDK.
        """
        if not self.mcp_session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            # 1. FIRST: Enforce policy via TameSDK
            logger.info(f"🛡️  Enforcing policy for MCP tool: {tool_name}")
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            logger.info(f"✅ Policy check passed for: {tool_name}")
            
            # 2. SECOND: Execute MCP tool call (only if policy allows)
            logger.info(f"📞 Calling MCP tool: {tool_name}")
            result = await self.mcp_session.call_tool(tool_name, arguments)
            
            logger.info(f"✅ MCP tool call completed: {tool_name}")
            
            # Extract content from MCP result
            content = []
            if hasattr(result, 'content') and result.content:
                for item in result.content:
                    if hasattr(item, 'text'):
                        content.append(item.text)
                    elif isinstance(item, dict) and 'text' in item:
                        content.append(item['text'])
                    else:
                        content.append(str(item))
            
            return {
                "success": True,
                "tool": tool_name,
                "content": content,
                "policy_decision": "allowed",
                "timestamp": datetime.now().isoformat()
            }
            
        except tamesdk.PolicyViolationException as e:
            logger.warning(f"🛡️  Policy blocked MCP tool: {tool_name} - {e}")
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "policy_decision": "blocked",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"💥 MCP tool call failed: {tool_name} - {e}")
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "policy_decision": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information via MCP."""
        return await self.call_mcp_tool_with_enforcement(
            "get_repository",
            {"owner": self.repo_owner, "repo": self.repo_name}
        )
    
    async def list_pull_requests(self) -> Dict[str, Any]:
        """List pull requests via MCP."""
        return await self.call_mcp_tool_with_enforcement(
            "list_pull_requests",
            {"owner": self.repo_owner, "repo": self.repo_name}
        )
    
    async def get_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """Get specific pull request via MCP."""
        return await self.call_mcp_tool_with_enforcement(
            "get_pull_request",
            {"owner": self.repo_owner, "repo": self.repo_name, "pull_number": pr_number}
        )
    
    async def create_issue_comment(self, issue_number: int, body: str) -> Dict[str, Any]:
        """Create issue comment via MCP."""
        return await self.call_mcp_tool_with_enforcement(
            "create_issue_comment",
            {
                "owner": self.repo_owner, 
                "repo": self.repo_name, 
                "issue_number": issue_number,
                "body": body
            }
        )
    
    async def create_issue(self, title: str, body: str, labels: List[str] = None) -> Dict[str, Any]:
        """Create issue via MCP."""
        args = {
            "owner": self.repo_owner,
            "repo": self.repo_name,
            "title": title,
            "body": body
        }
        if labels:
            args["labels"] = labels
            
        return await self.call_mcp_tool_with_enforcement("create_issue", args)
    
    async def list_repository_issues(self) -> Dict[str, Any]:
        """List repository issues via MCP."""
        return await self.call_mcp_tool_with_enforcement(
            "list_issues",
            {"owner": self.repo_owner, "repo": self.repo_name}
        )
    
    async def get_file_contents(self, path: str, ref: str = "main") -> Dict[str, Any]:
        """Get file contents via MCP."""
        return await self.call_mcp_tool_with_enforcement(
            "get_file_contents",
            {"owner": self.repo_owner, "repo": self.repo_name, "path": path, "ref": ref}
        )
    
    # Dangerous operations that should be blocked by policy
    async def create_pull_request(self, title: str, body: str, head: str, base: str) -> Dict[str, Any]:
        """Attempt to create PR via MCP (should be blocked)."""
        return await self.call_mcp_tool_with_enforcement(
            "create_pull_request",
            {
                "owner": self.repo_owner,
                "repo": self.repo_name,
                "title": title,
                "body": body,
                "head": head,
                "base": base
            }
        )
    
    async def update_file(self, path: str, content: str, message: str) -> Dict[str, Any]:
        """Attempt to update file via MCP (should be blocked)."""
        import base64
        return await self.call_mcp_tool_with_enforcement(
            "update_file",
            {
                "owner": self.repo_owner,
                "repo": self.repo_name,
                "path": path,
                "content": base64.b64encode(content.encode()).decode(),
                "message": message
            }
        )
    
    async def run_real_mcp_demo(self) -> Dict[str, Any]:
        """Run comprehensive demo using real MCP tools with TameSDK enforcement."""
        results = {
            "session_id": self.config.session_id,
            "agent_id": self.config.agent_id,
            "timestamp": datetime.now().isoformat(),
            "mcp_tools_available": [tool.name for tool in self.github_tools],
            "operations": []
        }
        
        # Define operations to test
        operations = [
            # READ OPERATIONS (should be allowed)
            ("📖 Get Repository Info", lambda: self.get_repository_info()),
            ("📋 List Pull Requests", lambda: self.list_pull_requests()),
            ("🔍 Get Specific PR", lambda: self.get_pull_request(1)),
            ("🐛 List Issues", lambda: self.list_repository_issues()),
            ("📄 Get File Contents", lambda: self.get_file_contents("README.md")),
            
            # COMMENT OPERATIONS (should be allowed)
            ("💬 Create Issue Comment", lambda: self.create_issue_comment(
                1, 
                f"""🤖 **Real MCP Agent Test**

This comment was posted by a **real MCP GitHub agent** using:
- ✅ **Real MCP protocol** (not direct API calls)
- ✅ **Real TameSDK policy enforcement**
- ✅ **Real GitHub MCP server**

**Session Details:**
- Session ID: `{self.config.session_id}`
- Agent: `{self.config.agent_id}`
- MCP Tools: {len(self.github_tools)} available
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

This proves that TameSDK can control real MCP agents! 🎯"""
            )),
            
            ("📝 Create Security Issue", lambda: self.create_issue(
                "🔒 Real MCP Agent Security Test",
                f"""## Real MCP Agent Security Demo

This issue was created by a **real MCP GitHub agent** with TameSDK enforcement.

### MCP Integration Details:
- **Protocol**: Model Context Protocol (MCP)
- **Server**: @modelcontextprotocol/server-github
- **Policy Engine**: TameSDK enforcement
- **Session**: `{self.config.session_id}`

### Available MCP Tools:
{chr(10).join(f"- {tool.name}" for tool in self.github_tools)}

### Policy Enforcement:
Every MCP tool call goes through TameSDK policy evaluation before execution.

*This is a real-world example of AI agent governance using MCP + TameSDK!*""",
                ["security", "mcp", "tamesdk", "demo"]
            )),
            
            # DANGEROUS OPERATIONS (should be blocked)
            ("🚫 Attempt to Create PR", lambda: self.create_pull_request(
                "Unauthorized PR", "This should be blocked", "feature", "main"
            )),
            ("🚫 Attempt to Update File", lambda: self.update_file(
                "DANGEROUS.txt", "This should not be created", "Unauthorized file creation"
            )),
        ]
        
        print("\\n" + "="*80)
        print("🚀 **REAL MCP GITHUB AGENT WITH TAMESDK ENFORCEMENT**")
        print("="*80)
        print(f"📊 Session: {self.config.session_id}")
        print(f"🔗 Dashboard: http://localhost:3000")
        print(f"🛠️  MCP Tools Available: {len(self.github_tools)}")
        print(f"🛡️  Every MCP call goes through TameSDK policy enforcement!")
        print("="*80)
        
        for description, operation in operations:
            print(f"\\n🔍 Testing: {description}")
            
            try:
                result = await operation()
                results["operations"].append(result)
                
                if result["success"]:
                    print(f"   ✅ {result['tool']} - ALLOWED (via MCP)")
                    if result.get("content"):
                        print(f"   📄 Result: {len(result['content'])} items returned")
                else:
                    print(f"   🛡️  {result['tool']} - {result['policy_decision'].upper()}")
                    if "policy" in result.get("error", "").lower():
                        print(f"   📋 TameSDK blocked this MCP operation")
                    else:
                        print(f"   ⚠️  Error: {result.get('error', 'Unknown error')}")
                        
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "policy_decision": "error"
                }
                results["operations"].append(error_result)
                print(f"   💥 ERROR: {e}")
        
        # Summary
        allowed = sum(1 for op in results["operations"] if op.get("success"))
        blocked = sum(1 for op in results["operations"] if not op.get("success"))
        
        print("\\n" + "="*80)
        print("📊 **REAL MCP AGENT DEMO RESULTS:**")
        print(f"   ✅ Allowed MCP Operations: {allowed}")
        print(f"   🛡️  Blocked MCP Operations: {blocked}")
        print(f"   🛠️  Total MCP Tools Available: {len(self.github_tools)}")
        print(f"   📊 All TameSDK decisions logged to dashboard")
        print("="*80)
        print("\\n🎯 **This proves real MCP + TameSDK integration works!**")
        print("   - Real MCP protocol (not API workarounds)")
        print("   - Real TameSDK policy enforcement")
        print("   - Real GitHub operations via MCP server")
        print("   - Complete audit trail in dashboard")
        
        return results
    
    async def close(self):
        """Clean up connections."""
        try:
            if self.mcp_session:
                # Close MCP session
                await self.mcp_session.close()
            
            if hasattr(self, 'stdio_client'):
                # Close stdio client
                await self.stdio_client.__aexit__(None, None, None)
                
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
        finally:
            # Close TameSDK client
            self.tame_client.close()

async def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real MCP GitHub Agent with TameSDK Enforcement")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    
    args = parser.parse_args()
    
    # Configuration
    config = AgentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        github_token=os.getenv("GITHUB_TOKEN"),
        tame_api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        repository=args.repo,
        session_id=f"real-mcp-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    if not config.openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable required")
        sys.exit(1)
    
    if not config.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize agent
    agent = RealMCPGitHubAgent(config)
    
    try:
        print(f"🚀 **REAL MCP GITHUB AGENT**")
        print(f"📋 Repository: {config.repository}")
        print(f"🆔 Session: {config.session_id}")
        print(f"🛡️  Real MCP + TameSDK integration!")
        
        # Connect to GitHub MCP server
        print("\\n🔌 Connecting to GitHub MCP server...")
        if not await agent.connect_to_github_mcp():
            print("❌ Failed to connect to GitHub MCP server")
            sys.exit(1)
        
        # Run comprehensive demo
        results = await agent.run_real_mcp_demo()
        
        print(f"\\n✅ **Real MCP Demo Complete!**")
        print(f"Check TameSDK dashboard for session: {results['session_id']}")
        
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())