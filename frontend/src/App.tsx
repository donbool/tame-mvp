import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAppStore } from '@/lib/store'
import { apiClient } from '@/lib/api'

// Pages
import Dashboard from '@/pages/Dashboard'
import SessionsPage from '@/pages/SessionsPage'
import SessionDetailPage from '@/pages/SessionDetailPage'
import PolicyPage from '@/pages/PolicyPage'

// Components
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import { Toaster } from '@/components/ui/toaster'

function App() {
  const { sidebarOpen, policyInfo, setPolicyInfo } = useAppStore()

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Load policy info
        const policy = await apiClient.getPolicyInfo()
        setPolicyInfo(policy)
      } catch (error) {
        console.error('Failed to load initial data:', error)
      }
    }

    loadInitialData()
  }, [setPolicyInfo])

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {/* Sidebar */}
        <aside 
          className={`fixed left-0 top-0 h-full z-40 transition-transform duration-300 ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <Sidebar />
        </aside>

        {/* Main content */}
        <div 
          className={`flex-1 flex flex-col transition-all duration-300 ${
            sidebarOpen ? 'ml-64' : 'ml-0'
          }`}
        >
          {/* Header */}
          <Header />

          {/* Page content */}
          <main className="flex-1 p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/sessions" element={<SessionsPage />} />
              <Route path="/sessions/:sessionId" element={<SessionDetailPage />} />
              <Route path="/policy" element={<PolicyPage />} />
            </Routes>
          </main>
        </div>
      </div>

      {/* Toast notifications */}
      <Toaster />
    </div>
  )
}

export default App 