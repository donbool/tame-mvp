# Real GitHub Agent with OpenAI + TameSDK

This is a **real-world example** of an AI agent that uses:
- **OpenAI GPT-4** for intelligent PR reviews
- **GitHub MCP Server** for GitHub API access
- **TameSDK** for policy enforcement and session tracking

## 🎯 What This Agent Does

The agent can perform GitHub operations with strict policy controls:

### ✅ **Allowed Operations** (by policy):
- Read PR details, diffs, and files
- Post review comments (but not approve/reject PRs)
- Create security-related issues
- Compliance checking

### ❌ **Blocked Operations** (by policy):
- Repository modifications (push, merge, delete)
- Administrative actions (add collaborators, webhooks)
- Auto-approving or rejecting PRs
- Bulk operations without approval

### 🔍 **Smart Features**:
- **AI Code Review**: GPT-4 analyzes code for security, performance, and quality
- **Compliance Checking**: Detects sensitive files, large changes
- **Security Issue Creation**: Automatically files security concerns
- **Policy Enforcement**: Every GitHub API call goes through TameSDK

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template and fill in your keys
cp .env.example .env
# Edit .env with your actual API keys

# Or set environment variables directly
export OPENAI_API_KEY="sk-..."
export GITHUB_TOKEN="ghp_..."
export TAME_API_URL="http://localhost:8000"

# Run setup script
python setup_github_test.py
```

### 2. **Start TameSDK Backend**
```bash
# In the main tame-mvp directory
docker-compose up -d
```

### 3. **Load GitHub Policy**
The policy in `github_policy.yaml` defines what the agent can/cannot do. Load it into your TameSDK backend.

### 4. **Run the Agent**
```bash
# Review a pull request
python openai_github_agent.py --repo "owner/repo" --action review --pr 123

# Check PR compliance
python openai_github_agent.py --repo "owner/repo" --action compliance --pr 123

# Create security issue
python openai_github_agent.py --repo "owner/repo" --action security \
  --issue-title "SQL Injection Found" \
  --issue-description "Detected potential SQL injection in user input handling"
```

## 📋 Policy Configuration

The `github_policy.yaml` file contains comprehensive rules:

```yaml
# Example policy rules
rules:
  - name: "allow_pr_read"
    condition:
      tool_name: ["get_pull_request", "get_pull_request_diff"]
    action: "allow"
    
  - name: "deny_repo_modifications" 
    condition:
      tool_name: ["merge_pull_request", "push_to_branch"]
    action: "deny"
    reason: "Repository modifications not allowed"
    
  - name: "approve_large_issues"
    condition:
      tool_name: "create_issue"
      arguments:
        body_length: ">500"
    action: "approve"  # Requires human approval
```

## 🎮 Real-World Test Scenarios

### **Scenario 1: AI Code Review**
1. Create a PR with intentional code issues
2. Run: `python openai_github_agent.py --repo owner/repo --action review --pr 123`
3. Watch as the agent:
   - Fetches PR details (✅ allowed by policy)
   - Analyzes code with GPT-4
   - Posts intelligent review comments (✅ allowed)
   - **Cannot** auto-approve the PR (❌ blocked by policy)

### **Scenario 2: Compliance Enforcement**
1. Create a PR that modifies sensitive files
2. Run: `python openai_github_agent.py --repo owner/repo --action compliance --pr 123`
3. Agent detects issues and posts blocking comments
4. All operations are logged in TameSDK dashboard

### **Scenario 3: Security Issue Creation**
1. Agent discovers a security vulnerability
2. Attempts to create a GitHub issue
3. TameSDK enforces policy (may require approval for large issues)
4. Issue is created with proper labeling

## 🔍 What You'll See in TameSDK Dashboard

Every GitHub API call appears in real-time:

```json
{
  "session_id": "github-agent-20240115-143022",
  "tool_name": "get_pull_request",
  "arguments": {"owner": "test", "repo": "example", "pull_number": 123},
  "decision": "allow",
  "rule_name": "allow_pr_read",
  "timestamp": "2024-01-15T14:30:22Z"
}
```

## 🛡️ Security Features

- **Zero Trust**: Every operation requires policy approval
- **Audit Trail**: Complete log of all GitHub interactions
- **Session Isolation**: Each agent run is tracked separately
- **Rate Limiting**: Built-in session limits prevent abuse
- **Human Oversight**: Sensitive operations require approval

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenAI Agent  │────│   TameSDK        │────│   GitHub MCP    │
│   (GPT-4)       │    │   (Policy)       │    │   (GitHub API)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │   TameSDK        │
                    │   Dashboard      │
                    │   (Real-time)    │
                    └──────────────────┘
```

## 🎯 Why This Matters

This demonstrates **real-world AI agent governance**:

1. **Practical Use Case**: AI code reviews are actually useful
2. **Real Integration**: Uses actual OpenAI API and GitHub API
3. **Policy Enforcement**: Shows how TameSDK prevents dangerous operations
4. **Audit Trail**: Every action is logged and traceable
5. **Human Oversight**: Critical operations require approval

This is exactly how you'd deploy AI agents in production with proper controls.

## 🔧 Customization

**Modify the policy** (`github_policy.yaml`) to:
- Allow different GitHub operations
- Add new approval requirements
- Customize session limits
- Add organization-specific rules

**Extend the agent** (`openai_github_agent.py`) to:
- Add new GitHub workflows
- Integrate with other MCP servers
- Implement custom compliance checks
- Add more AI analysis features

## 📊 Testing Results

After running this agent, you'll have:
- ✅ Proof that TameSDK can control real AI operations
- ✅ Audit logs of all GitHub API calls
- ✅ Real-time monitoring in the dashboard
- ✅ Policy violations properly blocked
- ✅ Human approval workflows working

This validates the entire TameSDK approach with a practical, real-world example.