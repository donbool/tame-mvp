#!/bin/bash

# tame Agent Test Framework - Quick Start Script
# This script sets up and runs the test environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 tame Agent Test Framework - Quick Start${NC}"
echo "=============================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check dependencies
echo -e "\n${BLUE}📋 Checking dependencies...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command_exists pip; then
    echo -e "${RED}❌ pip is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 and pip are available${NC}"

# Check if we're in the right directory
if [ ! -f "mock_agent.py" ]; then
    echo -e "${RED}❌ Please run this script from the tests/agent_test directory${NC}"
    exit 1
fi

# Install dependencies
echo -e "\n${BLUE}📦 Installing test framework dependencies...${NC}"

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

pip install -r requirements.txt

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Check if tame backend is running
echo -e "\n${BLUE}🔍 Checking tame backend...${NC}"

tame_URL="http://localhost:8000"

if port_in_use 8000; then
    echo -e "${GREEN}✅ Backend appears to be running on port 8000${NC}"
    
    # Try to ping the health endpoint
    if command_exists curl; then
        if curl -s "$tame_URL/health" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ tame API is responding${NC}"
        else
            echo -e "${YELLOW}⚠️  Port 8000 is in use but tame API is not responding${NC}"
            echo -e "${YELLOW}   Make sure the tame backend is running properly${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  No service detected on port 8000${NC}"
    echo -e "${YELLOW}   Starting tame backend...${NC}"
    
    # Try to start the backend
    if [ -f "../../backend/app/main.py" ]; then
        echo -e "${BLUE}📡 Starting tame backend in background...${NC}"
        cd ../../backend
        pip install aiosqlite >/dev/null 2>&1  # Install SQLite driver
        DATABASE_URL='sqlite+aiosqlite:///./test_tame.db' python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        cd - >/dev/null
        
        echo -e "${GREEN}✅ Backend started with PID $BACKEND_PID${NC}"
        echo -e "${BLUE}   Waiting for backend to initialize...${NC}"
        sleep 5
        
        # Check if backend is responding
        if command_exists curl && curl -s "$tame_URL/health" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is now responding${NC}"
        else
            echo -e "${RED}❌ Backend failed to start properly${NC}"
            echo -e "${YELLOW}   Please start the backend manually:${NC}"
            echo -e "${YELLOW}   cd ../../backend && pip install aiosqlite${NC}"
            echo -e "${YELLOW}   DATABASE_URL='sqlite+aiosqlite:///./test_tame.db' python3 -m uvicorn app.main:app --reload${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Backend not found at ../../backend/app/main.py${NC}"
        echo -e "${YELLOW}   Please start the backend manually:${NC}"
        echo -e "${YELLOW}   cd ../../backend && pip install aiosqlite${NC}"
        echo -e "${YELLOW}   DATABASE_URL='sqlite+aiosqlite:///./test_tame.db' python3 -m uvicorn app.main:app --reload${NC}"
        exit 1
    fi
fi

# Run tests
echo -e "\n${BLUE}🧪 Running test scenarios...${NC}"

echo -e "\n${BLUE}1. Quick API connectivity test${NC}"
python3 run_tests.py --check-api

echo -e "\n${BLUE}2. Running safe operations scenario${NC}"
python3 run_tests.py --scenario safe_operations

echo -e "\n${BLUE}3. Running mixed scenario for comprehensive testing${NC}"
python3 run_tests.py --scenario mixed_scenario --verbose

echo -e "\n${BLUE}4. Interactive mode demo${NC}"
echo -e "${YELLOW}   Starting interactive mode - try these commands:${NC}"
echo -e "${YELLOW}   - help (show available commands)${NC}"
echo -e "${YELLOW}   - stats (show current statistics)${NC}"
echo -e "${YELLOW}   - tool search_web {\"query\": \"test\"} (test a safe tool)${NC}"
echo -e "${YELLOW}   - scenario dangerous_operations (test policy enforcement)${NC}"
echo -e "${YELLOW}   - exit (quit interactive mode)${NC}"
echo ""

python3 mock_agent.py --interactive

# Summary
echo -e "\n${GREEN}🎉 Quick start completed successfully!${NC}"
echo ""
echo -e "${BLUE}📚 Next steps:${NC}"
echo "• Review the test results above"
echo "• Explore different scenarios: python3 run_tests.py --scenario <name>"
echo "• Try the interactive mode: python3 mock_agent.py --interactive"
echo "• Run all tests: python3 run_tests.py"
echo "• Check the README.md for detailed documentation"
echo ""
echo -e "${BLUE}🔧 Available test scenarios:${NC}"
echo "• safe_operations - Test allowed operations"
echo "• dangerous_operations - Test denied operations"
echo "• approval_required - Test approval workflows"
echo "• mixed_scenario - Test various outcomes"
echo ""
echo -e "${BLUE}📊 Test different policies:${NC}"
echo "• Strict: policies/test_strict.yml"
echo "• Permissive: policies/test_permissive.yml" 
echo "• Conditional: policies/test_conditional.yml"
echo ""
echo -e "${GREEN}Happy testing! 🚀${NC}" 