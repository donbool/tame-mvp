# Tame MVP - Project Structure

**Professional AI Agent Runtime Control Platform**

## 📁 Clean Project Structure

```
tame-mvp/
├── README.md                    # Main project documentation
├── docker-compose.yml           # Multi-service orchestration
├── docker.env                   # Environment configuration
├── policies.yml                 # Global policy configuration
│
├── backend/                     # FastAPI Backend Service
│   ├── Dockerfile              # Backend container definition
│   ├── requirements.txt        # Python dependencies
│   ├── policies.yml            # Backend-specific policies
│   └── app/
│       ├── main.py             # FastAPI application entry
│       ├── api/                # REST API endpoints
│       │   ├── enforcement.py  # Policy enforcement endpoints
│       │   ├── policies.py     # Policy management endpoints
│       │   ├── sessions.py     # Session management endpoints
│       │   └── compliance.py   # Compliance and audit endpoints
│       ├── core/               # Core infrastructure
│       │   ├── config.py       # Configuration management
│       │   └── database.py     # Database connections
│       ├── models/             # Data models
│       │   ├── audit_log.py    # Audit logging models
│       │   ├── policy_version.py # Policy versioning models
│       │   └── session_log.py  # Session tracking models
│       └── services/           # Business logic
│           ├── policy_engine.py      # Policy evaluation engine
│           ├── compliance_service.py # Compliance checking
│           └── websocket_manager.py  # Real-time notifications
│
├── frontend/                    # React TypeScript Frontend
│   ├── Dockerfile              # Frontend container definition
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite build configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── src/
│       ├── main.tsx            # React application entry
│       ├── App.tsx             # Main application component
│       ├── globals.css         # Global styles
│       ├── components/         # Reusable UI components
│       │   ├── Header.tsx      # Navigation header
│       │   ├── Sidebar.tsx     # Navigation sidebar
│       │   └── ui/             # Base UI components
│       ├── pages/              # Application pages
│       │   ├── SessionsPage.tsx        # Session monitoring
│       │   ├── SessionDetailPage.tsx   # Session details
│       │   ├── PolicyPage.tsx          # Policy management
│       │   ├── CompliancePage.tsx      # Compliance dashboard
│       │   ├── IntegrationPage.tsx     # Integration guides
│       │   └── SettingsPage.tsx        # Application settings
│       ├── lib/                # Utilities and helpers
│       │   ├── api.ts          # API client
│       │   ├── store.ts        # State management
│       │   └── utils.ts        # Helper functions
│       └── hooks/              # Custom React hooks
│           └── use-toast.ts    # Toast notifications
│
├── tamesdk/                     # Professional Python SDK
│   ├── setup.py               # Package installation
│   ├── tamesdk/               # Main package
│   │   ├── __init__.py        # Package exports
│   │   ├── client.py          # Sync/Async clients
│   │   ├── decorators.py      # @enforce_policy decorators
│   │   ├── exceptions.py      # Custom exception hierarchy
│   │   ├── models.py          # Data models and types
│   │   ├── config.py          # Configuration management
│   │   └── cli.py             # Command-line interface
│   └── tamesdk.egg-info/      # Package metadata
│
├── cli/                        # Standalone CLI Tools
│   └── tamesdk                 # Standalone CLI script
│
└── tests/                      # Test Suites
    ├── mock_agent_test/        # Mock agent testing framework
    │   ├── README.md           # Test documentation
    │   ├── mock_agent.py       # Mock agent implementation
    │   ├── mock_tools.py       # Mock tool definitions
    │   ├── run_tests.py        # Test runner
    │   ├── requirements.txt    # Test dependencies
    │   └── policies/           # Test policy configurations
    └── real-agent/             # Real agent integration tests
        ├── real_mcp_agent.py   # MCP agent with TameSDK
        ├── requirements.txt    # Integration test dependencies
        └── sample_policy.yaml  # Sample policy for testing
```

## 🏗️ Architecture Overview

### **Backend Service (FastAPI)**
- **Policy Engine**: Evaluates rules against tool calls
- **Session Management**: Tracks agent activity across sessions
- **Compliance Service**: Audit trails and reporting
- **WebSocket Manager**: Real-time notifications
- **Database**: PostgreSQL for data persistence
- **Redis**: Caching and session storage

### **Frontend Application (React + TypeScript)**
- **Session Monitoring**: Real-time view of agent activity
- **Policy Management**: Create and edit policy rules
- **Compliance Dashboard**: Audit reports and analytics
- **Integration Guides**: Documentation and examples
- **Settings Management**: Configuration and preferences

### **TameSDK (Python Package)**
- **Sync/Async Clients**: Both synchronous and asynchronous API clients
- **Decorators**: `@enforce_policy` for easy integration
- **Exception Handling**: Comprehensive error management
- **Configuration**: Environment and file-based configuration
- **CLI Tools**: Command-line interface for testing and management

### **Testing Framework**
- **Mock Agent Tests**: Isolated testing with mock tools
- **Real Agent Tests**: Integration testing with actual AI frameworks
- **Policy Testing**: Validation of policy rules and configurations

## 🚀 Software Engineering Practices

### **Code Quality**
- ✅ **Type Hints**: Full type annotations throughout
- ✅ **Error Handling**: Comprehensive exception hierarchy
- ✅ **Documentation**: Docstrings and inline comments
- ✅ **Modularity**: Clear separation of concerns
- ✅ **Testing**: Mock and integration test suites

### **Project Structure**
- ✅ **Clean Architecture**: Layered design with clear boundaries
- ✅ **Dependency Management**: Isolated package dependencies
- ✅ **Configuration Management**: Environment-based configuration
- ✅ **Docker Containerization**: Production-ready containers
- ✅ **Package Structure**: Professional Python packaging

### **Development Workflow**
- ✅ **Development Mode**: Editable package installation
- ✅ **Hot Reloading**: Frontend and backend development servers
- ✅ **Environment Isolation**: Separate development/production configs
- ✅ **CLI Tools**: Command-line utilities for development
- ✅ **Test Automation**: Automated test execution

## 🔧 Getting Started

### **1. Start the Platform**
```bash
docker-compose up -d
```

### **2. Install TameSDK**
```bash
cd tamesdk
pip install -e .
```

### **3. Test Integration**
```bash
# Test CLI
tamesdk status

# Test Python SDK
python -c "import tamesdk; print('✅ TameSDK Ready!')"

# Run agent tests
cd tests/real-agent
python real_mcp_agent.py
```

### **4. Access Web Interface**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 Key Features

- **🛡️ Policy Enforcement**: Real-time control over AI agent actions
- **📈 Session Monitoring**: Comprehensive tracking and analytics
- **🔄 Easy Integration**: 2-line decorator integration
- **⚡ High Performance**: Async support for scalability
- **🎯 Professional Quality**: Enterprise-grade code and documentation
- **🧪 Comprehensive Testing**: Mock and real-world test suites

## 🎯 Clean, Professional Codebase

This project structure follows exquisite software engineering practices:

1. **Clear Separation of Concerns**: Each directory has a single responsibility
2. **Professional Packaging**: Pip-installable SDK with proper versioning
3. **Comprehensive Documentation**: README files and inline documentation
4. **Modern Development Stack**: TypeScript, FastAPI, Docker, pytest
5. **Production Ready**: Container orchestration and environment management
6. **Developer Experience**: CLI tools, hot reloading, easy setup

The codebase is now clean, organized, and follows industry best practices for professional software development.