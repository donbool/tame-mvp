# GitHub Agent Setup Guide

## 🔐 **Safe API Key Management**

### **Step 1: Copy Environment Template**
```bash
cp .env.example .env
```

### **Step 2: Get Required API Keys**

#### **OpenAI API Key**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key starting with `sk-`
4. Add to `.env`: `OPENAI_API_KEY=sk-your-key-here`

#### **GitHub Personal Access Token**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:user`, `user:email`
4. Copy the token starting with `ghp_`
5. Add to `.env`: `GITHUB_TOKEN=ghp_your-token-here`

### **Step 3: Verify Environment**
```bash
# Check that keys are loaded
python -c "import os; print('✅ OpenAI key loaded' if os.getenv('OPENAI_API_KEY') else '❌ Missing OpenAI key')"
python -c "import os; print('✅ GitHub token loaded' if os.getenv('GITHUB_TOKEN') else '❌ Missing GitHub token')"
```

## 🚀 **Quick Start**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment (see above)
cp .env.example .env
# Edit .env with your keys

# 3. Start TameSDK backend
cd ../.. && docker-compose up -d && cd tests/real-agent

# 4. Create test repository and PR
python setup_github_test.py

# 5. Run the agent
python openai_github_agent.py --repo "your-username/test-repo" --action review --pr 1
```

## 🎯 **Test Scenarios**

### **Scenario 1: PR Review**
```bash
python openai_github_agent.py --repo "owner/repo" --action review --pr 123
```

### **Scenario 2: Compliance Check**
```bash
python openai_github_agent.py --repo "owner/repo" --action compliance --pr 123
```

### **Scenario 3: Security Issue**
```bash
python openai_github_agent.py --repo "owner/repo" --action security \
  --issue-title "SQL Injection Found" \
  --issue-description "Detected potential SQL injection vulnerability"
```

## 📋 **Environment Variables Reference**

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key for GPT-4 | `sk-proj-...` |
| `GITHUB_TOKEN` | ✅ | GitHub Personal Access Token | `ghp_...` |
| `TAME_API_URL` | ❌ | TameSDK backend URL | `http://localhost:8000` |
| `TAME_SESSION_ID` | ❌ | Custom session identifier | `my-test-session` |
| `TAME_AGENT_ID` | ❌ | Agent identifier | `github-pr-agent` |
| `TAME_USER_ID` | ❌ | User identifier | `developer` |

## 🔒 **Security Notes**

- ✅ **`.env` files are in `.gitignore`** - Your keys won't be committed
- ✅ **Use `.env.example`** - Template shows required variables without exposing secrets
- ✅ **Minimal permissions** - GitHub token only needs repo access
- ✅ **Local testing** - All keys stay on your machine

## 🛠️ **Troubleshooting**

### **"OpenAI API key not found"**
- Check `.env` file exists and has `OPENAI_API_KEY=sk-...`
- Verify with: `echo $OPENAI_API_KEY`

### **"GitHub token invalid"**
- Ensure token has `repo` scope
- Test with: `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user`

### **"MCP GitHub server failed"**
- Install Node.js: `brew install node`
- Verify: `npx --version`

### **"TameSDK connection failed"**
- Start backend: `docker-compose up -d`
- Check: `curl http://localhost:8000/health`

## 📊 **What You'll See**

After successful setup, you'll have:
- ✅ Real AI agent performing GitHub operations
- ✅ Policy enforcement on every API call
- ✅ Real-time session tracking in TameSDK dashboard
- ✅ Audit trail of all GitHub interactions
- ✅ Safe key management with `.env` files

This is a complete real-world example of production AI agent governance!