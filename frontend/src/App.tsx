import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard'; // Default import
import { SessionsPage } from './pages/SessionsPage';
import SessionDetailPage from './pages/SessionDetailPage'; // Default import  
import PolicyPage from './pages/PolicyPage'; // Default import
import IntegrationPage from './pages/IntegrationPage'; // Default import
import { CompliancePage } from './pages/CompliancePage';
import SettingsPage from './pages/SettingsPage'; // Default import

function App() {
  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/sessions" element={<SessionsPage />} />
            <Route path="/sessions/:sessionId" element={<SessionDetailPage />} />
            <Route path="/policy" element={<PolicyPage />} />
            <Route path="/integration" element={<IntegrationPage />} />
            <Route path="/compliance" element={<CompliancePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App; 