import { useEffect, useState } from 'react'
import { useAppStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import { Activity, Shield, Users, AlertTriangle } from 'lucide-react'

export default function Dashboard() {
  const { sessions, setSessions, policyInfo } = useAppStore()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalSessions: 0,
    activeSessions: 0,
    totalCalls: 0,
    deniedCalls: 0
  })

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true)
        
        // Load recent sessions
        const sessionsData = await apiClient.getSessions({ page: 1, page_size: 10 })
        setSessions(sessionsData.sessions)
        
        // Calculate stats
        const totalCalls = sessionsData.sessions.reduce((sum, s) => sum + s.total_calls, 0)
        const deniedCalls = sessionsData.sessions.reduce((sum, s) => sum + s.denied_calls, 0)
        
        setStats({
          totalSessions: sessionsData.total_count,
          activeSessions: sessionsData.sessions.filter(s => !s.end_time).length,
          totalCalls,
          deniedCalls
        })
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [setSessions])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Overview of AI agent policy enforcement</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Total Sessions</p>
              <p className="text-2xl font-bold">{stats.totalSessions}</p>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Active Sessions</p>
              <p className="text-2xl font-bold">{stats.activeSessions}</p>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center">
            <Shield className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Total Tool Calls</p>
              <p className="text-2xl font-bold">{stats.totalCalls}</p>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Denied Calls</p>
              <p className="text-2xl font-bold">{stats.deniedCalls}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Sessions */}
      <div className="bg-card border border-border rounded-lg">
        <div className="p-6 border-b border-border">
          <h2 className="text-xl font-semibold">Recent Sessions</h2>
        </div>
        <div className="p-6">
          {sessions.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">No sessions found</p>
          ) : (
            <div className="space-y-4">
              {sessions.slice(0, 5).map((session) => (
                <div key={session.session_id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                  <div>
                    <p className="font-medium font-mono text-sm">{session.session_id}</p>
                    <p className="text-sm text-muted-foreground">
                      {session.total_calls} calls • {session.allowed_calls} allowed • {session.denied_calls} denied
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">
                      {new Date(session.start_time).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Policy Info */}
      {policyInfo && (
        <div className="bg-card border border-border rounded-lg">
          <div className="p-6 border-b border-border">
            <h2 className="text-xl font-semibold">Current Policy</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Version</p>
                <p className="text-lg font-mono">{policyInfo.version}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Rules</p>
                <p className="text-lg">{policyInfo.rules_count}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Hash</p>
                <p className="text-lg font-mono text-muted-foreground">
                  {policyInfo.hash.substring(0, 8)}...
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 