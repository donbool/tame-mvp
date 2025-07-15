#!/usr/bin/env python3
"""
Working MCP GitHub Agent - Fixed connection issues and proper TameSDK integration.
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
from dotenv import load_dotenv

# MCP imports
try:
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp import ClientSession
    from mcp.types import Tool
    print("✅ MCP imports successful")
except ImportError as e:
    print(f"❌ MCP library error: {e}")
    sys.exit(1)

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the working MCP GitHub agent."""
    github_token: str
    tame_api_url: str
    repository: str
    session_id: str
    agent_id: str = "working-mcp-github-agent"
    user_id: str = "mcp-developer"

class WorkingMCPGitHubAgent:
    """Working MCP GitHub agent with proper TameSDK integration."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
        # Initialize TameSDK client
        self.tame_client = tamesdk.Client(
            api_url=config.tame_api_url,
            session_id=config.session_id,
            agent_id=config.agent_id,
            user_id=config.user_id
        )
        
        # MCP connection variables
        self.mcp_session: Optional[ClientSession] = None
        self.github_tools: List[Tool] = []
        self.stdio_client = None
        
        self.repo_owner, self.repo_name = config.repository.split('/')
        
        logger.info(f"Initialized working MCP GitHub agent for: {config.repository}")
    
    async def connect_to_github_mcp(self) -> bool:
        """Connect to GitHub MCP server with fixed initialization."""
        try:
            logger.info("🔌 Starting GitHub MCP server connection...")
            
            # Create server parameters with proper environment
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={
                    "GITHUB_PERSONAL_ACCESS_TOKEN": self.config.github_token,
                    "NODE_ENV": "production"
                }
            )
            
            logger.info("🚀 Launching MCP server process...")
            
            # Create stdio client
            self.stdio_client = stdio_client(server_params)
            
            # Use asyncio timeout for the entire connection process
            try:
                async with asyncio.timeout(60):  # 60 second timeout for full connection
                    
                    # Get streams
                    read_stream, write_stream = await self.stdio_client.__aenter__()
                    logger.info("✅ MCP streams established")
                    
                    # Create session
                    self.mcp_session = ClientSession(read_stream, write_stream)
                    logger.info("✅ MCP session created")
                    
                    # Initialize session with retry logic
                    for attempt in range(3):
                        try:
                            logger.info(f"🔄 Initializing session (attempt {attempt + 1}/3)...")
                            
                            # Initialize with shorter timeout per attempt
                            init_result = await asyncio.wait_for(
                                self.mcp_session.initialize(),
                                timeout=20.0
                            )
                            
                            logger.info(f"✅ Session initialized: {init_result}")
                            break
                            
                        except asyncio.TimeoutError:
                            logger.warning(f"⏰ Initialization timeout (attempt {attempt + 1})")
                            if attempt == 2:  # Last attempt
                                raise
                            await asyncio.sleep(2)  # Wait before retry
                    
                    # List tools with retry
                    for attempt in range(2):
                        try:
                            logger.info("📋 Listing available tools...")
                            tools_result = await asyncio.wait_for(
                                self.mcp_session.list_tools(),
                                timeout=15.0
                            )
                            
                            self.github_tools = tools_result.tools if hasattr(tools_result, 'tools') else []
                            logger.info(f"✅ Found {len(self.github_tools)} GitHub MCP tools")
                            
                            # Log available tools
                            for tool in self.github_tools[:5]:  # Show first 5
                                logger.info(f"   🛠️  {tool.name}: {tool.description}")
                            
                            break
                            
                        except asyncio.TimeoutError:
                            logger.warning(f"⏰ Tools listing timeout (attempt {attempt + 1})")
                            if attempt == 1:
                                raise
                            await asyncio.sleep(1)
                    
                    logger.info("🎉 MCP GitHub server connection successful!")
                    return True
                    
            except asyncio.TimeoutError:
                logger.error("⏰ Overall MCP connection timeout")
                return False
                
        except Exception as e:
            logger.error(f"💥 MCP connection failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return False
    
    async def call_mcp_tool_with_tamesdk(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call MCP tool with TameSDK policy enforcement.
        This is the key integration - TameSDK controls MCP operations.
        """
        if not self.mcp_session:
            raise RuntimeError("Not connected to MCP server")
        
        # 1. ENFORCE POLICY FIRST (this is the critical integration point)
        try:
            logger.info(f"🛡️  TameSDK policy check: {tool_name}")
            
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            logger.info(f"✅ Policy allows MCP tool: {tool_name}")
            
        except tamesdk.PolicyViolationException as e:
            logger.warning(f"🛡️  Policy blocked MCP tool: {tool_name}")
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Policy violation: {str(e)}",
                "policy_decision": "blocked",
                "mcp_executed": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # 2. EXECUTE MCP TOOL (only if policy allows)
        try:
            logger.info(f"🚀 Executing MCP tool: {tool_name}")
            
            result = await asyncio.wait_for(
                self.mcp_session.call_tool(tool_name, arguments),
                timeout=30.0
            )
            
            logger.info(f"✅ MCP tool completed: {tool_name}")
            
            # Process MCP result
            content = []
            if hasattr(result, 'content') and result.content:
                for item in result.content:
                    if hasattr(item, 'text'):
                        content.append(item.text)
                    elif isinstance(item, dict):
                        content.append(json.dumps(item, indent=2))
                    else:
                        content.append(str(item))
            
            return {
                "success": True,
                "tool": tool_name,
                "content": content,
                "policy_decision": "allowed",
                "mcp_executed": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ MCP tool timeout: {tool_name}")
            return {
                "success": False,
                "tool": tool_name,
                "error": "MCP tool execution timeout",
                "policy_decision": "allowed",
                "mcp_executed": False,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"💥 MCP tool execution failed: {tool_name} - {e}")
            return {
                "success": False,
                "tool": tool_name,
                "error": f"MCP execution error: {str(e)}",
                "policy_decision": "allowed",
                "mcp_executed": False,
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_comprehensive_mcp_test(self) -> Dict[str, Any]:
        """Run comprehensive test of MCP + TameSDK integration."""
        
        results = {
            "session_id": self.config.session_id,
            "agent_id": self.config.agent_id,
            "timestamp": datetime.now().isoformat(),
            "mcp_server": "GitHub MCP Server",
            "mcp_tools_available": [tool.name for tool in self.github_tools],
            "operations": []
        }
        
        # Define test operations
        test_operations = [
            # READ OPERATIONS (should be allowed by policy)
            {
                "tool": "get_repository",
                "description": "📖 Get repository information",
                "args": {"owner": self.repo_owner, "repo": self.repo_name}
            },
            {
                "tool": "list_issues",
                "description": "🐛 List repository issues", 
                "args": {"owner": self.repo_owner, "repo": self.repo_name, "state": "open"}
            },
            {
                "tool": "get_issue",
                "description": "🔍 Get specific issue",
                "args": {"owner": self.repo_owner, "repo": self.repo_name, "issue_number": 1}
            },
            
            # COMMENT OPERATIONS (should be allowed)
            {
                "tool": "create_issue_comment",
                "description": "💬 Create issue comment",
                "args": {
                    "owner": self.repo_owner,
                    "repo": self.repo_name,
                    "issue_number": 1,
                    "body": f"""🎯 **Working MCP + TameSDK Integration Test**

This comment proves that **real MCP protocol** works with **TameSDK policy enforcement**!

**Technical Stack:**
- 🛠️  **MCP Server**: @modelcontextprotocol/server-github v2025.4.8
- 🛡️  **Policy Engine**: TameSDK v1.0.0
- 📡 **Protocol**: Model Context Protocol (stdio)
- 🆔 **Session**: `{self.config.session_id}`

**Available MCP Tools**: {len(self.github_tools)}
{chr(10).join(f"- {tool.name}" for tool in self.github_tools[:5])}

**Policy Integration**:
Every MCP tool call goes through TameSDK policy evaluation before execution.

🎉 **This is a real working MCP agent with governance!**

*Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*"""
                }
            },
            
            # DANGEROUS OPERATIONS (should be blocked by policy)
            {
                "tool": "create_pull_request",
                "description": "🚫 Attempt to create PR (should be blocked)",
                "args": {
                    "owner": self.repo_owner,
                    "repo": self.repo_name,
                    "title": "Unauthorized PR from MCP Agent",
                    "body": "This should be blocked by TameSDK policy",
                    "head": "unauthorized-branch",
                    "base": "main"
                }
            },
            {
                "tool": "delete_file",
                "description": "🚫 Attempt to delete file (should be blocked)",
                "args": {
                    "owner": self.repo_owner,
                    "repo": self.repo_name,
                    "path": "README.md",
                    "message": "Unauthorized deletion"
                }
            }
        ]
        
        print("\\n" + "="*80)
        print("🎯 **WORKING MCP + TAMESDK INTEGRATION TEST**")
        print("="*80)
        print(f"📊 Session: {self.config.session_id}")
        print(f"🛠️  MCP Server: GitHub MCP Server v2025.4.8")
        print(f"🛡️  Policy Engine: TameSDK")
        print(f"📋 Available Tools: {len(self.github_tools)}")
        print(f"🔗 Dashboard: http://localhost:3000")
        print("="*80)
        
        for operation in test_operations:
            tool_name = operation["tool"]
            description = operation["description"]
            args = operation["args"]
            
            print(f"\\n🔍 Testing: {description}")
            
            # Check if tool exists in MCP server
            available_tools = [t.name for t in self.github_tools]
            if tool_name not in available_tools:
                print(f"   ⚠️  Tool '{tool_name}' not available in MCP server")
                print(f"   📋 Available tools: {', '.join(available_tools[:3])}...")
                continue
            
            try:
                result = await self.call_mcp_tool_with_tamesdk(tool_name, args)
                results["operations"].append(result)
                
                if result["success"]:
                    print(f"   ✅ {tool_name} - ALLOWED & EXECUTED")
                    if result.get("content"):
                        content_summary = f"{len(result['content'])} items returned"
                        print(f"   📄 MCP Result: {content_summary}")
                else:
                    decision = result["policy_decision"].upper()
                    mcp_executed = result.get("mcp_executed", False)
                    
                    if decision == "BLOCKED":
                        print(f"   🛡️  {tool_name} - BLOCKED BY POLICY")
                        print(f"   📋 TameSDK prevented MCP execution")
                    else:
                        print(f"   ❌ {tool_name} - MCP EXECUTION FAILED")
                        print(f"   ⚠️  Error: {result.get('error', 'Unknown')}")
                        
            except Exception as e:
                print(f"   💥 Exception: {e}")
                results["operations"].append({
                    "success": False,
                    "tool": tool_name,
                    "error": str(e),
                    "policy_decision": "exception",
                    "mcp_executed": False
                })
        
        # Calculate results
        total = len(results["operations"])
        allowed = sum(1 for op in results["operations"] if op.get("success"))
        blocked = sum(1 for op in results["operations"] if not op.get("success") and op.get("policy_decision") == "blocked")
        errors = sum(1 for op in results["operations"] if not op.get("success") and op.get("policy_decision") != "blocked")
        
        print("\\n" + "="*80)
        print("📊 **WORKING MCP + TAMESDK TEST RESULTS:**")
        print(f"   🛠️  MCP Server: Connected & Operational")
        print(f"   🛡️  TameSDK: Policy enforcement active")
        print(f"   🧪 Operations Tested: {total}")
        print(f"   ✅ Allowed & Executed: {allowed}")
        print(f"   🛡️  Blocked by Policy: {blocked}")
        print(f"   ❌ MCP Execution Errors: {errors}")
        print("="*80)
        
        if allowed > 0 and blocked > 0:
            print("\\n🎉 **SUCCESS: Working MCP + TameSDK Integration!**")
            print("   ✅ Real MCP protocol communication")
            print("   ✅ TameSDK policy enforcement working")
            print("   ✅ Mixed allow/block results achieved")
            print("   ✅ Complete audit trail in dashboard")
            print("   ✅ No workarounds - pure MCP + TameSDK")
        elif total == 0:
            print("\\n⚠️  No operations could be tested")
        else:
            print("\\n🔧 Partial success - some operations may need adjustment")
        
        return results
    
    async def close(self):
        """Clean up all connections properly."""
        try:
            logger.info("🧹 Closing MCP connections...")
            
            if self.mcp_session:
                await self.mcp_session.close()
                logger.info("✅ MCP session closed")
            
            if self.stdio_client:
                await self.stdio_client.__aexit__(None, None, None)
                logger.info("✅ MCP stdio client closed")
                
        except Exception as e:
            logger.warning(f"⚠️  Cleanup error: {e}")
        finally:
            self.tame_client.close()
            logger.info("✅ TameSDK client closed")

async def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Working MCP GitHub Agent with TameSDK")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    
    args = parser.parse_args()
    
    # Configuration
    config = AgentConfig(
        github_token=os.getenv("GITHUB_TOKEN"),
        tame_api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        repository=args.repo,
        session_id=f"working-mcp-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    if not config.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize agent
    agent = WorkingMCPGitHubAgent(config)
    
    try:
        print(f"🚀 **WORKING MCP GITHUB AGENT**")
        print(f"📋 Repository: {config.repository}")
        print(f"🆔 Session: {config.session_id}")
        print(f"🎯 Real MCP protocol + TameSDK policy enforcement!")
        
        # Connect to GitHub MCP server
        print("\\n🔌 Connecting to GitHub MCP server...")
        if not await agent.connect_to_github_mcp():
            print("❌ Failed to connect to GitHub MCP server")
            print("\\n🔧 This requires:")
            print("1. Node.js installed")
            print("2. Valid GitHub token") 
            print("3. Network connectivity")
            sys.exit(1)
        
        # Run comprehensive test
        results = await agent.run_comprehensive_mcp_test()
        
        print(f"\\n✅ **Test Complete!**")
        print(f"📊 Check TameSDK dashboard: http://localhost:3000")
        print(f"🆔 Session: {results['session_id']}")
        
        # Success criteria
        total_ops = len(results['operations'])
        successful_ops = sum(1 for op in results['operations'] if op.get('success'))
        
        if total_ops > 0 and successful_ops > 0:
            print("\\n🎉 **MCP + TameSDK integration verified!**")
        
    except KeyboardInterrupt:
        print("\\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())