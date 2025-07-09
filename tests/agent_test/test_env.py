#!/usr/bin/env python3
"""
Configure Runlok backend for testing with SQLite instead of PostgreSQL.
This makes testing easier without requiring database server setup.
"""

import os
import sys

def setup_test_environment():
    """Set up environment variables for testing."""
    
    # Use SQLite for testing (no server required)
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_runlok.db"
    
    # Disable Redis for testing
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    
    # Set other test-friendly settings
    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["JWT_SECRET"] = "test-jwt-secret"
    os.environ["HMAC_SECRET"] = "test-hmac-secret"
    
    print("✅ Test environment configured:")
    print(f"   Database: SQLite (file: test_runlok.db)")
    print(f"   Redis: {os.environ['REDIS_URL']}")
    print(f"   Log Level: {os.environ['LOG_LEVEL']}")

def start_backend():
    """Start the backend with test configuration."""
    setup_test_environment()
    
    # Change to backend directory
    backend_dir = "../../backend"
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
        print(f"📁 Changed to backend directory: {os.getcwd()}")
    
    # Import and run the backend
    try:
        import uvicorn
        print("🚀 Starting Runlok backend with test configuration...")
        
        # This will start the server - run in separate terminal/process
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not found. Install it with: pip install uvicorn")
        return False
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        start_backend()
    else:
        setup_test_environment()
        print("\nTo start the backend with test config:")
        print("python3 test_env.py start")
        print("\nOr manually:")
        print("cd ../../backend")
        print("DATABASE_URL='sqlite+aiosqlite:///./test_runlok.db' python3 -m uvicorn app.main:app --reload") 