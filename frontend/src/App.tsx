import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { SessionsPage } from './pages/SessionsPage';
import { SessionDetailPage } from './pages/SessionDetailPage';
import { PolicyPage } from './pages/PolicyPage';
import { CompliancePage } from './pages/CompliancePage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sessions" element={<SessionsPage />} />
            <Route path="/sessions/:sessionId" element={<SessionDetailPage />} />
            <Route path="/policy" element={<PolicyPage />} />
            <Route path="/compliance" element={<CompliancePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 