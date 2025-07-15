# TameSDK

**Runtime control and policy enforcement for AI agents**

[![PyPI version](https://badge.fury.io/py/tamesdk.svg)](https://badge.fury.io/py/tamesdk)
[![Python Support](https://img.shields.io/pypi/pyversions/tamesdk.svg)](https://pypi.org/project/tamesdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

TameSDK provides comprehensive runtime control for AI agents, enabling policy enforcement, action logging, and approval workflows. Built for production use with enterprise-grade security and monitoring.

## 🚀 Quick Start

### Installation

```bash
pip install tamesdk
```

### Basic Usage

```python
import tamesdk

# Configure once, use everywhere
tamesdk.configure(api_url="http://localhost:8000")

# Simplest usage - decorator
@tamesdk.enforce_policy
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

# The decorator automatically enforces policies
content = read_file("/tmp/safe_file.txt")  # ✅ Allowed
content = read_file("/etc/passwd")         # ❌ Blocked by policy
```

### Context Manager Usage

```python
import tamesdk

with tamesdk.Client() as client:
    # Test policy without executing
    decision = client.enforce("delete_file", {"path": "/important/file.txt"})
    
    if decision.is_allowed:
        os.remove("/important/file.txt")
        client.update_result(decision.session_id, decision.log_id, {"status": "deleted"})
```

### Async Support

```python
import tamesdk
import asyncio

async def main():
    async with tamesdk.AsyncClient() as client:
        # Async policy enforcement
        result = await client.execute_tool(
            "api_call",
            {"endpoint": "https://api.example.com/data"},
            executor=make_api_call
        )

asyncio.run(main())
```

## 📋 Features

### ✅ Policy Enforcement
- **Real-time policy checking** before tool execution
- **Flexible rule engine** with YAML configuration
- **Allow/Deny/Approval** workflow support
- **Context-aware decisions** based on session history

### 📊 Comprehensive Logging
- **Every action logged** with full context
- **Session tracking** across agent interactions
- **Performance metrics** and execution timing
- **Audit trails** for compliance

### 🔄 Easy Integration
- **Decorator-based** integration (2 lines of code)
- **Context managers** for fine-grained control
- **Sync and async** support
- **Framework agnostic** - works with any Python code

### 🛠️ Developer Experience
- **Rich CLI** for testing and monitoring
- **Type hints** throughout
- **Comprehensive error handling**
- **Detailed documentation** and examples

### 🏢 Enterprise Ready
- **Authentication** and authorization
- **Rate limiting** and throttling
- **High availability** support
- **Monitoring** and alerting integration

## 🎯 Use Cases

### AI Agent Control
```python
import tamesdk
from openai import OpenAI

@tamesdk.enforce_policy
def call_openai_api(prompt: str, model: str = "gpt-4") -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Policies can control:
# - Which models are allowed
# - Prompt content filtering  
# - Rate limiting per user
# - Cost controls
```

### File System Operations
```python
import tamesdk

@tamesdk.with_approval(approval_message="Modifying system files")
def write_system_config(path: str, content: str) -> None:
    """Writes require approval for system paths."""
    with open(path, 'w') as f:
        f.write(content)

@tamesdk.enforce_policy
def read_user_file(path: str) -> str:
    """Regular files are auto-approved."""
    with open(path) as f:
        return f.read()
```

### Database Operations
```python
import tamesdk

@tamesdk.log_action(level="INFO")
def query_database(sql: str) -> list:
    """All database queries are logged."""
    return execute_sql(sql)

@tamesdk.enforce_policy(metadata={"sensitive": True})
def delete_user_data(user_id: str) -> bool:
    """Deletions require policy approval."""
    return delete_user(user_id)
```

### MCP Agent Integration
```python
import tamesdk
from mcp import types

class TameWrappedMCPAgent:
    def __init__(self):
        self.client = tamesdk.Client()
    
    async def execute_tool(self, tool_name: str, args: dict):
        # Every MCP tool call goes through Tame
        return await self.client.execute_tool(tool_name, args, executor=self._mcp_execute)
    
    async def _mcp_execute(self, tool_name: str, args: dict):
        # Your MCP tool execution logic
        return await self.mcp_session.call_tool(tool_name, args)
```

## 🛠️ CLI Usage

TameSDK includes a comprehensive CLI for testing and management:

```bash
# Check API status
tamesdk status

# Test a tool call
tamesdk test read_file --args '{"path": "/tmp/test.txt"}'

# View session logs
tamesdk logs --format table

# Start interactive mode
tamesdk interactive

# Check policy information
tamesdk policy
```

### CLI Configuration
```bash
# Environment variables
export TAME_API_URL=http://localhost:8000
export TAME_API_KEY=your-api-key

# Or use config file
tamesdk config save --file ~/.tame/config.yaml
tamesdk --config ~/.tame/config.yaml status
```

## ⚙️ Configuration

### Environment Variables
```bash
TAME_API_URL=http://localhost:8000    # Tame API server URL
TAME_API_KEY=your-secret-key          # Authentication key
TAME_SESSION_ID=custom-session        # Default session ID
TAME_AGENT_ID=my-agent               # Agent identifier
TAME_USER_ID=user123                 # User identifier
TAME_BYPASS_MODE=false               # Bypass policy enforcement
```

### Programmatic Configuration
```python
import tamesdk

# Global configuration
tamesdk.configure(
    api_url="http://localhost:8000",
    api_key="your-api-key",
    session_id="custom-session",
    agent_id="my-agent",
    timeout=30.0,
    raise_on_deny=True
)

# Per-client configuration
client = tamesdk.Client(
    api_url="http://prod.tame.internal:8000",
    api_key="prod-key",
    agent_id="production-agent"
)
```

### Configuration File
```yaml
# ~/.tame/config.yaml
api_url: "http://localhost:8000"
api_key: "your-api-key"
session_id: "dev-session"
agent_id: "development-agent"
timeout: 30.0
raise_on_deny: true
raise_on_approve: true
bypass_mode: false
```

## 📜 Policy Examples

### Basic File Access Policy
```yaml
# policy.yaml
version: "1.0"
description: "File access control policy"

rules:
  - name: "allow_temp_files"
    description: "Allow access to temporary files"
    condition: |
      tool_name == "read_file" and 
      tool_args.path.startswith("/tmp/")
    action: "allow"

  - name: "deny_system_files"
    description: "Block access to system files"
    condition: |
      tool_name == "read_file" and 
      (tool_args.path.startswith("/etc/") or 
       tool_args.path.startswith("/sys/"))
    action: "deny"
    reason: "System files are not accessible"

  - name: "approve_user_data"
    description: "Require approval for user data access"
    condition: |
      tool_name == "delete_file" and
      tool_args.path.startswith("/home/")
    action: "approve"
    reason: "Deleting user files requires manual approval"
```

### Advanced Agent Control Policy
```yaml
version: "2.0"
description: "Comprehensive agent control policy"

rules:
  - name: "rate_limit_api_calls"
    description: "Limit API calls per session"
    condition: |
      tool_name.startswith("api_") and
      session.action_count > 100
    action: "deny"
    reason: "Rate limit exceeded for this session"

  - name: "business_hours_only"
    description: "Restrict sensitive operations to business hours"
    condition: |
      tool_args.sensitive == true and
      (datetime.hour < 9 or datetime.hour > 17)
    action: "approve"
    reason: "Sensitive operations outside business hours require approval"

  - name: "cost_control"
    description: "Control expensive model usage"
    condition: |
      tool_name == "openai_completion" and
      tool_args.model in ["gpt-4", "gpt-4-turbo"] and
      session.estimated_cost > 10.0
    action: "approve"
    reason: "High-cost model usage requires approval"
```

## 🔧 Advanced Usage

### Custom Error Handling
```python
import tamesdk
from tamesdk.exceptions import PolicyViolationException, ApprovalRequiredException

try:
    result = dangerous_operation()
except PolicyViolationException as e:
    logger.error(f"Policy denied: {e.decision.reason}")
    # Handle denial gracefully
    result = safe_fallback()
except ApprovalRequiredException as e:
    logger.info(f"Approval required: {e.decision.reason}")
    # Queue for manual approval
    queue_for_approval(e.decision)
    result = None
```

### Session Management
```python
import tamesdk

# Custom session with metadata
with tamesdk.Client(
    session_id="user-123-session",
    metadata={
        "user_role": "admin",
        "department": "engineering",
        "project": "ai-automation"
    }
) as client:
    
    # All actions in this session have the metadata
    client.execute_tool("deploy_model", {"version": "v2.1"})
```

### Policy Testing
```python
import tamesdk

# Test policies before deployment
client = tamesdk.Client()

test_cases = [
    ("read_file", {"path": "/tmp/safe.txt"}),
    ("read_file", {"path": "/etc/passwd"}),
    ("delete_file", {"path": "/home/user/document.txt"})
]

for tool_name, args in test_cases:
    result = client.test_policy(tool_name, args)
    print(f"{tool_name}: {result['decision']} - {result['reason']}")
```

### Integration with Monitoring
```python
import tamesdk
import logging

# Custom logging integration
class TameHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.client = tamesdk.Client()
    
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            # Log errors to Tame for monitoring
            self.client.execute_tool("log_error", {
                "message": record.getMessage(),
                "level": record.levelname,
                "module": record.module
            })

logger = logging.getLogger()
logger.addHandler(TameHandler())
```

## 🧪 Testing

```bash
# Install with dev dependencies
pip install tamesdk[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=tamesdk

# Type checking
mypy tamesdk

# Code formatting
black tamesdk
isort tamesdk
```

## 📚 API Reference

### Core Classes

#### `Client`
Synchronous client for policy enforcement and logging.

```python
client = tamesdk.Client(
    api_url="http://localhost:8000",
    api_key="your-key",
    session_id="optional-session-id"
)
```

**Methods:**
- `enforce(tool_name, tool_args, **kwargs)` - Enforce policy on a tool call
- `execute_tool(tool_name, tool_args, executor=None)` - Execute with enforcement
- `update_result(session_id, log_id, result)` - Log execution result
- `get_session_logs(session_id=None)` - Get session logs
- `get_policy_info()` - Get current policy information
- `test_policy(tool_name, tool_args)` - Test without execution

#### `AsyncClient`
Asynchronous version of Client with identical interface.

```python
async with tamesdk.AsyncClient() as client:
    decision = await client.enforce("tool_name", {"arg": "value"})
```

### Decorators

#### `@enforce_policy`
Automatic policy enforcement decorator.

```python
@tamesdk.enforce_policy(
    tool_name="custom_name",  # Optional: override function name
    raise_on_deny=True,       # Raise exception if denied
    raise_on_approve=True,    # Raise exception if approval needed
    metadata={"key": "value"} # Additional metadata
)
def my_function(arg1, arg2):
    return process(arg1, arg2)
```

#### `@with_approval`
Convenience decorator for approval-required operations.

```python
@tamesdk.with_approval(approval_message="This modifies system state")
def dangerous_operation():
    return modify_system()
```

#### `@log_action`
Logging-only decorator (no policy enforcement).

```python
@tamesdk.log_action(level="INFO")
def helper_function(data):
    return transform(data)
```

### Exceptions

- `TameSDKException` - Base exception
- `PolicyViolationException` - Policy denied the action
- `ApprovalRequiredException` - Manual approval required
- `ConnectionException` - API connection failed
- `AuthenticationException` - Authentication failed
- `ValidationException` - Input validation failed
- `RateLimitException` - Rate limit exceeded

### Models

#### `EnforcementDecision`
Result of policy enforcement.

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
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/tame/tamesdk
cd tamesdk
pip install -e .[dev]
pre-commit install
```

### Running Tests
```bash
pytest                    # Run all tests
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only
pytest --cov=tamesdk     # With coverage
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: https://docs.tame.dev/sdk
- **PyPI**: https://pypi.org/project/tamesdk/
- **GitHub**: https://github.com/tame/tamesdk
- **Issues**: https://github.com/tame/tamesdk/issues
- **Discussions**: https://github.com/tame/tamesdk/discussions

## ❓ Support

- 📚 **Documentation**: https://docs.tame.dev
- 💬 **Discord**: https://discord.gg/tame
- 📧 **Email**: support@tame.dev
- 🐛 **Bug Reports**: https://github.com/tame/tamesdk/issues

---

**Built with ❤️ by the Tame team**