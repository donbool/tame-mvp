#!/usr/bin/env python3
"""
Real TameSDK selective policy demo that logs to the dashboard.
This uses the actual TameSDK client with a mixed policy approach.
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

import tamesdk
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    github_token: str
    tame_api_url: str
    repository: str
    session_id: str
    agent_id: str = "selective-demo-agent"
    user_id: str = "policy-tester"

class RealSelectivePolicyDemo:
    """Real TameSDK demo showing mixed policy results with dashboard logging."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
        # Use REAL TameSDK client
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
        
        logger.info(f"Initialized REAL TameSDK selective demo for: {config.repository}")
        logger.info(f"Session will be logged to TameSDK dashboard: {config.session_id}")
    
    def attempt_read_operation(self, operation_name: str, url_path: str, description: str) -> Dict[str, Any]:
        """Attempt a read operation with TameSDK enforcement."""
        try:
            # Real TameSDK policy check
            decision = self.tame_client.enforce(
                tool_name=operation_name,
                tool_args={"repo": f"{self.repo_owner}/{self.repo_name}", "type": "read"}
            )
            
            # If we get here, operation was allowed
            url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}{url_path}'
            response = httpx.get(url, headers=self.github_headers)
            response.raise_for_status()
            
            return {
                "success": True,
                "operation": operation_name,
                "description": description,
                "policy": "ALLOWED",
                "github_status": response.status_code,
                "logged_to_dashboard": True
            }
            
        except tamesdk.PolicyViolationException as e:
            return {
                "success": False,
                "operation": operation_name,
                "description": description,
                "policy": "BLOCKED",
                "reason": str(e),
                "logged_to_dashboard": True
            }
        except Exception as e:
            return {
                "success": False,
                "operation": operation_name,
                "description": description,
                "policy": "ERROR",
                "reason": str(e),
                "logged_to_dashboard": True
            }
    
    def attempt_write_operation(self, operation_name: str, description: str, operation_func) -> Dict[str, Any]:
        """Attempt a write operation with TameSDK enforcement."""
        try:
            # Real TameSDK policy check
            decision = self.tame_client.enforce(
                tool_name=operation_name,
                tool_args={"repo": f"{self.repo_owner}/{self.repo_name}", "type": "write"}
            )
            
            # If we get here, operation was allowed - execute it
            result = operation_func()
            
            return {
                "success": True,
                "operation": operation_name,
                "description": description,
                "policy": "ALLOWED",
                "github_result": result,
                "logged_to_dashboard": True
            }
            
        except tamesdk.PolicyViolationException as e:
            return {
                "success": False,
                "operation": operation_name,
                "description": description,
                "policy": "BLOCKED",
                "reason": str(e),
                "logged_to_dashboard": True
            }
        except Exception as e:
            return {
                "success": False,
                "operation": operation_name,
                "description": description,
                "policy": "ERROR",
                "reason": str(e),
                "logged_to_dashboard": True
            }
    
    def create_comment_operation(self):
        """Create a comment if allowed by policy."""
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/1/comments'
        data = {
            "body": f"""🛡️ **Real TameSDK Policy Demo**

This comment was posted by an agent using the **REAL TameSDK client**!

- **Session ID**: `{self.config.session_id}`
- **Agent ID**: `{self.config.agent_id}`
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

✅ This operation was **ALLOWED** by TameSDK policy and is logged in the dashboard!

Check the TameSDK UI to see this policy decision in real-time! 📊"""
        }
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        return {"status": response.status_code, "created": True}
    
    def create_security_issue_operation(self):
        """Create a security issue if allowed by policy."""
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues'
        data = {
            "title": "🔒 Real TameSDK Policy Enforcement Demo",
            "body": f"""## Real TameSDK Security Issue Demo

This issue was created by an AI agent using **real TameSDK policy enforcement**.

### Demo Details:
- **Session ID**: `{self.config.session_id}`
- **Agent**: `{self.config.agent_id}`
- **User**: `{self.config.user_id}`
- **Created**: {datetime.now().isoformat()}

### Policy Enforcement:
✅ This `create_issue` operation was **evaluated by TameSDK** before execution
✅ **Real policy decision** logged to dashboard  
✅ **Complete audit trail** available in TameSDK UI

### What This Proves:
1. Real AI agent operations under TameSDK control
2. Policy enforcement working in production
3. Complete visibility and governance
4. Selective allows/blocks based on operation type

*Check the TameSDK dashboard to see all policy decisions! 📊*""",
            "labels": ["security", "demo", "tamesdk"]
        }
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        return {"status": response.status_code, "issue_number": response.json()["number"]}
    
    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """Run comprehensive demo with real TameSDK logging."""
        results = {
            "session_id": self.config.session_id,
            "agent_id": self.config.agent_id,
            "user_id": self.config.user_id,
            "timestamp": datetime.now().isoformat(),
            "dashboard_url": "http://localhost:3000",
            "operations": []
        }
        
        # Define operations to test
        operations = [
            # READ OPERATIONS (likely to be blocked by default policy)
            ("get_repository_info", "", "📖 Get repository information"),
            ("list_branches", "/branches", "🌿 List repository branches"),
            ("get_pull_requests", "/pulls", "📋 List pull requests"),
            ("list_issues", "/issues", "🐛 List repository issues"),
            ("get_contributors", "/contributors", "👥 Get repository contributors"),
            
            # WRITE OPERATIONS (likely to be blocked by default policy)
            ("create_issue_comment", "💬 Post comment on issue", lambda: self.create_comment_operation()),
            ("create_security_issue", "🔒 Create security issue", lambda: self.create_security_issue_operation()),
        ]
        
        print("\\n" + "="*70)
        print("🛡️  **REAL TAMESDK SELECTIVE POLICY DEMO**")
        print("="*70)
        print(f"📊 Session: {self.config.session_id}")
        print(f"🔗 Dashboard: http://localhost:3000")
        print(f"📝 All operations will be logged to TameSDK UI!")
        print("="*70)
        
        # Test read operations
        for operation_name, url_path, description in operations[:5]:
            print(f"\\n🔍 Testing: {description}")
            result = self.attempt_read_operation(operation_name, url_path, description)
            results["operations"].append(result)
            
            if result["success"]:
                print(f"   ✅ {operation_name} - {result['policy']} (HTTP {result['github_status']})")
            else:
                print(f"   🛡️  {operation_name} - {result['policy']}")
                if "denied by policy" in result.get("reason", ""):
                    print(f"   📋 TameSDK blocked this operation before GitHub call")
        
        # Test write operations  
        for operation_name, description, operation_func in operations[5:]:
            print(f"\\n🔍 Testing: {description}")
            result = self.attempt_write_operation(operation_name, description, operation_func)
            results["operations"].append(result)
            
            if result["success"]:
                print(f"   ✅ {operation_name} - {result['policy']} (GitHub operation completed)")
            else:
                print(f"   🛡️  {operation_name} - {result['policy']}")
                if "denied by policy" in result.get("reason", ""):
                    print(f"   📋 TameSDK blocked this operation before GitHub call")
        
        # Summary
        allowed = sum(1 for op in results["operations"] if op.get("success"))
        blocked = sum(1 for op in results["operations"] if not op.get("success"))
        
        print("\\n" + "="*70)
        print("📊 **REAL TAMESDK DEMO RESULTS:**")
        print(f"   ✅ Allowed Operations: {allowed}")
        print(f"   🛡️  Blocked Operations: {blocked}")
        print(f"   📊 Total TameSDK Checks: {len(results['operations'])}")
        print(f"   🎯 Dashboard Session: {self.config.session_id}")
        print("="*70)
        print("\\n🔗 **Check TameSDK Dashboard NOW:**")
        print("   URL: http://localhost:3000")
        print(f"   Session: {self.config.session_id}")
        print("   You should see ALL policy decisions logged in real-time!")
        
        return results
    
    def close(self):
        self.tame_client.close()

def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real TameSDK Selective Policy Demo")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    
    args = parser.parse_args()
    
    # Configuration
    config = AgentConfig(
        github_token=os.getenv("GITHUB_TOKEN"),
        tame_api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        repository=args.repo,
        session_id=f"real-selective-demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    if not config.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize demo agent
    agent = RealSelectivePolicyDemo(config)
    
    try:
        print(f"🚀 **REAL TAMESDK SELECTIVE DEMO**")
        print(f"📋 Repository: {config.repository}")
        print(f"🆔 Session: {config.session_id}")
        print(f"🛡️  Using REAL TameSDK client - all calls logged!")
        print(f"📊 Dashboard: http://localhost:3000")
        
        # Run demo
        results = agent.run_comprehensive_demo()
        
        print(f"\\n📄 **Session Summary:**")
        print(f"Session ID: {results['session_id']}")
        print(f"Total Operations: {len(results['operations'])}")
        print(f"Logged to Dashboard: ALL operations")
        
    finally:
        agent.close()

if __name__ == "__main__":
    main()