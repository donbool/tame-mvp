#!/usr/bin/env python3
"""
Simplified GitHub Agent with direct GitHub API and TameSDK policy enforcement.
This bypasses MCP server issues and uses GitHub API directly with TameSDK wrapping.
"""

import asyncio
import os
import sys
import json
import base64
from typing import Dict, Any, Optional
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
    """Configuration for the GitHub agent."""
    openai_api_key: str
    github_token: str
    tame_api_url: str
    repository: str
    session_id: str
    agent_id: str = "github-pr-agent"
    user_id: str = "developer"

class TameEnforcedGitHubAgent:
    """GitHub agent with direct API calls wrapped in TameSDK policy enforcement."""
    
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
        
        logger.info(f"Initialized GitHub agent for repository: {config.repository}")
    
    def get_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """Get PR details with TameSDK policy enforcement."""
        # Enforce policy before GitHub API call
        decision = self.tame_client.enforce(
            tool_name="get_pull_request",
            tool_args={"pr_number": pr_number, "repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_pull_request_diff(self, pr_number: int) -> Dict[str, Any]:
        """Get PR diff with TameSDK policy enforcement."""
        # Enforce policy before GitHub API call
        decision = self.tame_client.enforce(
            tool_name="get_pull_request_diff",
            tool_args={"pr_number": pr_number, "repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}'
        headers = {**self.github_headers, 'Accept': 'application/vnd.github.v3.diff'}
        
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.text,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_pull_request_files(self, pr_number: int) -> Dict[str, Any]:
        """Get PR file changes with TameSDK policy enforcement."""
        # Enforce policy before GitHub API call
        decision = self.tame_client.enforce(
            tool_name="get_pull_request_files",
            tool_args={"pr_number": pr_number, "repo": f"{self.repo_owner}/{self.repo_name}"}
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/files'
        response = httpx.get(url, headers=self.github_headers)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    
    def create_pull_request_review(self, pr_number: int, body: str, event: str = "COMMENT") -> Dict[str, Any]:
        """Create PR review comment with TameSDK policy enforcement."""
        # Enforce policy before GitHub API call
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
        data = {
            "body": body,
            "event": event
        }
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    
    def create_issue_comment(self, pr_number: int, body: str) -> Dict[str, Any]:
        """Create issue comment with TameSDK policy enforcement."""
        # Enforce policy before GitHub API call
        decision = self.tame_client.enforce(
            tool_name="create_issue_comment",
            tool_args={
                "pr_number": pr_number,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "body_length": len(body)
            }
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments'
        data = {"body": body}
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    
    def create_issue(self, title: str, body: str, labels: list = None) -> Dict[str, Any]:
        """Create GitHub issue with TameSDK policy enforcement."""
        # Enforce policy before GitHub API call
        decision = self.tame_client.enforce(
            tool_name="create_issue",
            tool_args={
                "title": title,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "labels": labels or [],
                "body_length": len(body)
            }
        )
        
        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues'
        data = {
            "title": title,
            "body": body,
            "labels": labels or []
        }
        
        response = httpx.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    
    def review_pull_request(self, pr_number: int, focus_areas: list = None) -> Dict[str, Any]:
        """
        Review a pull request using AI analysis and post comments.
        All GitHub operations are policy-enforced via TameSDK.
        """
        focus_areas = focus_areas or ["security", "performance", "code quality"]
        
        try:
            # 1. Get PR details (policy-enforced)
            logger.info(f"🔍 Getting PR #{pr_number} details...")
            pr_details = self.get_pull_request(pr_number)
            
            if not pr_details["success"]:
                return {"error": "Failed to fetch PR details", "details": pr_details}
            
            # 2. Get PR diff (policy-enforced)  
            logger.info(f"📄 Getting PR #{pr_number} diff...")
            pr_diff = self.get_pull_request_diff(pr_number)
            
            if not pr_diff["success"]:
                return {"error": "Failed to fetch PR diff", "details": pr_diff}
            
            # 3. Get PR files (policy-enforced)
            logger.info(f"📁 Getting PR #{pr_number} files...")
            pr_files = self.get_pull_request_files(pr_number)
            
            # 4. AI analysis of the PR
            logger.info("🤖 Running AI analysis...")
            pr_info = pr_details['data']
            diff_content = pr_diff['data']
            files_info = pr_files['data'] if pr_files['success'] else []
            
            analysis_prompt = f"""You are a senior security-focused code reviewer. Analyze this pull request:

**PR Title:** {pr_info['title']}
**PR Description:** {pr_info['body'] or 'No description provided'}

**Files Changed:** {', '.join([f['filename'] for f in files_info])}

**Code Changes:**
```diff
{diff_content}
```

Focus on: {', '.join(focus_areas)}

Provide a structured review with:
1. **Security Assessment** - Any vulnerabilities, hardcoded secrets, injection risks
2. **Performance Issues** - Blocking operations, inefficient patterns  
3. **Code Quality** - Error handling, maintainability, best practices
4. **Specific Recommendations** - Actionable fixes for each issue found

Be thorough but concise. Flag serious security issues prominently.
"""
            
            # Get AI review
            ai_response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert security-focused code reviewer. Provide detailed, actionable feedback."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            review_content = ai_response.choices[0].message.content
            
            # 5. Post review comment (policy-enforced)
            logger.info("💬 Posting AI review comment...")
            comment_body = f"""## 🤖 AI Security & Code Review

{review_content}

---
**Review Details:**
- **Agent:** TameSDK-enforced AI reviewer
- **Model:** GPT-4
- **Focus Areas:** {', '.join(focus_areas)}
- **Session ID:** {self.config.session_id}
- **Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

*This review was conducted by an AI agent with policy enforcement via TameSDK. All operations are logged and audited.*"""
            
            comment_result = self.create_pull_request_review(
                pr_number=pr_number,
                body=comment_body,
                event="COMMENT"
            )
            
            return {
                "success": True,
                "pr_number": pr_number,
                "review_posted": comment_result["success"],
                "ai_analysis": review_content,
                "operations_count": 4,  # PR details, diff, files, comment
                "session_id": self.config.session_id
            }
            
        except Exception as e:
            logger.error(f"PR review failed: {e}")
            return {"success": False, "error": str(e)}
    
    def check_pr_compliance(self, pr_number: int) -> Dict[str, Any]:
        """Check if a PR meets compliance requirements."""
        try:
            logger.info(f"🔍 Checking compliance for PR #{pr_number}...")
            
            # Get PR files (policy-enforced)
            pr_files = self.get_pull_request_files(pr_number)
            
            if not pr_files["success"]:
                return {"error": "Failed to fetch PR files"}
            
            # Analyze files for compliance issues
            compliance_issues = []
            files_data = pr_files["data"]
            
            for file_info in files_data:
                filename = file_info.get("filename", "")
                changes = file_info.get("changes", 0)
                additions = file_info.get("additions", 0)
                
                # Check for sensitive files
                sensitive_patterns = ["password", "secret", "key", "token", ".env", "config.json", "credentials"]
                if any(pattern in filename.lower() for pattern in sensitive_patterns):
                    compliance_issues.append(f"⚠️  **Sensitive file detected:** `{filename}` - Review for exposed secrets")
                
                # Check for large files
                if changes > 500:
                    compliance_issues.append(f"📏 **Large change:** `{filename}` ({changes} lines) - Consider breaking into smaller changes")
                
                # Check for specific file types that need review
                if filename.endswith(('.sql', '.sh', '.ps1')):
                    compliance_issues.append(f"🔒 **Script file:** `{filename}` - Requires security review")
            
            # If compliance issues found, add blocking comment (policy-enforced)
            if compliance_issues:
                logger.info("⚠️  Compliance issues found, posting warning...")
                
                blocking_comment = f"""## 🚨 **Compliance Review Required**

This PR has been flagged for the following compliance concerns:

{chr(10).join(f"• {issue}" for issue in compliance_issues)}

### **Required Actions:**
- [ ] Review and address the flagged items above
- [ ] Ensure no sensitive data is committed to the repository
- [ ] Verify all secrets are properly externalized
- [ ] Consider breaking large changes into smaller, focused PRs

### **Security Checklist:**
- [ ] No hardcoded passwords, API keys, or tokens
- [ ] No database connection strings with credentials
- [ ] No `.env` files or configuration with secrets
- [ ] All user inputs are properly validated and sanitized

---
**Compliance Check Details:**
- **Agent:** TameSDK-enforced compliance checker
- **Files Reviewed:** {len(files_data)}
- **Issues Found:** {len(compliance_issues)}
- **Session ID:** {self.config.session_id}

*This automated compliance check helps ensure security and quality standards. All operations are policy-controlled and audited.*"""
                
                comment_result = self.create_issue_comment(pr_number, blocking_comment)
                
                return {
                    "compliant": False,
                    "issues_count": len(compliance_issues),
                    "issues": compliance_issues,
                    "comment_posted": comment_result["success"],
                    "action": "FLAGGED",
                    "session_id": self.config.session_id
                }
            
            # No issues found
            logger.info("✅ No compliance issues detected")
            return {
                "compliant": True,
                "issues_count": 0,
                "issues": [],
                "action": "APPROVED",
                "session_id": self.config.session_id
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {"success": False, "error": str(e)}
    
    def create_security_issue(self, title: str, description: str, labels: list = None) -> Dict[str, Any]:
        """Create a security issue in the repository (policy-enforced)."""
        labels = labels or ["security", "needs-review"]
        
        issue_body = f"""## 🔒 Security Concern

{description}

### **Reported By**
- **Agent:** TameSDK-enforced security agent
- **Session ID:** {self.config.session_id}
- **Timestamp:** {datetime.now().isoformat()}

### **Recommended Actions**
- [ ] Investigate the security concern thoroughly
- [ ] Implement necessary security fixes
- [ ] Review similar patterns across the codebase
- [ ] Update security documentation if needed
- [ ] Consider adding automated security checks

### **Priority**
This issue was automatically created by an AI security agent and should be reviewed promptly.

---
*This security issue was created automatically by an AI agent with policy enforcement via TameSDK.*"""
        
        try:
            logger.info(f"🔒 Creating security issue: {title}")
            result = self.create_issue(
                title=f"🔒 {title}",
                body=issue_body,
                labels=labels
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create security issue: {e}")
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Clean up connections."""
        self.tame_client.close()

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Agent with TameSDK Policy Enforcement")
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
        print("❌ Error: OPENAI_API_KEY environment variable required")
        sys.exit(1)
    
    if not config.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)
    
    # Initialize agent
    agent = TameEnforcedGitHubAgent(config)
    
    try:
        print(f"🚀 GitHub agent initialized!")
        print(f"📋 Repository: {config.repository}")
        print(f"🆔 Session: {config.session_id}")
        print(f"🛡️  All operations are policy-enforced via TameSDK")
        
        # Execute requested action
        if args.action == "review" and args.pr:
            print(f"\\n🔍 Reviewing PR #{args.pr}...")
            result = agent.review_pull_request(args.pr)
            print(f"\\n✅ Review completed!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
            
        elif args.action == "compliance" and args.pr:
            print(f"\\n✅ Checking compliance for PR #{args.pr}...")
            result = agent.check_pr_compliance(args.pr)
            print(f"\\n📋 Compliance check completed!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
            
        elif args.action == "security" and args.issue_title and args.issue_description:
            print(f"\\n🔒 Creating security issue...")
            result = agent.create_security_issue(args.issue_title, args.issue_description)
            print(f"\\n🔒 Security issue created!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
            
        else:
            print("❌ Error: Invalid action or missing parameters")
            print("\\nExamples:")
            print(f"  python3 simple_github_agent.py --repo {args.repo} --action review --pr 1")
            print(f"  python3 simple_github_agent.py --repo {args.repo} --action compliance --pr 1")
            print(f"  python3 simple_github_agent.py --repo {args.repo} --action security --issue-title 'Security Issue' --issue-description 'Description'")
        
    finally:
        agent.close()

if __name__ == "__main__":
    main()