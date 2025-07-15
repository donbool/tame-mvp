#!/usr/bin/env python3
"""
Demo agent showing selective policy enforcement - some operations allowed, others blocked.
This creates a mock policy backend that demonstrates clear allows vs blocks.
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

# Mock policy decisions for demo
DEMO_POLICY = {
    # ALLOWED operations
    "get_repository_info": "allow",
    "list_branches": "allow", 
    "get_pull_request": "allow",
    "get_pull_request_commits": "allow",
    "list_repository_issues": "allow",
    "create_issue_comment": "allow",
    "create_pull_request_review": "allow",
    "create_issue": "allow",
    
    # BLOCKED operations  
    "merge_pull_request": "deny",
    "delete_branch": "deny",
    "create_pull_request": "deny",
    "update_file": "deny",
    "approve_pull_request": "deny",
    "add_collaborator": "deny",
    "update_repository_settings": "deny"
}

class MockTameClient:
    """Mock TameSDK client that demonstrates selective policy enforcement."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.call_count = 0
        
    def enforce(self, tool_name: str, tool_args: Dict[str, Any], **kwargs):
        self.call_count += 1
        
        # Get policy decision
        decision = DEMO_POLICY.get(tool_name, "deny")
        
        logger.info(f"🛡️  TameSDK Policy Check #{self.call_count}: {tool_name} → {decision.upper()}")
        
        if decision == "deny":
            # Simulate TameSDK policy violation
            raise tamesdk.PolicyViolationException(
                f"Tool call '{tool_name}' denied by policy: Matched rule: selective_demo_policy"
            )
        
        # Return mock decision for allowed operations
        return type('Decision', (), {
            'action': type('Action', (), {'value': 'allow'})(),
            'session_id': self.session_id,
            'rule_name': 'selective_demo_allow',
            'reason': 'Operation allowed by demo policy'
        })()
    
    def close(self):
        pass

@dataclass
class AgentConfig:
    github_token: str
    repository: str
    session_id: str

class SelectivePolicyDemo:
    """Demo agent showing clear policy allows vs blocks."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
        # Use mock TameSDK client for demo
        self.tame_client = MockTameClient(config.session_id)
        
        # GitHub API headers
        self.github_headers = {
            'Authorization': f'token {config.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        self.repo_owner, self.repo_name = config.repository.split('/')
        
        logger.info(f"Initialized selective policy demo for: {config.repository}")
    
    def safe_operation_1(self) -> Dict[str, Any]:
        """Safe read operation - should be ALLOWED."""
        # TameSDK policy check
        decision = self.tame_client.enforce(
            tool_name="get_repository_info",
            tool_args={"repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        # Perform actual operation
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {"success": True, "operation": "get_repository_info", "policy": "ALLOWED"}
    
    def safe_operation_2(self) -> Dict[str, Any]:
        """Safe read operation - should be ALLOWED."""
        decision = self.tame_client.enforce(
            tool_name="list_branches",
            tool_args={"repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/branches'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {"success": True, "operation": "list_branches", "policy": "ALLOWED"}
    
    def safe_operation_3(self) -> Dict[str, Any]:
        """Safe comment operation - should be ALLOWED."""
        decision = self.tame_client.enforce(
            tool_name="create_issue_comment",
            tool_args={"issue_number": 1, "repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/1/comments'
        data = {"body": "🤖 **Selective Policy Demo**\\n\\nThis comment was allowed by TameSDK policy! ✅"}
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        
        return {"success": True, "operation": "create_issue_comment", "policy": "ALLOWED"}
    
    def dangerous_operation_1(self) -> Dict[str, Any]:
        """Dangerous merge operation - should be BLOCKED."""
        try:
            decision = self.tame_client.enforce(
                tool_name="merge_pull_request",
                tool_args={"pr_number": 1, "repo": f"{self.repo_owner}/{self.repo_name}"}
            )
            
            # This should never execute due to policy block
            return {"success": True, "operation": "merge_pull_request", "policy": "ALLOWED"}
            
        except Exception as e:
            return {"success": False, "operation": "merge_pull_request", "policy": "BLOCKED", "reason": str(e)}
    
    def dangerous_operation_2(self) -> Dict[str, Any]:
        """Dangerous file modification - should be BLOCKED."""
        try:
            decision = self.tame_client.enforce(
                tool_name="update_file",
                tool_args={"path": "malicious.txt", "repo": f"{self.repo_owner}/{self.repo_name}"}
            )
            
            # This should never execute due to policy block
            return {"success": True, "operation": "update_file", "policy": "ALLOWED"}
            
        except Exception as e:
            return {"success": False, "operation": "update_file", "policy": "BLOCKED", "reason": str(e)}
    
    def dangerous_operation_3(self) -> Dict[str, Any]:
        """Dangerous admin operation - should be BLOCKED."""
        try:
            decision = self.tame_client.enforce(
                tool_name="add_collaborator",
                tool_args={"username": "hacker", "repo": f"{self.repo_owner}/{self.repo_name}"}
            )
            
            # This should never execute due to policy block
            return {"success": True, "operation": "add_collaborator", "policy": "ALLOWED"}
            
        except Exception as e:
            return {"success": False, "operation": "add_collaborator", "policy": "BLOCKED", "reason": str(e)}
    
    def run_selective_demo(self) -> Dict[str, Any]:
        """Run demo showing clear policy allows vs blocks."""
        results = {
            "session_id": self.config.session_id,
            "timestamp": datetime.now().isoformat(),
            "demo_policy": DEMO_POLICY,
            "operations": []
        }
        
        operations = [
            ("✅ Safe Read Operation", self.safe_operation_1),
            ("✅ Safe List Operation", self.safe_operation_2), 
            ("✅ Safe Comment Operation", self.safe_operation_3),
            ("❌ Dangerous Merge Operation", self.dangerous_operation_1),
            ("❌ Dangerous File Operation", self.dangerous_operation_2),
            ("❌ Dangerous Admin Operation", self.dangerous_operation_3),
        ]
        
        print("\\n" + "="*60)
        print("🛡️  **SELECTIVE POLICY ENFORCEMENT DEMO**")
        print("="*60)
        
        for description, operation_func in operations:
            print(f"\\n🔍 Testing: {description}")
            
            try:
                result = operation_func()
                results["operations"].append(result)
                
                if result["success"]:
                    print(f"   ✅ {result['operation']} - {result['policy']}")
                else:
                    print(f"   🛡️  {result['operation']} - {result['policy']}")
                    print(f"   📋 Reason: {result.get('reason', 'Policy violation')}")
                    
            except Exception as e:
                error_result = {"success": False, "error": str(e)}
                results["operations"].append(error_result)
                print(f"   💥 ERROR: {e}")
        
        # Summary
        allowed = sum(1 for op in results["operations"] if op.get("success"))
        blocked = sum(1 for op in results["operations"] if not op.get("success"))
        
        print("\\n" + "="*60)
        print("📊 **SELECTIVE POLICY DEMO RESULTS:**")
        print(f"   ✅ Allowed Operations: {allowed}")
        print(f"   🛡️  Blocked Operations: {blocked}")
        print(f"   📋 Total Policy Checks: {self.tame_client.call_count}")
        print("="*60)
        
        return results
    
    def close(self):
        self.tame_client.close()

def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Selective Policy Enforcement Demo")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    
    args = parser.parse_args()
    
    # Configuration
    config = AgentConfig(
        github_token=os.getenv("GITHUB_TOKEN"),
        repository=args.repo,
        session_id=f"selective-demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    if not config.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize demo agent
    agent = SelectivePolicyDemo(config)
    
    try:
        print(f"🚀 **SELECTIVE POLICY DEMO**")
        print(f"📋 Repository: {config.repository}")
        print(f"🆔 Session: {config.session_id}")
        print(f"🛡️  Demo Policy: 50% Allow, 50% Block")
        
        # Run demo
        results = agent.run_selective_demo()
        
        print(f"\\n📄 **Complete Results:**")
        print(json.dumps(results, indent=2))
        
    finally:
        agent.close()

if __name__ == "__main__":
    main()