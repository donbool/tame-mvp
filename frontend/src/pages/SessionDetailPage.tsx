import { useParams } from 'react-router-dom'

export default function SessionDetailPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Session Details</h1>
        <p className="text-muted-foreground">Session ID: {sessionId}</p>
      </div>
      
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-muted-foreground">Session detail page - Coming soon!</p>
      </div>
    </div>
  )
} 