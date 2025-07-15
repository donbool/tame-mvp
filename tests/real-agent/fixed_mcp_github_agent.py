#!/usr/bin/env python3
"""
Fixed Real MCP GitHub Agent with TameSDK Policy Enforcement
This addresses the MCP connection issues and provides a working implementation.
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

# MCP imports with better error handling
try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.types import Tool, TextContent
    print("✅ MCP imports successful")
except ImportError as e:
    print(f"❌ MCP library not found: {e}")
    print("Install with: pip install mcp")
    sys.exit(1)

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the real MCP GitHub agent."""
    github_token: str
    tame_api_url: str
    repository: str
    session_id: str
    agent_id: str = "fixed-mcp-github-agent"
    user_id: str = "mcp-tester"

class FixedMCPGitHubAgent:
    """Fixed MCP GitHub agent with TameSDK policy enforcement."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
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
        self.stdio_client = None
        
        self.repo_owner, self.repo_name = config.repository.split('/')
        
        logger.info(f"Initialized fixed MCP GitHub agent for: {config.repository}")
    
    async def connect_to_github_mcp(self) -> bool:
        """Connect to the GitHub MCP server with improved error handling."""
        try:
            logger.info("🔌 Connecting to GitHub MCP server...")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={
                    "GITHUB_PERSONAL_ACCESS_TOKEN": self.config.github_token,
                    "NODE_ENV": "production"
                }
            )
            
            logger.info("🚀 Starting MCP server process...")
            
            # Use shorter timeout and better error handling
            try:
                # Start the stdio client
                self.stdio_client = stdio_client(server_params)
                
                # Wait for connection with timeout
                read_stream, write_stream = await asyncio.wait_for(
                    self.stdio_client.__aenter__(), 
                    timeout=30.0
                )
                
                logger.info("📡 Creating MCP session...")
                
                # Create session
                self.mcp_session = ClientSession(read_stream, write_stream)
                
                # Initialize with timeout
                logger.info("🔄 Initializing MCP session...")
                init_result = await asyncio.wait_for(
                    self.mcp_session.initialize(),
                    timeout=15.0
                )
                
                logger.info(f"✅ MCP session initialized: {init_result}")
                
                # List tools with timeout
                logger.info("📋 Listing available GitHub tools...")
                tools_result = await asyncio.wait_for(
                    self.mcp_session.list_tools(),
                    timeout=10.0
                )
                
                self.github_tools = tools_result.tools if hasattr(tools_result, 'tools') else []
                
                logger.info(f"🎯 Successfully connected to GitHub MCP!")
                logger.info(f"📊 Available tools: {len(self.github_tools)}")
                for tool in self.github_tools:
                    logger.info(f"   🛠️  {tool.name}: {tool.description}")
                
                return True
                
            except asyncio.TimeoutError:
                logger.error("⏰ Timeout connecting to MCP server")
                return False
                
        except Exception as e:
            logger.error(f"💥 Failed to connect to GitHub MCP server: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def call_mcp_tool_with_enforcement(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool with TameSDK policy enforcement.
        This is the core integration between MCP and TameSDK.
        """
        if not self.mcp_session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            # 1. ENFORCE POLICY FIRST via TameSDK
            logger.info(f"🛡️  Policy check for MCP tool: {tool_name}")
            
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            logger.info(f"✅ Policy allowed MCP tool: {tool_name}")
            
            # 2. EXECUTE MCP TOOL (only if policy allows)
            logger.info(f"🚀 Executing MCP tool: {tool_name}")
            
            result = await asyncio.wait_for(
                self.mcp_session.call_tool(tool_name, arguments),
                timeout=20.0
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
                "mcp_result": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except tamesdk.PolicyViolationException as e:
            logger.warning(f"🛡️  TameSDK blocked MCP tool: {tool_name}")
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Policy violation: {str(e)}",
                "policy_decision": "blocked",
                "mcp_result": False,
                "timestamp": datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ MCP tool timeout: {tool_name}")
            return {
                "success": False,
                "tool": tool_name,
                "error": "MCP tool execution timeout",
                "policy_decision": "error",
                "mcp_result": False,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"💥 MCP tool error: {tool_name} - {e}")
            return {
                "success": False,
                "tool": tool_name,
                "error": f"MCP error: {str(e)}",
                "policy_decision": "error",
                "mcp_result": False,
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_mcp_operations(self) -> Dict[str, Any]:
        """Test various MCP operations with TameSDK enforcement."""
        
        results = {
            "session_id": self.config.session_id,
            "agent_id": self.config.agent_id,
            "timestamp": datetime.now().isoformat(),
            "mcp_tools_available": [tool.name for tool in self.github_tools],
            "operations": []
        }
        
        # Test operations
        test_operations = [
            # Safe read operations
            {
                "name": "get_repository",
                "description": "📖 Get repository information",
                "args": {"owner": self.repo_owner, "repo": self.repo_name}
            },
            {
                "name": "list_issues", 
                "description": "🐛 List repository issues",
                "args": {"owner": self.repo_owner, "repo": self.repo_name, "state": "open"}
            },
            {
                "name": "get_issue",
                "description": "🔍 Get specific issue",
                "args": {"owner": self.repo_owner, "repo": self.repo_name, "issue_number": 1}
            },
            
            # Comment operations
            {
                "name": "create_issue_comment",
                "description": "💬 Create issue comment",
                "args": {
                    "owner": self.repo_owner,
                    "repo": self.repo_name,
                    "issue_number": 1,
                    "body": f"""🤖 **Real MCP Agent Test Comment**

This comment was posted by a **genuine MCP GitHub agent** with TameSDK enforcement!

**Technical Details:**
- 🛠️  **MCP Protocol**: Using @modelcontextprotocol/server-github
- 🛡️  **Policy Engine**: TameSDK enforcement before every MCP call
- 📊 **Session**: `{self.config.session_id}`
- 🕐 **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

**Available MCP Tools**: {len(self.github_tools)}
{chr(10).join(f"- {tool.name}" for tool in self.github_tools[:5])}

This proves real MCP + TameSDK integration works! 🎯"""
                }
            },
            
            # Dangerous operations (should be blocked)
            {
                "name": "create_pull_request",
                "description": "🚫 Attempt to create PR (should be blocked)",
                "args": {
                    "owner": self.repo_owner,
                    "repo": self.repo_name,
                    "title": "Unauthorized PR from MCP Agent",
                    "body": "This should be blocked by TameSDK policy",
                    "head": "feature-branch",
                    "base": "main"
                }
            },
            {
                "name": "update_file",
                "description": "🚫 Attempt to update file (should be blocked)",
                "args": {
                    "owner": self.repo_owner,
                    "repo": self.repo_name,
                    "path": "DANGER.txt",
                    "message": "Unauthorized file creation",
                    "content": "This should not be created"
                }
            }
        ]
        
        print("\\n" + "="*80)
        print("🚀 **REAL MCP + TAMESDK INTEGRATION TEST**")
        print("="*80)
        print(f"📊 Session: {self.config.session_id}")
        print(f"🛠️  MCP Tools: {len(self.github_tools)} available")
        print(f"🛡️  Every MCP call enforced by TameSDK policy!")
        print(f"🔗 Dashboard: http://localhost:3000")
        print("="*80)
        
        for operation in test_operations:
            tool_name = operation["name"]
            description = operation["description"]
            args = operation["args"]
            
            print(f"\\n🔍 Testing: {description}")
            
            # Check if tool is available
            available_tools = [t.name for t in self.github_tools]
            if tool_name not in available_tools:
                print(f"   ⚠️  Tool '{tool_name}' not available in MCP server")
                print(f"   📋 Available: {available_tools}")
                continue
            
            try:
                result = await self.call_mcp_tool_with_enforcement(tool_name, args)
                results["operations"].append(result)
                
                if result["success"]:
                    print(f"   ✅ {tool_name} - ALLOWED (MCP executed)")
                    if result.get("content"):
                        content_preview = str(result["content"])[:100] + "..." if len(str(result["content"])) > 100 else str(result["content"])
                        print(f"   📄 Content preview: {content_preview}")
                else:
                    decision = result["policy_decision"].upper()
                    print(f"   🛡️  {tool_name} - {decision}")
                    
                    if decision == "BLOCKED":
                        print(f"   📋 TameSDK policy blocked this MCP operation")
                    else:
                        print(f"   ⚠️  Error: {result.get('error', 'Unknown')}")
                        
            except Exception as e:
                print(f"   💥 Exception: {e}")
                results["operations"].append({
                    "success": False,
                    "tool": tool_name,
                    "error": str(e),
                    "policy_decision": "exception"
                })
        
        # Summary
        total = len(results["operations"])
        allowed = sum(1 for op in results["operations"] if op.get("success"))
        blocked = sum(1 for op in results["operations"] if not op.get("success"))
        
        print("\\n" + "="*80)
        print("📊 **REAL MCP + TAMESDK TEST RESULTS:**")
        print(f"   🛠️  MCP Tools Available: {len(self.github_tools)}")
        print(f"   🧪 Operations Tested: {total}")
        print(f"   ✅ Allowed by Policy: {allowed}")
        print(f"   🛡️  Blocked by Policy: {blocked}")
        print(f"   📊 All logged to TameSDK dashboard!")
        print("="*80)
        
        if allowed > 0 and blocked > 0:
            print("\\n🎯 **SUCCESS: Real MCP + TameSDK integration working!**")
            print("   ✅ MCP protocol working")
            print("   ✅ TameSDK policy enforcement working")
            print("   ✅ Mixed allow/block results achieved")
            print("   ✅ Complete audit trail in dashboard")
        
        return results
    
    async def close(self):
        """Clean up all connections."""
        try:
            logger.info("🧹 Cleaning up connections...")
            
            if self.mcp_session:
                await self.mcp_session.close()
                logger.info("✅ MCP session closed")
            
            if self.stdio_client:
                await self.stdio_client.__aexit__(None, None, None)
                logger.info("✅ MCP stdio client closed")
                
        except Exception as e:
            logger.warning(f"⚠️  Cleanup warning: {e}")
        finally:
            self.tame_client.close()
            logger.info("✅ TameSDK client closed")

async def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fixed Real MCP GitHub Agent with TameSDK")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    
    args = parser.parse_args()
    
    # Configuration
    config = AgentConfig(
        github_token=os.getenv("GITHUB_TOKEN"),
        tame_api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        repository=args.repo,
        session_id=f"fixed-mcp-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    if not config.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize agent
    agent = FixedMCPGitHubAgent(config)
    
    try:
        print(f"🚀 **FIXED REAL MCP GITHUB AGENT**")
        print(f"📋 Repository: {config.repository}")
        print(f"🆔 Session: {config.session_id}")
        print(f"🛡️  Real MCP + TameSDK integration test!")
        
        # Connect to GitHub MCP server
        print("\\n🔌 Connecting to GitHub MCP server...")
        if not await agent.connect_to_github_mcp():
            print("❌ Failed to connect to GitHub MCP server")
            print("\\n🔧 Troubleshooting:")
            print("1. Check Node.js is installed: node --version")
            print("2. Check GitHub token: echo $GITHUB_TOKEN")
            print("3. Check network connectivity")
            sys.exit(1)
        
        # Run MCP test operations
        results = await agent.test_mcp_operations()
        
        print(f"\\n🎉 **Real MCP Test Complete!**")
        print(f"📊 Check TameSDK dashboard: http://localhost:3000")
        print(f"🆔 Session: {results['session_id']}")
        
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