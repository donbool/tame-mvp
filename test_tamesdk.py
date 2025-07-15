#!/usr/bin/env python3
"""
Test TameSDK functionality
"""

import tamesdk

# Configure TameSDK
tamesdk.configure(
    api_url="http://localhost:8000",
    bypass_mode=True  # Enable bypass mode for testing
)

print("🎯 TameSDK Test")
print("===============")

# Test 1: Basic decorator usage
print("\n📝 Test 1: Basic Decorator")

@tamesdk.enforce_policy
def read_file(path: str) -> str:
    """Read a file with policy enforcement."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {path}"

try:
    result = read_file("/tmp/test.txt")
    print(f"✅ Decorator test: {result}")
except Exception as e:
    print(f"❌ Decorator test failed: {e}")

# Test 2: Client usage
print("\n🔧 Test 2: Client Usage")

try:
    with tamesdk.Client() as client:
        decision = client.enforce(
            "test_operation",
            {"param": "value"},
            raise_on_deny=False,
            raise_on_approve=False
        )
        print(f"✅ Client test: {decision.action.value} - {decision.reason}")
except Exception as e:
    print(f"❌ Client test failed: {e}")

# Test 3: Configuration
print("\n⚙️ Test 3: Configuration")

config = tamesdk.get_config()
print(f"✅ Config test:")
print(f"   API URL: {config.api_url}")
print(f"   Bypass mode: {config.bypass_mode}")
print(f"   Session ID: {config.session_id}")

print("\n🎉 All tests completed!")
print("\n💡 Quick start:")
print("   1. @tamesdk.enforce_policy   # Decorator on any function")
print("   2. tamesdk.Client()          # Direct client usage") 
print("   3. tamesdk.configure()       # Configure settings")