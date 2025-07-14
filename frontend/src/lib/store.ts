import { create } from 'zustand'
import type { SessionSummary, PolicyInfo } from './api'
import { apiClient } from './api'

interface AppState {
  // UI State
  sidebarOpen: boolean
  darkMode: boolean
  liveUpdates: boolean
  
  // Data State
  sessions: SessionSummary[]
  policyInfo: PolicyInfo | null
  
  // Actions
  toggleSidebar: () => void
  toggleDarkMode: () => void
  setLiveUpdates: (enabled: boolean) => void
  setSessions: (sessions: SessionSummary[]) => void
  setPolicyInfo: (policy: PolicyInfo | null) => void
  loadPolicyInfo: () => Promise<void>
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial UI state
  sidebarOpen: true,
  darkMode: false,
  liveUpdates: false,
  
  // Initial data state
  sessions: [],
  policyInfo: null,
  
  // UI actions
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
  setLiveUpdates: (enabled) => set({ liveUpdates: enabled }),
  
  // Data actions
  setSessions: (sessions) => set({ sessions }),
  setPolicyInfo: (policyInfo) => set({ policyInfo }),
  
  loadPolicyInfo: async () => {
    try {
      const policyInfo = await apiClient.getPolicyInfo()
      set({ policyInfo })
    } catch (error) {
      console.error('Failed to load policy info:', error)
      // Don't set error state here, just log it
    }
  }
}))

// Load policy info on app start
useAppStore.getState().loadPolicyInfo() 