import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useAppStore } from '@/lib/store'
import {
  List,
  Shield,
  Settings,
  Activity,
  Eye,
  FileCheck,
  Code2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { useState } from 'react'

const navigation = [
  {
    name: 'Sessions',
    href: '/sessions',
    icon: List,
    description: 'Live activity & session history'
  },
  {
    name: 'Policy',
    href: '/policy',
    icon: Shield,
    description: 'Policy management'
  },
  {
    name: 'Integration',
    href: '/integration',
    icon: Code2,
    description: 'MCP & SDK documentation'
  },
  {
    name: 'Compliance',
    href: '/compliance',
    icon: FileCheck,
    description: 'EU AI Act & GDPR compliance'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'System configuration'
  }
]

export default function Sidebar() {
  const location = useLocation()
  const { policyInfo, liveUpdates, setLiveUpdates } = useAppStore()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div
      className={cn(
        'h-full bg-card border-r border-border flex flex-col transition-all duration-300',
        collapsed ? 'w-14' : 'w-64'
      )}
    >
      {/* Collapse Toggle */}
      <div className={cn('flex items-center justify-between p-2 border-b border-border', collapsed ? 'justify-center' : '')}>
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="p-2 rounded hover:bg-muted transition-colors"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
        {!collapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="w-4 h-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">tame</h1>
              <p className="text-xs text-muted-foreground">Policy Enforcement</p>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className={cn('flex-1 p-4 space-y-2 transition-all duration-300', collapsed ? 'p-2' : 'p-4')}>
        {navigation.map((item) => {
          const isActive = location.pathname === item.href ||
            (item.href !== '/' && location.pathname.startsWith(item.href))

          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center px-2 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent',
                'space-x-3'
              )}
              title={collapsed ? item.name : undefined}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <div
                className={cn(
                  'flex-1 transition-all duration-300',
                  collapsed ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100 w-auto'
                )}
                style={{ minWidth: collapsed ? 0 : 0, maxWidth: collapsed ? 0 : '200px' }}
              >
                <div className="font-medium whitespace-nowrap">{item.name}</div>
                <div className="text-xs opacity-75 whitespace-nowrap">{item.description}</div>
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Status Section */}
      <div className={cn('p-4 border-t border-border space-y-4 transition-all duration-300', collapsed ? 'p-2' : 'p-4')}>
        {/* Policy Status */}
        {policyInfo && !collapsed && (
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
          <div className={cn('text-xs font-medium text-muted-foreground uppercase tracking-wide', collapsed && 'text-center')}>Live Updates</div>
          <button
            onClick={() => setLiveUpdates(!liveUpdates)}
            className={cn(
              'flex items-center w-full px-3 py-2 rounded-lg text-sm transition-colors',
              liveUpdates
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-muted text-muted-foreground hover:bg-accent',
              collapsed ? 'justify-center' : 'space-x-2'
            )}
            title={collapsed ? (liveUpdates ? 'Disable Live Updates' : 'Enable Live Updates') : undefined}
          >
            <Eye className="w-4 h-4" />
            {!collapsed && <span>{liveUpdates ? 'Enabled' : 'Disabled'}</span>}
            {liveUpdates && !collapsed && (
              <Activity className="w-3 h-3 animate-pulse ml-auto" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
} 