import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import type { PolicyInfo } from '@/lib/api'
import { Shield, CheckCircle, XCircle, Clock, AlertTriangle, RefreshCw } from 'lucide-react'

export default function PolicyPage() {
  const [policyInfo, setPolicyInfo] = useState<PolicyInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [testResult, setTestResult] = useState<any>(null)
  const [testLoading, setTestLoading] = useState(false)
  const [testToolName, setTestToolName] = useState('search_web')
  const [testArgs, setTestArgs] = useState('{"query": "test"}')

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
        <button
          onClick={loadPolicyInfo}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

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
  )
} 