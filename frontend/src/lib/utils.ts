import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTimestamp(timestamp: string | Date): string {
  const date = new Date(timestamp)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date)
}

export function formatDuration(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(1)}s`
  } else {
    return `${(ms / 60000).toFixed(1)}m`
  }
}

export function getDecisionColor(decision: string): string {
  switch (decision) {
    case 'allow':
      return 'text-green-600 dark:text-green-400'
    case 'deny':
      return 'text-red-600 dark:text-red-400'
    case 'approve':
      return 'text-yellow-600 dark:text-yellow-400'
    default:
      return 'text-muted-foreground'
  }
}

export function getDecisionIcon(decision: string): string {
  switch (decision) {
    case 'allow':
      return '✓'
    case 'deny':
      return '✗'
    case 'approve':
      return '⚠'
    default:
      return '?'
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function formatJSON(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

export function generateSessionId(): string {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15)
} 