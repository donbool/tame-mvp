import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useAppStore } from '@/lib/store'
import { 
  Home,
  List,
  Shield,
  Settings,
  Activity,
  Eye
} from 'lucide-react'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    description: 'Overview and live activity'
  },
  {
    name: 'Sessions',
    href: '/sessions',
    icon: List,
    description: 'Agent session logs'
  },
  {
    name: 'Policy',
    href: '/policy',
    icon: Shield,
    description: 'Policy management'
  }
]

export default function Sidebar() {
  const location = useLocation()
  const { policyInfo, liveUpdates, setLiveUpdates } = useAppStore()

  return (
    <div className="w-64 h-full bg-card border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Shield className="w-4 h-4 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Runlok</h1>
            <p className="text-xs text-muted-foreground">Policy Enforcement</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href || 
                          (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              <item.icon className="w-4 h-4" />
              <div className="flex-1">
                <div className="font-medium">{item.name}</div>
                <div className="text-xs opacity-75">{item.description}</div>
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Status Section */}
      <div className="p-4 border-t border-border space-y-4">
        {/* Policy Status */}
        {policyInfo && (
          <div className="space-y-2">
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Policy Status
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Version:</span>
                <span className="font-mono text-xs">{policyInfo.version}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Rules:</span>
                <span>{policyInfo.rules_count}</span>
              </div>
            </div>
          </div>
        )}

        {/* Live Updates Toggle */}
        <div className="space-y-2">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Live Updates
          </div>
          <button
            onClick={() => setLiveUpdates(!liveUpdates)}
            className={cn(
              "flex items-center space-x-2 w-full px-3 py-2 rounded-lg text-sm transition-colors",
              liveUpdates
                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                : "bg-muted text-muted-foreground hover:bg-accent"
            )}
          >
            <Eye className="w-4 h-4" />
            <span>{liveUpdates ? 'Enabled' : 'Disabled'}</span>
            {liveUpdates && (
              <Activity className="w-3 h-3 animate-pulse ml-auto" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
} 