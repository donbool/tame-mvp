import { Link, useLocation } from 'react-router-dom';

export function Header() {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-900">
              Runlok
            </Link>
            <span className="ml-2 text-sm text-gray-500">AI Policy Enforcement</span>
          </div>

          <nav className="flex space-x-8">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/sessions"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/sessions') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Sessions
            </Link>
            <Link
              to="/policy"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/policy') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Policy
            </Link>
            <Link
              to="/compliance"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/compliance') 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Compliance
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
} 