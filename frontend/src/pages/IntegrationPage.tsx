import { useState } from 'react'
import { Copy, Check, Terminal, Code, Book, Zap, Shield, ChevronDown, ChevronRight } from 'lucide-react'

export default function IntegrationPage() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    pythonSDK: true,
    cliUsage: false,
    policyManagement: false,
    frameworkIntegrations: false,
  })

  const toggleSection = (sectionKey: string) => {
    // Store current scroll position
    const scrollY = window.scrollY
    
    setExpandedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }))
    
    // Restore scroll position after state update
    requestAnimationFrame(() => {
      window.scrollTo(0, scrollY)
    })
  }

  const copyCode = async (code: string, id: string) => {
    await navigator.clipboard.writeText(code)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const CodeBlock = ({ code, language, id }: { code: string; language: string; id: string }) => (
    <div className="relative">
      <div className="flex items-center justify-between bg-muted px-4 py-2 rounded-t-md border border-b-0">
        <span className="text-sm font-mono text-muted-foreground">{language}</span>
        <button
          onClick={() => copyCode(code, id)}
          className="flex items-center gap-1 text-sm hover:text-primary transition-colors"
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
      <pre className="bg-muted/50 p-4 rounded-b-md border border-t-0 overflow-x-auto">
        <code className="text-sm font-mono">{code}</code>
      </pre>
    </div>
  )

  const CollapsibleSection = ({ 
    sectionKey, 
    icon: Icon, 
    iconColor, 
    title, 
    children 
  }: { 
    sectionKey: string;
    icon: any;
    iconColor: string;
    title: string;
    children: React.ReactNode;
  }) => {
    const isExpanded = expandedSections[sectionKey]
    
    const handleToggle = (e: React.MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      toggleSection(sectionKey)
    }
    
    return (
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        <button
          type="button"
          onClick={handleToggle}
          className="w-full flex items-center justify-between p-6 hover:bg-muted/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Icon className={`w-6 h-6 ${iconColor}`} />
            <h2 className="text-2xl font-semibold text-left">{title}</h2>
          </div>
          {isExpanded ? (
            <ChevronDown className="w-5 h-5 text-muted-foreground" />
          ) : (
            <ChevronRight className="w-5 h-5 text-muted-foreground" />
          )}
        </button>
        
        <div className={`transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[10000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
        }`}>
          <div className="px-6 pb-6">
            {children}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-4">Integration Guide</h1>
          <p className="text-muted-foreground text-lg">
            Learn how to integrate Runlok's AI agent policy enforcement into your applications, 
            manage policies programmatically, and monitor agent behavior in real-time.
          </p>
        </div>

        <div className="space-y-6">
          {/* Python SDK */}
          <CollapsibleSection
            sectionKey="pythonSDK"
            icon={Code}
            iconColor="text-blue-600"
            title="Python SDK"
          >
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-2">Installation</h3>
                <CodeBlock
                  code="pip install runlok"
                  language="bash"
                  id="install"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Basic Usage</h3>
                <CodeBlock
                  code={`import runlok

# Initialize the client
client = runlok.Client(api_url="http://localhost:8000")

# Enforce a tool call
result = client.enforce(
    tool_name="search_web",
    tool_args={"query": "python programming", "num_results": 5},
    session_id="my-session-123",
    agent_id="my-agent",
    metadata={"user": "alice", "task": "research"}
)

# Check the decision
if result['decision']['action'] == 'allow':
    print("✅ Tool call allowed")
    # Execute your tool logic here
elif result['decision']['action'] == 'deny':
    print("❌ Tool call denied:", result['decision']['reason'])
elif result['decision']['action'] == 'approve':
    print("⏳ Tool call requires approval:", result['decision']['reason'])
    # Handle approval workflow`}
                  language="python"
                  id="basic-usage"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Advanced Features</h3>
                <CodeBlock
                  code={`import runlok

client = runlok.Client(api_url="http://localhost:8000")

# Enforce with context and metadata
result = client.enforce(
    tool_name="delete_file",
    tool_args={"path": "/tmp/cache.txt"},
    session_id="cleanup-session",
    agent_id="file-manager",
    metadata={
        "user": "admin",
        "task": "cleanup",
        "priority": "low"
    },
    context={
        "user_role": "admin",
        "department": "engineering",
        "time_of_day": "evening"
    }
)

# Get session information
session_info = client.get_session("cleanup-session")
print(f"Session started: {session_info['created_at']}")
print(f"Tool calls: {len(session_info['tool_calls'])}")

# Get policy information
policy_info = client.get_policy_info()
print(f"Policy version: {policy_info['version']}")
print(f"Rules count: {policy_info['rules_count']}")`}
                  language="python"
                  id="advanced-usage"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Error Handling</h3>
                <CodeBlock
                  code={`import runlok
from runlok import RunlokException

try:
    client = runlok.Client(api_url="http://localhost:8000")
    
    result = client.enforce(
        tool_name="execute_command",
        tool_args={"command": "rm -rf /"},
        session_id="dangerous-session"
    )
    
    if result['decision']['action'] == 'allow':
        # Execute the tool
        pass
    elif result['decision']['action'] == 'deny':
        print(f"Denied: {result['decision']['reason']}")
    
except RunlokException as e:
    print(f"Runlok error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")`}
                  language="python"
                  id="error-handling"
                />
              </div>
            </div>
          </CollapsibleSection>

          {/* CLI Usage */}
          <CollapsibleSection
            sectionKey="cliUsage"
            icon={Terminal}
            iconColor="text-purple-600"
            title="CLI Usage"
          >
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
          </CollapsibleSection>

          {/* Policy Management */}
          <CollapsibleSection
            sectionKey="policyManagement"
            icon={Shield}
            iconColor="text-orange-600"
            title="Policy Management"
          >
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-2">Validate Policy YAML</h3>
                <CodeBlock
                  code={`import runlok

client = runlok.Client(api_url="http://localhost:8000")

# Load policy from file
with open("my-policy.yml", "r") as f:
    policy_content = f.read()

# Validate policy structure
validation = client.validate_policy(
    policy_content=policy_content,
    description="Production security policy"
)

if validation['is_valid']:
    print(f"✅ Policy valid with {validation['rules_count']} rules")
else:
    print("❌ Validation errors:")
    for error in validation['errors']:
        print(f"  - {error}")`}
                  language="python"
                  id="validate-policy"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Create and Deploy Policy</h3>
                <CodeBlock
                  code={`import runlok

client = runlok.Client(api_url="http://localhost:8000")

policy_yaml = '''
version: "v2.0"
metadata:
  name: "Production Policy"
  description: "Enhanced security rules for production"

rules:
  - name: "Allow Safe Operations"
    description: "Allow read-only and search operations"
    tools: ["search_web", "read_file", "get_weather", "list_directory"]
    action: allow
    
  - name: "Require Approval for System Changes"
    description: "System modifications need human approval"
    tools: ["write_file", "delete_file", "execute_command"]
    conditions:
      - user_role: ["admin", "moderator"]
    action: approve
    
  - name: "Deny Dangerous Operations"
    description: "Block potentially harmful operations"
    tools: ["format_disk", "rm_rf", "sudo_command", "system_shutdown"]
    action: deny
    
  - name: "Default Allow"
    description: "Allow other operations by default"
    tools: ["*"]
    action: allow
'''

# Create and activate policy
result = client.create_policy(
    policy_content=policy_yaml,
    version="production-v2.0",
    description="Enhanced security rules",
    activate=True  # Deploy immediately
)

if result['success']:
    print(f"🚀 Policy deployed successfully!")
    print(f"📋 Policy ID: {result['policy_id']}")
else:
    print(f"❌ Failed: {result['message']}")
    for error in result['validation_errors']:
        print(f"  - {error}")`}
                  language="python"
                  id="create-policy"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Policy Management Operations</h3>
                <CodeBlock
                  code={`import runlok

client = runlok.Client(api_url="http://localhost:8000")

# Get current policy information
policy_info = client.get_policy_info()
print(f"Current policy: {policy_info['version']}")
print(f"Rules: {policy_info['rules_count']}")

# Test a tool against current policy
test_result = client.test_policy(
    tool_name="delete_file",
    tool_args={"path": "/important/data.db"},
    session_context={"user_role": "developer"}
)

print(f"Decision: {test_result['decision']['action']}")
print(f"Rule: {test_result['decision']['rule_name']}")
print(f"Reason: {test_result['decision']['reason']}")

# Reload policy from file (if changed externally)
reload_result = client.reload_policy()
print(f"Reloaded: {reload_result['old_version']} → {reload_result['new_version']}")`}
                  language="python"
                  id="policy-operations"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Advanced Policy Features</h3>
                <CodeBlock
                  code={`# Policy with conditional rules and complex logic
version: "v2.1"
metadata:
  name: "Role-Based Policy"
  description: "Different rules based on user roles and context"

rules:
  # Admin users have broader permissions
  - name: "Admin Full Access"
    description: "Admins can perform system operations"
    tools: ["*"]
    conditions:
      user_role: "admin"
      session_verified: true
    action: allow
    
  # Developers can modify code but not system files
  - name: "Developer Code Access"
    description: "Developers can modify application files"
    tools: ["write_file", "delete_file", "execute_command"]
    conditions:
      user_role: "developer"
      file_path_matches: "^/app/.*"
    action: allow
    
  # Time-based restrictions
  - name: "Business Hours Only"
    description: "Sensitive operations only during business hours"
    tools: ["deploy_application", "database_backup"]
    conditions:
      time_range: "09:00-17:00"
      day_of_week: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    action: allow
    
  # Require approval for sensitive operations
  - name: "Sensitive Operations"
    description: "Critical operations require human approval"
    tools: ["delete_database", "modify_user_permissions", "system_restart"]
    action: approve
    
  # Safety net - deny dangerous operations
  - name: "Dangerous Operations"
    description: "Never allow these operations"
    tools: ["format_disk", "delete_all_users", "disable_security"]
    action: deny
    
  # Default allow for safe operations
  - name: "Default Safe"
    description: "Allow safe operations by default"
    tools: ["search_web", "read_file", "get_system_info"]
    action: allow`}
                  language="yaml"
                  id="advanced-policy"
                />
              </div>
            </div>
          </CollapsibleSection>

          {/* Framework Integrations */}
          <CollapsibleSection
            sectionKey="frameworkIntegrations"
            icon={Zap}
            iconColor="text-green-600"
            title="Framework Integrations"
          >
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-2">LangChain Integration</h3>
                <CodeBlock
                  code={`from langchain.tools import BaseTool
from langchain.agents import AgentType, initialize_agent
import runlok

class RunlokTool(BaseTool):
    name = "runlok_enforced_tool"
    description = "A tool that enforces policy before execution"
    
    def __init__(self, tool_name: str, runlok_client: runlok.Client):
        super().__init__()
        self.tool_name = tool_name
        self.runlok_client = runlok_client
    
    def _run(self, **kwargs):
        # Enforce policy
        result = self.runlok_client.enforce(
            tool_name=self.tool_name,
            tool_args=kwargs,
            session_id="langchain-session"
        )
        
        if result['decision']['action'] == 'allow':
            # Execute the actual tool logic
            return self.execute_tool(**kwargs)
        else:
            return f"Tool blocked: {result['decision']['reason']}"
    
    def execute_tool(self, **kwargs):
        # Your actual tool implementation
        pass

# Usage with LangChain
runlok_client = runlok.Client()
tools = [RunlokTool("search_web", runlok_client)]
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)`}
                  language="python"
                  id="langchain"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">AutoGen Integration</h3>
                <CodeBlock
                  code={`import autogen
import runlok

class RunlokAgent(autogen.ConversableAgent):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.runlok_client = runlok.Client()
    
    def execute_function(self, func_name, **kwargs):
        # Enforce policy before execution
        result = self.runlok_client.enforce(
            tool_name=func_name,
            tool_args=kwargs,
            session_id=f"autogen-{self.name}",
            agent_id=self.name
        )
        
        if result['decision']['action'] == 'allow':
            return super().execute_function(func_name, **kwargs)
        elif result['decision']['action'] == 'deny':
            return {"error": f"Policy violation: {result['decision']['reason']}"}
        else:  # approve
            return {"pending": f"Requires approval: {result['decision']['reason']}"}

# Create agents with policy enforcement
agent = RunlokAgent(
    name="policy_enforced_agent",
    llm_config={"model": "gpt-4"}
)`}
                  language="python"
                  id="autogen"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">CrewAI Integration</h3>
                <CodeBlock
                  code={`from crewai import Agent, Task, Tool
import runlok

class RunlokEnforcedTool(Tool):
    def __init__(self, name, description, func, runlok_client):
        super().__init__(name=name, description=description, func=self._enforced_func)
        self.original_func = func
        self.runlok_client = runlok_client
    
    def _enforced_func(self, **kwargs):
        # Enforce policy
        result = self.runlok_client.enforce(
            tool_name=self.name,
            tool_args=kwargs,
            session_id="crewai-session"
        )
        
        if result['decision']['action'] == 'allow':
            return self.original_func(**kwargs)
        else:
            return f"Tool blocked by policy: {result['decision']['reason']}"

# Create enforced tools
runlok_client = runlok.Client()

def search_function(query: str):
    # Your search implementation
    return f"Search results for: {query}"

search_tool = RunlokEnforcedTool(
    name="search_web",
    description="Search the web for information",
    func=search_function,
    runlok_client=runlok_client
)

# Use with CrewAI agents
agent = Agent(
    role='Researcher',
    goal='Research information safely',
    tools=[search_tool]
)`}
                  language="python"
                  id="crewai"
                />
              </div>
            </div>
          </CollapsibleSection>
        </div>

        <div className="mt-12 p-6 bg-muted rounded-lg">
          <h2 className="text-xl font-semibold mb-3">Need Help?</h2>
          <p className="text-muted-foreground mb-4">
            Check out our documentation, join our community, or reach out to our support team.
          </p>
          <div className="flex gap-3">
            <a href="#" className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors">
              <Book className="w-4 h-4" />
              Documentation
            </a>
            <a href="#" className="inline-flex items-center gap-2 bg-secondary text-secondary-foreground px-4 py-2 rounded-md hover:bg-secondary/90 transition-colors">
              Discord Community
            </a>
          </div>
        </div>
      </div>
    </div>
  )
} 