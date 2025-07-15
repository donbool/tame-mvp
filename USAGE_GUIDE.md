# TameSDK Complete Usage Guide

**Comprehensive documentation for runtime control of AI agents**

---

## 📚 Table of Contents

1. [Quick Start](#-quick-start)
2. [Installation](#-installation)
3. [Configuration](#-configuration)
4. [Python SDK Usage](#-python-sdk-usage)
5. [CLI Usage](#-cli-usage)
6. [Real-World Examples](#-real-world-examples)
7. [Advanced Features](#-advanced-features)
8. [Error Handling](#-error-handling)
9. [Best Practices](#-best-practices)
10. [Troubleshooting](#-troubleshooting)
11. [API Reference](#-api-reference)

---

## 🚀 Quick Start

### **30-Second Setup**

```bash
# 1. Start the Tame platform
docker-compose up -d

# 2. Install TameSDK
cd tamesdk && pip install -e .

# 3. Test it works
tamesdk status

# 4. Use in Python (2 lines!)
python -c "
import tamesdk

@tamesdk.enforce_policy
def read_file(path: str):
    return open(path).read()

# This function now has automatic policy enforcement!
"
```

---

## 📦 Installation

### **Method 1: Development Installation (Recommended)**

```bash
# Clone and install in development mode
cd /path/to/tame-mvp/tamesdk
pip install -e .

# Verify installation
python -c "import tamesdk; print(f'TameSDK {tamesdk.__version__} installed!')"
```

### **Method 2: Production Installation**

```bash
# Build and install the package
cd /path/to/tame-mvp/tamesdk
pip install .

# Or install from wheel
python setup.py bdist_wheel
pip install dist/tamesdk-1.0.0-py3-none-any.whl
```

### **Dependencies**

- **Python**: 3.8+
- **Required**: `httpx >= 0.24.0`
- **Optional**: `mcp >= 1.0.0` (for MCP agent integration)

---

## ⚙️ Configuration

### **Environment Variables (Easiest)**

```bash
export TAME_API_URL="http://localhost:8000"
export TAME_API_KEY="your-secret-key"
export TAME_SESSION_ID="my-session"
export TAME_AGENT_ID="my-agent"
export TAME_USER_ID="my-user"
export TAME_BYPASS_MODE="false"
```

### **Programmatic Configuration**

```python
import tamesdk

# Global configuration (set once)
tamesdk.configure(
    api_url="http://localhost:8000",
    api_key="your-secret-key",
    session_id="my-session-123",
    agent_id="openai-agent",
    user_id="john-doe",
    bypass_mode=False,  # Set to True for development
    raise_on_deny=True,
    raise_on_approve=True
)

# Check current configuration
config = tamesdk.get_config()
print(f"API URL: {config.api_url}")
print(f"Session: {config.session_id}")
```

### **Configuration File**

```yaml
# ~/.tame/config.yaml
api_url: "http://localhost:8000"
api_key: "your-secret-key"
session_id: "my-session"
agent_id: "my-agent"
user_id: "my-user"
bypass_mode: false
raise_on_deny: true
raise_on_approve: true
```

```python
# Load from file
config = tamesdk.load_config("~/.tame/config.yaml")
tamesdk.configure(**config.__dict__)
```

---

## 🐍 Python SDK Usage

### **Method 1: Decorators (Simplest - 2 Lines!)**

```python
import tamesdk

# Basic policy enforcement
@tamesdk.enforce_policy
def read_file(path: str) -> str:
    """This function is now policy-controlled!"""
    with open(path, 'r') as f:
        return f.read()

# Advanced decorator with options
@tamesdk.enforce_policy(
    tool_name="custom_file_reader",
    metadata={"category": "file_operations", "risk": "low"},
    raise_on_deny=True
)
def safe_read_file(path: str) -> str:
    return open(path).read()

# Require approval for dangerous operations
@tamesdk.with_approval(
    approval_message="This operation modifies system files"
)
def write_system_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)

# Log-only (no policy enforcement)
@tamesdk.log_action(level="INFO")
def helper_function(data: dict) -> dict:
    return {"processed": data}
```

### **Method 2: Client Usage (Most Control)**

```python
import tamesdk

# Synchronous client
with tamesdk.Client() as client:
    # Test policy without executing
    decision = client.enforce(
        tool_name="delete_file",
        tool_args={"path": "/important/file.txt"},
        raise_on_deny=False,
        raise_on_approve=False
    )
    
    if decision.is_allowed:
        print("✅ Policy allows this action")
        # Execute your tool here
        result = delete_file("/important/file.txt")
        
        # Log the result
        client.update_result(
            decision.session_id,
            decision.log_id,
            {"status": "success", "result": result}
        )
    elif decision.is_denied:
        print(f"❌ Policy denied: {decision.reason}")
    elif decision.requires_approval:
        print(f"⏳ Approval required: {decision.reason}")
```

### **Method 3: Async Usage (High Performance)**

```python
import asyncio
import tamesdk

async def main():
    async with tamesdk.AsyncClient() as client:
        # Async policy enforcement
        decision = await client.enforce(
            "api_call",
            {"endpoint": "https://api.example.com/data"}
        )
        
        if decision.is_allowed:
            # Execute async operation
            result = await make_api_call("https://api.example.com/data")
            
            # Log result
            await client.update_result(
                decision.session_id,
                decision.log_id,
                {"status": "success", "data": result}
            )

asyncio.run(main())
```

### **Method 4: Execute Tool Helper**

```python
import tamesdk

def my_tool_executor(tool_name: str, tool_args: dict):
    """Your actual tool execution logic"""
    if tool_name == "read_file":
        return open(tool_args["path"]).read()
    elif tool_name == "write_file":
        with open(tool_args["path"], 'w') as f:
            f.write(tool_args["content"])
        return "File written successfully"

# Automatic enforcement + execution + logging
with tamesdk.Client() as client:
    result = client.execute_tool(
        tool_name="read_file",
        tool_args={"path": "/tmp/file.txt"},
        executor=my_tool_executor
    )
    
    if result.success:
        print(f"✅ Tool executed: {result.result}")
    else:
        print(f"❌ Tool failed: {result.error}")
```

---

## 💻 CLI Usage

### **Installation Verification**

```bash
# Check if CLI is installed
tamesdk --help

# Alternative way to run CLI
python -m tamesdk.cli --help
```

### **Basic Commands**

```bash
# Check connection status
tamesdk status

# Test a tool call
tamesdk test read_file --args '{"path": "/tmp/file.txt"}'

# Show policy information
tamesdk policy

# Start interactive mode
tamesdk interactive
```

### **Advanced CLI Usage**

```bash
# Test with custom API URL
tamesdk --api-url http://prod.example.com:8000 status

# Test with complex arguments
tamesdk test api_call --args '{
  "url": "https://api.example.com",
  "method": "POST",
  "headers": {"Authorization": "Bearer token"},
  "body": {"query": "test"}
}'

# Enforce a tool call (returns exit codes)
tamesdk enforce --tool delete_file --args '{"path": "/tmp/test"}'
echo "Exit code: $?"  # 0=allow, 2=deny, 3=approve
```

### **Interactive Mode**

```bash
tamesdk interactive

# Once in interactive mode:
tamesdk> help
tamesdk> status
tamesdk> policy
tamesdk> test read_file {"path": "/tmp/test.txt"}
tamesdk> test api_call url=https://example.com,method=GET
tamesdk> config
tamesdk> quit
```

### **CLI Configuration**

```bash
# Use environment variables
export TAME_API_URL="http://localhost:8000"
export TAME_API_KEY="your-key"
tamesdk status

# Or pass as arguments
tamesdk --api-url http://localhost:8000 status
```

---

## 🌍 Real-World Examples

### **OpenAI Integration**

```python
import tamesdk
import openai

# Configure TameSDK
tamesdk.configure(
    api_url="http://localhost:8000",
    agent_id="openai-assistant",
    user_id="john-doe"
)

# Method 1: Decorator approach
@tamesdk.enforce_policy(
    tool_name="openai_completion",
    metadata={"provider": "openai", "cost_tracking": True}
)
def call_openai(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 1000):
    """Call OpenAI with automatic policy enforcement."""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# Method 2: Client approach
class OpenAIClient:
    def __init__(self):
        self.tame_client = tamesdk.Client()
        self.openai_client = openai.OpenAI()
    
    def completion(self, prompt: str, model: str = "gpt-3.5-turbo"):
        # Enforce policy first
        decision = self.tame_client.enforce(
            "openai_completion",
            {
                "prompt": prompt,
                "model": model,
                "estimated_tokens": len(prompt) * 4,
                "estimated_cost": self._estimate_cost(model, len(prompt))
            }
        )
        
        if decision.is_allowed:
            # Execute OpenAI call
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.choices[0].message.content
            
            # Log the result
            self.tame_client.update_result(
                decision.session_id,
                decision.log_id,
                {
                    "tokens_used": response.usage.total_tokens,
                    "actual_cost": self._calculate_cost(model, response.usage.total_tokens),
                    "result_length": len(result)
                }
            )
            
            return result
    
    def _estimate_cost(self, model: str, prompt_length: int) -> float:
        rates = {"gpt-3.5-turbo": 0.002, "gpt-4": 0.03}
        estimated_tokens = prompt_length * 4
        return (estimated_tokens / 1000) * rates.get(model, 0.002)

# Usage
try:
    result = call_openai("Explain quantum computing", model="gpt-4")
    print(f"✅ Response: {result}")
except tamesdk.PolicyViolationException as e:
    print(f"❌ Blocked by policy: {e.decision.reason}")
except tamesdk.ApprovalRequiredException as e:
    print(f"⏳ Requires approval: {e.decision.reason}")
```

### **MCP Agent Integration**

```python
import asyncio
import tamesdk
from mcp import types
from mcp.client.stdio import stdio_client

class TameMCPAgent:
    """MCP Agent with TameSDK integration."""
    
    def __init__(self, agent_id: str):
        self.tame_client = tamesdk.AsyncClient(agent_id=agent_id)
        self.mcp_session = None
    
    async def connect_mcp(self, server_command: list):
        """Connect to MCP server."""
        self.mcp_session = await stdio_client(server_command).__aenter__()
        await self.mcp_session.initialize()
    
    async def execute_tool(self, tool_name: str, arguments: dict):
        """Execute MCP tool with policy enforcement."""
        
        # Enforce policy through TameSDK
        decision = await self.tame_client.enforce(
            tool_name=tool_name,
            tool_args=arguments,
            metadata={"mcp_agent": True, "tool_category": self._categorize_tool(tool_name)}
        )
        
        if decision.is_allowed:
            # Execute via MCP
            result = await self.mcp_session.call_tool(tool_name, arguments)
            
            # Extract result content
            content = []
            for item in result.content:
                if isinstance(item, types.TextContent):
                    content.append(item.text)
            
            # Log result
            await self.tame_client.update_result(
                decision.session_id,
                decision.log_id,
                {"status": "success", "content": content}
            )
            
            return content
    
    def _categorize_tool(self, tool_name: str) -> str:
        """Categorize tool for policy decisions."""
        if "read" in tool_name.lower():
            return "read"
        elif "write" in tool_name.lower() or "create" in tool_name.lower():
            return "write"
        elif "delete" in tool_name.lower():
            return "delete"
        else:
            return "other"

# Usage
async def main():
    agent = TameMCPAgent("mcp-file-agent")
    await agent.connect_mcp(["python", "filesystem_server.py"])
    
    try:
        result = await agent.execute_tool("read_file", {"path": "/tmp/test.txt"})
        print(f"✅ File content: {result}")
    except tamesdk.PolicyViolationException as e:
        print(f"❌ Blocked: {e.decision.reason}")

asyncio.run(main())
```

### **Database Operations**

```python
import tamesdk
import psycopg2

@tamesdk.enforce_policy(
    tool_name="database_query",
    metadata={"database": "production", "sensitive": True}
)
def execute_query(sql: str, params: tuple = None):
    """Execute database query with policy enforcement."""
    conn = psycopg2.connect("postgresql://user:pass@localhost/db")
    cursor = conn.cursor()
    cursor.execute(sql, params)
    
    if sql.strip().upper().startswith('SELECT'):
        return cursor.fetchall()
    else:
        conn.commit()
        return cursor.rowcount

@tamesdk.with_approval(
    approval_message="Deleting user data requires manual approval"
)
def delete_user_data(user_id: int):
    """Delete user data (requires approval)."""
    return execute_query("DELETE FROM users WHERE id = %s", (user_id,))

# Usage
try:
    users = execute_query("SELECT * FROM users LIMIT 10")
    print(f"✅ Found {len(users)} users")
    
    # This will require approval
    delete_user_data(123)
    
except tamesdk.ApprovalRequiredException as e:
    print(f"⏳ Manual approval required: {e.decision.reason}")
    # In production, you'd queue this for approval workflow
```

### **File System Operations**

```python
import tamesdk
import os
import shutil

class FileManager:
    """File operations with TameSDK integration."""
    
    def __init__(self):
        self.client = tamesdk.Client()
    
    @tamesdk.enforce_policy(metadata={"operation": "read", "risk": "low"})
    def read_file(self, path: str) -> str:
        """Read file contents."""
        with open(path, 'r') as f:
            return f.read()
    
    @tamesdk.enforce_policy(metadata={"operation": "write", "risk": "medium"})
    def write_file(self, path: str, content: str) -> bool:
        """Write file contents."""
        with open(path, 'w') as f:
            f.write(content)
        return True
    
    @tamesdk.with_approval(approval_message="File deletion requires approval")
    def delete_file(self, path: str) -> bool:
        """Delete file (requires approval)."""
        os.remove(path)
        return True
    
    def batch_operation(self, operations: list):
        """Execute multiple file operations."""
        results = []
        
        for op in operations:
            try:
                decision = self.client.enforce(
                    f"file_{op['action']}",
                    op['args'],
                    raise_on_deny=False,
                    raise_on_approve=False
                )
                
                if decision.is_allowed:
                    # Execute operation
                    if op['action'] == 'read':
                        result = self.read_file(op['args']['path'])
                    elif op['action'] == 'write':
                        result = self.write_file(op['args']['path'], op['args']['content'])
                    
                    results.append({"success": True, "result": result})
                else:
                    results.append({
                        "success": False, 
                        "error": f"Policy {decision.action.value}: {decision.reason}"
                    })
                    
            except Exception as e:
                results.append({"success": False, "error": str(e)})
        
        return results

# Usage
fm = FileManager()

# Single operations
content = fm.read_file("/tmp/safe_file.txt")
fm.write_file("/tmp/output.txt", "Hello TameSDK!")

# Batch operations
operations = [
    {"action": "read", "args": {"path": "/tmp/file1.txt"}},
    {"action": "write", "args": {"path": "/tmp/file2.txt", "content": "data"}},
    {"action": "read", "args": {"path": "/etc/passwd"}},  # This might be denied
]

results = fm.batch_operation(operations)
for i, result in enumerate(results):
    if result["success"]:
        print(f"✅ Operation {i+1}: Success")
    else:
        print(f"❌ Operation {i+1}: {result['error']}")
```

---

## 🔧 Advanced Features

### **Custom Error Handling**

```python
import tamesdk
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyAwareService:
    """Service with comprehensive error handling."""
    
    def __init__(self):
        self.client = tamesdk.Client()
        self.fallback_mode = False
    
    def execute_with_fallback(self, tool_name: str, tool_args: dict, fallback_func=None):
        """Execute with policy enforcement and fallback options."""
        try:
            # Try policy enforcement
            decision = self.client.enforce(tool_name, tool_args)
            
            if decision.is_allowed:
                return self._execute_tool(tool_name, tool_args)
                
        except tamesdk.PolicyViolationException as e:
            logger.warning(f"Policy denied {tool_name}: {e.decision.reason}")
            
            if fallback_func:
                logger.info(f"Executing fallback for {tool_name}")
                return fallback_func(tool_args)
            else:
                raise
                
        except tamesdk.ApprovalRequiredException as e:
            logger.info(f"Approval required for {tool_name}: {e.decision.reason}")
            
            # Queue for approval (implementation depends on your workflow)
            approval_id = self._queue_for_approval(e.decision)
            raise tamesdk.ApprovalRequiredException(e.decision) from e
            
        except tamesdk.ConnectionException as e:
            logger.error(f"Cannot connect to Tame API: {e}")
            
            if self.fallback_mode:
                logger.warning(f"Executing {tool_name} in fallback mode")
                return self._execute_tool(tool_name, tool_args)
            else:
                raise
                
        except Exception as e:
            logger.error(f"Unexpected error in {tool_name}: {e}")
            raise
    
    def _execute_tool(self, tool_name: str, tool_args: dict):
        """Your actual tool execution logic."""
        # Implementation depends on your tools
        pass
    
    def _queue_for_approval(self, decision) -> str:
        """Queue decision for manual approval."""
        # Implementation depends on your approval workflow
        return f"approval-{decision.log_id}"

# Usage with fallback
service = PolicyAwareService()

def safe_fallback(args):
    """Safe fallback when policy denies action."""
    return f"Fallback result for {args}"

try:
    result = service.execute_with_fallback(
        "risky_operation",
        {"data": "sensitive"},
        fallback_func=safe_fallback
    )
    print(f"✅ Result: {result}")
    
except Exception as e:
    print(f"❌ Failed: {e}")
```

### **Session Management**

```python
import tamesdk
from datetime import datetime, timedelta

class SessionManager:
    """Advanced session management."""
    
    def __init__(self, base_session_id: str):
        self.base_session_id = base_session_id
        self.clients = {}
    
    def get_client(self, context: str) -> tamesdk.Client:
        """Get client for specific context."""
        session_id = f"{self.base_session_id}-{context}"
        
        if session_id not in self.clients:
            self.clients[session_id] = tamesdk.Client(
                session_id=session_id,
                metadata={"context": context, "created_at": datetime.now().isoformat()}
            )
        
        return self.clients[session_id]
    
    def execute_in_context(self, context: str, tool_name: str, tool_args: dict):
        """Execute tool in specific session context."""
        client = self.get_client(context)
        return client.execute_tool(tool_name, tool_args)
    
    def get_session_summary(self, context: str = None) -> dict:
        """Get summary for specific context or all contexts."""
        if context:
            client = self.get_client(context)
            return self._summarize_session(client)
        else:
            summaries = {}
            for ctx, client in self.clients.items():
                summaries[ctx] = self._summarize_session(client)
            return summaries
    
    def _summarize_session(self, client: tamesdk.Client) -> dict:
        """Create session summary."""
        try:
            # This would use the session logs endpoint when available
            return {
                "session_id": client.session_id,
                "agent_id": client.agent_id,
                "user_id": client.user_id,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old session clients."""
        # Implementation would check session ages and clean up
        pass

# Usage
session_manager = SessionManager("user-123-session")

# Execute in different contexts
result1 = session_manager.execute_in_context(
    "file-operations",
    "read_file",
    {"path": "/tmp/file.txt"}
)

result2 = session_manager.execute_in_context(
    "api-calls", 
    "http_request",
    {"url": "https://api.example.com"}
)

# Get summaries
summaries = session_manager.get_session_summary()
print(f"📊 Session summaries: {summaries}")
```

### **Policy Testing Framework**

```python
import tamesdk
import json
from typing import List, Dict, Any

class PolicyTester:
    """Framework for testing policies."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.client = tamesdk.Client(api_url=api_url)
        self.test_results = []
    
    def run_test_suite(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a suite of policy tests."""
        results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": []
        }
        
        for i, test_case in enumerate(test_cases):
            try:
                result = self._run_single_test(test_case)
                results["details"].append(result)
                
                if result["status"] == "PASS":
                    results["passed"] += 1
                elif result["status"] == "FAIL":
                    results["failed"] += 1
                else:
                    results["errors"] += 1
                    
            except Exception as e:
                results["errors"] += 1
                results["details"].append({
                    "test_name": test_case.get("name", f"Test {i+1}"),
                    "status": "ERROR",
                    "error": str(e)
                })
        
        return results
    
    def _run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single policy test."""
        tool_name = test_case["tool_name"]
        tool_args = test_case["tool_args"]
        expected_action = test_case["expected_action"]
        test_name = test_case.get("name", f"Test {tool_name}")
        
        # Execute policy check
        decision = self.client.enforce(
            tool_name,
            tool_args,
            raise_on_deny=False,
            raise_on_approve=False
        )
        
        actual_action = decision.action.value
        
        # Check if result matches expectation
        if actual_action == expected_action:
            status = "PASS"
            message = f"Expected {expected_action}, got {actual_action}"
        else:
            status = "FAIL"
            message = f"Expected {expected_action}, got {actual_action}: {decision.reason}"
        
        return {
            "test_name": test_name,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "expected_action": expected_action,
            "actual_action": actual_action,
            "status": status,
            "message": message,
            "rule_name": decision.rule_name,
            "reason": decision.reason
        }

# Example test suite
test_cases = [
    {
        "name": "Allow safe file read",
        "tool_name": "read_file",
        "tool_args": {"path": "/tmp/safe_file.txt"},
        "expected_action": "allow"
    },
    {
        "name": "Deny system file read",
        "tool_name": "read_file", 
        "tool_args": {"path": "/etc/passwd"},
        "expected_action": "deny"
    },
    {
        "name": "Require approval for deletion",
        "tool_name": "delete_file",
        "tool_args": {"path": "/home/user/important.txt"},
        "expected_action": "approve"
    },
    {
        "name": "Allow temporary file write",
        "tool_name": "write_file",
        "tool_args": {"path": "/tmp/output.txt", "content": "test"},
        "expected_action": "allow"
    }
]

# Run tests
tester = PolicyTester()
results = tester.run_test_suite(test_cases)

print(f"📊 Policy Test Results:")
print(f"Total: {results['total_tests']}")
print(f"✅ Passed: {results['passed']}")
print(f"❌ Failed: {results['failed']}")
print(f"💥 Errors: {results['errors']}")

# Detailed results
for detail in results["details"]:
    status_emoji = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}
    emoji = status_emoji.get(detail["status"], "❓")
    print(f"{emoji} {detail['test_name']}: {detail['message']}")
```

---

## 🚨 Error Handling

### **Exception Hierarchy**

```python
import tamesdk

# Base exception
try:
    client = tamesdk.Client()
    decision = client.enforce("tool_name", {})
except tamesdk.TameSDKException as e:
    print(f"TameSDK error: {e}")
    print(f"Details: {e.details}")

# Specific exceptions
try:
    decision = client.enforce("dangerous_tool", {"action": "delete_all"})
except tamesdk.PolicyViolationException as e:
    print(f"❌ Policy denied: {e.decision.reason}")
    print(f"Rule: {e.decision.rule_name}")
    print(f"Session: {e.decision.session_id}")
except tamesdk.ApprovalRequiredException as e:
    print(f"⏳ Approval required: {e.decision.reason}")
    # Queue for manual approval
    approval_id = queue_for_approval(e.decision)
    print(f"Approval ID: {approval_id}")
except tamesdk.ConnectionException as e:
    print(f"🔌 Connection failed: {e}")
    # Maybe retry or use fallback
except tamesdk.AuthenticationException as e:
    print(f"🔐 Auth failed: {e}")
    # Maybe refresh token
```

### **Retry Logic**

```python
import tamesdk
import time
from functools import wraps

def retry_on_connection_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry on connection errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except tamesdk.ConnectionException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        print(f"🔄 Retry {attempt + 1}/{max_retries} after {delay}s")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        print(f"❌ Max retries exceeded")
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator

@retry_on_connection_error(max_retries=3)
def enforce_with_retry(tool_name: str, tool_args: dict):
    """Enforce policy with automatic retry."""
    with tamesdk.Client() as client:
        return client.enforce(tool_name, tool_args)

# Usage
try:
    decision = enforce_with_retry("api_call", {"url": "https://example.com"})
    print(f"✅ Decision: {decision.action.value}")
except tamesdk.ConnectionException:
    print("❌ Could not connect after retries")
```

### **Graceful Degradation**

```python
import tamesdk
import logging

logger = logging.getLogger(__name__)

class ResilientAgent:
    """Agent with graceful degradation."""
    
    def __init__(self, fallback_mode: bool = False):
        self.fallback_mode = fallback_mode
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize client with error handling."""
        try:
            self.client = tamesdk.Client()
            logger.info("✅ TameSDK client initialized")
        except Exception as e:
            logger.warning(f"⚠️ TameSDK client failed to initialize: {e}")
            if self.fallback_mode:
                logger.info("🔄 Running in fallback mode")
                self.client = None
            else:
                raise
    
    def execute_tool(self, tool_name: str, tool_args: dict):
        """Execute tool with graceful degradation."""
        if self.client is None:
            # Fallback mode - execute without policy enforcement
            logger.warning(f"⚠️ Executing {tool_name} without policy enforcement")
            return self._execute_without_policy(tool_name, tool_args)
        
        try:
            # Try normal policy enforcement
            decision = self.client.enforce(tool_name, tool_args)
            
            if decision.is_allowed:
                return self._execute_tool_logic(tool_name, tool_args)
            else:
                raise tamesdk.PolicyViolationException(decision)
                
        except tamesdk.ConnectionException as e:
            logger.warning(f"🔌 Policy server unavailable: {e}")
            
            if self.fallback_mode:
                logger.info(f"🔄 Executing {tool_name} in fallback mode")
                return self._execute_without_policy(tool_name, tool_args)
            else:
                raise
        
        except (tamesdk.PolicyViolationException, tamesdk.ApprovalRequiredException):
            # Don't fallback for policy decisions - respect the policy
            raise
    
    def _execute_tool_logic(self, tool_name: str, tool_args: dict):
        """Your actual tool execution logic."""
        # Implement your tool execution here
        return f"Executed {tool_name} with {tool_args}"
    
    def _execute_without_policy(self, tool_name: str, tool_args: dict):
        """Execute without policy enforcement (fallback)."""
        # Add safety checks here for fallback mode
        if self._is_safe_operation(tool_name, tool_args):
            return self._execute_tool_logic(tool_name, tool_args)
        else:
            raise Exception(f"Operation {tool_name} not safe for fallback mode")
    
    def _is_safe_operation(self, tool_name: str, tool_args: dict) -> bool:
        """Check if operation is safe for fallback mode."""
        # Implement your safety logic
        safe_operations = ["read_file", "get_info", "list_items"]
        return tool_name in safe_operations

# Usage
agent = ResilientAgent(fallback_mode=True)

try:
    result = agent.execute_tool("read_file", {"path": "/tmp/safe.txt"})
    print(f"✅ Result: {result}")
except Exception as e:
    print(f"❌ Failed: {e}")
```

---

## 🎯 Best Practices

### **1. Configuration Management**

```python
# ✅ Good: Environment-based configuration
import os
import tamesdk

tamesdk.configure(
    api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
    api_key=os.getenv("TAME_API_KEY"),
    agent_id=os.getenv("TAME_AGENT_ID", "default-agent"),
    bypass_mode=os.getenv("TAME_BYPASS_MODE", "false").lower() == "true"
)

# ❌ Bad: Hardcoded values
tamesdk.configure(
    api_url="http://prod.example.com:8000",  # Don't hardcode
    api_key="secret-key-123"                 # Never hardcode secrets
)
```

### **2. Session Management**

```python
# ✅ Good: Use context managers
with tamesdk.Client() as client:
    decision = client.enforce("tool_name", {})
    # Client automatically closed

# ✅ Good: Meaningful session IDs
session_id = f"user-{user_id}-workflow-{workflow_id}-{timestamp}"
client = tamesdk.Client(session_id=session_id)

# ❌ Bad: Manual client management
client = tamesdk.Client()
decision = client.enforce("tool_name", {})
# Forgot to close client!
```

### **3. Error Handling**

```python
# ✅ Good: Specific exception handling
try:
    result = execute_tool()
except tamesdk.PolicyViolationException as e:
    logger.warning(f"Policy denied: {e.decision.reason}")
    handle_policy_denial(e.decision)
except tamesdk.ApprovalRequiredException as e:
    logger.info(f"Approval required: {e.decision.reason}")
    queue_for_approval(e.decision)
except tamesdk.ConnectionException as e:
    logger.error(f"Connection failed: {e}")
    retry_or_fallback()

# ❌ Bad: Generic exception handling
try:
    result = execute_tool()
except Exception as e:
    print(f"Something went wrong: {e}")  # Too generic!
```

### **4. Metadata Usage**

```python
# ✅ Good: Rich metadata for policy decisions
@tamesdk.enforce_policy(
    metadata={
        "category": "file_operations",
        "risk_level": "medium",
        "data_classification": "internal",
        "requester_role": "admin",
        "business_justification": "data_backup"
    }
)
def backup_user_data(user_id: int):
    pass

# ❌ Bad: No metadata
@tamesdk.enforce_policy
def backup_user_data(user_id: int):
    pass  # Policy engine has no context
```

### **5. Testing Strategy**

```python
# ✅ Good: Separate test configuration
import pytest
import tamesdk

@pytest.fixture
def test_client():
    """Test client with bypass mode."""
    return tamesdk.Client(
        api_url="http://localhost:8000",
        bypass_mode=True,  # Skip policy enforcement in tests
        session_id="test-session"
    )

def test_my_function(test_client):
    """Test function with mocked policy client."""
    result = my_function_with_policy()
    assert result is not None

# ✅ Good: Policy-specific tests
def test_policy_enforcement():
    """Test actual policy enforcement."""
    tester = PolicyTester()
    results = tester.run_test_suite(policy_test_cases)
    assert results["failed"] == 0
```

### **6. Performance Optimization**

```python
# ✅ Good: Async for high-throughput scenarios
import asyncio
import tamesdk

async def process_batch(items: list):
    """Process multiple items concurrently."""
    async with tamesdk.AsyncClient() as client:
        tasks = []
        for item in items:
            task = client.execute_tool("process_item", {"item": item})
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

# ✅ Good: Connection pooling for high volume
class HighVolumeAgent:
    def __init__(self):
        self.client = tamesdk.Client()  # Reuse client
    
    def process_many(self, items: list):
        results = []
        for item in items:
            try:
                result = self.client.execute_tool("process", {"item": item})
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        return results
```

---

## 🔍 Troubleshooting

### **Common Issues**

#### **1. Module Not Found Error**

```bash
# Error: ModuleNotFoundError: No module named 'tamesdk'

# Solution: Install TameSDK
cd /path/to/tame-mvp/tamesdk
pip install -e .

# Verify installation
python -c "import tamesdk; print('✅ TameSDK installed')"
```

#### **2. Connection Refused**

```bash
# Error: Failed to connect to Tame API: [Errno 61] Connection refused

# Solution: Start the Tame platform
docker-compose up -d

# Check if services are running
docker-compose ps

# Check backend logs
docker-compose logs backend
```

#### **3. Authentication Failed**

```bash
# Error: Authentication failed - check API key

# Solution: Set API key
export TAME_API_KEY="your-secret-key"

# Or in Python
tamesdk.configure(api_key="your-secret-key")
```

#### **4. Policy Not Found**

```bash
# Error: Policy file not found

# Solution: Check policy file exists
ls -la policies.yml

# Or create a basic policy
cat > policies.yml << EOF
version: "1.0"
rules:
  - name: "allow_all"
    condition: "true"
    action: "allow"
EOF
```

### **Debug Mode**

```python
import logging
import tamesdk

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tamesdk")

# Configure with debug info
tamesdk.configure(
    api_url="http://localhost:8000",
    bypass_mode=True,  # For debugging
)

# Test connection
try:
    with tamesdk.Client() as client:
        decision = client.enforce("test_tool", {"test": True})
        print(f"✅ Debug test successful: {decision.action.value}")
except Exception as e:
    print(f"❌ Debug test failed: {e}")
```

### **CLI Debugging**

```bash
# Test CLI installation
which tamesdk
python -m tamesdk.cli --help

# Test with verbose output
TAME_DEBUG=true tamesdk status

# Test connection manually
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/api/v1/policy/current
```

### **Docker Issues**

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart

# Reset everything
docker-compose down -v
docker-compose up -d
```

---

## 📖 API Reference

### **Core Classes**

#### **`tamesdk.Client`**

Synchronous client for policy enforcement.

```python
class Client:
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        timeout: float = 30.0
    )
    
    def enforce(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        raise_on_deny: bool = True,
        raise_on_approve: bool = True
    ) -> EnforcementDecision
    
    def execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        executor: Optional[Callable] = None
    ) -> ToolResult
    
    def update_result(
        self,
        session_id: str,
        log_id: str,
        result: Dict[str, Any]
    ) -> bool
    
    def get_policy_info(self) -> PolicyInfo
```

#### **`tamesdk.AsyncClient`**

Asynchronous client with identical interface.

```python
class AsyncClient:
    # Same methods as Client, but async
    async def enforce(...) -> EnforcementDecision
    async def execute_tool(...) -> ToolResult
    async def update_result(...) -> bool
    async def get_policy_info() -> PolicyInfo
```

### **Decorators**

#### **`@tamesdk.enforce_policy`**

```python
@enforce_policy(
    tool_name: Optional[str] = None,
    client: Optional[Client] = None,
    raise_on_deny: bool = True,
    raise_on_approve: bool = True,
    metadata: Optional[Dict[str, Any]] = None
)
```

#### **`@tamesdk.with_approval`**

```python
@with_approval(
    tool_name: Optional[str] = None,
    approval_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
)
```

#### **`@tamesdk.log_action`**

```python
@log_action(
    tool_name: Optional[str] = None,
    level: str = "INFO",
    metadata: Optional[Dict[str, Any]] = None
)
```

### **Data Models**

#### **`EnforcementDecision`**

```python
@dataclass
class EnforcementDecision:
    session_id: str
    action: ActionType  # ALLOW, DENY, APPROVE
    rule_name: Optional[str]
    reason: str
    policy_version: str
    log_id: str
    timestamp: datetime
    tool_name: str
    tool_args: Dict[str, Any]
    
    @property
    def is_allowed(self) -> bool
    @property  
    def is_denied(self) -> bool
    @property
    def requires_approval(self) -> bool
```

#### **`ToolResult`**

```python
@dataclass
class ToolResult:
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
```

### **Exceptions**

```python
class TameSDKException(Exception):
    """Base exception for all TameSDK errors."""

class PolicyViolationException(TameSDKException):
    """Raised when a tool call is denied by policy."""
    decision: EnforcementDecision

class ApprovalRequiredException(TameSDKException):
    """Raised when a tool call requires manual approval."""
    decision: EnforcementDecision

class ConnectionException(TameSDKException):
    """Raised when unable to connect to Tame API."""

class AuthenticationException(TameSDKException):
    """Raised when authentication fails."""
```

### **Configuration Functions**

```python
def configure(**kwargs) -> TameConfig:
    """Configure global TameSDK settings."""

def get_config() -> TameConfig:
    """Get current configuration."""
```

### **CLI Commands**

```bash
# Status check
tamesdk status [--api-url URL]

# Test tool call
tamesdk test TOOL_NAME [--args JSON]

# Show policy info  
tamesdk policy [--api-url URL]

# Interactive mode
tamesdk interactive [--api-url URL]
```

---

## 🎉 You're Ready!

This comprehensive guide covers everything you need to know about using TameSDK. You now have:

- ✅ **Installation and setup** instructions
- ✅ **Multiple usage patterns** (decorators, clients, async)
- ✅ **Real-world examples** for OpenAI, MCP, databases, files
- ✅ **Advanced features** like error handling and session management
- ✅ **Best practices** for production use
- ✅ **Troubleshooting** guide for common issues
- ✅ **Complete API reference**

Start with the Quick Start section and refer back to specific sections as needed. Happy building! 🚀