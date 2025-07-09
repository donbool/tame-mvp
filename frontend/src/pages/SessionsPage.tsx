import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAppStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import { 
  Activity, 
  Pause, 
  Play, 
  Filter, 
  Download, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  XCircle, 
  Eye, 
  Users, 
  Zap,
  History,
  Calendar,
  ChevronRight 
} from 'lucide-react'

interface LiveToolCall {
  id: string
  timestamp: string
  session_id: string
  agent_id?: string
  user_id?: string
  tool_name: string
  tool_args: Record<string, any>
  decision: 'allow' | 'deny' | 'approve'
  rule_name?: string
  reason: string
  execution_time_ms?: number
  status: 'pending' | 'executing' | 'completed' | 'failed'
}

interface RealtimeStats {
  total_calls_today: number
  active_sessions: number
  calls_per_minute: number
  violation_rate: number
  avg_response_time: number
}

export function SessionsPage() {
  const { sessions, setSessions, liveUpdates, setLiveUpdates } = useAppStore()
  const [activeTab, setActiveTab] = useState<'live' | 'history'>('live')
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const pageSize = 20

  // Live monitoring state
  const [toolCalls, setToolCalls] = useState<LiveToolCall[]>([])
  const [stats, setStats] = useState<RealtimeStats>({
    total_calls_today: 0,
    active_sessions: 0,
    calls_per_minute: 0,
    violation_rate: 0,
    avg_response_time: 0
  })
  const [filters, setFilters] = useState({
    decision: 'all',
    tool_name: '',
    agent_id: '',
    session_id: ''
  })
  const [isConnected, setIsConnected] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadSessions()
  }, [page])

  // Mock real-time data generation
  useEffect(() => {
    if (!liveUpdates || activeTab !== 'live') {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      setIsConnected(false)
      return
    }

    setIsConnected(true)

    // Simulate WebSocket connection
    intervalRef.current = setInterval(() => {
      generateMockToolCall()
      updateStats()
    }, 2000 + Math.random() * 3000) // Random interval between 2-5 seconds

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [liveUpdates, activeTab])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getSessions({ page, page_size: pageSize })
      setSessions(data.sessions)
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateMockToolCall = () => {
    const tools = ['search_web', 'read_file', 'write_file', 'delete_file', 'execute_command', 'send_email', 'get_weather', 'create_directory']
    const decisions = ['allow', 'deny', 'approve'] as const
    const agents = ['claude-assistant', 'gpt-agent', 'custom-agent', 'automation-bot']
    const users = ['user-123', 'admin-456', 'developer-789']

    const tool = tools[Math.floor(Math.random() * tools.length)]
    const adjustedDecision = Math.random() < 0.7 ? 'allow' : Math.random() < 0.8 ? 'deny' : 'approve'

    const newCall: LiveToolCall = {
      id: `call-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      session_id: `session-${Math.floor(Math.random() * 100)}`,
      agent_id: agents[Math.floor(Math.random() * agents.length)],
      user_id: users[Math.floor(Math.random() * users.length)],
      tool_name: tool,
      tool_args: generateMockArgs(tool),
      decision: adjustedDecision,
      rule_name: adjustedDecision === 'allow' ? 'Default Allow' : adjustedDecision === 'deny' ? 'Security Policy' : 'Approval Required',
      reason: getDecisionReason(tool, adjustedDecision),
      execution_time_ms: adjustedDecision === 'allow' ? Math.floor(Math.random() * 2000) + 100 : undefined,
      status: adjustedDecision === 'allow' ? 'completed' : adjustedDecision === 'deny' ? 'failed' : 'pending'
    }

    setToolCalls(prev => [newCall, ...prev.slice(0, 99)]) // Keep only last 100 calls

    // Auto-scroll to top when new call arrives
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0
    }
  }

  const generateMockArgs = (tool: string): Record<string, any> => {
    switch (tool) {
      case 'search_web':
        return { query: 'AI safety research' }
      case 'read_file':
        return { path: '/etc/hosts' }
      case 'write_file':
        return { path: '/tmp/output.txt', content: 'Hello world' }
      case 'delete_file':
        return { path: '/important/config.json' }
      case 'execute_command':
        return { command: 'ls -la' }
      case 'send_email':
        return { to: 'admin@company.com', subject: 'Alert' }
      case 'get_weather':
        return { location: 'San Francisco' }
      case 'create_directory':
        return { path: '/tmp/new_folder' }
      default:
        return {}
    }
  }

  const getDecisionReason = (tool: string, decision: string): string => {
    if (decision === 'allow') {
      return 'Tool allowed by default policy'
    } else if (decision === 'deny') {
      return tool.includes('delete') || tool.includes('execute') 
        ? 'Potentially dangerous operation blocked'
        : 'Access denied by security policy'
    } else {
      return 'Manual approval required for this operation'
    }
  }

  const updateStats = () => {
    setStats(prev => ({
      total_calls_today: prev.total_calls_today + 1,
      active_sessions: Math.floor(Math.random() * 20) + 5,
      calls_per_minute: Math.floor(Math.random() * 30) + 10,
      violation_rate: Math.random() * 0.15, // 0-15%
      avg_response_time: Math.floor(Math.random() * 500) + 100
    }))
  }

  const filteredCalls = toolCalls.filter(call => {
    if (filters.decision !== 'all' && call.decision !== filters.decision) return false
    if (filters.tool_name && !call.tool_name.toLowerCase().includes(filters.tool_name.toLowerCase())) return false
    if (filters.agent_id && !call.agent_id?.toLowerCase().includes(filters.agent_id.toLowerCase())) return false
    if (filters.session_id && !call.session_id.toLowerCase().includes(filters.session_id.toLowerCase())) return false
    return true
  })

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'allow':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'deny':
        return <XCircle className="w-4 h-4 text-red-600" />
      case 'approve':
        return <Clock className="w-4 h-4 text-yellow-600" />
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-600" />
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

  const exportData = () => {
    const dataToExport = activeTab === 'live' ? filteredCalls : sessions
    const dataStr = JSON.stringify(dataToExport, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `runlok-${activeTab}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Sessions</h1>
          <p className="text-muted-foreground">Monitor live activity and view session history</p>
        </div>
        <div className="flex items-center gap-3">
          {activeTab === 'live' && (
            <>
              <div className="flex items-center gap-2 text-sm">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
              <button
                onClick={() => setLiveUpdates(!liveUpdates)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
                  liveUpdates 
                    ? 'bg-red-600 text-white hover:bg-red-700' 
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {liveUpdates ? (
                  <>
                    <Pause className="w-4 h-4" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Start
                  </>
                )}
              </button>
            </>
          )}
          <button
            onClick={exportData}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('live')}
            className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'live'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
            }`}
          >
            <Activity className="w-4 h-4" />
            Live Activity
            {liveUpdates && activeTab === 'live' && (
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            )}
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'history'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
            }`}
          >
            <History className="w-4 h-4" />
            Session History
          </button>
        </nav>
      </div>

      {/* Live Activity Tab */}
      {activeTab === 'live' && (
        <div className="space-y-6">
          {/* Real-time Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div className="bg-card border border-border rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm text-muted-foreground">Calls Today</p>
                  <p className="text-xl font-bold">{stats.total_calls_today}</p>
                </div>
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-green-600" />
                <div>
                  <p className="text-sm text-muted-foreground">Active Sessions</p>
                  <p className="text-xl font-bold">{stats.active_sessions}</p>
                </div>
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-sm text-muted-foreground">Calls/min</p>
                  <p className="text-xl font-bold">{stats.calls_per_minute}</p>
                </div>
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <div>
                  <p className="text-sm text-muted-foreground">Violation Rate</p>
                  <p className="text-xl font-bold">{(stats.violation_rate * 100).toFixed(1)}%</p>
                </div>
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-orange-600" />
                <div>
                  <p className="text-sm text-muted-foreground">Avg Response</p>
                  <p className="text-xl font-bold">{stats.avg_response_time}ms</p>
                </div>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-3 mb-4">
              <Filter className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold">Filters</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Decision</label>
                <select
                  value={filters.decision}
                  onChange={(e) => setFilters(prev => ({ ...prev, decision: e.target.value }))}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                >
                  <option value="all">All Decisions</option>
                  <option value="allow">Allow</option>
                  <option value="deny">Deny</option>
                  <option value="approve">Approve</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Tool Name</label>
                <input
                  type="text"
                  value={filters.tool_name}
                  onChange={(e) => setFilters(prev => ({ ...prev, tool_name: e.target.value }))}
                  placeholder="Filter by tool name..."
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Agent ID</label>
                <input
                  type="text"
                  value={filters.agent_id}
                  onChange={(e) => setFilters(prev => ({ ...prev, agent_id: e.target.value }))}
                  placeholder="Filter by agent..."
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Session ID</label>
                <input
                  type="text"
                  value={filters.session_id}
                  onChange={(e) => setFilters(prev => ({ ...prev, session_id: e.target.value }))}
                  placeholder="Filter by session..."
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                />
              </div>
            </div>

            <div className="mt-4 text-sm text-muted-foreground">
              Showing {filteredCalls.length} of {toolCalls.length} tool calls
            </div>
          </div>

          {/* Live Tool Calls */}
          <div className="bg-card border border-border rounded-lg">
            <div className="p-4 border-b border-border">
              <div className="flex items-center gap-2">
                <Eye className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-semibold">Live Tool Calls</h2>
                {liveUpdates && (
                  <Activity className="w-4 h-4 text-green-600 animate-pulse" />
                )}
              </div>
            </div>

            <div 
              ref={scrollRef}
              className="max-h-96 overflow-y-auto"
            >
              {filteredCalls.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground">
                  {toolCalls.length === 0 ? (
                    liveUpdates ? 'Waiting for tool calls...' : 'Start monitoring to see live tool calls'
                  ) : (
                    'No tool calls match the current filters'
                  )}
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {filteredCalls.map((call) => (
                    <div key={call.id} className="p-4 hover:bg-accent/50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            {getDecisionIcon(call.decision)}
                            <span className="font-medium font-mono text-sm">{call.tool_name}</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getDecisionColor(call.decision)}`}>
                              {call.decision.toUpperCase()}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {formatTimestamp(call.timestamp)}
                            </span>
                          </div>
                          
                          <div className="text-sm text-muted-foreground mb-2">
                            <strong>Session:</strong> {call.session_id} • 
                            <strong> Agent:</strong> {call.agent_id} • 
                            <strong> User:</strong> {call.user_id}
                          </div>
                          
                          <div className="text-sm text-muted-foreground mb-2">
                            <strong>Reason:</strong> {call.reason}
                            {call.rule_name && (
                              <span> • <strong>Rule:</strong> {call.rule_name}</span>
                            )}
                          </div>
                          
                          <div className="text-xs text-muted-foreground">
                            <strong>Args:</strong> {JSON.stringify(call.tool_args)}
                          </div>
                          
                          {call.execution_time_ms && (
                            <div className="text-xs text-muted-foreground mt-1">
                              <strong>Execution time:</strong> {call.execution_time_ms}ms
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Session History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-muted-foreground">Loading sessions...</div>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-lg">
              <div className="p-6 border-b border-border">
                <h2 className="text-xl font-semibold">Session History</h2>
              </div>
              <div className="divide-y divide-border">
                {sessions.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground">
                    No sessions found
                  </div>
                ) : (
                  sessions.map((session) => (
                    <Link
                      key={session.session_id}
                      to={`/sessions/${session.session_id}`}
                      className="block p-6 hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <Calendar className="w-4 h-4 text-muted-foreground" />
                            <h3 className="font-medium font-mono text-sm">{session.session_id}</h3>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              session.end_time 
                                ? 'text-gray-600 bg-gray-50 border border-gray-200' 
                                : 'text-green-600 bg-green-50 border border-green-200'
                            }`}>
                              {session.end_time ? 'Completed' : 'Active'}
                            </span>
                          </div>
                          
                          <div className="flex items-center gap-6 text-sm text-muted-foreground mb-2">
                            <span>Started: {formatDate(session.start_time)}</span>
                            {session.end_time && (
                              <span>Ended: {formatDate(session.end_time)}</span>
                            )}
                          </div>
                          
                          <div className="flex items-center gap-6 text-sm">
                            <span className="text-blue-600">
                              <strong>{session.total_calls}</strong> total calls
                            </span>
                            <span className="text-green-600">
                              <strong>{session.allowed_calls}</strong> allowed
                            </span>
                            <span className="text-red-600">
                              <strong>{session.denied_calls}</strong> denied
                            </span>
                            <span className="text-yellow-600">
                              <strong>{session.approved_calls}</strong> approved
                            </span>
                          </div>
                          
                          {(session.agent_id || session.user_id) && (
                            <div className="mt-2 flex items-center gap-6 text-xs text-muted-foreground">
                              {session.agent_id && (
                                <span><strong>Agent:</strong> {session.agent_id}</span>
                              )}
                              {session.user_id && (
                                <span><strong>User:</strong> {session.user_id}</span>
                              )}
                            </div>
                          )}
                        </div>
                        <ChevronRight className="w-5 h-5 text-muted-foreground" />
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
} 