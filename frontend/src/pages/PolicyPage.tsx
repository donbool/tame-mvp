import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import type { PolicyInfo } from '@/lib/api'
import { Shield, CheckCircle, XCircle, Clock, AlertTriangle, RefreshCw, Plus, Save, Eye, FileText } from 'lucide-react'

export default function PolicyPage() {
  const [policyInfo, setPolicyInfo] = useState<PolicyInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [testResult, setTestResult] = useState<any>(null)
  const [testLoading, setTestLoading] = useState(false)
  const [testToolName, setTestToolName] = useState('search_web')
  const [testArgs, setTestArgs] = useState('{"query": "test"}')
  
  // Add a new tab for templates
  const [activeTab, setActiveTab] = useState<'view' | 'create' | 'templates'>('view')

  // Policy templates data
  const policyTemplates = [
    {
      id: 'gmail-safe',
      title: 'Gmail Agent: Safe Email Policy',
      description: 'Blocks external addresses, requires approval for attachments.',
      yaml: `version: "1.0"
metadata:
  name: "Gmail Safe Policy"
  description: "Block external, require approval for attachments."
rules:
  - name: "Allow Internal Emails"
    action: allow
    tools: ["send_email"]
    conditions:
      arg_contains:
        to: "@yourcompany.com"
  - name: "Require Approval for Attachments"
    action: approve
    tools: ["send_email"]
    conditions:
      arg_contains:
        attachments: "*"
  - name: "Deny External Emails"
    action: deny
    tools: ["send_email"]
    conditions:
      arg_not_contains:
        to: "@yourcompany.com"
  - name: "Default Deny"
    action: deny
    tools: ["*"]
`,
    },
    {
      id: 'slack-safe',
      title: 'Slack Bot: Channel Restriction',
      description: 'Allow only certain channels, log all messages.',
      yaml: `version: "1.0"
metadata:
  name: "Slack Channel Policy"
  description: "Allow only #general and #alerts. Log all messages."
rules:
  - name: "Allow General Channels"
    action: allow
    tools: ["post_to_slack"]
    conditions:
      arg_contains:
        channel: "#general"
  - name: "Allow Alerts Channel"
    action: allow
    tools: ["post_to_slack"]
    conditions:
      arg_contains:
        channel: "#alerts"
  - name: "Deny Other Channels"
    action: deny
    tools: ["post_to_slack"]
  - name: "Default Deny"
    action: deny
    tools: ["*"]
`,
    },
    {
      id: 'deploy-safe',
      title: 'Deployment Agent: Human Signoff',
      description: 'Require human approval for deploys, enforce time windows.',
      yaml: `version: "1.0"
metadata:
  name: "Deployment Policy"
  description: "Require approval and restrict deploy times."
rules:
  - name: "Require Approval for Deploy"
    action: approve
    tools: ["deploy_code"]
  - name: "Allow Deploys in Window"
    action: allow
    tools: ["deploy_code"]
    conditions:
      session_context:
        time_of_day: "business_hours"
  - name: "Deny All Other Deploys"
    action: deny
    tools: ["deploy_code"]
  - name: "Default Deny"
    action: deny
    tools: ["*"]
`,
    },
    {
      id: 'data-safe',
      title: 'Data Analysis Agent: Log & Block PII',
      description: 'Log all dataset access, block PII export.',
      yaml: `version: "1.0"
metadata:
  name: "Data Analysis Policy"
  description: "Log access, block PII export."
rules:
  - name: "Allow Dataset Access"
    action: allow
    tools: ["read_dataset"]
  - name: "Deny PII Export"
    action: deny
    tools: ["export_data"]
    conditions:
      arg_contains:
        content: "PII"
  - name: "Default Deny"
    action: deny
    tools: ["*"]
`,
    },
    {
      id: 'safe-defaults',
      title: 'Safe Defaults',
      description: 'Allow only safe tools, deny everything else.',
      yaml: `version: "1.0"
metadata:
  name: "Safe Defaults"
  description: "Allow only safe tools."
rules:
  - name: "Allow Safe Tools"
    action: allow
    tools: ["search_web", "read_file", "get_weather"]
  - name: "Deny Dangerous Tools"
    action: deny
    tools: ["delete_file", "execute_command", "format_disk"]
  - name: "Default Deny"
    action: deny
    tools: ["*"]
`,
    },
  ]

  // Template preview state
  const [previewTemplate, setPreviewTemplate] = useState<string | null>(null)
  const [newPolicy, setNewPolicy] = useState({
    version: '',
    description: '',
    content: `version: "1.0"
metadata:
  name: "Custom Policy"
  description: "Custom policy for AI agent enforcement"

rules:
  - name: "Allow Safe Tools"
    description: "Allow read-only and search operations"
    tools: ["search_web", "read_file", "get_weather"]
    action: allow
    
  - name: "Deny Dangerous Operations"
    description: "Block potentially harmful operations"
    tools: ["delete_file", "execute_command", "format_disk"]
    action: deny
    
  - name: "Default Allow"
    description: "Allow other tools by default"
    tools: ["*"]
    action: allow`,
    activate: true
  })
  const [validationResult, setValidationResult] = useState<any>(null)
  const [validating, setValidating] = useState(false)
  const [creating, setCreating] = useState(false)
  const [createResult, setCreateResult] = useState<any>(null)

  // Policy autogeneration state
  const [autoTask, setAutoTask] = useState('')
  const [autoTools, setAutoTools] = useState('search_web, send_email, read_file')
  const [autoPolicy, setAutoPolicy] = useState('')
  const [autoError, setAutoError] = useState<string | null>(null)

  const loadPolicyInfo = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getPolicyInfo()
      setPolicyInfo(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load policy info')
      console.error('Failed to load policy info:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPolicyInfo()
  }, [])

  const handleTestPolicy = async () => {
    if (!testToolName.trim()) return

    try {
      setTestLoading(true)
      let args = {}
      
      if (testArgs.trim()) {
        try {
          args = JSON.parse(testArgs)
        } catch (e) {
          alert('Invalid JSON in arguments')
          return
        }
      }

      const result = await apiClient.testPolicy({
        tool_name: testToolName,
        tool_args: args
      })
      
      setTestResult(result)
    } catch (err) {
      console.error('Failed to test policy:', err)
      alert('Failed to test policy: ' + (err instanceof Error ? err.message : 'Unknown error'))
    } finally {
      setTestLoading(false)
    }
  }

  const handleValidatePolicy = async () => {
    if (!newPolicy.content.trim()) return

    try {
      setValidating(true)
      setValidationResult(null)
      
      const result = await apiClient.validatePolicy(newPolicy.content, newPolicy.description)
      setValidationResult(result)
    } catch (err) {
      console.error('Failed to validate policy:', err)
      setValidationResult({
        is_valid: false,
        errors: [err instanceof Error ? err.message : 'Validation failed'],
        rules_count: 0
      })
    } finally {
      setValidating(false)
    }
  }

  const handleCreatePolicy = async () => {
    if (!newPolicy.version.trim() || !newPolicy.content.trim()) {
      alert('Please provide both version and policy content')
      return
    }

    try {
      setCreating(true)
      setCreateResult(null)
      
      const result = await apiClient.createPolicy({
        policy_content: newPolicy.content,
        version: newPolicy.version,
        description: newPolicy.description,
        activate: newPolicy.activate
      })
      
      setCreateResult(result)
      
      if (result.success) {
        // Reset form
        setNewPolicy(prev => ({
          ...prev,
          version: '',
          description: ''
        }))
        
        // Reload policy info if activated
        if (newPolicy.activate) {
          await loadPolicyInfo()
        }
        
        // Switch back to view tab
        setTimeout(() => setActiveTab('view'), 2000)
      }
    } catch (err) {
      console.error('Failed to create policy:', err)
      setCreateResult({
        success: false,
        policy_id: '',
        version: newPolicy.version,
        message: err instanceof Error ? err.message : 'Failed to create policy',
        validation_errors: []
      })
    } finally {
      setCreating(false)
    }
  }

  const handleAutogeneratePolicy = () => {
    setAutoError(null)
    if (!autoTask.trim() || !autoTools.trim()) {
      setAutoError('Please provide both a task description and at least one tool.')
      return
    }
    const tools = autoTools.split(',').map(t => t.trim()).filter(Boolean)
    if (tools.length === 0) {
      setAutoError('Please provide at least one tool.')
      return
    }
    // Simple rule-based policy autogeneration
    const yaml =
`version: "1.0"
metadata:
  name: "Autogenerated Policy"
  description: "Policy for: ${autoTask}"
rules:
  - name: "Allow Safe Tools"
    description: "Allow only the specified tools for this task."
    tools: [${tools.map(t => '"' + t + '"').join(', ')}]
    action: allow
  - name: "Deny All Others"
    description: "Deny any tool not explicitly allowed."
    tools: ["*"]
    action: deny
`
    setAutoPolicy(yaml)
  }

  const handleInsertAutogen = () => {
    setNewPolicy(prev => ({
      ...prev,
      content: autoPolicy
    }))
  }

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'allow':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'deny':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'approve':
        return <Clock className="w-5 h-5 text-yellow-600" />
      default:
        return <Shield className="w-5 h-5 text-gray-600" />
    }
  }

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'allow':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'deny':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'approve':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Policy Management</h1>
          <p className="text-muted-foreground">View and manage enforcement policies</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading policy information...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Policy Management</h1>
          <p className="text-muted-foreground">View and manage enforcement policies</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="text-red-600 text-center">
            <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
            <p className="font-medium">Failed to load policy information</p>
            <p className="text-sm mt-1">{error}</p>
            <button 
              onClick={loadPolicyInfo}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Policy Management</h1>
          <p className="text-muted-foreground">View and manage enforcement policies</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadPolicyInfo}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('view')}
            className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'view'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
            }`}
          >
            <Eye className="w-4 h-4" />
            View Policy
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'create'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
            }`}
          >
            <Plus className="w-4 h-4" />
            Create Policy
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'templates'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
            }`}
          >
            <FileText className="w-4 h-4" />
            Templates
          </button>
        </nav>
      </div>

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="space-y-6">
          <div className="bg-card border border-border rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-6 h-6 text-blue-600" />
              Policy Templates
            </h2>
            <p className="text-muted-foreground mb-6">Browse pre-built policy templates for common agent and integration scenarios. Click "Use This Template" to start a new policy with the selected configuration.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {policyTemplates.map((tpl) => (
                <div key={tpl.id} className="border border-border rounded-lg p-4 bg-muted/50 flex flex-col">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold">{tpl.title}</h3>
                  </div>
                  <p className="text-muted-foreground text-sm mb-2">{tpl.description}</p>
                  <button
                    onClick={() => setPreviewTemplate(tpl.id)}
                    className="text-blue-600 text-xs underline mb-2 self-start"
                  >
                    {previewTemplate === tpl.id ? 'Hide YAML' : 'Preview YAML'}
                  </button>
                  {previewTemplate === tpl.id && (
                    <pre className="bg-background p-3 rounded border text-xs overflow-x-auto mb-2">{tpl.yaml}</pre>
                  )}
                  <button
                    onClick={() => {
                      setActiveTab('create')
                      setNewPolicy(prev => ({ ...prev, content: tpl.yaml }))
                    }}
                    className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 mt-auto"
                  >
                    Use This Template
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* View Policy Tab */}
      {activeTab === 'view' && (
        <div className="space-y-6">
          {/* Current Policy Info */}
          {policyInfo && (
            <div className="bg-card border border-border rounded-lg">
              <div className="p-6 border-b border-border">
                <h2 className="text-xl font-semibold">Current Policy</h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Version</p>
                    <p className="text-lg font-mono">{policyInfo.version}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Rules Count</p>
                    <p className="text-lg font-bold">{policyInfo.rules_count}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Hash</p>
                    <p className="text-lg font-mono text-muted-foreground">
                      {policyInfo.hash.length > 16 ? `${policyInfo.hash.substring(0, 16)}...` : policyInfo.hash}
                    </p>
                  </div>
                </div>

                {/* Policy Rules */}
                {policyInfo.rules && policyInfo.rules.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Policy Rules</h3>
                    <div className="space-y-4">
                      {policyInfo.rules.map((rule, index) => (
                        <div key={index} className="border border-border rounded-lg p-4">
                          <div className="flex items-center gap-3 mb-2">
                            <h4 className="font-medium">{rule.name}</h4>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                              rule.action === 'allow' ? 'text-green-600 bg-green-50 border-green-200' :
                              rule.action === 'deny' ? 'text-red-600 bg-red-50 border-red-200' :
                              rule.action === 'approve' ? 'text-yellow-600 bg-yellow-50 border-yellow-200' :
                              'text-gray-600 bg-gray-50 border-gray-200'
                            }`}>
                              {rule.action.toUpperCase()}
                            </span>
                          </div>
                          
                          <div className="text-sm text-muted-foreground mb-2">
                            <strong>Tools:</strong> {rule.tools.join(', ')}
                          </div>
                          
                          {rule.description && (
                            <p className="text-sm text-muted-foreground">{rule.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Policy Tester */}
          <div className="bg-card border border-border rounded-lg">
            <div className="p-6 border-b border-border">
              <h2 className="text-xl font-semibold">Test Policy</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Test how a tool call would be evaluated against the current policy
              </p>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-muted-foreground mb-2 block">
                    Tool Name
                  </label>
                  <input
                    type="text"
                    value={testToolName}
                    onChange={(e) => setTestToolName(e.target.value)}
                    placeholder="e.g., search_web, read_file, delete_file"
                    className="w-full px-3 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium text-muted-foreground mb-2 block">
                    Tool Arguments (JSON)
                  </label>
                  <textarea
                    value={testArgs}
                    onChange={(e) => setTestArgs(e.target.value)}
                    placeholder='{"query": "test", "path": "/tmp/file"}'
                    rows={3}
                    className="w-full px-3 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  />
                </div>
              </div>

              <div className="mt-6">
                <button
                  onClick={handleTestPolicy}
                  disabled={testLoading || !testToolName.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {testLoading ? 'Testing...' : 'Test Policy'}
                </button>
              </div>

              {/* Test Result */}
              {testResult && (
                <div className="mt-6 p-4 border border-border rounded-lg">
                  <div className="flex items-center gap-3 mb-3">
                    {getDecisionIcon(testResult.decision.action)}
                    <h3 className="font-medium">Policy Test Result</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getDecisionColor(testResult.decision.action)}`}>
                      {testResult.decision.action.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div>
                      <strong>Tool:</strong> {testResult.tool_name}
                    </div>
                    <div>
                      <strong>Rule:</strong> {testResult.decision.rule_name || 'N/A'}
                    </div>
                    <div>
                      <strong>Reason:</strong> {testResult.decision.reason}
                    </div>
                    <div>
                      <strong>Policy Version:</strong> {testResult.decision.policy_version}
                    </div>
                    
                    {Object.keys(testResult.tool_args).length > 0 && (
                      <div>
                        <strong>Arguments:</strong>
                        <pre className="mt-1 text-xs bg-accent p-2 rounded border overflow-x-auto">
                          {JSON.stringify(testResult.tool_args, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create Policy Tab */}
      {activeTab === 'create' && (
        <div className="space-y-6">
          {/* Policy Autogeneration Card */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Policy Autogenerator
            </h2>
            <p className="text-muted-foreground mb-4">Describe your agent's task and list the tools it will use. We'll generate a safe starter policy for you.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1">Task Description</label>
                <textarea
                  value={autoTask}
                  onChange={e => setAutoTask(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                  rows={3}
                  placeholder="E.g. An agent that sends emails and searches the web for research."
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Tools (comma-separated)</label>
                <input
                  type="text"
                  value={autoTools}
                  onChange={e => setAutoTools(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                  placeholder="search_web, send_email, read_file"
                />
              </div>
            </div>
            <button
              onClick={handleAutogeneratePolicy}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Generate Policy
            </button>
            {autoError && <div className="text-red-600 mt-2">{autoError}</div>}
            {autoPolicy && (
              <div className="mt-4">
                <label className="block text-sm font-medium mb-1">Generated Policy YAML</label>
                <pre className="bg-muted/50 p-4 rounded border overflow-x-auto text-sm mb-2">{autoPolicy}</pre>
                <button
                  onClick={handleInsertAutogen}
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Insert into Policy Editor
                </button>
              </div>
            )}
          </div>
          {/* End Policy Autogeneration Card */}

          {/* Existing policy editor and creation UI follows here... */}
          <div className="bg-card border border-border rounded-lg">
            <div className="p-6 border-b border-border">
              <h2 className="text-xl font-semibold">Create New Policy</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Design a new policy configuration and deploy it to your system
              </p>
            </div>
            <div className="p-6 space-y-6">
              {/* Policy Metadata */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-muted-foreground mb-2 block">
                    Policy Version *
                  </label>
                  <input
                    type="text"
                    value={newPolicy.version}
                    onChange={(e) => setNewPolicy(prev => ({ ...prev, version: e.target.value }))}
                    placeholder="e.g., v2.0, production-2024"
                    className="w-full px-3 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium text-muted-foreground mb-2 block">
                    Description
                  </label>
                  <input
                    type="text"
                    value={newPolicy.description}
                    onChange={(e) => setNewPolicy(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Brief description of this policy"
                    className="w-full px-3 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Policy Content */}
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-2 block">
                  Policy YAML Content *
                </label>
                <textarea
                  value={newPolicy.content}
                  onChange={(e) => setNewPolicy(prev => ({ ...prev, content: e.target.value }))}
                  rows={20}
                  className="w-full px-3 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  placeholder="Enter your policy YAML configuration..."
                />
              </div>

              {/* Options */}
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="activate"
                  checked={newPolicy.activate}
                  onChange={(e) => setNewPolicy(prev => ({ ...prev, activate: e.target.checked }))}
                  className="rounded border-border"
                />
                <label htmlFor="activate" className="text-sm">
                  Activate this policy immediately after creation
                </label>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3">
                <button
                  onClick={handleValidatePolicy}
                  disabled={validating || !newPolicy.content.trim()}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
                >
                  <FileText className="w-4 h-4" />
                  {validating ? 'Validating...' : 'Validate'}
                </button>
                
                <button
                  onClick={handleCreatePolicy}
                  disabled={creating || !newPolicy.content.trim() || !newPolicy.version.trim()}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  {creating ? 'Creating...' : 'Create Policy'}
                </button>
              </div>

              {/* Validation Result */}
              {validationResult && (
                <div className={`p-4 border rounded-lg ${
                  validationResult.is_valid 
                    ? 'border-green-200 bg-green-50' 
                    : 'border-red-200 bg-red-50'
                }`}>
                  <h3 className="font-medium mb-2">Validation Result</h3>
                  <p className="text-sm">
                    {validationResult.is_valid ? 'Policy is valid and ready to deploy.' : 'Policy contains errors and cannot be deployed.'}
                  </p>
                  {!validationResult.is_valid && (
                    <ul className="mt-2 text-sm text-red-600 list-disc list-inside">
                      {validationResult.errors.map((error: string, index: number) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  )}
                  <p className="text-sm mt-2">
                    <strong>Total Rules:</strong> {validationResult.rules_count}
                  </p>
                </div>
              )}

              {/* Create Result */}
              {createResult && (
                <div className={`p-4 border rounded-lg ${
                  createResult.success
                    ? 'border-green-200 bg-green-50'
                    : 'border-red-200 bg-red-50'
                }`}>
                  <h3 className="font-medium mb-2">Policy Creation Result</h3>
                  <p className="text-sm">
                    {createResult.success ? 'Policy created successfully!' : 'Failed to create policy.'}
                  </p>
                  {!createResult.success && (
                    <p className="text-sm text-red-600">
                      <strong>Message:</strong> {createResult.message}
                    </p>
                  )}
                  {!createResult.success && createResult.validation_errors && createResult.validation_errors.length > 0 && (
                    <div className="mt-2 text-sm text-red-600">
                      <strong>Validation Errors:</strong>
                      <ul className="list-disc list-inside">
                        {createResult.validation_errors.map((error: string, index: number) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {createResult.policy_id && (
                    <p className="text-sm mt-2">
                      <strong>Policy ID:</strong> {createResult.policy_id}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}