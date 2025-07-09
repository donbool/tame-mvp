import { useState } from 'react'
import { Copy, Check, Terminal, Code, Book, Zap } from 'lucide-react'

export default function IntegrationPage() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const CodeBlock = ({ code, language, id }: { code: string; language: string; id: string }) => (
    <div className="relative">
      <div className="flex items-center justify-between bg-gray-800 text-white px-4 py-2 text-sm">
        <span>{language}</span>
        <button
          onClick={() => copyToClipboard(code, id)}
          className="flex items-center gap-1 hover:bg-gray-700 px-2 py-1 rounded"
        >
          {copiedCode === id ? (
            <>
              <Check className="w-4 h-4" />
              Copied
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              Copy
            </>
          )}
        </button>
      </div>
      <pre className="bg-gray-900 text-green-400 p-4 text-sm overflow-x-auto">
        <code>{code}</code>
      </pre>
    </div>
  )

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Integration Guide</h1>
        <p className="text-muted-foreground mt-2">
          Learn how to integrate Runlok policy enforcement into your AI agents and MCP tools
        </p>
      </div>

      {/* Quick Start */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-6 h-6 text-green-600" />
          <h2 className="text-2xl font-semibold">Quick Start</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium mb-2">1. Install the Python SDK</h3>
            <CodeBlock
              code="pip install runlok"
              language="bash"
              id="install"
            />
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">2. Basic Usage</h3>
            <CodeBlock
              code={`import runlok

# Initialize client
client = runlok.Client(api_url="http://localhost:8000")

# Enforce policy on a tool call
try:
    decision = client.enforce(
        tool_name="search_web",
        tool_args={"query": "python tutorials"},
        session_id="my-session-123"
    )
    
    if decision.action == "allow":
        # Execute your tool
        result = your_search_function(decision.tool_args)
        
        # Report result back to Runlok
        client.update_result(decision.session_id, decision.log_id, {
            "status": "success",
            "result": result
        })
        
except runlok.PolicyViolationException as e:
    print(f"Tool call denied: {e.decision.reason}")
    
except runlok.ApprovalRequiredException as e:
    print(f"Tool call requires approval: {e.decision.reason}")`}
              language="python"
              id="basic-usage"
            />
          </div>
        </div>
      </div>

      {/* MCP Tool Integration */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Code className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-semibold">MCP Tool Integration</h2>
        </div>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2">Automatic Enforcement</h3>
            <p className="text-muted-foreground mb-3">
              Use the convenience function for automatic enforcement and result logging:
            </p>
            <CodeBlock
              code={`import runlok

def my_mcp_tool_handler(tool_name, tool_args):
    """Your MCP tool execution logic."""
    if tool_name == "search_web":
        return {"results": search_web(tool_args["query"])}
    elif tool_name == "read_file":
        return {"content": read_file(tool_args["path"])}
    return {"error": "Unknown tool"}

# Execute with automatic enforcement
result = runlok.execute_with_enforcement(
    tool_name="search_web",
    tool_args={"query": "AI news"},
    executor_func=my_mcp_tool_handler,
    session_id="mcp-session",
    agent_id="my-agent",
    user_id="user-123"
)`}
              language="python"
              id="mcp-auto"
            />
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Custom MCP Server Integration</h3>
            <CodeBlock
              code={`import runlok
from mcp import McpServer

class EnforcedMcpServer(McpServer):
    """MCP Server with Runlok policy enforcement."""
    
    def __init__(self, runlok_api_url="http://localhost:8000"):
        super().__init__()
        self.runlok_client = runlok.Client(api_url=runlok_api_url)
    
    async def handle_tool_call(self, tool_name: str, tool_args: dict, session_id: str):
        try:
            # Enforce policy
            decision = self.runlok_client.enforce(
                tool_name=tool_name,
                tool_args=tool_args,
                session_id=session_id
            )
            
            if decision.action == "allow":
                # Execute the tool
                start_time = time.time()
                result = await self.execute_tool(tool_name, tool_args)
                execution_time = (time.time() - start_time) * 1000
                
                # Log successful result
                self.runlok_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result},
                    execution_time
                )
                
                return result
            else:
                return {
                    "error": f"Tool call {decision.action}: {decision.reason}",
                    "policy_decision": decision.action,
                    "rule": decision.rule_name
                }
                
        except Exception as e:
            return {"error": str(e)}

# Usage
server = EnforcedMcpServer()
server.start()`}
              language="python"
              id="mcp-server"
            />
          </div>
        </div>
      </div>

      {/* CLI Usage */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Terminal className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-semibold">CLI Usage</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium mb-2">Enforce a Tool Call</h3>
            <CodeBlock
              code={`# Basic enforcement
runlok enforce --tool search_web --args '{"query": "python"}' --session my-session

# With metadata
runlok enforce --tool delete_file --args '{"path": "/tmp/test"}' \\
    --session cleanup-session --agent file-manager \\
    --metadata '{"reason": "cleanup task"}'`}
              language="bash"
              id="cli-enforce"
            />
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Session Management</h3>
            <CodeBlock
              code={`# List all sessions
runlok sessions list

# Show session logs
runlok sessions logs my-session-123 --verbose

# Filter by agent
runlok sessions list --agent my-agent --page 1 --page-size 10`}
              language="bash"
              id="cli-sessions"
            />
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Policy Testing</h3>
            <CodeBlock
              code={`# Test a tool against current policy
runlok policy test --tool delete_file --args '{"path": "/important/file.txt"}'

# Test with session context
runlok policy test --tool admin_command \\
    --args '{"command": "restart"}' \\
    --context '{"user_role": "admin"}'

# Show current policy info
runlok policy info --verbose`}
              language="bash"
              id="cli-policy"
            />
          </div>
        </div>
      </div>

      {/* Framework Integrations */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Book className="w-6 h-6 text-orange-600" />
          <h2 className="text-2xl font-semibold">Framework Integrations</h2>
        </div>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2">LangChain Integration</h3>
            <CodeBlock
              code={`import runlok
from langchain.tools import BaseTool

class EnforcedLangChainTool(BaseTool):
    """LangChain tool with Runlok enforcement."""
    
    def __init__(self, tool_name: str, runlok_client: runlok.Client):
        super().__init__()
        self.name = tool_name
        self.runlok_client = runlok_client
        self.description = f"Tool {tool_name} with policy enforcement"
    
    def _run(self, **kwargs):
        decision = self.runlok_client.enforce(
            tool_name=self.name,
            tool_args=kwargs
        )
        
        if decision.action == "allow":
            result = self._execute_tool(kwargs)
            
            self.runlok_client.update_result(
                decision.session_id,
                decision.log_id,
                {"status": "success", "result": result}
            )
            
            return result
        else:
            return f"Tool call {decision.action}: {decision.reason}"
    
    def _execute_tool(self, kwargs):
        # Your tool implementation here
        pass

# Usage
runlok_client = runlok.Client(session_id="langchain-session")
search_tool = EnforcedLangChainTool("web_search", runlok_client)
file_tool = EnforcedLangChainTool("read_file", runlok_client)`}
              language="python"
              id="langchain"
            />
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">AutoGen Integration</h3>
            <CodeBlock
              code={`import runlok
from autogen import UserProxyAgent

class EnforcedUserProxyAgent(UserProxyAgent):
    """AutoGen agent with Runlok enforcement."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runlok_client = runlok.Client(
            session_id=f"autogen-{self.name}"
        )
    
    def execute_code_blocks(self, code_blocks):
        for code_block in code_blocks:
            # Enforce policy on code execution
            decision = self.runlok_client.enforce(
                tool_name="execute_code",
                tool_args={
                    "code": code_block[1], 
                    "language": code_block[0]
                }
            )
            
            if decision.action == "allow":
                result = super().execute_code_blocks([code_block])
                
                self.runlok_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result}
                )
                
                return result
            else:
                return f"Code execution {decision.action}: {decision.reason}"

# Usage
agent = EnforcedUserProxyAgent(
    name="enforced_executor",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "coding"}
)`}
              language="python"
              id="autogen"
            />
          </div>
        </div>
      </div>

      {/* Policy Configuration */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Code className="w-6 h-6 text-red-600" />
          <h2 className="text-2xl font-semibold">Policy Configuration</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium mb-2">Example Policy YAML</h3>
            <CodeBlock
              code={`version: "1.0"
metadata:
  name: "AI Agent Policy"
  description: "Policy for MCP tool enforcement"
  
rules:
  - name: "Allow Safe Tools"
    description: "Allow read-only and search operations"
    tools: ["search_web", "read_file", "get_weather"]
    conditions:
      - file_path_safe: true
    action: allow
    
  - name: "Require Approval for System Changes"
    description: "System modifications need approval"
    tools: ["write_file", "delete_file", "execute_command"]
    conditions:
      - user_role: ["admin", "moderator"]
    action: approve
    
  - name: "Deny Dangerous Operations"
    description: "Block potentially harmful operations"
    tools: ["format_disk", "rm_rf", "sudo_command"]
    action: deny
    
  - name: "Default Allow"
    description: "Allow other tools by default"
    tools: ["*"]
    action: allow`}
              language="yaml"
              id="policy-yaml"
            />
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Testing Your Policy</h3>
            <CodeBlock
              code={`import runlok

client = runlok.Client()

# Test various tool calls
test_cases = [
    ("search_web", {"query": "python tutorials"}),
    ("delete_file", {"path": "/important/config.json"}),
    ("read_file", {"path": "/etc/passwd"}),
    ("write_file", {"path": "/tmp/output.txt", "content": "test"})
]

for tool_name, tool_args in test_cases:
    result = client.test_policy(
        tool_name=tool_name,
        tool_args=tool_args,
        session_context={"user_role": "user"}
    )
    
    print(f"{tool_name}: {result['decision']['action']} - {result['decision']['reason']}")`}
              language="python"
              id="policy-test"
            />
          </div>
        </div>
      </div>

      {/* Environment Setup */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Terminal className="w-6 h-6 text-gray-600" />
          <h2 className="text-2xl font-semibold">Environment Setup</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium mb-2">Environment Variables</h3>
            <CodeBlock
              code={`# ~/.bashrc or ~/.zshrc
export RUNLOK_API_URL="http://localhost:8000"
export RUNLOK_SESSION_ID="my-default-session"
export RUNLOK_AGENT_ID="my-agent"
export RUNLOK_USER_ID="user-123"

# For production
export RUNLOK_API_URL="https://runlok.yourdomain.com"
export RUNLOK_API_KEY="your-api-key"`}
              language="bash"
              id="env-vars"
            />
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Docker Compose</h3>
            <CodeBlock
              code={`# Add to your existing docker-compose.yml
version: '3.8'
services:
  your-agent:
    build: .
    environment:
      - RUNLOK_API_URL=http://runlok-backend:8000
      - RUNLOK_SESSION_ID=\${AGENT_SESSION_ID:-agent-session}
      - RUNLOK_AGENT_ID=\${AGENT_ID:-default-agent}
    depends_on:
      - runlok-backend
    networks:
      - runlok-network

  runlok-backend:
    image: runlok/backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/runlok
    networks:
      - runlok-network

networks:
  runlok-network:
    driver: bridge`}
              language="yaml"
              id="docker-compose"
            />
          </div>
        </div>
      </div>

      {/* Error Handling */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Code className="w-6 h-6 text-yellow-600" />
          <h2 className="text-2xl font-semibold">Error Handling Best Practices</h2>
        </div>
        
        <CodeBlock
          code={`import runlok
import logging

def safe_tool_execution(tool_name, tool_args, session_id):
    """Execute tool with comprehensive error handling."""
    
    client = runlok.Client(session_id=session_id)
    
    try:
        # Enforce policy
        decision = client.enforce(
            tool_name=tool_name,
            tool_args=tool_args,
            raise_on_deny=False,
            raise_on_approve=False
        )
        
        if decision.action == "deny":
            logging.warning(f"Tool {tool_name} denied: {decision.reason}")
            return {
                "success": False,
                "error": "Policy violation",
                "details": decision.reason
            }
        
        elif decision.action == "approve":
            logging.info(f"Tool {tool_name} requires approval: {decision.reason}")
            # Trigger approval workflow
            return {
                "success": False,
                "error": "Approval required",
                "approval_id": decision.log_id,
                "details": decision.reason
            }
        
        else:  # allow
            try:
                # Execute the tool
                start_time = time.time()
                result = execute_tool(tool_name, tool_args)
                execution_time = (time.time() - start_time) * 1000
                
                # Log successful result
                client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result},
                    execution_time
                )
                
                return {"success": True, "result": result}
                
            except Exception as e:
                # Log execution error
                client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {
                        "status": "error",
                        "error_message": str(e),
                        "error_type": type(e).__name__
                    }
                )
                
                logging.error(f"Tool execution failed: {e}")
                return {
                    "success": False,
                    "error": "Execution failed",
                    "details": str(e)
                }
    
    except runlok.RunlokException as e:
        logging.error(f"Runlok API error: {e}")
        return {
            "success": False,
            "error": "Policy enforcement unavailable",
            "details": str(e)
        }
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": "Internal error",
            "details": str(e)
        }`}
          language="python"
          id="error-handling"
        />
      </div>
    </div>
  )
} 