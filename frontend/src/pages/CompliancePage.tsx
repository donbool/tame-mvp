import React, { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';

interface ComplianceReport {
  report_metadata: {
    generated_at: string;
    period_start: string;
    period_end: string;
    total_audit_events: number;
    total_ai_decisions: number;
  };
  ai_system_usage: {
    total_tool_calls: number;
    allowed_calls: number;
    denied_calls: number;
    approval_required: number;
    unique_agents: number;
    unique_users: number;
  };
  risk_assessment: {
    high_risk_events: number;
    policy_violations: number;
    data_exports: number;
    unauthorized_access_attempts: number;
  };
  data_governance: {
    archived_sessions: number;
    retention_compliance: {
      overdue_deletions: number;
      retention_policy_compliant: boolean;
    };
    data_integrity_status: {
      chain_intact: boolean;
      integrity_violations: number;
    };
  };
  eu_ai_act_compliance: {
    assessment_date: string;
    compliance_status: string;
    system_classification: string;
    audit_trail_verified: boolean;
  };
}

interface RetentionStatus {
  retention_compliance: {
    upcoming_deletions: number;
    overdue_deletions: number;
    archived_sessions: number;
    compliance_status: string;
  };
  upcoming_actions: Array<{
    session_id: string;
    retention_until: string;
    days_remaining: number;
    agent_id: string;
  }>;
  overdue_actions: Array<{
    session_id: string;
    retention_until: string;
    days_overdue: number;
    agent_id: string;
  }>;
}

export function CompliancePage() {
  const [report, setReport] = useState<ComplianceReport | null>(null);
  const [retentionStatus, setRetentionStatus] = useState<RetentionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [reportPeriod, setReportPeriod] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadComplianceData();
  }, []);

  const loadComplianceData = async () => {
    try {
      setLoading(true);
      
      // Load compliance report
      const reportResponse = await apiClient.post('/compliance/report/generate', {
        start_date: reportPeriod.start_date + 'T00:00:00Z',
        end_date: reportPeriod.end_date + 'T23:59:59Z',
        report_type: 'summary'
      });
      setReport(reportResponse.data);

      // Load retention status
      const retentionResponse = await apiClient.get('/compliance/retention/status');
      setRetentionStatus(retentionResponse.data);
      
    } catch (error) {
      console.error('Failed to load compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateFullReport = async () => {
    try {
      const response = await apiClient.post('/compliance/report/generate', {
        start_date: reportPeriod.start_date + 'T00:00:00Z',
        end_date: reportPeriod.end_date + 'T23:59:59Z',
        report_type: 'detailed'
      });
      
      // Download the report
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `compliance_report_${reportPeriod.start_date}_${reportPeriod.end_date}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert('Detailed compliance report downloaded');
    } catch (error) {
      console.error('Failed to generate detailed report:', error);
      alert('Failed to generate detailed report');
    }
  };

  const verifyAuditIntegrity = async () => {
    try {
      const response = await apiClient.get(`/compliance/integrity/verify?start_date=${reportPeriod.start_date}T00:00:00Z&end_date=${reportPeriod.end_date}T23:59:59Z`);
      
      const status = response.data.integrity_verification;
      const message = status.chain_intact 
        ? `✅ Audit log integrity verified. ${status.total_entries_verified} entries checked, no violations found.`
        : `❌ Audit log integrity compromised! ${status.integrity_violations} violations found in ${status.total_entries_verified} entries.`;
      
      alert(message);
    } catch (error) {
      console.error('Failed to verify audit integrity:', error);
      alert('Failed to verify audit integrity');
    }
  };

  const cleanupExpiredData = async (dryRun: boolean) => {
    try {
      const response = await apiClient.post(`/compliance/retention/cleanup?dry_run=${dryRun}`);
      
      if (dryRun) {
        alert(`Dry run: Would delete ${response.data.would_delete} expired session logs`);
      } else {
        alert(`Cleanup completed: Deleted ${response.data.deleted_count} expired session logs`);
        loadComplianceData(); // Reload data
      }
    } catch (error) {
      console.error('Failed to cleanup expired data:', error);
      alert('Failed to cleanup expired data');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">EU AI Act Compliance Dashboard</h1>
        <div className="flex gap-2">
          <button
            onClick={generateFullReport}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Generate Report
          </button>
          <button
            onClick={verifyAuditIntegrity}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Verify Integrity
          </button>
        </div>
      </div>

      {/* Report Period Selector */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex gap-4 items-center">
          <label className="text-sm font-medium">Report Period:</label>
          <input
            type="date"
            value={reportPeriod.start_date}
            onChange={(e) => setReportPeriod(prev => ({ ...prev, start_date: e.target.value }))}
            className="px-3 py-1 border border-gray-300 rounded"
          />
          <span>to</span>
          <input
            type="date"
            value={reportPeriod.end_date}
            onChange={(e) => setReportPeriod(prev => ({ ...prev, end_date: e.target.value }))}
            className="px-3 py-1 border border-gray-300 rounded"
          />
          <button
            onClick={loadComplianceData}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Update Report
          </button>
        </div>
      </div>

      {report && (
        <>
          {/* Compliance Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">Compliance Status</h3>
              <div className="text-2xl font-bold text-green-600">
                {report.eu_ai_act_compliance.compliance_status.toUpperCase()}
              </div>
              <p className="text-sm text-gray-600">
                Classification: {report.eu_ai_act_compliance.system_classification}
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">Total AI Decisions</h3>
              <div className="text-2xl font-bold text-blue-600">
                {report.ai_system_usage.total_tool_calls.toLocaleString()}
              </div>
              <p className="text-sm text-gray-600">
                Across {report.ai_system_usage.unique_agents} agents
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">Policy Violations</h3>
              <div className="text-2xl font-bold text-red-600">
                {report.risk_assessment.policy_violations}
              </div>
              <p className="text-sm text-gray-600">
                Denied actions
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">Data Integrity</h3>
              <div className={`text-2xl font-bold ${report.data_governance.data_integrity_status.chain_intact ? 'text-green-600' : 'text-red-600'}`}>
                {report.data_governance.data_integrity_status.chain_intact ? '✅ INTACT' : '❌ COMPROMISED'}
              </div>
              <p className="text-sm text-gray-600">
                Audit trail status
              </p>
            </div>
          </div>

          {/* Detailed Statistics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">AI System Usage</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Allowed Actions:</span>
                  <span className="font-medium text-green-600">{report.ai_system_usage.allowed_calls}</span>
                </div>
                <div className="flex justify-between">
                  <span>Denied Actions:</span>
                  <span className="font-medium text-red-600">{report.ai_system_usage.denied_calls}</span>
                </div>
                <div className="flex justify-between">
                  <span>Approval Required:</span>
                  <span className="font-medium text-yellow-600">{report.ai_system_usage.approval_required}</span>
                </div>
                <div className="flex justify-between">
                  <span>Unique Users:</span>
                  <span className="font-medium">{report.ai_system_usage.unique_users}</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Risk Assessment</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>High Risk Events:</span>
                  <span className="font-medium text-red-600">{report.risk_assessment.high_risk_events}</span>
                </div>
                <div className="flex justify-between">
                  <span>Data Exports:</span>
                  <span className="font-medium">{report.risk_assessment.data_exports}</span>
                </div>
                <div className="flex justify-between">
                  <span>Unauthorized Access:</span>
                  <span className="font-medium text-red-600">{report.risk_assessment.unauthorized_access_attempts}</span>
                </div>
                <div className="flex justify-between">
                  <span>Total Audit Events:</span>
                  <span className="font-medium">{report.report_metadata.total_audit_events}</span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Data Retention Status */}
      {retentionStatus && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Data Retention Compliance</h3>
            <div className="flex gap-2">
              <button
                onClick={() => cleanupExpiredData(true)}
                className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
              >
                Preview Cleanup
              </button>
              {retentionStatus.retention_compliance.overdue_deletions > 0 && (
                <button
                  onClick={() => {
                    if (confirm('This will permanently delete expired data. Continue?')) {
                      cleanupExpiredData(false);
                    }
                  }}
                  className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                >
                  Run Cleanup
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {retentionStatus.retention_compliance.archived_sessions}
              </div>
              <div className="text-sm text-gray-600">Archived Sessions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {retentionStatus.retention_compliance.upcoming_deletions}
              </div>
              <div className="text-sm text-gray-600">Upcoming Deletions</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${retentionStatus.retention_compliance.overdue_deletions > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {retentionStatus.retention_compliance.overdue_deletions}
              </div>
              <div className="text-sm text-gray-600">Overdue Deletions</div>
            </div>
          </div>

          <div className={`p-3 rounded ${retentionStatus.retention_compliance.compliance_status === 'compliant' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            <strong>Status:</strong> {retentionStatus.retention_compliance.compliance_status === 'compliant' ? 'Compliant with retention policies' : 'Non-compliant - action required'}
          </div>

          {/* Upcoming Actions */}
          {retentionStatus.upcoming_actions.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Upcoming Retention Actions:</h4>
              <div className="space-y-2">
                {retentionStatus.upcoming_actions.slice(0, 5).map((action, index) => (
                  <div key={index} className="flex justify-between items-center text-sm p-2 bg-yellow-50 rounded">
                    <span>{action.session_id.substring(0, 20)}... ({action.agent_id})</span>
                    <span className="text-yellow-600">{action.days_remaining} days remaining</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Overdue Actions */}
          {retentionStatus.overdue_actions.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Overdue Actions (Compliance Risk):</h4>
              <div className="space-y-2">
                {retentionStatus.overdue_actions.slice(0, 5).map((action, index) => (
                  <div key={index} className="flex justify-between items-center text-sm p-2 bg-red-50 rounded">
                    <span>{action.session_id.substring(0, 20)}... ({action.agent_id})</span>
                    <span className="text-red-600">{action.days_overdue} days overdue</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* EU AI Act Information */}
      <div className="bg-blue-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">EU AI Act Compliance Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h4 className="font-medium mb-2">Logging & Audit:</h4>
            <ul className="space-y-1">
              <li>• Comprehensive tool call logging</li>
              <li>• HMAC signature verification</li>
              <li>• Immutable audit trail</li>
              <li>• Policy decision tracking</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Data Governance:</h4>
            <ul className="space-y-1">
              <li>• Automated data retention</li>
              <li>• Secure archiving system</li>
              <li>• Export for regulatory reporting</li>
              <li>• GDPR compliance ready</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 