import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import { SessionsPage } from './pages/SessionsPage';
import SessionDetailPage from './pages/SessionDetailPage';
import PolicyPage from './pages/PolicyPage';
import IntegrationPage from './pages/IntegrationPage';
import { CompliancePage } from './pages/CompliancePage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<SessionsPage />} />
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