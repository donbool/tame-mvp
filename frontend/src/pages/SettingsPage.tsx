import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Save, RefreshCw, AlertTriangle, CheckCircle, Settings as SettingsIcon, Bell, Server, Shield, Eye } from 'lucide-react'

interface SystemSettings {
  api_configuration: {
    base_url: string
    timeout: number
    rate_limit: number
    max_retries: number
  }
  policy_settings: {
    default_action: string
    strict_mode: boolean
    auto_reload: boolean
    validation_enabled: boolean
  }
  notification_settings: {
    slack_webhook_url: string
    email_notifications: boolean
    violation_alerts: boolean
    approval_alerts: boolean
  }
  monitoring_settings: {
    real_time_updates: boolean
    session_timeout: number
    log_retention_days: number
    performance_monitoring: boolean
  }
  security_settings: {
    require_api_key: boolean
    enable_cors: boolean
    allowed_origins: string[]
    enable_audit_log: boolean
  }
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      setError(null)
      // For now, mock the settings since we don't have backend endpoint yet
      const mockSettings: SystemSettings = {
        api_configuration: {
          base_url: "http://localhost:8000",
          timeout: 30,
          rate_limit: 100,
          max_retries: 3
        },
        policy_settings: {
          default_action: "deny",
          strict_mode: true,
          auto_reload: true,
          validation_enabled: true
        },
        notification_settings: {
          slack_webhook_url: "",
          email_notifications: false,
          violation_alerts: true,
          approval_alerts: true
        },
        monitoring_settings: {
          real_time_updates: true,
          session_timeout: 3600,
          log_retention_days: 90,
          performance_monitoring: true
        },
        security_settings: {
          require_api_key: false,
          enable_cors: true,
          allowed_origins: ["*"],
          enable_audit_log: true
        }
      }
      
      // In production, this would be:
      // const response = await apiClient.get('/api/v1/settings')
      // setSettings(response.data)
      
      setTimeout(() => {
        setSettings(mockSettings)
        setLoading(false)
      }, 500)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings')
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    if (!settings) return

    try {
      setSaving(true)
      setSaveStatus('idle')
      
      // In production, this would be:
      // await apiClient.put('/api/v1/settings', settings)
      
      // Mock save delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setSaveStatus('success')
      setTimeout(() => setSaveStatus('idle'), 3000)
      
    } catch (err) {
      setSaveStatus('error')
      setError(err instanceof Error ? err.message : 'Failed to save settings')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } finally {
      setSaving(false)
    }
  }

  const updateSettings = (section: keyof SystemSettings, key: string, value: any) => {
    if (!settings) return
    
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [key]: value
      }
    })
  }

  const testSlackWebhook = async () => {
    if (!settings?.notification_settings.slack_webhook_url) {
      alert('Please enter a Slack webhook URL first')
      return
    }

    try {
      // Mock webhook test
      const response = await fetch(settings.notification_settings.slack_webhook_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: '🔒 Runlok test notification: Policy enforcement system is working!',
          username: 'Runlok',
          icon_emoji: ':shield:'
        })
      })

      if (response.ok) {
        alert('✅ Slack webhook test successful!')
      } else {
        alert('❌ Slack webhook test failed: ' + response.statusText)
      }
    } catch (error) {
      alert('❌ Slack webhook test failed: ' + (error instanceof Error ? error.message : 'Network error'))
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Configure system settings and preferences</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading settings...</div>
        </div>
      </div>
    )
  }

  if (error && !settings) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Configure system settings and preferences</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="text-red-600 text-center">
            <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
            <p className="font-medium">Failed to load settings</p>
            <p className="text-sm mt-1">{error}</p>
            <button 
              onClick={loadSettings}
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
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Configure system settings and preferences</p>
        </div>
        <div className="flex items-center gap-2">
          {saveStatus === 'success' && (
            <div className="flex items-center gap-1 text-green-600">
              <CheckCircle className="w-4 h-4" />
              Saved
            </div>
          )}
          {saveStatus === 'error' && (
            <div className="flex items-center gap-1 text-red-600">
              <AlertTriangle className="w-4 h-4" />
              Error
            </div>
          )}
          <button
            onClick={saveSettings}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {settings && (
        <div className="space-y-6">
          {/* API Configuration */}
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Server className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-semibold">API Configuration</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Base URL</label>
                <input
                  type="url"
                  value={settings.api_configuration.base_url}
                  onChange={(e) => updateSettings('api_configuration', 'base_url', e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                  placeholder="http://localhost:8000"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Timeout (seconds)</label>
                <input
                  type="number"
                  value={settings.api_configuration.timeout}
                  onChange={(e) => updateSettings('api_configuration', 'timeout', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                  min="1"
                  max="300"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Rate Limit (req/min)</label>
                <input
                  type="number"
                  value={settings.api_configuration.rate_limit}
                  onChange={(e) => updateSettings('api_configuration', 'rate_limit', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                  min="1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Max Retries</label>
                <input
                  type="number"
                  value={settings.api_configuration.max_retries}
                  onChange={(e) => updateSettings('api_configuration', 'max_retries', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                  min="0"
                  max="10"
                />
              </div>
            </div>
          </div>

          {/* Policy Settings */}
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-5 h-5 text-green-600" />
              <h2 className="text-xl font-semibold">Policy Settings</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Default Action</label>
                <select
                  value={settings.policy_settings.default_action}
                  onChange={(e) => updateSettings('policy_settings', 'default_action', e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                >
                  <option value="allow">Allow</option>
                  <option value="deny">Deny</option>
                  <option value="approve">Require Approval</option>
                </select>
                <p className="text-xs text-muted-foreground mt-1">
                  Default action when no specific policy rule matches
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.policy_settings.strict_mode}
                    onChange={(e) => updateSettings('policy_settings', 'strict_mode', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Strict Mode</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.policy_settings.auto_reload}
                    onChange={(e) => updateSettings('policy_settings', 'auto_reload', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Auto-reload Policies</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.policy_settings.validation_enabled}
                    onChange={(e) => updateSettings('policy_settings', 'validation_enabled', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Policy Validation</span>
                </label>
              </div>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Bell className="w-5 h-5 text-orange-600" />
              <h2 className="text-xl font-semibold">Notifications</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Slack Webhook URL</label>
                <div className="flex gap-2">
                  <input
                    type="url"
                    value={settings.notification_settings.slack_webhook_url}
                    onChange={(e) => updateSettings('notification_settings', 'slack_webhook_url', e.target.value)}
                    className="flex-1 px-3 py-2 border border-border rounded-md bg-background"
                    placeholder="https://hooks.slack.com/services/..."
                  />
                  <button
                    onClick={testSlackWebhook}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Test
                  </button>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Configure Slack webhook for policy violation alerts
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.notification_settings.email_notifications}
                    onChange={(e) => updateSettings('notification_settings', 'email_notifications', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Email Notifications</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.notification_settings.violation_alerts}
                    onChange={(e) => updateSettings('notification_settings', 'violation_alerts', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Policy Violation Alerts</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.notification_settings.approval_alerts}
                    onChange={(e) => updateSettings('notification_settings', 'approval_alerts', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Approval Required Alerts</span>
                </label>
              </div>
            </div>
          </div>

          {/* Monitoring Settings */}
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Eye className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-semibold">Monitoring</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Session Timeout (seconds)</label>
                  <input
                    type="number"
                    value={settings.monitoring_settings.session_timeout}
                    onChange={(e) => updateSettings('monitoring_settings', 'session_timeout', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-border rounded-md bg-background"
                    min="60"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Log Retention (days)</label>
                  <input
                    type="number"
                    value={settings.monitoring_settings.log_retention_days}
                    onChange={(e) => updateSettings('monitoring_settings', 'log_retention_days', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-border rounded-md bg-background"
                    min="1"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.monitoring_settings.real_time_updates}
                    onChange={(e) => updateSettings('monitoring_settings', 'real_time_updates', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Real-time Updates</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.monitoring_settings.performance_monitoring}
                    onChange={(e) => updateSettings('monitoring_settings', 'performance_monitoring', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Performance Monitoring</span>
                </label>
              </div>
            </div>
          </div>

          {/* Security Settings */}
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <SettingsIcon className="w-5 h-5 text-red-600" />
              <h2 className="text-xl font-semibold">Security</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Allowed Origins (CORS)</label>
                <textarea
                  value={settings.security_settings.allowed_origins.join('\n')}
                  onChange={(e) => updateSettings('security_settings', 'allowed_origins', e.target.value.split('\n').filter(Boolean))}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                  rows={3}
                  placeholder="*&#10;https://yourdomain.com&#10;http://localhost:3000"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  One origin per line. Use * for all origins (not recommended for production)
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.security_settings.require_api_key}
                    onChange={(e) => updateSettings('security_settings', 'require_api_key', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Require API Key</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.security_settings.enable_cors}
                    onChange={(e) => updateSettings('security_settings', 'enable_cors', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Enable CORS</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.security_settings.enable_audit_log}
                    onChange={(e) => updateSettings('security_settings', 'enable_audit_log', e.target.checked)}
                    className="rounded border-border"
                  />
                  <span className="text-sm">Enable Audit Log</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 