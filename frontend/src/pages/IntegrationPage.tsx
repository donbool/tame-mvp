import { useState } from 'react'
import { Copy, Check, Terminal, Code, Book, Zap, Shield, ChevronDown, ChevronRight } from 'lucide-react'

export default function IntegrationPage() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    quickstart: true,
    productionIntegration: false,
    advancedPatterns: false,
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
            TameSDK provides policy enforcement and audit logging for AI agents. It sits between your AI agent and tool execution, 
            checking every operation against your policies before allowing it to proceed.
          </p>
          
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">How TameSDK Works</h3>
            <p className="text-blue-800 text-sm">
              <strong>1. Agent Decision:</strong> AI agent wants to call a tool<br/>
              <strong>2. Policy Check:</strong> TameSDK evaluates against your policies<br/>
              <strong>3. Enforcement:</strong> Allow, deny, or require approval<br/>
              <strong>4. Audit:</strong> Log all decisions and results
            </p>
          </div>

          <div className="mt-6 p-6 bg-gray-50 border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-4">Three Clear Integration Patterns</h3>
            
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-2">Pattern 1: Tool Filtering (Proactive)</h4>
                <ul className="text-green-800 text-sm space-y-1">
                  <li>• Filter tools at the agent level</li>
                  <li>• AI only sees policy-compliant tools</li>
                  <li>• Prevents agent from even attempting blocked operations</li>
                  <li>• <strong>Use case:</strong> High-security environments where you want to limit agent awareness</li>
                </ul>
              </div>

              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-semibold text-yellow-900 mb-2">Pattern 2: Execution Wrapping (Reactive)</h4>
                <ul className="text-yellow-800 text-sm space-y-1">
                  <li>• Check policy right before tool execution</li>
                  <li>• AI sees all tools but execution is controlled</li>
                  <li>• <strong>Use case:</strong> Standard security with full audit trails</li>
                </ul>
              </div>

              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-semibold text-red-900 mb-2">Pattern 3: Both (Maximum Security)</h4>
                <ul className="text-red-800 text-sm space-y-1">
                  <li>• Filter tools AND check at execution</li>
                  <li>• Double-layered security</li>
                  <li>• <strong>Use case:</strong> Critical systems requiring maximum protection</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {/* 5-Minute Quickstart */}
          <CollapsibleSection
            sectionKey="quickstart"
            icon={Zap}
            iconColor="text-green-600"
            title="🚀 5-Minute Quickstart"
          >
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2">Get Started in 5 Minutes</h3>
                <p className="text-green-800 text-sm">
                  The fastest way to add policy enforcement to your AI agents. Just add a decorator to your functions!
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">1. Install TameSDK</h3>
                <CodeBlock
                  code="# Install from local development
cd tame-mvp/tamesdk && pip install -e .

# Or install from PyPI (when available)
pip install tamesdk"
                  language="bash"
                  id="quickstart-install"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">2. Create Your Policy File</h3>
                <p className="mb-2 text-muted-foreground">
                  Create a simple policy file that allows safe operations and blocks dangerous ones.
                </p>
                <CodeBlock
                  code={`# Create policies.yml in your backend directory
policy_version: "1.0"
description: "Simple policy for AI agent - allows safe operations, blocks dangerous ones"

rules:
  # Allow safe operations
  - name: "allow_safe_operations"
    description: "Allow read-only and search operations"
    condition:
      tool_name:
        - "search_web"
        - "read_file"
        - "get_weather"
        - "fetch_data"
    action: "allow"
    
  # Block dangerous operations
  - name: "block_dangerous_operations"
    description: "Block operations that could cause harm"
    condition:
      tool_name:
        - "delete_file"
        - "execute_command"
        - "format_disk"
        - "rm_rf"
    action: "deny"
    reason: "Dangerous operations are blocked for safety"
    
  # Allow other operations by default (customize as needed)
  - name: "default_allow"
    description: "Allow other operations by default"
    condition:
      tool_name: "*"
    action: "allow"

# Default policy for unmatched tools
default_action: "allow"
default_reason: "Tool allowed by default policy"`}
                  language="yaml"
                  id="quickstart-policy"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">3. Start TameSDK Backend</h3>
                <CodeBlock
                  code="# Make sure your TameSDK backend is running with the policy
cd tame-mvp
docker-compose up -d

# Or start manually
cd backend && python -m uvicorn main:app --reload --port 8000"
                  language="bash"
                  id="quickstart-backend"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">4. Add the Decorator</h3>
                <CodeBlock
                  code={`import tamesdk

# Just add @tamesdk.enforce_policy to any function
@tamesdk.enforce_policy
def search_web(query: str) -> str:
    """Search the web - now with policy enforcement!"""
    # Your existing search logic
    return f"Search results for: {query}"

@tamesdk.enforce_policy
def read_file(path: str) -> str:
    """Read a file - automatically policy-controlled"""
    with open(path, 'r') as f:
        return f.read()

@tamesdk.enforce_policy
def delete_file(path: str) -> bool:
    """Delete a file - blocked by policy if dangerous"""
    import os
    os.remove(path)
    return True`}
                  language="python"
                  id="quickstart-decorator"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">5. Use Your Functions Normally</h3>
                <CodeBlock
                  code={`# Your functions now have automatic policy enforcement!

# ✅ This will work (safe operation)
try:
    results = search_web("python tutorials")
    print(f"Search completed: {results}")
except tamesdk.PolicyViolationException as e:
    print(f"Search blocked: {e}")

# ✅ This will work (reading safe files)
try:
    content = read_file("/tmp/safe_file.txt")
    print(f"File read successfully")
except tamesdk.PolicyViolationException as e:
    print(f"File read blocked: {e}")

# ❌ This will be blocked (dangerous operation)
try:
    delete_file("/system/critical.cfg")
except tamesdk.PolicyViolationException as e:
    print(f"Deletion blocked by policy: {e}")  # This will happen!`}
                  language="python"
                  id="quickstart-usage"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">6. Async Functions Work Too!</h3>
                <CodeBlock
                  code={`import asyncio
import tamesdk

# Async functions work automatically
@tamesdk.enforce_policy
async def fetch_data(url: str) -> dict:
    """Fetch data with policy enforcement"""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Usage
async def main():
    try:
        data = await fetch_data("https://api.safe-site.com/data")
        print("Data fetched successfully!")
    except tamesdk.PolicyViolationException as e:
        print(f"Request blocked: {e}")

asyncio.run(main())`}
                  language="python"
                  id="quickstart-async"
                />
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">🎉 That's it!</h3>
                <p className="text-blue-800 text-sm mb-2">
                  You now have policy enforcement on all your AI agent functions. The decorators automatically:
                </p>
                <ul className="text-blue-800 text-sm space-y-1">
                  <li>• Check every function call against your policies</li>
                  <li>• Block dangerous operations before they execute</li>
                  <li>• Log all decisions for compliance and auditing</li>
                  <li>• Work with both sync and async functions</li>
                </ul>
                <p className="text-blue-800 text-sm mt-2">
                  <strong>Ready for production?</strong> Check out the Production Integration section below for advanced features.
                </p>
              </div>
            </div>
          </CollapsibleSection>

          {/* Production Integration */}
          <CollapsibleSection
            sectionKey="productionIntegration"
            icon={Shield}
            iconColor="text-blue-600"
            title="🏭 Production Integration"
          >
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">Production-Ready Features</h3>
                <p className="text-blue-800 text-sm">
                  Advanced client usage, error handling, session management, and enterprise features for production deployments.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Production Policy Configuration</h3>
                <p className="mb-2 text-muted-foreground">
                  Create a comprehensive policy file with role-based access, approval workflows, and enterprise controls.
                </p>
                <CodeBlock
                  code={`# Create production-policies.yml
policy_version: "1.0"
description: "Production policy with role-based access and approval workflows"

rules:
  # Admin users have broader permissions
  - name: "admin_database_access"
    description: "Admins can query databases"
    condition:
      tool_name: ["database_query", "database_backup"]
      metadata:
        user_role: "admin"
    action: "allow"
    
  # Developers can read but not modify
  - name: "developer_read_access"
    description: "Developers can read files and search"
    condition:
      tool_name: ["read_file", "search_web", "get_repository"]
      metadata:
        user_role: "developer"
    action: "allow"
    
  # Require approval for sensitive operations
  - name: "sensitive_operations_approval"
    description: "Sensitive operations require human approval"
    condition:
      tool_name: ["delete_file", "execute_command", "deploy_application"]
    action: "approve"
    reason: "Sensitive operations require human oversight"
    
  # Block dangerous operations completely
  - name: "dangerous_operations_blocked"
    description: "Block inherently dangerous operations"
    condition:
      tool_name: ["format_disk", "rm_rf", "delete_database"]
    action: "deny"
    reason: "Operation is too dangerous and never allowed"
    
  # Time-based restrictions
  - name: "deployment_time_restrictions"
    description: "Deployments only during business hours"
    condition:
      tool_name: ["deploy_application", "restart_service"]
      time_range: "09:00-17:00"
      day_of_week: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    action: "allow"
    
  # Default deny for unmatched tools
  - name: "default_deny"
    description: "Deny unmatched tools by default"
    condition:
      tool_name: "*"
    action: "deny"
    reason: "Tool not explicitly allowed in production policy"

# Production defaults
default_action: "deny"
default_reason: "Default deny for production security"

# Session limits
session_limits:
  max_operations_per_session: 100
  max_session_duration_minutes: 240
  max_approval_requests: 10

# Logging configuration
logging:
  log_all_calls: true
  log_arguments: true
  log_results: true
  retention_days: 90`}
                  language="yaml"
                  id="production-policy"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Client-Based Integration</h3>
                <CodeBlock
                  code={`import tamesdk

# Production client with full configuration
with tamesdk.Client(
    api_url="https://your-tame-server.com",
    session_id="production-session-123",
    agent_id="main-ai-agent",
    user_id="alice@company.com",
    timeout=30.0
) as client:
    
    # Manual policy enforcement with full control
    decision = client.enforce(
        tool_name="database_query",
        tool_args={"query": "SELECT * FROM users", "limit": 100},
        metadata={
            "department": "engineering",
            "risk_level": "medium",
            "compliance_required": True
        }
    )
    
    if decision.is_allowed:
        # Execute your operation
        results = execute_database_query(decision.tool_args)
        
        # Log the results for audit trail
        client.update_result(
            decision.session_id,
            decision.log_id,
            {"status": "success", "rows_returned": len(results)}
        )
        
        print(f"Query executed successfully: {len(results)} rows")
    
    elif decision.is_denied:
        print(f"Query denied: {decision.reason}")
        # Handle denial (logging, alerts, etc.)
    
    elif decision.requires_approval:
        print(f"Query requires approval: {decision.reason}")
        # Implement approval workflow
        approval_id = request_approval(decision)
        print(f"Approval requested: {approval_id}")
    
    # Get policy information
    policy_info = client.get_policy_info()
    print(f"Policy version: {policy_info.version}")
    print(f"Rules active: {policy_info.rules_count}")`}
                  language="python"
                  id="production-client"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Enterprise Error Handling</h3>
                <CodeBlock
                  code={`import tamesdk
from tamesdk import (
    PolicyViolationException,
    ApprovalRequiredException,
    ConnectionException,
    TameSDKException
)
import logging

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def secure_operation_with_fallback(operation_name: str, args: dict):
    """Production-ready operation with comprehensive error handling."""
    
    try:
        with tamesdk.Client(
            api_url="https://your-tame-server.com",
            session_id="production-session",
            raise_on_deny=True,  # Convert denials to exceptions
            raise_on_approve=True  # Convert approvals to exceptions
        ) as client:
            
            decision = client.enforce(
                tool_name=operation_name,
                tool_args=args
            )
            
            # If we get here, operation is allowed
            result = execute_operation(operation_name, args)
            
            # Log success
            client.update_result(
                decision.session_id,
                decision.log_id,
                {"status": "success", "result": result}
            )
            
            return {"success": True, "result": result}
            
    except PolicyViolationException as e:
        # Handle policy violations
        logger.warning(f"Policy violation: {operation_name} - {e}")
        return {
            "success": False,
            "error": "policy_violation",
            "message": str(e),
            "rule": e.rule_name
        }
        
    except ApprovalRequiredException as e:
        # Handle approval requirements
        logger.info(f"Approval required: {operation_name} - {e}")
        approval_id = request_approval(e)
        return {
            "success": False,
            "error": "approval_required",
            "message": str(e),
            "approval_id": approval_id
        }
        
    except ConnectionException as e:
        # Handle TameSDK connectivity issues
        logger.error(f"TameSDK connection error: {e}")
        
        if FALLBACK_MODE_ENABLED:
            # Graceful degradation
            logger.info("Falling back to operation without policy enforcement")
            result = execute_operation(operation_name, args)
            return {"success": True, "result": result, "fallback": True}
        else:
            return {
                "success": False,
                "error": "connection_failed",
                "message": "Policy enforcement unavailable"
            }
            
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in {operation_name}: {e}")
        return {
            "success": False,
            "error": "unexpected_error",
            "message": str(e)
        }

# Usage in production
result = secure_operation_with_fallback("database_query", {"table": "users"})
if result["success"]:
    print(f"Operation completed: {result['result']}")
else:
    print(f"Operation failed: {result['error']} - {result['message']}")`}
                  language="python"
                  id="production-error-handling"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Session Management</h3>
                <CodeBlock
                  code={`import tamesdk
import uuid
from datetime import datetime

class ProductionAgentSession:
    """Production-ready session management for AI agents."""
    
    def __init__(self, user_id: str, agent_id: str):
        self.user_id = user_id
        self.agent_id = agent_id
        self.session_id = f"{agent_id}-{uuid.uuid4().hex[:8]}"
        self.start_time = datetime.now()
        
        # Initialize TameSDK client
        self.client = tamesdk.Client(
            api_url="https://your-tame-server.com",
            session_id=self.session_id,
            agent_id=self.agent_id,
            user_id=self.user_id
        )
    
    def enforce_with_context(self, tool_name: str, tool_args: dict, context: dict = None):
        """Enforce policy with rich context information."""
        
        # Add session context
        metadata = {
            "session_start": self.start_time.isoformat(),
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            **(context or {})
        }
        
        return self.client.enforce(
            tool_name=tool_name,
            tool_args=tool_args,
            metadata=metadata
        )
    
    def get_session_summary(self):
        """Get session statistics and summary."""
        policy_info = self.client.get_policy_info()
        
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "start_time": self.start_time,
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "policy_version": policy_info.version,
            "rules_active": policy_info.rules_count
        }
    
    def close(self):
        """Clean up session resources."""
        self.client.close()

# Usage in production
session = ProductionAgentSession(
    user_id="alice@company.com",
    agent_id="customer-service-bot"
)

try:
    # Use session throughout agent lifecycle
    decision = session.enforce_with_context(
        tool_name="customer_lookup",
        tool_args={"email": "customer@example.com"},
        context={"department": "support", "priority": "high"}
    )
    
    if decision.is_allowed:
        # Execute operation
        result = lookup_customer(decision.tool_args)
        print(f"Customer lookup successful")
    
    # Get session summary
    summary = session.get_session_summary()
    print(f"Session summary: {summary}")
    
finally:
    session.close()`}
                  language="python"
                  id="production-session"
                />
              </div>
            </div>
          </CollapsibleSection>

          {/* Advanced Patterns */}
          <CollapsibleSection
            sectionKey="advancedPatterns"
            icon={Code}
            iconColor="text-purple-600"
            title="🔧 Advanced Patterns"
          >
            <div className="space-y-4">
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <h3 className="font-semibold text-purple-900 mb-2">Complex Integration Scenarios</h3>
                <p className="text-purple-800 text-sm">
                  Advanced patterns for complex enterprise scenarios, multiple integration approaches, and specialized use cases.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Advanced Policy Configuration</h3>
                <p className="mb-2 text-muted-foreground">
                  Create sophisticated policies with conditional logic, context-aware rules, and multi-layered security.
                </p>
                <CodeBlock
                  code={`# Create advanced-policies.yml
policy_version: "1.0"
description: "Advanced policy with conditional logic and context-aware rules"

rules:
  # Context-aware GitHub operations
  - name: "github_read_operations"
    description: "Allow GitHub read operations for all users"
    condition:
      tool_name: ["get_repository", "list_issues", "get_pull_request"]
      arguments:
        owner: "!private-org"  # Exclude private organization
    action: "allow"
    
  # Multi-condition approval requirements
  - name: "conditional_file_operations"
    description: "File operations based on path and user"
    condition:
      tool_name: ["delete_file", "update_file"]
      AND:
        - arguments:
            path: "^/app/.*"  # Only app directory
        - metadata:
            user_role: ["admin", "developer"]
        - time_range: "09:00-17:00"
    action: "approve"
    reason: "File modifications require approval during business hours"
    
  # Pattern-based tool filtering
  - name: "mcp_tool_filtering"
    description: "MCP tools based on server and operation type"
    condition:
      tool_name: ".*_mcp_.*"  # Any MCP tool
      metadata:
        mcp_server: ["github", "filesystem"]  # Only trusted servers
        operation_type: "read"
    action: "allow"
    
  # Dynamic approval based on risk score
  - name: "risk_based_approval"
    description: "Approval required for high-risk operations"
    condition:
      metadata:
        risk_score: ">7"  # Risk score above 7
    action: "approve"
    reason: "High-risk operations require human approval"
    
  # Cascade rule for tool patterns
  - name: "cascade_tool_patterns"
    description: "Different actions for different tool patterns"
    cascade:
      - condition:
          tool_name: "search_.*"
        action: "allow"
      - condition:
          tool_name: "read_.*"
        action: "allow"
      - condition:
          tool_name: "write_.*"
        action: "approve"
      - condition:
          tool_name: "delete_.*"
        action: "deny"
    
  # Session context rules
  - name: "session_based_limits"
    description: "Limits based on session activity"
    condition:
      session_context:
        operations_count: ">50"
    action: "approve"
    reason: "High activity sessions require oversight"

# Advanced defaults
default_action: "deny"
default_reason: "Advanced policy requires explicit rules"

# Complex session limits
session_limits:
  max_operations_per_session: 200
  max_operations_per_minute: 10
  max_concurrent_sessions: 5
  session_timeout_minutes: 120

# Advanced logging
logging:
  log_all_calls: true
  log_arguments: true
  log_results: true
  log_context: true
  sensitive_fields: ["password", "token", "secret", "key"]
  retention_days: 365
  audit_webhook: "https://your-audit-system.com/webhook"`}
                  language="yaml"
                  id="advanced-policy"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Pattern 1: Tool Filtering (Proactive)</h3>
                <p className="mb-2 text-muted-foreground">
                  Filter tools at the agent level so AI only sees policy-compliant tools. Best for high-security environments.
                </p>
                <CodeBlock
                  code={`import tamesdk
from openai import OpenAI

class ToolFilteringAgent:
    def __init__(self, openai_api_key: str):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.tame_client = tamesdk.Client(
            api_url="https://your-tame-server.com",
            session_id="tool-filtering-session",
            agent_id="filtered-agent"
        )
    
    def get_filtered_tools(self, available_tools: list):
        """Filter tools based on policy before showing to AI."""
        filtered_tools = []
        
        for tool in available_tools:
            try:
                # Check if tool is allowed by policy
                decision = self.tame_client.enforce(
                    tool_name=tool["function"]["name"],
                    tool_args={}  # Empty args for availability check
                )
                if decision.is_allowed:
                    filtered_tools.append(tool)
            except tamesdk.PolicyViolationException:
                # Skip tools that are blocked by policy
                continue
        
        return filtered_tools
    
    def chat_with_filtered_tools(self, message: str, all_tools: list):
        """Chat with AI using only policy-approved tools."""
        # Filter tools first
        approved_tools = self.get_filtered_tools(all_tools)
        
        print(f"Agent sees {len(approved_tools)} out of {len(all_tools)} available tools")
        
        # AI only sees approved tools
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            tools=approved_tools,  # Pre-filtered!
            tool_choice="auto"
        )
        
        return response

# Usage
agent = ToolFilteringAgent("sk-...")
all_tools = [
    {"function": {"name": "search_web", "description": "Search the web"}},
    {"function": {"name": "delete_file", "description": "Delete a file"}},
    {"function": {"name": "read_file", "description": "Read a file"}}
]

response = agent.chat_with_filtered_tools("Help me research Python", all_tools)
# AI will only see tools that pass policy check`}
                  language="python"
                  id="pattern-1-filtering"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Pattern 2: Execution Wrapping (Reactive)</h3>
                <p className="mb-2 text-muted-foreground">
                  Check policy right before tool execution. AI sees all tools but execution is controlled. Best for standard security.
                </p>
                <CodeBlock
                  code={`import tamesdk
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class ExecutionWrappingAgent:
    def __init__(self, session_id: str):
        self.tame_client = tamesdk.Client(
            api_url="https://your-tame-server.com",
            session_id=session_id,
            agent_id="execution-wrapping-agent"
        )
        self.mcp_session = None
    
    async def connect_to_mcp(self, mcp_command: list, env: dict = None):
        """Connect to MCP server."""
        server_params = StdioServerParameters(
            command=mcp_command[0],
            args=mcp_command[1:],
            env=env or {}
        )
        
        stdio_client_instance = stdio_client(server_params)
        read_stream, write_stream = await stdio_client_instance.__aenter__()
        self.mcp_session = ClientSession(read_stream, write_stream)
        await self.mcp_session.initialize()
    
    async def execute_tool_with_policy_check(self, tool_name: str, arguments: dict):
        """Execute MCP tool with policy check at execution time."""
        try:
            # Policy check happens RIGHT BEFORE execution
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            if decision.is_allowed:
                # Execute via MCP
                result = await self.mcp_session.call_tool(tool_name, arguments)
                
                # Log the result
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": str(result)}
                )
                
                return result
            else:
                return f"Execution blocked by policy: {decision.reason}"
                
        except tamesdk.PolicyViolationException as e:
            return f"Policy violation: {e}"

# Usage
agent = ExecutionWrappingAgent("execution-wrapping-session")
await agent.connect_to_mcp(["npx", "-y", "@modelcontextprotocol/server-github"])

# AI can see all tools, but execution is controlled
result = await agent.execute_tool_with_policy_check(
    "get_repository", 
    {"owner": "microsoft", "repo": "vscode"}
)
# Policy check happens here, not at tool discovery`}
                  language="python"
                  id="pattern-2-execution"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Pattern 3: Combined (Maximum Security)</h3>
                <p className="mb-2 text-muted-foreground">
                  Both filter tools AND check at execution for maximum security. Best for critical systems.
                </p>
                <CodeBlock
                  code={`import tamesdk
from openai import OpenAI
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class MaximumSecurityAgent:
    def __init__(self, openai_api_key: str, mcp_command: list):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.tame_client = tamesdk.Client(
            api_url="https://your-tame-server.com",
            session_id="maximum-security-session",
            agent_id="maximum-security-agent"
        )
        self.mcp_command = mcp_command
        self.mcp_session = None
    
    async def connect_to_mcp(self, env: dict = None):
        """Connect to MCP server."""
        server_params = StdioServerParameters(
            command=self.mcp_command[0],
            args=self.mcp_command[1:],
            env=env or {}
        )
        
        stdio_client_instance = stdio_client(server_params)
        read_stream, write_stream = await stdio_client_instance.__aenter__()
        self.mcp_session = ClientSession(read_stream, write_stream)
        await self.mcp_session.initialize()
    
    async def get_double_filtered_tools(self):
        """LAYER 1: Filter tools at agent level."""
        tools_result = await self.mcp_session.list_tools()
        filtered_tools = []
        
        for tool in tools_result.tools:
            try:
                # First policy check - tool availability
                decision = self.tame_client.enforce(
                    tool_name=tool.name,
                    tool_args={}
                )
                if decision.is_allowed:
                    filtered_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description
                        }
                    })
            except tamesdk.PolicyViolationException:
                continue
        
        return filtered_tools
    
    async def execute_with_double_check(self, tool_name: str, arguments: dict):
        """LAYER 2: Double-check policy at execution time."""
        try:
            # Second policy check - execution time
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            if decision.is_allowed:
                # Execute via MCP
                result = await self.mcp_session.call_tool(tool_name, arguments)
                
                # Log the result
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": str(result)}
                )
                
                return result
            else:
                return f"Double-check failed: {decision.reason}"
                
        except tamesdk.PolicyViolationException as e:
            return f"Execution policy violation: {e}"
    
    async def chat_with_maximum_security(self, user_message: str):
        """Chat with both tool filtering and execution checking."""
        # Layer 1: Get policy-filtered tools
        filtered_tools = await self.get_double_filtered_tools()
        
        print(f"Layer 1 - Agent sees {len(filtered_tools)} policy-approved tools")
        
        # Create completion with filtered tools
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}],
            tools=filtered_tools,
            tool_choice="auto"
        )
        
        # Layer 2: Execute with double-checking
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                print(f"Layer 2 - Executing {tool_name} with double security check...")
                result = await self.execute_with_double_check(tool_name, tool_args)
                print(f"Result: {result}")
        
        return response

# Usage
agent = MaximumSecurityAgent(
    openai_api_key="sk-...",
    mcp_command=["npx", "-y", "@modelcontextprotocol/server-github"]
)

await agent.connect_to_mcp({"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."})

# This uses BOTH filtering and execution checking
await agent.chat_with_maximum_security("List recent issues in the repository")
# Two layers of security: filtered tools + execution checking`}
                  language="python"
                  id="pattern-3-combined"
                />
              </div>
            </div>
          </CollapsibleSection>

          {/* MCP Agent Integration */}
          <CollapsibleSection
            sectionKey="mcpIntegration"
            icon={Zap}
            iconColor="text-yellow-500"
            title="MCP Agent Integration"
          >
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-2">Real MCP Agent Integration</h3>
                <p className="mb-2 text-muted-foreground">
                  In this pattern, TameSDK wraps MCP tool calls. The agent connects to an MCP server, but every tool execution 
                  is checked against your policies first.
                </p>
                <CodeBlock
                  code={`import asyncio
import tamesdk
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class MCPGitHubAgent:
    def __init__(self, github_token: str, session_id: str):
        # Initialize TameSDK client
        self.tame_client = tamesdk.Client(
            api_url="http://localhost:8000",
            session_id=session_id,
            agent_id="github-mcp-agent",
            user_id="developer"
        )
        
        # Initialize MCP client
        self.mcp_session = None
        self.github_token = github_token
    
    async def connect_to_github_mcp(self):
        """Connect to GitHub MCP server."""
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_PERSONAL_ACCESS_TOKEN": self.github_token}
        )
        
        self.stdio_client = stdio_client(server_params)
        read_stream, write_stream = await self.stdio_client.__aenter__()
        self.mcp_session = ClientSession(read_stream, write_stream)
        await self.mcp_session.initialize()
    
    async def call_mcp_tool_with_enforcement(self, tool_name: str, arguments: dict):
        """Call MCP tool with TameSDK policy enforcement."""
        try:
            # 1. ENFORCE POLICY FIRST
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            if decision.is_allowed:
                # 2. EXECUTE MCP TOOL (only if policy allows)
                result = await self.mcp_session.call_tool(tool_name, arguments)
                
                # 3. LOG THE RESULT
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "mcp_result": str(result)}
                )
                
                return result
            else:
                print(f"🛡️  Policy blocked: {decision.reason}")
                return None
                
        except tamesdk.PolicyViolationException as e:
            print(f"❌ Policy violation: {e}")
            return None
    
    async def get_repository_info(self, owner: str, repo: str):
        """Get repository information via MCP with policy enforcement."""
        return await self.call_mcp_tool_with_enforcement(
            "get_repository",
            {"owner": owner, "repo": repo}
        )
    
    async def create_issue_comment(self, owner: str, repo: str, issue_number: int, body: str):
        """Create issue comment via MCP with policy enforcement."""
        return await self.call_mcp_tool_with_enforcement(
            "create_issue_comment",
            {"owner": owner, "repo": repo, "issue_number": issue_number, "body": body}
        )
    
    def close(self):
        """Clean up connections."""
        self.tame_client.close()

# Usage example
async def main():
    agent = MCPGitHubAgent(
        github_token="ghp_xxxxx",
        session_id="github-session-001"
    )
    
    await agent.connect_to_github_mcp()
    
    # These operations will be enforced by TameSDK policy
    repo_info = await agent.get_repository_info("owner", "repo")
    comment_result = await agent.create_issue_comment(
        "owner", "repo", 1, "This comment was policy-enforced!"
    )
    
    agent.close()

if __name__ == "__main__":
    asyncio.run(main())`}
                  language="python"
                  id="mcp-agent-example"
                />
              </div>
              <div>
                <h3 className="text-lg font-medium mb-2">MCP Integration Tips</h3>
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold text-amber-900 mb-2">Integration Patterns</h4>
                  <div className="text-amber-800 text-sm space-y-2">
                    <div><strong>Pattern 1:</strong> Wrap MCP tool calls (most common) - Policy check before MCP execution</div>
                    <div><strong>Pattern 2:</strong> Filter tools at agent level - Remove blocked tools before agent sees them</div>
                    <div><strong>Pattern 3:</strong> Both - Maximum security with filtering + execution enforcement</div>
                  </div>
                </div>
                
                <ul className="list-disc pl-6 text-muted-foreground text-sm">
                  <li>TameSDK sits <strong>between</strong> your agent and tool execution, not inside the MCP server</li>
                  <li>Call <code>client.enforce(tool_name, tool_args)</code> before every tool execution</li>
                  <li>Use <code>decision.is_allowed</code> to check if the operation is permitted</li>
                  <li>Always call <code>client.update_result()</code> to log operation results for audit trails</li>
                  <li>Handle <code>PolicyViolationException</code> and <code>ApprovalRequiredException</code> appropriately</li>
                  <li>Configure <code>api_url</code> to point to your backend (Docker: <code>http://backend:8000</code>, Local: <code>http://localhost:8000</code>)</li>
                  <li>Use context managers (<code>with Client()</code>) for automatic cleanup</li>
                </ul>
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
                <h3 className="text-lg font-medium mb-2">Installation and Setup</h3>
                <CodeBlock
                  code={`# Install TameSDK
pip install -e ./tamesdk

# Check connection and status
tamesdk status

# Get current policy information
tamesdk policy`}
                  language="bash"
                  id="cli-setup"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Test Tool Calls</h3>
                <CodeBlock
                  code={`# Test a tool against current policy
tamesdk test search_web --args '{"query": "python programming"}'

# Test with complex arguments
tamesdk test delete_file --args '{"path": "/tmp/test.txt", "force": true}'

# Test enforcement with exit codes (useful for CI/CD)
tamesdk enforce --tool dangerous_operation --args '{"action": "format_disk"}'
# Exit code 0 = allowed, 1 = denied, 2 = approval required`}
                  language="bash"
                  id="cli-test"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Interactive Mode</h3>
                <CodeBlock
                  code={`# Launch interactive testing mode
tamesdk interactive

# In interactive mode, you can:
# - Test multiple tools quickly
# - See policy decisions in real-time
# - Modify arguments and re-test
# - View session history

# Example interactive session:
> tool: search_web
> args: {"query": "AI safety", "count": 5}
✅ ALLOWED - Safe search operation

> tool: delete_file  
> args: {"path": "/system/critical.cfg"}
❌ DENIED - System file deletion blocked by policy`}
                  language="bash"
                  id="cli-interactive"
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
                  code={`import tamesdk

client = tamesdk.Client(api_url="http://localhost:8000")

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
                  code={`import tamesdk

client = tamesdk.Client(api_url="http://localhost:8000")

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
                  code={`import tamesdk

client = tamesdk.Client(api_url="http://localhost:8000")

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
import tamesdk

class TameEnforcedTool(BaseTool):
    name = "tame_enforced_tool"
    description = "A tool that enforces policy before execution"
    
    def __init__(self, tool_name: str, tame_client: tamesdk.Client):
        super().__init__()
        self.tool_name = tool_name
        self.tame_client = tame_client
    
    def _run(self, **kwargs):
        try:
            # Enforce policy
            decision = self.tame_client.enforce(
                tool_name=self.tool_name,
                tool_args=kwargs
            )
            
            if decision.is_allowed:
                # Execute the actual tool logic
                result = self.execute_tool(**kwargs)
                
                # Log the result
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result}
                )
                
                return result
            else:
                return f"Tool blocked: {decision.reason}"
                
        except tamesdk.PolicyViolationException as e:
            return f"Policy violation: {e}"
    
    def execute_tool(self, **kwargs):
        # Your actual tool implementation
        return f"Executed {self.tool_name} with args: {kwargs}"

# Usage with LangChain
tame_client = tamesdk.Client(
    api_url="http://localhost:8000",
    session_id="langchain-session",
    agent_id="langchain-agent"
)

tools = [TameEnforcedTool("search_web", tame_client)]
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)`}
                  language="python"
                  id="langchain"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">AutoGen Integration</h3>
                <CodeBlock
                  code={`import autogen
import tamesdk

class TameEnforcedAgent(autogen.ConversableAgent):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.tame_client = tamesdk.Client(
            api_url="http://localhost:8000",
            session_id=f"autogen-{name}",
            agent_id=name
        )
    
    def execute_function(self, func_name, **kwargs):
        try:
            # Enforce policy before execution
            decision = self.tame_client.enforce(
                tool_name=func_name,
                tool_args=kwargs
            )
            
            if decision.is_allowed:
                result = super().execute_function(func_name, **kwargs)
                
                # Log the result
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result}
                )
                
                return result
            elif decision.is_denied:
                return {"error": f"Policy violation: {decision.reason}"}
            else:  # requires approval
                return {"pending": f"Requires approval: {decision.reason}"}
                
        except tamesdk.PolicyViolationException as e:
            return {"error": f"Policy violation: {e}"}
    
    def __del__(self):
        # Clean up client connection
        if hasattr(self, 'tame_client'):
            self.tame_client.close()

# Create agents with policy enforcement
agent = TameEnforcedAgent(
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
import tamesdk

class TameEnforcedTool(Tool):
    def __init__(self, name, description, func, tame_client):
        super().__init__(name=name, description=description, func=self._enforced_func)
        self.original_func = func
        self.tame_client = tame_client
    
    def _enforced_func(self, **kwargs):
        try:
            # Enforce policy
            decision = self.tame_client.enforce(
                tool_name=self.name,
                tool_args=kwargs
            )
            
            if decision.is_allowed:
                result = self.original_func(**kwargs)
                
                # Log the result
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result}
                )
                
                return result
            else:
                return f"Tool blocked by policy: {decision.reason}"
                
        except tamesdk.PolicyViolationException as e:
            return f"Policy violation: {e}"

# Create enforced tools
tame_client = tamesdk.Client(
    api_url="http://localhost:8000",
    session_id="crewai-session",
    agent_id="crewai-agent"
)

def search_function(query: str):
    # Your search implementation
    return f"Search results for: {query}"

search_tool = TameEnforcedTool(
    name="search_web",
    description="Search the web for information",
    func=search_function,
    tame_client=tame_client
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

              <div>
                <h3 className="text-lg font-medium mb-2">OpenAI Agent SDK - Pattern 1: Tool Filtering</h3>
                <p className="mb-2 text-muted-foreground">
                  This pattern filters tools at the agent level, so the AI only sees tools that are policy-compliant.
                </p>
                <CodeBlock
                  code={`from openai import OpenAI
import tamesdk

class TameEnforcedOpenAIAgent:
    def __init__(self, openai_api_key: str):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.tame_client = tamesdk.Client(
            api_url="http://localhost:8000",
            session_id="openai-agent-session",
            agent_id="openai-agent"
        )
    
    def create_completion_with_tools(self, messages: list, tools: list):
        """Create completion with policy-enforced tools."""
        # Filter tools based on policy
        allowed_tools = []
        for tool in tools:
            try:
                decision = self.tame_client.enforce(
                    tool_name=tool["function"]["name"],
                    tool_args=tool["function"].get("parameters", {})
                )
                if decision.is_allowed:
                    allowed_tools.append(tool)
            except tamesdk.PolicyViolationException:
                # Skip tools that are blocked by policy
                continue
        
        # Create completion with allowed tools only
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=allowed_tools,
            tool_choice="auto"
        )
        
        return response
    
    def execute_tool_call(self, tool_call):
        """Execute a tool call with policy enforcement."""
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        try:
            # Enforce policy
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=tool_args
            )
            
            if decision.is_allowed:
                # Execute the tool (implement your tool logic here)
                result = self.execute_actual_tool(tool_name, tool_args)
                
                # Log the result
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": result}
                )
                
                return result
            else:
                return f"Tool execution blocked: {decision.reason}"
                
        except tamesdk.PolicyViolationException as e:
            return f"Policy violation: {e}"
    
    def execute_actual_tool(self, tool_name: str, tool_args: dict):
        """Implement your actual tool logic here."""
        if tool_name == "search_web":
            return f"Search results for: {tool_args.get('query', '')}"
        elif tool_name == "read_file":
            return f"File content: {tool_args.get('path', '')}"
        else:
            return f"Unknown tool: {tool_name}"

# Usage example
agent = TameEnforcedOpenAIAgent(openai_api_key="sk-...")

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }
]

messages = [{"role": "user", "content": "Search for information about AI safety"}]
response = agent.create_completion_with_tools(messages, tools)`}
                  language="python"
                  id="openai-agent"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">MCP Server Integration - Pattern 2: Execution Wrapping</h3>
                <p className="mb-2 text-muted-foreground">
                  This pattern wraps MCP tool execution, checking policy right before each tool call.
                </p>
                <CodeBlock
                  code={`import asyncio
import tamesdk
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class TameEnforcedMCPClient:
    def __init__(self, mcp_server_command: list, session_id: str):
        self.mcp_server_command = mcp_server_command
        self.tame_client = tamesdk.Client(
            api_url="http://localhost:8000",
            session_id=session_id,
            agent_id="mcp-client"
        )
        self.mcp_session = None
        self.stdio_client = None
    
    async def connect_to_mcp_server(self, env: dict = None):
        """Connect to MCP server with policy enforcement."""
        server_params = StdioServerParameters(
            command=self.mcp_server_command[0],
            args=self.mcp_server_command[1:],
            env=env or {}
        )
        
        self.stdio_client = stdio_client(server_params)
        read_stream, write_stream = await self.stdio_client.__aenter__()
        self.mcp_session = ClientSession(read_stream, write_stream)
        await self.mcp_session.initialize()
        
        # Get available tools
        tools_result = await self.mcp_session.list_tools()
        print(f"Available MCP tools: {[tool.name for tool in tools_result.tools]}")
    
    async def call_mcp_tool_with_enforcement(self, tool_name: str, arguments: dict):
        """Call MCP tool with TameSDK policy enforcement."""
        if not self.mcp_session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            # 1. ENFORCE POLICY FIRST
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            if decision.is_allowed:
                # 2. EXECUTE MCP TOOL
                result = await self.mcp_session.call_tool(tool_name, arguments)
                
                # 3. LOG THE RESULT
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "mcp_result": str(result)}
                )
                
                return result
            else:
                return f"Tool blocked by policy: {decision.reason}"
                
        except tamesdk.PolicyViolationException as e:
            return f"Policy violation: {e}"
    
    async def close(self):
        """Clean up connections."""
        if self.mcp_session:
            await self.mcp_session.close()
        if self.stdio_client:
            await self.stdio_client.__aexit__(None, None, None)
        self.tame_client.close()

# Usage examples for different MCP servers
async def github_mcp_example():
    """Example with GitHub MCP server."""
    client = TameEnforcedMCPClient(
        mcp_server_command=["npx", "-y", "@modelcontextprotocol/server-github"],
        session_id="github-mcp-session"
    )
    
    await client.connect_to_mcp_server({
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxx"
    })
    
    # These calls will be policy-enforced
    repo_info = await client.call_mcp_tool_with_enforcement(
        "get_repository",
        {"owner": "microsoft", "repo": "vscode"}
    )
    
    await client.close()

# Run the examples
asyncio.run(github_mcp_example())`}
                  language="python"
                  id="mcp-servers"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Anthropic MCP Integration</h3>
                <CodeBlock
                  code={`import asyncio
import tamesdk
from anthropic import Anthropic
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class TameEnforcedAnthropicMCPAgent:
    def __init__(self, anthropic_api_key: str):
        self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        self.tame_client = tamesdk.Client(
            api_url="http://localhost:8000",
            session_id="anthropic-mcp-session",
            agent_id="anthropic-mcp-agent"
        )
        self.mcp_clients = {}  # Store multiple MCP connections
    
    async def connect_mcp_server(self, server_name: str, command: list, env: dict = None):
        """Connect to an MCP server."""
        server_params = StdioServerParameters(
            command=command[0],
            args=command[1:],
            env=env or {}
        )
        
        stdio_client_instance = stdio_client(server_params)
        read_stream, write_stream = await stdio_client_instance.__aenter__()
        session = ClientSession(read_stream, write_stream)
        await session.initialize()
        
        # Get available tools
        tools_result = await session.list_tools()
        
        self.mcp_clients[server_name] = {
            "session": session,
            "stdio_client": stdio_client_instance,
            "tools": tools_result.tools
        }
        
        print(f"Connected to {server_name} with {len(tools_result.tools)} tools")
    
    async def execute_tool_with_enforcement(self, tool_name: str, arguments: dict):
        """Execute tool with policy enforcement across all MCP servers."""
        # Find which server has this tool
        target_server = None
        for server_name, client_info in self.mcp_clients.items():
            for tool in client_info["tools"]:
                if tool.name == tool_name:
                    target_server = server_name
                    break
            if target_server:
                break
        
        if not target_server:
            return f"Tool {tool_name} not found in any connected MCP server"
        
        try:
            # Enforce policy
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            if decision.is_allowed:
                # Execute via MCP
                session = self.mcp_clients[target_server]["session"]
                result = await session.call_tool(tool_name, arguments)
                
                # Log the result
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {
                        "status": "success",
                        "server": target_server,
                        "result": str(result)
                    }
                )
                
                return result
            else:
                return f"Tool blocked by policy: {decision.reason}"
                
        except tamesdk.PolicyViolationException as e:
            return f"Policy violation: {e}"
    
    async def close(self):
        """Clean up all connections."""
        for server_name, client_info in self.mcp_clients.items():
            await client_info["session"].close()
            await client_info["stdio_client"].__aexit__(None, None, None)
        
        self.tame_client.close()

# Usage example
async def main():
    agent = TameEnforcedAnthropicMCPAgent("your-anthropic-api-key")
    
    # Connect to multiple MCP servers
    await agent.connect_mcp_server(
        "github",
        ["npx", "-y", "@modelcontextprotocol/server-github"],
        {"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxx"}
    )
    
    await agent.connect_mcp_server(
        "filesystem",
        ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
        {"ALLOWED_PATHS": "/home/user/documents"}
    )
    
    await agent.close()

asyncio.run(main())`}
                  language="python"
                  id="anthropic-mcp"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Pattern 3: Combined Filtering + Execution (Maximum Security)</h3>
                <p className="mb-2 text-muted-foreground">
                  This pattern combines both tool filtering and execution wrapping for maximum security.
                </p>
                <CodeBlock
                  code={`import asyncio
import tamesdk
from openai import OpenAI
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class MaxSecurityAgent:
    def __init__(self, openai_api_key: str, mcp_server_command: list):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.tame_client = tamesdk.Client(
            api_url="http://localhost:8000",
            session_id="max-security-session",
            agent_id="max-security-agent"
        )
        self.mcp_server_command = mcp_server_command
        self.mcp_session = None
    
    async def connect_to_mcp(self, env: dict = None):
        """Connect to MCP server."""
        server_params = StdioServerParameters(
            command=self.mcp_server_command[0],
            args=self.mcp_server_command[1:],
            env=env or {}
        )
        
        stdio_client_instance = stdio_client(server_params)
        read_stream, write_stream = await stdio_client_instance.__aenter__()
        self.mcp_session = ClientSession(read_stream, write_stream)
        await self.mcp_session.initialize()
    
    async def get_filtered_tools(self):
        """PATTERN 1: Filter tools at agent level."""
        tools_result = await self.mcp_session.list_tools()
        filtered_tools = []
        
        for tool in tools_result.tools:
            try:
                # Check if tool is allowed by policy
                decision = self.tame_client.enforce(
                    tool_name=tool.name,
                    tool_args={}  # Empty args for availability check
                )
                if decision.is_allowed:
                    filtered_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {"type": "object", "properties": {}}
                        }
                    })
            except tamesdk.PolicyViolationException:
                # Tool is blocked, don't include it
                continue
        
        return filtered_tools
    
    async def execute_tool_with_double_check(self, tool_name: str, arguments: dict):
        """PATTERN 2: Double-check policy at execution time."""
        try:
            # SECOND POLICY CHECK at execution time
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=arguments
            )
            
            if decision.is_allowed:
                # Execute via MCP
                result = await self.mcp_session.call_tool(tool_name, arguments)
                
                # Log the result
                self.tame_client.update_result(
                    decision.session_id,
                    decision.log_id,
                    {"status": "success", "result": str(result)}
                )
                
                return result
            else:
                return f"Double-check failed: {decision.reason}"
                
        except tamesdk.PolicyViolationException as e:
            return f"Execution policy violation: {e}"
    
    async def chat_with_maximum_security(self, user_message: str):
        """Chat with both tool filtering and execution checking."""
        # 1. Get policy-filtered tools (so agent only sees allowed tools)
        filtered_tools = await self.get_filtered_tools()
        
        print(f"Agent sees {len(filtered_tools)} policy-approved tools")
        
        # 2. Create completion with filtered tools
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}],
            tools=filtered_tools,
            tool_choice="auto"
        )
        
        # 3. Execute any tool calls with double-checking
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                print(f"Executing {tool_name} with double security check...")
                result = await self.execute_tool_with_double_check(tool_name, tool_args)
                print(f"Result: {result}")
        
        return response

# Usage example
async def main():
    agent = MaxSecurityAgent(
        openai_api_key="sk-...",
        mcp_server_command=["npx", "-y", "@modelcontextprotocol/server-github"]
    )
    
    await agent.connect_to_mcp({"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."})
    
    # This uses BOTH filtering and execution checking
    await agent.chat_with_maximum_security("List the recent issues in the repository")

asyncio.run(main())`}
                  language="python"
                  id="combined-pattern"
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