#!/usr/bin/env python3
"""
Real-world OpenAI Agent with GitHub MCP integration and TameSDK policy enforcement.

This agent can:
- Connect to GitHub via MCP server
- Review pull requests and add comments
- Create issues and manage repositories
- All operations are policy-controlled via TameSDK

Usage:
    python openai_github_agent.py --repo "owner/repo" --task "review PR #123"
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from datetime import datetime

import tamesdk
from openai import OpenAI

# MCP imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Error: MCP library not found. Install with: pip install mcp")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the GitHub agent."""
    openai_api_key: str
    github_token: str
    tame_api_url: str
    repository: str
    session_id: str
    agent_id: str = "github-pr-agent"
    user_id: str = "developer"

class TameEnforcedGitHubAgent:
    """OpenAI agent with GitHub MCP tools wrapped in TameSDK policy enforcement."""
    
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
        
        # Available GitHub MCP tools
        self.github_tools = []
        self.mcp_session: Optional[ClientSession] = None
        
        logger.info(f"Initialized GitHub agent for repository: {config.repository}")
    
    async def connect_to_github_mcp(self):
        """Connect to GitHub MCP server."""
        try:
            # GitHub MCP server parameters
            server_params = StdioServerParameters(
                command="npx",
                args=[
                    "-y", "@modelcontextprotocol/server-github",
                    "--github-token", self.config.github_token
                ],
                env={
                    "GITHUB_PERSONAL_ACCESS_TOKEN": self.config.github_token
                }
            )
            
            # Connect to MCP server
            self.mcp_session = await stdio_client(server_params).__aenter__()
            
            # Get available tools
            tools_result = await self.mcp_session.list_tools()
            self.github_tools = tools_result.tools
            
            logger.info(f"Connected to GitHub MCP. Available tools: {[tool.name for tool in self.github_tools]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to GitHub MCP: {e}")
            return False
    
    @tamesdk.enforce_policy
    async def call_github_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a GitHub MCP tool with TameSDK policy enforcement.
        
        This decorator automatically enforces policies before executing any GitHub operation.
        """
        if not self.mcp_session:
            raise RuntimeError("Not connected to GitHub MCP server")
        
        logger.info(f"Executing GitHub tool: {tool_name} with args: {arguments}")
        
        try:
            # Call the MCP tool
            result = await self.mcp_session.call_tool(tool_name, arguments)
            
            # Log successful execution
            logger.info(f"GitHub tool {tool_name} executed successfully")
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result.content,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"GitHub tool {tool_name} failed: {e}")
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def review_pull_request(self, pr_number: int, focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Review a pull request using AI analysis and post comments.
        All GitHub operations are policy-enforced via TameSDK.
        """
        focus_areas = focus_areas or ["security", "performance", "code quality"]
        
        try:
            # 1. Get PR details (policy-enforced)
            pr_details = await self.call_github_tool("get_pull_request", {
                "owner": self.config.repository.split("/")[0],
                "repo": self.config.repository.split("/")[1],
                "pull_number": pr_number
            })
            
            if not pr_details["success"]:
                return {"error": "Failed to fetch PR details", "details": pr_details}
            
            # 2. Get PR diff (policy-enforced)
            pr_diff = await self.call_github_tool("get_pull_request_diff", {
                "owner": self.config.repository.split("/")[0],
                "repo": self.config.repository.split("/")[1],
                "pull_number": pr_number
            })
            
            if not pr_diff["success"]:
                return {"error": "Failed to fetch PR diff", "details": pr_diff}
            
            # 3. AI analysis of the PR
            analysis_prompt = f"""
            You are a senior code reviewer. Analyze this pull request:
            
            PR Details: {json.dumps(pr_details['result'], indent=2)}
            
            Code Changes: {pr_diff['result']}
            
            Focus on: {', '.join(focus_areas)}
            
            Provide a structured review with:
            1. Overall assessment (APPROVE/REQUEST_CHANGES/COMMENT)
            2. Specific issues found
            3. Suggestions for improvement
            4. Security concerns (if any)
            
            Keep feedback constructive and specific.
            """
            
            # Get AI review
            ai_response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer focusing on security, performance, and best practices."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3
            )
            
            review_content = ai_response.choices[0].message.content
            
            # 4. Post review comment (policy-enforced)
            comment_result = await self.call_github_tool("create_pull_request_review", {
                "owner": self.config.repository.split("/")[0],
                "repo": self.config.repository.split("/")[1],
                "pull_number": pr_number,
                "body": f"🤖 **AI Code Review**\n\n{review_content}\n\n---\n*Review conducted by TameSDK-enforced AI agent*",
                "event": "COMMENT"  # Can be APPROVE, REQUEST_CHANGES, or COMMENT
            })
            
            return {
                "success": True,
                "pr_number": pr_number,
                "review_posted": comment_result["success"],
                "ai_analysis": review_content,
                "github_operations": [pr_details, pr_diff, comment_result]
            }
            
        except Exception as e:
            logger.error(f"PR review failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_pr_compliance(self, pr_number: int) -> Dict[str, Any]:
        """
        Check if a PR meets compliance requirements and potentially block it.
        """
        try:
            # Get PR files (policy-enforced)
            pr_files = await self.call_github_tool("get_pull_request_files", {
                "owner": self.config.repository.split("/")[0],
                "repo": self.config.repository.split("/")[1],
                "pull_number": pr_number
            })
            
            if not pr_files["success"]:
                return {"error": "Failed to fetch PR files"}
            
            # Analyze files for compliance issues
            compliance_issues = []
            
            for file_info in pr_files["result"]:
                filename = file_info.get("filename", "")
                
                # Check for sensitive files
                if any(sensitive in filename.lower() for sensitive in ["password", "secret", "key", "token", ".env"]):
                    compliance_issues.append(f"⚠️  Potential sensitive file: {filename}")
                
                # Check for large files
                if file_info.get("changes", 0) > 1000:
                    compliance_issues.append(f"📏 Large file change: {filename} ({file_info['changes']} lines)")
            
            # If compliance issues found, add blocking comment (policy-enforced)
            if compliance_issues:
                blocking_comment = f"""
🚨 **Compliance Issues Detected**

This PR has been flagged for the following compliance concerns:

{chr(10).join(f"• {issue}" for issue in compliance_issues)}

**Action Required:**
- Review and address the flagged issues
- Ensure no sensitive data is committed
- Consider breaking large changes into smaller PRs

*This check was performed by TameSDK-enforced compliance agent*
                """
                
                comment_result = await self.call_github_tool("create_issue_comment", {
                    "owner": self.config.repository.split("/")[0],
                    "repo": self.config.repository.split("/")[1],
                    "issue_number": pr_number,
                    "body": blocking_comment
                })
                
                return {
                    "compliant": False,
                    "issues": compliance_issues,
                    "comment_posted": comment_result["success"],
                    "action": "BLOCKED"
                }
            
            return {
                "compliant": True,
                "issues": [],
                "action": "APPROVED"
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_security_issue(self, title: str, description: str, labels: List[str] = None) -> Dict[str, Any]:
        """
        Create a security issue in the repository (policy-enforced).
        """
        labels = labels or ["security", "needs-review"]
        
        issue_body = f"""
## Security Concern

{description}

**Reported by:** TameSDK-enforced security agent
**Timestamp:** {datetime.now().isoformat()}

### Recommended Actions:
- [ ] Investigate the security concern
- [ ] Implement necessary fixes
- [ ] Update security documentation if needed

---
*This issue was created automatically by an AI security agent with policy enforcement*
        """
        
        try:
            result = await self.call_github_tool("create_issue", {
                "owner": self.config.repository.split("/")[0],
                "repo": self.config.repository.split("/")[1],
                "title": f"🔒 {title}",
                "body": issue_body,
                "labels": labels
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create security issue: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Clean up connections."""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)
        self.tame_client.close()

async def main():
    """Main execution function."""
    import argparse
    
    # Try to load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    parser = argparse.ArgumentParser(description="OpenAI GitHub Agent with TameSDK Policy Enforcement")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    parser.add_argument("--action", choices=["review", "compliance", "security"], default="review", 
                       help="Action to perform")
    parser.add_argument("--pr", type=int, help="Pull request number")
    parser.add_argument("--issue-title", help="Security issue title")
    parser.add_argument("--issue-description", help="Security issue description")
    
    args = parser.parse_args()
    
    # Configuration
    config = AgentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        github_token=os.getenv("GITHUB_TOKEN"),
        tame_api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        repository=args.repo,
        session_id=f"github-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    if not config.openai_api_key:
        print("Error: OPENAI_API_KEY environment variable required")
        sys.exit(1)
    
    if not config.github_token:
        print("Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize agent
    agent = TameEnforcedGitHubAgent(config)
    
    try:
        # Connect to GitHub MCP
        if not await agent.connect_to_github_mcp():
            print("Failed to connect to GitHub MCP server")
            sys.exit(1)
        
        print(f"🚀 GitHub agent connected! Session: {config.session_id}")
        print(f"📋 Available tools: {[tool.name for tool in agent.github_tools]}")
        print(f"🛡️  All operations are policy-enforced via TameSDK")
        
        # Execute requested action
        if args.action == "review" and args.pr:
            print(f"\n🔍 Reviewing PR #{args.pr}...")
            result = await agent.review_pull_request(args.pr)
            print(f"Review result: {json.dumps(result, indent=2)}")
            
        elif args.action == "compliance" and args.pr:
            print(f"\n✅ Checking compliance for PR #{args.pr}...")
            result = await agent.check_pr_compliance(args.pr)
            print(f"Compliance result: {json.dumps(result, indent=2)}")
            
        elif args.action == "security" and args.issue_title and args.issue_description:
            print(f"\n🔒 Creating security issue...")
            result = await agent.create_security_issue(args.issue_title, args.issue_description)
            print(f"Security issue result: {json.dumps(result, indent=2)}")
            
        else:
            print("Error: Invalid action or missing parameters")
            print("Examples:")
            print("  python openai_github_agent.py --repo owner/repo --action review --pr 123")
            print("  python openai_github_agent.py --repo owner/repo --action compliance --pr 123")
            print("  python openai_github_agent.py --repo owner/repo --action security --issue-title 'SQL Injection' --issue-description 'Found potential SQL injection'")
        
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())