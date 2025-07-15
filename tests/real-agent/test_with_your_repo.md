# Testing with Your GitHub Repository

## 🎯 **Testing Plan for `donbool/tame-github-mcp-test`**

### **Step 1: Environment Setup**
```bash
# In /Users/benji/Desktop/tame/tame-mvp/tests/real-agent/

# Copy environment template
cp .env.example .env

# Edit .env with your tokens
nano .env
```

Add to `.env`:
```bash
OPENAI_API_KEY=your-openai-key-here
GITHUB_TOKEN=your-github-token-here
TAME_API_URL=http://localhost:8000
GITHUB_USER=donbool
```

### **Step 2: Install Dependencies**
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import openai, mcp, tamesdk; print('✅ All packages installed')"
```

### **Step 3: Start TameSDK Backend**
```bash
# From tame-mvp root directory
cd ../..
docker-compose up -d
cd tests/real-agent

# Verify backend is running
curl http://localhost:8000/health
```

### **Step 4: Create Test PR for Agent Review**

**Option A: Manual PR Creation**
1. Go to https://github.com/donbool/tame-github-mcp-test
2. Create a new branch: `test-pr-for-ai-review`
3. Add a file with intentional issues (see test file below)
4. Create PR from that branch to main

**Option B: Automated PR Creation**
```bash
# Use the setup script to create test PR
python setup_github_test.py
# When prompted, enter: donbool/tame-github-mcp-test
```

### **Test File Content** (add this to your test PR):

Create `security_test.py`:
```python
# Test file with intentional security and quality issues
import os
import requests
import sqlite3

def vulnerable_function(user_input):
    # SQL Injection vulnerability
    conn = sqlite3.connect('users.db')
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor = conn.execute(query)
    
    # Hardcoded secrets (should be flagged)
    api_key = "sk-1234567890abcdef"
    password = "admin123"
    
    # Performance issue: blocking requests in loop
    results = []
    for i in range(100):
        response = requests.get(f"https://api.example.com/user/{i}")
        results.append(response.json())
    
    return results

def another_security_issue():
    # Using eval (dangerous)
    user_code = input("Enter code: ")
    return eval(user_code)

# Exposed environment variables
DATABASE_URL = "postgresql://admin:password123@localhost/prod"
```

### **Step 5: Test Real Agent Operations**

**Test 1: AI Code Review**
```bash
python openai_github_agent.py \
  --repo "donbool/tame-github-mcp-test" \
  --action review \
  --pr 1  # Use your actual PR number
```

**Expected behavior:**
- ✅ Agent reads PR details (allowed by policy)
- ✅ Agent analyzes code with GPT-4
- ✅ Agent posts intelligent review comment (allowed)
- ❌ Agent CANNOT approve/reject PR (blocked by policy)
- 📊 All operations appear in TameSDK dashboard

**Test 2: Compliance Check**
```bash
python openai_github_agent.py \
  --repo "donbool/tame-github-mcp-test" \
  --action compliance \
  --pr 1
```

**Expected behavior:**
- ✅ Detects security issues in test file
- ✅ Posts compliance warning comment
- 📊 Policy enforcement logged in TameSDK

**Test 3: Security Issue Creation**
```bash
python openai_github_agent.py \
  --repo "donbool/tame-github-mcp-test" \
  --action security \
  --issue-title "Hardcoded API Keys Detected" \
  --issue-description "Found hardcoded API keys in security_test.py that should be moved to environment variables"
```

**Expected behavior:**
- ✅ Creates GitHub issue with security label
- 📊 Issue creation logged in TameSDK
- 🔍 May require approval if issue body is large

### **Step 6: Monitor TameSDK Dashboard**

1. Open http://localhost:3000 (TameSDK frontend)
2. Look for your session: `github-agent-YYYYMMDD-HHMMSS`
3. Watch real-time policy decisions:
   - `get_pull_request` → ALLOW
   - `create_pull_request_review` → ALLOW  
   - `merge_pull_request` → DENY (if attempted)

### **Step 7: Test Policy Violations**

**Try Blocked Operation** (should fail):
```bash
# This should be blocked by policy
# (Would need to modify agent code to attempt this)
```

The policy prevents:
- Merging PRs
- Pushing code
- Administrative operations
- Auto-approving PRs

## 🎯 **What Makes This Real-World**

### **Real MCP Agent Patterns:**
✅ **Authentic MCP Integration**: Uses actual `@modelcontextprotocol/server-github`
✅ **Real OpenAI API**: GPT-4 for actual code analysis  
✅ **Standard Architecture**: MCP client → MCP server → GitHub API
✅ **Production Patterns**: Async operations, error handling, logging

### **Real Business Use Case:**
✅ **Code Review Automation**: AI reviews PRs for security/quality
✅ **Policy Enforcement**: Prevent dangerous operations
✅ **Compliance Checking**: Automated security scanning
✅ **Audit Trail**: Complete logging of all operations

### **Real Developer Experience:**
✅ **Standard Tools**: Uses official OpenAI SDK and MCP libraries
✅ **Environment Variables**: Standard `.env` pattern
✅ **Error Handling**: Graceful failures and retries
✅ **Documentation**: Production-quality README and setup

## 🚀 **Ready to Test?**

1. **Set up `.env`** with your tokens
2. **Start TameSDK**: `docker-compose up -d`
3. **Create test PR** with security issues
4. **Run agent**: Test all three operations
5. **Watch dashboard**: See real-time policy enforcement

This demonstrates exactly how TameSDK would work in production - real AI operations with real-time governance!