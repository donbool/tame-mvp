# Runlok Agent Test Framework

This test framework provides a realistic AI agent simulation to test Runlok's policy enforcement capabilities.

## Overview

The test framework includes:
- **Mock Agent**: Simulates an AI agent making various tool calls
- **Mock Tools**: Common tools like file operations, web requests, system commands
- **Test Scenarios**: Predefined scenarios that trigger different policy decisions
- **Policy Configs**: Different policy configurations for testing

## Quick Start

1. **Start the Runlok backend**:
   ```bash
   cd ../backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Install test dependencies**:
   ```bash
   cd tests/agent_test
   pip install -r requirements.txt
   ```

3. **Run test scenarios**:
   ```bash
   python3 run_tests.py
   ```

## Test Agent Features

The mock agent (`mock_agent.py`) simulates realistic behavior:
- **File Operations**: Reading, writing, deleting files
- **Web Requests**: API calls, data fetching
- **System Commands**: Terminal operations, system info
- **Communication**: Email sending, Slack messages
- **Data Access**: Database queries, cloud storage

## Test Scenarios

### 1. **Safe Operations Test**
- Tests tools that should always be allowed
- Verifies basic functionality works

### 2. **Dangerous Operations Test** 
- Tests tools that should be denied
- Verifies security policies work

### 3. **Approval Required Test**
- Tests tools requiring human approval
- Simulates approval workflows

### 4. **Context-Based Restrictions**
- Tests policies based on user roles, content, etc.
- Verifies conditional logic

### 5. **Rate Limiting Test**
- Tests frequency-based restrictions
- Verifies throttling works

## Policy Configurations

### `policies/test_strict.yml`
- Strict security policy
- Most operations denied or require approval

### `policies/test_permissive.yml` 
- Permissive policy for development
- Most operations allowed

### `policies/test_conditional.yml`
- Complex conditional rules
- Different rules for different user roles

## Running Specific Tests

```bash
# Run only safe operations
python3 run_tests.py --scenario safe

# Run with specific policy
python3 run_tests.py --policy policies/test_strict.yml

# Enable verbose logging
python3 run_tests.py --verbose

# Test specific agent behavior
python3 mock_agent.py --tool read_file --args '{"path": "/etc/passwd"}'
```

## Adding Custom Tests

1. Create new scenario in `scenarios/`
2. Define tools and expected outcomes
3. Add to test runner configuration

## Expected Output

The test runner will show:
- ✅ **Allowed**: Operations that passed policy
- ❌ **Denied**: Operations blocked by policy  
- ⏳ **Approval Required**: Operations needing approval
- 📊 **Summary**: Overall test results and policy effectiveness 