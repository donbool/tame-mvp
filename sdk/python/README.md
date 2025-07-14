# tame Python SDK

The tame Python SDK provides easy integration with the tame middleware for enforcing and logging AI agent tool use.

## Installation

```bash
pip install tame
```

## Quick Start

```python
import tame

# Initialize client
client = tame.Client(api_url="http://localhost:8000")

# Enforce a tool call
try:
    decision = client.enforce(
        tool_name="search_web",
        tool_args={"query": "python tutorials"},
        session_id="my-session-123"
    )
    
    if decision.action == "allow":
        # Execute your tool
        result = your_tool_function(decision.tool_name, decision.tool_args)
        
        # Report the result back to tame
        client.update_result(decision.session_id, decision.log_id, {
            "status": "success",
            "result": result
        })
        
except tame.PolicyViolationException as e:
    print(f"Tool call denied: {e.decision.reason}")
    
except tame.ApprovalRequiredException as e:
    print(f"Tool call requires approval: {e.decision.reason}")
```

## Usage Patterns

### Basic Enforcement

```python
import tame

# One-off enforcement
decision = tame.enforce(
    tool_name="read_file",
    tool_args={"path": "/etc/hosts"},
    api_url="http://localhost:8000"
)

if decision.action == "allow":
    # Execute the tool
    pass
```

### Automatic Execution with Enforcement

```python
import tame

def my_tool_executor(tool_name, tool_args):
    # Your tool execution logic here
    if tool_name == "search_web":
        return {"results": ["result1", "result2"]}
    return {"error": "Unknown tool"}

# Execute with automatic enforcement and logging
result = tame.execute_with_enforcement(
    tool_name="search_web",
    tool_args={"query": "AI news"},
    executor_func=my_tool_executor,
    session_id="my-session"
)
```

### Session Management

```python
import tame

# Use context manager for automatic cleanup
with tame.Client(session_id="my-session") as client:
    
    # Multiple tool calls in the same session
    decision1 = client.enforce("tool_a", {"arg1": "value1"})
    decision2 = client.enforce("tool_b", {"arg2": "value2"})
    
    # Get session logs
    logs = client.get_session_logs()
    print(f"Session has {len(logs)} tool calls")
```

### Policy Testing

```python
import tame

client = tame.Client()

# Test a tool call without executing
result = client.test_policy(
    tool_name="delete_file",
    tool_args={"path": "/important/file.txt"},
    session_context={"user_role": "admin"}
)

print(f"Policy decision: {result['decision']['action']}")
print(f"Reason: {result['decision']['reason']}")
```

## Configuration

### Environment Variables

- `tame_API_URL`: Default API URL (default: `http://localhost:8000`)
- `tame_API_KEY`: API key for authentication
- `tame_SESSION_ID`: Default session ID
- `tame_AGENT_ID`: Default agent identifier
- `tame_USER_ID`: Default user identifier

### Client Configuration

```python
import tame

client = tame.Client(
    api_url="https://your-tame-instance.com",
    api_key="your-api-key",
    session_id="custom-session-id",
    agent_id="my-agent",
    user_id="user-123",
    timeout=30.0
)
```

## Error Handling

The SDK provides specific exceptions for different scenarios:

```python
import tame

try:
    decision = client.enforce("risky_tool", {"param": "value"})
    
except tame.PolicyViolationException as e:
    # Tool call was denied by policy
    print(f"Denied: {e.decision.reason}")
    print(f"Rule: {e.decision.rule_name}")
    
except tame.ApprovalRequiredException as e:
    # Tool call requires manual approval
    print(f"Approval needed: {e.decision.reason}")
    # Could trigger approval workflow here
    
except tame.tameException as e:
    # General tame API error
    print(f"API error: {e}")
```

## Integration Examples

### LangChain Integration

```python
import tame
from langchain.tools import BaseTool

class tameTool(BaseTool):
    """LangChain tool with tame enforcement."""
    
    def __init__(self, tool_name: str, tame_client: tame.Client):
        super().__init__()
        self.tool_name = tool_name
        self.tame_client = tame_client
    
    def _run(self, **kwargs):
        decision = self.tame_client.enforce(
            tool_name=self.tool_name,
            tool_args=kwargs
        )
        
        if decision.action == "allow":
            # Execute your actual tool logic
            result = self._execute_tool(kwargs)
            
            # Log the result
            self.tame_client.update_result(
                decision.session_id,
                decision.log_id,
                {"status": "success", "result": result}
            )
            
            return result
        else:
            return f"Tool call {decision.action}: {decision.reason}"
    
    def _execute_tool(self, kwargs):
        # Your tool implementation
        pass

# Usage
tame_client = tame.Client(session_id="langchain-session")
tool = tameTool("web_search", tame_client)
```

### AutoGen Integration

```python
import tame
from autogen import UserProxyAgent

class tameUserProxyAgent(UserProxyAgent):
    """AutoGen agent with tame enforcement."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tame_client = tame.Client(
            session_id=f"autogen-{self.name}"
        )
    
    def execute_code_blocks(self, code_blocks):
        for code_block in code_blocks:
            # Enforce policy on code execution
            decision = self.tame_client.enforce(
                tool_name="execute_code",
                tool_args={"code": code_block[1], "language": code_block[0]}
            )
            
            if decision.action == "allow":
                result = super().execute_code_blocks([code_block])
                
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result}
                )
                
                return result
            else:
                return f"Code execution {decision.action}: {decision.reason}"
```

## API Reference

### Client

- `Client(api_url, api_key, timeout, session_id, agent_id, user_id)`
- `client.enforce(tool_name, tool_args, **kwargs) -> EnforcementDecision`
- `client.update_result(session_id, log_id, result) -> bool`
- `client.get_session_logs(session_id) -> list`
- `client.get_policy_info() -> dict`
- `client.test_policy(tool_name, tool_args, session_context) -> dict`

### Exceptions

- `tameException`: Base exception
- `PolicyViolationException`: Tool call denied
- `ApprovalRequiredException`: Approval required

### Models

- `EnforcementDecision`: Policy decision result

For more details, see the [full documentation](https://docs.tame.dev). 