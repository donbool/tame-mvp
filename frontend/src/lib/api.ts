// Always use relative paths in browser to utilize Vite proxy
const API_BASE_URL = '/api/v1'

export interface SessionLog {
  id: string
  session_id: string
  timestamp: string
  tool_name: string
  tool_args: Record<string, any>
  tool_result?: Record<string, any>
  policy_version: string
  policy_decision: string
  policy_rule?: string
  execution_status?: string
  execution_duration_ms?: string
  error_message?: string
  agent_id?: string
  user_id?: string
}

export interface SessionSummary {
  session_id: string
  start_time: string
  end_time?: string
  total_calls: number
  allowed_calls: number
  denied_calls: number
  approved_calls: number
  agent_id?: string
  user_id?: string
}

export interface PolicyInfo {
  version: string
  hash: string
  rules_count: number
  rules: Array<{
    name: string
    action: string
    tools: string[]
    description?: string
  }>
}

export interface ApiResponse<T> {
  data: T
  error?: string
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Sessions API
  async getSessions(params: {
    page?: number
    page_size?: number
    agent_id?: string
    user_id?: string
  } = {}): Promise<{
    sessions: SessionSummary[]
    total_count: number
    page: number
    page_size: number
  }> {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value))
      }
    })

    const endpoint = `/sessions?${searchParams.toString()}`
    return this.request(endpoint)
  }

  async getSessionLogs(sessionId: string): Promise<SessionLog[]> {
    return this.request(`/sessions/${sessionId}`)
  }

  async getSessionSummary(sessionId: string): Promise<SessionSummary> {
    return this.request(`/sessions/${sessionId}/summary`)
  }

  async deleteSession(sessionId: string): Promise<{ status: string; logs_deleted: number }> {
    return this.request(`/sessions/${sessionId}`, {
      method: 'DELETE',
    })
  }

  // Policy API
  async getPolicyInfo(): Promise<PolicyInfo> {
    return this.request('/policy/current')
  }

  async testPolicy(params: {
    tool_name: string
    tool_args?: Record<string, any>
    session_context?: Record<string, any>
  }): Promise<{
    tool_name: string
    tool_args: Record<string, any>
    session_context: Record<string, any>
    decision: {
      action: string
      rule_name?: string
      reason: string
      policy_version: string
    }
  }> {
    const searchParams = new URLSearchParams()
    searchParams.append('tool_name', params.tool_name)
    
    if (params.tool_args) {
      searchParams.append('tool_args', JSON.stringify(params.tool_args))
    }
    
    if (params.session_context) {
      searchParams.append('session_context', JSON.stringify(params.session_context))
    }

    return this.request(`/policy/test?${searchParams.toString()}`)
  }

  async validatePolicy(policyContent: string, description?: string): Promise<{
    is_valid: boolean
    errors: string[]
    rules_count: number
    version?: string
  }> {
    return this.request('/policy/validate', {
      method: 'POST',
      body: JSON.stringify({
        policy_content: policyContent,
        description,
      }),
    })
  }

  async reloadPolicy(): Promise<{
    status: string
    old_version: string
    new_version: string
    rules_count: number
  }> {
    return this.request('/policy/reload', {
      method: 'POST',
    })
  }

  async createPolicy(params: {
    policy_content: string
    version: string
    description?: string
    activate?: boolean
  }): Promise<{
    success: boolean
    policy_id: string
    version: string
    message: string
    validation_errors: string[]
  }> {
    return this.request('/policy/create', {
      method: 'POST',
      body: JSON.stringify({
        policy_content: params.policy_content,
        version: params.version,
        description: params.description,
        activate: params.activate ?? true,
      }),
    })
  }

  // Enforcement API
  async enforceToolCall(params: {
    tool_name: string
    tool_args: Record<string, any>
    session_id?: string
    agent_id?: string
    user_id?: string
    metadata?: Record<string, any>
  }): Promise<{
    session_id: string
    decision: string
    rule_name?: string
    reason: string
    policy_version: string
    log_id: string
    timestamp: string
  }> {
    return this.request('/enforce', {
      method: 'POST',
      body: JSON.stringify(params),
    })
  }

  async updateToolResult(
    sessionId: string,
    logId: string,
    result: Record<string, any>
  ): Promise<{ status: string; log_id: string }> {
    return this.request(`/enforce/${sessionId}/result?log_id=${logId}`, {
      method: 'POST',
      body: JSON.stringify(result),
    })
  }
}

export const apiClient = new ApiClient()

// WebSocket connection for real-time updates
export class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private messageHandlers: Array<(message: any) => void> = []

  connect(sessionId: string) {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/${sessionId}`
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          this.messageHandlers.forEach(handler => handler(message))
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.attemptReconnect(sessionId)
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }

  private attemptReconnect(sessionId: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
      
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        this.connect(sessionId)
      }, delay)
    }
  }

  onMessage(handler: (message: any) => void) {
    this.messageHandlers.push(handler)
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.messageHandlers = []
  }
}

export const wsClient = new WebSocketClient() 