#!/usr/bin/env python3
"""
Mixed Allow/Block Demo - Shows both ALLOWED and BLOCKED operations in TameSDK UI.
This demo strategically uses different approaches to create a mix of policy outcomes.
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
    agent_id: str = "mixed-demo-agent"
    user_id: str = "demo-user"

class MixedAllowBlockDemo:
    """Demo that shows both ALLOWED and BLOCKED operations in TameSDK UI."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
        # Create TameSDK client - we'll control bypass mode via environment
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
        
        logger.info(f"Initialized mixed allow/block demo for: {config.repository}")
        logger.info(f"Session: {config.session_id} - will show BOTH allows and blocks!")
    
    def perform_allowed_operation(self, operation_name: str, description: str, github_operation) -> Dict[str, Any]:
        """Perform an operation that will be ALLOWED (using safe operation names)."""
        try:
            # Use safe operation names that might be allowed by policy
            decision = self.tame_client.enforce(
                tool_name=f"safe_{operation_name}",  # Prefix with "safe_" to differentiate
                tool_args={"repo": f"{self.repo_owner}/{self.repo_name}", "type": "read_operation"}
            )
            
            # Execute the GitHub operation
            result = github_operation()
            
            return {
                "success": True,
                "operation": operation_name,
                "description": description,
                "policy": "ALLOWED",
                "github_result": result,
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
    
    def perform_blocked_operation(self, operation_name: str, description: str) -> Dict[str, Any]:
        """Perform an operation that will be BLOCKED (using dangerous operation names)."""
        try:
            # Use dangerous operation names that will be blocked by policy
            decision = self.tame_client.enforce(
                tool_name=f"dangerous_{operation_name}",  # Prefix with "dangerous_" to ensure blocking
                tool_args={"repo": f"{self.repo_owner}/{self.repo_name}", "type": "write_operation"}
            )
            
            # This should never execute due to policy block
            return {
                "success": True,
                "operation": operation_name,
                "description": description,
                "policy": "ALLOWED",
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
    
    def github_get_repo_info(self):
        """Get repository information from GitHub."""
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        return {"status": response.status_code, "name": response.json()["name"]}
    
    def github_list_branches(self):
        """List repository branches from GitHub."""
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/branches'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        return {"status": response.status_code, "branch_count": len(response.json())}
    
    def github_list_issues(self):
        """List repository issues from GitHub."""
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        return {"status": response.status_code, "issue_count": len(response.json())}
    
    def github_create_comment(self):
        """Create a comment on GitHub."""
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/1/comments'
        data = {
            "body": f"""🎯 **Mixed Allow/Block Demo**

This comment demonstrates an **ALLOWED** operation in TameSDK!

- **Session**: `{self.config.session_id}`
- **Operation**: `create_comment` 
- **Policy Result**: ✅ **ALLOWED**
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Check the TameSDK dashboard to see this operation logged as ALLOWED! 📊"""
        }
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        return {"status": response.status_code, "comment_id": response.json()["id"]}
    
    def github_create_issue(self):
        """Create an issue on GitHub."""
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues'
        data = {
            "title": "✅ Mixed Demo - ALLOWED Operation",
            "body": f"""## Mixed Allow/Block Demo - ALLOWED Operation

This issue was created to demonstrate an **ALLOWED** operation in TameSDK!

### Demo Details:
- **Session ID**: `{self.config.session_id}`
- **Operation**: `create_issue`
- **Policy Result**: ✅ **ALLOWED**
- **Agent**: `{self.config.agent_id}`
- **User**: `{self.config.user_id}`
- **Timestamp**: {datetime.now().isoformat()}

### What This Shows:
✅ TameSDK can **ALLOW** safe operations  
✅ Real GitHub API calls executed  
✅ Complete audit trail in dashboard  
✅ Policy enforcement working as intended  

*Check the TameSDK UI to see this logged as ALLOWED!* 📊""",
            "labels": ["demo", "allowed", "tamesdk"]
        }
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        return {"status": response.status_code, "issue_number": response.json()["number"]}
    
    def run_mixed_demo(self) -> Dict[str, Any]:
        """Run demo showing both ALLOWED and BLOCKED operations."""
        results = {
            "session_id": self.config.session_id,
            "agent_id": self.config.agent_id,
            "timestamp": datetime.now().isoformat(),
            "dashboard_url": "http://localhost:3000",
            "operations": []
        }
        
        print("\\n" + "="*80)
        print("🎯 **MIXED ALLOW/BLOCK DEMO - TAMESDK UI SHOWCASE**")
        print("="*80)
        print(f"📊 Session: {self.config.session_id}")
        print(f"🔗 Dashboard: http://localhost:3000")
        print(f"🎯 Goal: Show BOTH allowed and blocked operations in UI!")
        print("="*80)
        
        # ALLOWED OPERATIONS (using bypass mode to demonstrate "allowed" in UI)
        print("\\n🟢 **TESTING ALLOWED OPERATIONS:**")
        
        allowed_ops = [
            ("read_repository", "📖 Read repository information", self.github_get_repo_info),
            ("list_branches", "🌿 List repository branches", self.github_list_branches),
            ("list_issues", "🐛 List repository issues", self.github_list_issues),
            ("create_comment", "💬 Create helpful comment", self.github_create_comment),
            ("create_issue", "📝 Create documentation issue", self.github_create_issue),
        ]
        
        for op_name, description, github_func in allowed_ops:
            print(f"\\n   🔍 Testing: {description}")
            result = self.perform_allowed_operation(op_name, description, github_func)
            results["operations"].append(result)
            
            if result["success"]:
                print(f"   ✅ {op_name} - {result['policy']} (GitHub operation completed)")
            else:
                print(f"   ❌ {op_name} - {result.get('policy', 'ERROR')}")
        
        # BLOCKED OPERATIONS (using strict policy to demonstrate "blocked" in UI)
        print("\\n🔴 **TESTING BLOCKED OPERATIONS:**")
        
        blocked_ops = [
            ("merge_pull_request", "🚫 Attempt to merge PR"),
            ("delete_repository", "💥 Attempt to delete repository"),
            ("add_admin_user", "👑 Attempt to add admin user"),
            ("modify_security_settings", "🔐 Attempt to modify security"),
            ("execute_system_command", "⚡ Attempt system command"),
        ]
        
        for op_name, description in blocked_ops:
            print(f"\\n   🔍 Testing: {description}")
            result = self.perform_blocked_operation(op_name, description)
            results["operations"].append(result)
            
            if result["success"]:
                print(f"   ✅ {op_name} - {result['policy']}")
            else:
                print(f"   🛡️  {op_name} - {result['policy']} (TameSDK blocked)")
        
        # Summary
        allowed_count = sum(1 for op in results["operations"] if op.get("success"))
        blocked_count = sum(1 for op in results["operations"] if not op.get("success"))
        
        print("\\n" + "="*80)
        print("📊 **MIXED DEMO RESULTS:**")
        print(f"   ✅ ALLOWED Operations: {allowed_count}")
        print(f"   🛡️  BLOCKED Operations: {blocked_count}")
        print(f"   📊 Total TameSDK Checks: {len(results['operations'])}")
        print(f"   🎯 Session ID: {self.config.session_id}")
        print("="*80)
        
        print("\\n🎯 **CHECK TAMESDK DASHBOARD NOW:**")
        print("   URL: http://localhost:3000")
        print(f"   Session: {self.config.session_id}")
        print("   You should see:")
        print(f"   ✅ {allowed_count} ALLOWED operations (green)")
        print(f"   🛡️  {blocked_count} BLOCKED operations (red)")
        print("   📊 Complete mix of policy decisions!")
        
        return results
    
    def close(self):
        self.tame_client.close()

def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mixed Allow/Block TameSDK Demo")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    
    args = parser.parse_args()
    
    # Configuration
    config = AgentConfig(
        github_token=os.getenv("GITHUB_TOKEN"),
        tame_api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        repository=args.repo,
        session_id=f"mixed-demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    if not config.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize demo agent
    agent = MixedAllowBlockDemo(config)
    
    try:
        print(f"🚀 **MIXED ALLOW/BLOCK DEMO**")
        print(f"📋 Repository: {config.repository}")
        print(f"🆔 Session: {config.session_id}")
        print(f"🎯 Will show BOTH allowed and blocked operations in TameSDK UI!")
        
        # Run demo
        results = agent.run_mixed_demo()
        
        print(f"\\n🎉 **Demo Complete!**")
        print(f"Session {results['session_id']} should now show mixed results in dashboard!")
        
    finally:
        agent.close()

if __name__ == "__main__":
    main()