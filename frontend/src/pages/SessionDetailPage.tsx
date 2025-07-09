import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiClient } from '@/lib/api'
import type { SessionLog, SessionSummary } from '@/lib/api'
import { ArrowLeft, Activity, Clock, Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

export default function SessionDetailPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const [logs, setLogs] = useState<SessionLog[]>([])
  const [summary, setSummary] = useState<SessionSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionId) return

    const loadSessionData = async () => {
      try {
        setLoading(true)
        setError(null)

        const [logsData, summaryData] = await Promise.all([
          apiClient.getSessionLogs(sessionId),
          apiClient.getSessionSummary(sessionId)
        ])

        setLogs(logsData)
        setSummary(summaryData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load session data')
        console.error('Failed to load session data:', err)
      } finally {
        setLoading(false)
      }
    }

    loadSessionData()
  }, [sessionId])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
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
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/sessions')}
            className="p-2 hover:bg-accent rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold">Session Details</h1>
            <p className="text-muted-foreground">Loading session data...</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading session details...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/sessions')}
            className="p-2 hover:bg-accent rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold">Session Details</h1>
            <p className="text-muted-foreground">Session ID: {sessionId}</p>
          </div>
        </div>
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="text-red-600 text-center">
            <p className="font-medium">Failed to load session data</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/sessions')}
          className="p-2 hover:bg-accent rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold">Session Details</h1>
          <p className="text-muted-foreground font-mono">{sessionId}</p>
        </div>
      </div>

      {/* Session Summary */}
      {summary && (
        <div className="bg-card border border-border rounded-lg">
          <div className="p-6 border-b border-border">
            <h2 className="text-xl font-semibold">Session Summary</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Started</p>
                <p className="text-lg">{formatDate(summary.start_time)}</p>
              </div>
              {summary.end_time && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Ended</p>
                  <p className="text-lg">{formatDate(summary.end_time)}</p>
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Calls</p>
                <p className="text-lg font-bold">{summary.total_calls}</p>
              </div>
              <div className="flex gap-4">
                <div>
                  <p className="text-sm font-medium text-green-600">Allowed</p>
                  <p className="text-lg font-bold text-green-600">{summary.allowed_calls}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-red-600">Denied</p>
                  <p className="text-lg font-bold text-red-600">{summary.denied_calls}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-yellow-600">Pending</p>
                  <p className="text-lg font-bold text-yellow-600">{summary.approved_calls}</p>
                </div>
              </div>
            </div>
            
            {(summary.agent_id || summary.user_id) && (
              <div className="mt-6 pt-6 border-t border-border">
                <div className="flex gap-6">
                  {summary.agent_id && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Agent ID</p>
                      <p className="font-mono">{summary.agent_id}</p>
                    </div>
                  )}
                  {summary.user_id && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">User ID</p>
                      <p className="font-mono">{summary.user_id}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Session Logs */}
      <div className="bg-card border border-border rounded-lg">
        <div className="p-6 border-b border-border">
          <h2 className="text-xl font-semibold">Tool Call Logs</h2>
        </div>
        <div className="divide-y divide-border">
          {logs.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <Activity className="w-12 h-12 mx-auto mb-4" />
              <p>No tool calls found for this session</p>
            </div>
          ) : (
            logs.map((log, index) => (
              <div key={log.id} className="p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    {getDecisionIcon(log.policy_decision)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-medium font-mono text-sm">{log.tool_name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getDecisionColor(log.policy_decision)}`}>
                        {log.policy_decision.toUpperCase()}
                      </span>
                      {log.policy_rule && (
                        <span className="text-xs text-muted-foreground">
                          Rule: {log.policy_rule}
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-muted-foreground mb-3">
                      {formatDate(log.timestamp)}
                      {log.execution_duration_ms && ` • ${log.execution_duration_ms}ms`}
                    </p>
                    
                    {/* Tool Arguments */}
                    <div className="mb-3">
                      <p className="text-sm font-medium text-muted-foreground mb-1">Arguments:</p>
                      <pre className="text-xs bg-accent p-3 rounded border overflow-x-auto">
                        {JSON.stringify(log.tool_args, null, 2)}
                      </pre>
                    </div>
                    
                    {/* Tool Result */}
                    {log.tool_result && (
                      <div className="mb-3">
                        <p className="text-sm font-medium text-muted-foreground mb-1">Result:</p>
                        <pre className="text-xs bg-accent p-3 rounded border overflow-x-auto">
                          {JSON.stringify(log.tool_result, null, 2)}
                        </pre>
                      </div>
                    )}
                    
                    {/* Error Message */}
                    {log.error_message && (
                      <div className="mb-3">
                        <p className="text-sm font-medium text-red-600 mb-1">Error:</p>
                        <p className="text-sm text-red-600 bg-red-50 p-3 rounded border border-red-200">
                          {log.error_message}
                        </p>
                      </div>
                    )}
                    
                    {/* Execution Status */}
                    {log.execution_status && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>Status: {log.execution_status}</span>
                        <span>Policy: {log.policy_version}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
} 