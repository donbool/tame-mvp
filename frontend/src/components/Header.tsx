import { useAppStore } from '@/lib/store'
import { Menu, Moon, Sun } from 'lucide-react'

export default function Header() {
  const { sidebarOpen, toggleSidebar, darkMode, toggleDarkMode } = useAppStore()

  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={toggleSidebar}
          className="p-2 hover:bg-accent rounded-lg transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <div>
          <h2 className="font-semibold">Runlok Dashboard</h2>
          <p className="text-sm text-muted-foreground">AI Agent Policy Enforcement</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <button
          onClick={toggleDarkMode}
          className="p-2 hover:bg-accent rounded-lg transition-colors"
        >
          {darkMode ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>
      </div>
    </header>
  )
} 