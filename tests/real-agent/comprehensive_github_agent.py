#!/usr/bin/env python3
"""
Comprehensive GitHub Agent demonstrating extensive TameSDK policy enforcement.
This agent attempts many different GitHub operations to show clear policy blocks and allows.
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

import tamesdk
from openai import OpenAI
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the comprehensive GitHub agent."""
    openai_api_key: str
    github_token: str
    tame_api_url: str
    repository: str
    session_id: str
    agent_id: str = "comprehensive-github-agent"
    user_id: str = "security-auditor"

class ComprehensiveGitHubAgent:
    """GitHub agent that performs many operations with detailed TameSDK policy enforcement."""
    
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
        
        # GitHub API headers
        self.github_headers = {
            'Authorization': f'token {config.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        self.repo_owner, self.repo_name = config.repository.split('/')
        
        logger.info(f"Initialized comprehensive GitHub agent for repository: {config.repository}")
    
    # ==================== READ OPERATIONS (should be ALLOWED) ====================
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information with TameSDK policy enforcement."""
        decision = self.tame_client.enforce(
            tool_name="get_repository_info",
            tool_args={"repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
    
    def list_branches(self) -> Dict[str, Any]:
        """List repository branches with TameSDK policy enforcement."""
        decision = self.tame_client.enforce(
            tool_name="list_branches",
            tool_args={"repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/branches'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
    
    def get_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """Get PR details with TameSDK policy enforcement."""
        decision = self.tame_client.enforce(
            tool_name="get_pull_request",
            tool_args={"pr_number": pr_number, "repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
    
    def get_pull_request_commits(self, pr_number: int) -> Dict[str, Any]:
        """Get PR commits with TameSDK policy enforcement."""
        decision = self.tame_client.enforce(
            tool_name="get_pull_request_commits",
            tool_args={"pr_number": pr_number, "repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/commits'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
    
    def list_repository_issues(self) -> Dict[str, Any]:
        """List repository issues with TameSDK policy enforcement."""
        decision = self.tame_client.enforce(
            tool_name="list_repository_issues",
            tool_args={"repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
    
    # ==================== COMMENT OPERATIONS (should be ALLOWED) ====================
    
    def create_issue_comment(self, issue_number: int, body: str) -> Dict[str, Any]:
        """Create issue comment with TameSDK policy enforcement."""
        decision = self.tame_client.enforce(
            tool_name="create_issue_comment",
            tool_args={
                "issue_number": issue_number,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "body_length": len(body)
            }
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}/comments'
        data = {"body": body}
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
    
    def create_pull_request_review(self, pr_number: int, body: str, event: str = "COMMENT") -> Dict[str, Any]:
        """Create PR review with TameSDK policy enforcement."""
        decision = self.tame_client.enforce(
            tool_name="create_pull_request_review",
            tool_args={
                "pr_number": pr_number,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "event": event,
                "body_length": len(body)
            }
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/reviews'
        data = {"body": body, "event": event}
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
    
    # ==================== SECURITY ISSUE CREATION (should be ALLOWED) ====================
    
    def create_security_issue(self, title: str, body: str) -> Dict[str, Any]:
        """Create security issue with TameSDK policy enforcement."""
        decision = self.tame_client.enforce(
            tool_name="create_issue",
            tool_args={
                "title": title,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "labels": ["security", "automated"],
                "body_length": len(body)
            }
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues'
        data = {
            "title": f"🔒 {title}",
            "body": body,
            "labels": ["security", "automated"]
        }
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
    
    # ==================== DANGEROUS OPERATIONS (should be BLOCKED) ====================
    
    def merge_pull_request(self, pr_number: int, commit_title: str = None) -> Dict[str, Any]:
        """Attempt to merge PR - SHOULD BE BLOCKED by policy."""
        try:
            decision = self.tame_client.enforce(
                tool_name="merge_pull_request",
                tool_args={
                    "pr_number": pr_number,
                    "repo": f"{self.repo_owner}/{self.repo_name}",
                    "commit_title": commit_title or f"Merge PR #{pr_number}"
                }
            )
            
            # This should never execute due to policy block
            url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/merge'
            data = {"commit_title": commit_title or f"Merge PR #{pr_number}"}
            
            response = httpx.put(url, headers=self.github_headers, json=data)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e), "blocked": True}
    
    def delete_branch(self, branch_name: str) -> Dict[str, Any]:
        """Attempt to delete branch - SHOULD BE BLOCKED by policy."""
        try:
            decision = self.tame_client.enforce(
                tool_name="delete_branch",
                tool_args={
                    "branch_name": branch_name,
                    "repo": f"{self.repo_owner}/{self.repo_name}"
                }
            )
            
            # This should never execute due to policy block
            url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/git/refs/heads/{branch_name}'
            response = httpx.delete(url, headers=self.github_headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e), "blocked": True}
    
    def create_pull_request(self, title: str, body: str, head: str, base: str) -> Dict[str, Any]:
        """Attempt to create PR - SHOULD BE BLOCKED by policy."""
        try:
            decision = self.tame_client.enforce(
                tool_name="create_pull_request",
                tool_args={
                    "title": title,
                    "repo": f"{self.repo_owner}/{self.repo_name}",
                    "head": head,
                    "base": base
                }
            )
            
            # This should never execute due to policy block
            url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls'
            data = {"title": title, "body": body, "head": head, "base": base}
            
            response = httpx.post(url, headers=self.github_headers, json=data)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e), "blocked": True}
    
    def update_file(self, path: str, content: str, message: str) -> Dict[str, Any]:
        """Attempt to update file - SHOULD BE BLOCKED by policy."""
        try:
            decision = self.tame_client.enforce(
                tool_name="update_file",
                tool_args={
                    "path": path,
                    "repo": f"{self.repo_owner}/{self.repo_name}",
                    "content_length": len(content)
                }
            )
            
            # This should never execute due to policy block
            import base64
            url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}'
            data = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode()
            }
            
            response = httpx.put(url, headers=self.github_headers, json=data)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e), "blocked": True}
    
    def approve_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """Attempt to approve PR - SHOULD BE BLOCKED by policy."""
        try:
            decision = self.tame_client.enforce(
                tool_name="approve_pull_request", 
                tool_args={
                    "pr_number": pr_number,
                    "repo": f"{self.repo_owner}/{self.repo_name}",
                    "event": "APPROVE"
                }
            )
            
            # This should never execute due to policy block
            url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/reviews'
            data = {"event": "APPROVE", "body": "Automatically approved by AI agent"}
            
            response = httpx.post(url, headers=self.github_headers, json=data)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e), "blocked": True}
    
    # ==================== ADMIN OPERATIONS (should be BLOCKED) ====================
    
    def add_collaborator(self, username: str) -> Dict[str, Any]:
        """Attempt to add collaborator - SHOULD BE BLOCKED by policy."""
        try:
            decision = self.tame_client.enforce(
                tool_name="add_collaborator",
                tool_args={
                    "username": username,
                    "repo": f"{self.repo_owner}/{self.repo_name}"
                }
            )
            
            # This should never execute due to policy block
            url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/collaborators/{username}'
            response = httpx.put(url, headers=self.github_headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e), "blocked": True}
    
    def update_repository_settings(self, description: str) -> Dict[str, Any]:
        """Attempt to update repo settings - SHOULD BE BLOCKED by policy."""
        try:
            decision = self.tame_client.enforce(
                tool_name="update_repository_settings",
                tool_args={
                    "repo": f"{self.repo_owner}/{self.repo_name}",
                    "description": description
                }
            )
            
            # This should never execute due to policy block
            url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
            data = {"description": description}
            
            response = httpx.patch(url, headers=self.github_headers, json=data)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e), "blocked": True}
    
    # ==================== COMPREHENSIVE TESTING ====================
    
    def run_comprehensive_test(self, pr_number: int) -> Dict[str, Any]:
        """Run comprehensive test showing many policy decisions."""
        results = {
            "session_id": self.config.session_id,
            "timestamp": datetime.now().isoformat(),
            "total_operations": 0,
            "allowed_operations": [],
            "blocked_operations": [],
            "errors": []
        }
        
        operations = [
            # READ OPERATIONS (should be allowed)
            ("get_repository_info", lambda: self.get_repository_info()),
            ("list_branches", lambda: self.list_branches()),
            ("get_pull_request", lambda: self.get_pull_request(pr_number)),
            ("get_pull_request_commits", lambda: self.get_pull_request_commits(pr_number)),
            ("list_repository_issues", lambda: self.list_repository_issues()),
            
            # COMMENT OPERATIONS (should be allowed)
            ("create_issue_comment", lambda: self.create_issue_comment(
                pr_number, "🤖 **Automated Security Scan Complete**\\n\\nThis comment was posted by the TameSDK-enforced AI agent during a comprehensive security review."
            )),
            ("create_pull_request_review", lambda: self.create_pull_request_review(
                pr_number, "🤖 **Comprehensive AI Review**\\n\\nThis PR has been analyzed by our AI security agent. All operations were policy-controlled via TameSDK.", "COMMENT"
            )),
            
            # SECURITY OPERATIONS (should be allowed)
            ("create_security_issue", lambda: self.create_security_issue(
                "Automated Security Scan Results",
                f"**Security Analysis Complete**\\n\\nThe AI agent has completed a comprehensive security scan of PR #{pr_number}.\\n\\n**Findings:** Multiple security vulnerabilities detected including SQL injection, hardcoded secrets, and unsafe eval() usage.\\n\\n**Recommendation:** Address all security issues before merging."
            )),
            
            # DANGEROUS OPERATIONS (should be blocked)
            ("merge_pull_request", lambda: self.merge_pull_request(pr_number)),
            ("delete_branch", lambda: self.delete_branch("test-branch")),
            ("create_pull_request", lambda: self.create_pull_request(
                "Automated PR", "This PR was created by AI", "feature-branch", "main"
            )),
            ("update_file", lambda: self.update_file(
                "DANGEROUS_FILE.txt", "This file should not be created by AI", "AI attempting file modification"
            )),
            ("approve_pull_request", lambda: self.approve_pull_request(pr_number)),
            
            # ADMIN OPERATIONS (should be blocked)
            ("add_collaborator", lambda: self.add_collaborator("malicious-user")),
            ("update_repository_settings", lambda: self.update_repository_settings("Modified by AI - THIS SHOULD BE BLOCKED")),
        ]
        
        for operation_name, operation_func in operations:
            results["total_operations"] += 1
            
            try:
                logger.info(f"🔍 Testing: {operation_name}")
                result = operation_func()
                
                if result.get("success"):
                    results["allowed_operations"].append({
                        "operation": operation_name,
                        "status": "ALLOWED",
                        "result": "✅ Operation completed successfully"
                    })
                    logger.info(f"✅ {operation_name} - ALLOWED")
                else:
                    results["blocked_operations"].append({
                        "operation": operation_name,
                        "status": "BLOCKED",
                        "reason": result.get("error", "Unknown error")
                    })
                    logger.info(f"❌ {operation_name} - BLOCKED: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                error_msg = str(e)
                if "denied by policy" in error_msg:
                    results["blocked_operations"].append({
                        "operation": operation_name,
                        "status": "BLOCKED", 
                        "reason": error_msg
                    })
                    logger.info(f"🛡️  {operation_name} - BLOCKED BY POLICY: {error_msg}")
                else:
                    results["errors"].append({
                        "operation": operation_name,
                        "error": error_msg
                    })
                    logger.error(f"💥 {operation_name} - ERROR: {error_msg}")
        
        # Summary
        logger.info(f"\\n📊 COMPREHENSIVE TEST SUMMARY:")
        logger.info(f"   Total Operations: {results['total_operations']}")
        logger.info(f"   Allowed: {len(results['allowed_operations'])}")
        logger.info(f"   Blocked: {len(results['blocked_operations'])}")
        logger.info(f"   Errors: {len(results['errors'])}")
        
        return results
    
    def close(self):
        """Clean up connections."""
        self.tame_client.close()

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive GitHub Agent with Extensive TameSDK Testing")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    parser.add_argument("--pr", type=int, required=True, help="Pull request number for testing")
    
    args = parser.parse_args()
    
    # Configuration
    config = AgentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        github_token=os.getenv("GITHUB_TOKEN"),
        tame_api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        repository=args.repo,
        session_id=f"comprehensive-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    if not config.openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable required")
        sys.exit(1)
    
    if not config.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize agent
    agent = ComprehensiveGitHubAgent(config)
    
    try:
        print(f"🚀 **COMPREHENSIVE GITHUB AGENT TESTING**")
        print(f"📋 Repository: {config.repository}")
        print(f"🆔 Session: {config.session_id}")
        print(f"🛡️  Testing extensive TameSDK policy enforcement")
        print(f"📊 Will attempt {15}+ different GitHub operations")
        print("\\n" + "="*60)
        
        # Run comprehensive test
        results = agent.run_comprehensive_test(args.pr)
        
        print("\\n" + "="*60)
        print("📊 **FINAL RESULTS:**")
        print(json.dumps(results, indent=2))
        
        print("\\n🎯 **Check TameSDK Dashboard for complete audit trail!**")
        print(f"   Session ID: {results['session_id']}")
        print(f"   URL: http://localhost:3000")
        
    finally:
        agent.close()

if __name__ == "__main__":
    main()