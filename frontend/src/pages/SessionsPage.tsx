import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../lib/api';

interface Session {
  session_id: string;
  start_time: string;
  end_time?: string;
  total_calls: number;
  allowed_calls: number;
  denied_calls: number;
  approved_calls: number;
  agent_id?: string;
  user_id?: string;
  is_archived?: boolean;
  archived_at?: string;
}

export function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedSessions, setSelectedSessions] = useState<string[]>([]);
  const [showArchived, setShowArchived] = useState(false);
  const [agentFilter, setAgentFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadSessions();
  }, [page, showArchived, agentFilter]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '50',
        include_archived: showArchived.toString()
      });
      
      if (agentFilter) {
        params.append('agent_id', agentFilter);
      }

      const response = await apiClient.get(`/sessions?${params}`);
      setSessions(response.data.sessions || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSession = (sessionId: string) => {
    setSelectedSessions(prev => 
      prev.includes(sessionId) 
        ? prev.filter(id => id !== sessionId)
        : [...prev, sessionId]
    );
  };

  const handleSelectAll = () => {
    if (selectedSessions.length === sessions.length) {
      setSelectedSessions([]);
    } else {
      setSelectedSessions(sessions.map(s => s.session_id));
    }
  };

  const handleArchiveSelected = async () => {
    if (selectedSessions.length === 0) return;
    
    try {
      const response = await apiClient.post('/sessions/bulk/archive', {
        session_ids: selectedSessions,
        archived_by: 'admin_user', // Should come from auth context
        retention_days: 2555 // ~7 years for EU AI Act compliance
      });
      
      alert(`Archived ${response.data.logs_archived} logs from ${selectedSessions.length} sessions`);
      setSelectedSessions([]);
      loadSessions();
    } catch (error) {
      console.error('Failed to archive sessions:', error);
      alert('Failed to archive sessions');
    }
  };

  const handleExportData = async (format: 'json' | 'csv') => {
    try {
      const params = new URLSearchParams({
        format,
        include_archived: showArchived.toString()
      });
      
      if (agentFilter) {
        params.append('agent_id', agentFilter);
      }

      const response = await fetch(`/api/v1/sessions/export?${params}`);
      
      if (format === 'csv') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sessions_export.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sessions_export.json';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
      
      alert('Export completed successfully');
    } catch (error) {
      console.error('Failed to export data:', error);
      alert('Failed to export data');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (session: Session) => {
    if (session.is_archived) return 'text-gray-500';
    if (session.denied_calls > 0) return 'text-red-600';
    if (session.approved_calls > 0) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getStatusText = (session: Session) => {
    if (session.is_archived) return 'Archived';
    if (session.denied_calls > 0) return 'Has Denials';
    if (session.approved_calls > 0) return 'Needs Approval';
    return 'All Allowed';
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Agent Sessions</h1>
        <div className="flex gap-4">
          <button
            onClick={() => handleExportData('csv')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Export CSV
          </button>
          <button
            onClick={() => handleExportData('json')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Export JSON
          </button>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showArchived}
              onChange={(e) => setShowArchived(e.target.checked)}
              className="mr-2"
            />
            Show Archived Sessions
          </label>
          
          <div className="flex items-center gap-2">
            <label>Filter by Agent:</label>
            <input
              type="text"
              value={agentFilter}
              onChange={(e) => setAgentFilter(e.target.value)}
              placeholder="Agent ID"
              className="px-3 py-1 border border-gray-300 rounded"
            />
          </div>

          {selectedSessions.length > 0 && (
            <div className="flex gap-2">
              <span className="text-sm text-gray-600">
                {selectedSessions.length} selected
              </span>
              <button
                onClick={handleArchiveSelected}
                className="px-3 py-1 bg-orange-600 text-white text-sm rounded hover:bg-orange-700"
              >
                Archive Selected
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Sessions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-4">
                <input
                  type="checkbox"
                  checked={selectedSessions.length === sessions.length && sessions.length > 0}
                  onChange={handleSelectAll}
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Session ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Agent
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Start Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Calls
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sessions.map((session) => (
              <tr
                key={session.session_id}
                className={`hover:bg-gray-50 ${session.is_archived ? 'opacity-60' : ''}`}
              >
                <td className="p-4">
                  <input
                    type="checkbox"
                    checked={selectedSessions.includes(session.session_id)}
                    onChange={() => handleSelectSession(session.session_id)}
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {session.session_id.substring(0, 20)}...
                  </div>
                  {session.user_id && (
                    <div className="text-sm text-gray-500">User: {session.user_id}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {session.agent_id || 'Unknown'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {formatDate(session.start_time)}
                  </div>
                  {session.end_time && (
                    <div className="text-sm text-gray-500">
                      Ended: {formatDate(session.end_time)}
                    </div>
                  )}
                  {session.archived_at && (
                    <div className="text-sm text-orange-600">
                      Archived: {formatDate(session.archived_at)}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    Total: {session.total_calls}
                  </div>
                  <div className="text-sm">
                    <span className="text-green-600">✓ {session.allowed_calls}</span>
                    {session.denied_calls > 0 && (
                      <span className="text-red-600 ml-2">✗ {session.denied_calls}</span>
                    )}
                    {session.approved_calls > 0 && (
                      <span className="text-yellow-600 ml-2">⏳ {session.approved_calls}</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`text-sm font-medium ${getStatusColor(session)}`}>
                    {getStatusText(session)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => navigate(`/sessions/${session.session_id}`)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    View Details
                  </button>
                  {!session.is_archived && (
                    <button
                      onClick={async () => {
                        if (confirm('Archive this session?')) {
                          try {
                            await apiClient.post(`/sessions/${session.session_id}/archive`, {
                              archived_by: 'admin_user'
                            });
                            loadSessions();
                          } catch (error) {
                            alert('Failed to archive session');
                          }
                        }
                      }}
                      className="text-orange-600 hover:text-orange-900"
                    >
                      Archive
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex justify-center">
          <div className="flex gap-2">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-4 py-2">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page === totalPages}
              className="px-4 py-2 border border-gray-300 rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Compliance Info */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">EU AI Act Compliance</h3>
        <div className="text-sm text-blue-800">
          <p>• Sessions are automatically archived after completion</p>
          <p>• Data retention: 7 years for compliance (configurable)</p>
          <p>• All tool decisions are logged with HMAC signatures</p>
          <p>• Export functionality available for auditing</p>
        </div>
      </div>
    </div>
  );
} 