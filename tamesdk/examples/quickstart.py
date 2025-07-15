#!/usr/bin/env python3
"""
TameSDK Quickstart Example

This example shows the simplest ways to get started with TameSDK
in just a few lines of code.
"""

import os
import asyncio
import tamesdk


def basic_decorator_example():
    """Simplest possible usage with decorators."""
    print("🎯 Basic Decorator Example")
    print("=" * 30)
    
    # Configure TameSDK (do this once in your app)
    tamesdk.configure(
        api_url=os.getenv("TAME_API_URL", "http://localhost:8000"),
        api_key=os.getenv("TAME_API_KEY"),
        bypass_mode=True  # For demo without real server
    )
    
    # Wrap any function with policy enforcement
    @tamesdk.enforce_policy
    def read_file(path: str) -> str:
        """Read a file with automatic policy enforcement."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return f"File not found: {path}"
    
    @tamesdk.with_approval(approval_message="Writing files requires approval")
    def write_file(path: str, content: str) -> str:
        """Write a file with approval requirement."""
        with open(path, 'w') as f:
            f.write(content)
        return f"Written to {path}"
    
    # Use the functions normally - policies are enforced automatically
    try:
        print("📖 Reading safe file...")
        content = read_file("/tmp/safe_file.txt")
        print(f"✅ Result: {content}")
    except Exception as e:
        print(f"❌ Read failed: {e}")
    
    try:
        print("✏️ Writing file (requires approval)...")
        result = write_file("/tmp/output.txt", "Hello TameSDK!")
        print(f"✅ Result: {result}")
    except tamesdk.ApprovalRequiredException as e:
        print(f"⏳ Approval required: {e.decision.reason}")
    except Exception as e:
        print(f"❌ Write failed: {e}")


def client_context_example():
    """Using TameSDK client directly for more control."""
    print("\n🔧 Client Context Example")
    print("=" * 30)
    
    # Use client for fine-grained control
    with tamesdk.Client() as client:
        
        # Test a policy without executing
        print("🧪 Testing policies...")
        test_cases = [
            ("read_file", {"path": "/tmp/safe.txt"}),
            ("read_file", {"path": "/etc/passwd"}),
            ("delete_file", {"path": "/important/data.db"})
        ]
        
        for tool_name, args in test_cases:
            try:
                decision = client.enforce(
                    tool_name, 
                    args,
                    raise_on_deny=False,
                    raise_on_approve=False
                )
                
                action_emoji = {
                    'allow': '✅',
                    'deny': '❌',
                    'approve': '⏳'
                }
                
                emoji = action_emoji.get(decision.action.value, '❓')
                print(f"  {emoji} {tool_name}: {decision.action.value} - {decision.reason}")
                
            except Exception as e:
                print(f"  ❌ {tool_name}: Error - {e}")
        
        # Execute with automatic enforcement
        print("\n🚀 Executing with enforcement...")
        try:
            result = client.execute_tool(
                "safe_operation",
                {"data": "some_data"},
                executor=lambda name, args: f"Processed {args['data']}"
            )
            print(f"✅ Execution result: {result.result}")
        except Exception as e:
            print(f"❌ Execution failed: {e}")


async def async_example():
    """Async usage for high-performance applications."""
    print("\n⚡ Async Example")
    print("=" * 20)
    
    async with tamesdk.AsyncClient() as client:
        
        # Concurrent policy enforcement
        async def check_policy(tool_name: str, args: dict):
            try:
                decision = await client.enforce(
                    tool_name, 
                    args,
                    raise_on_deny=False,
                    raise_on_approve=False
                )
                return f"{tool_name}: {decision.action.value}"
            except Exception as e:
                return f"{tool_name}: Error - {e}"
        
        # Run multiple policy checks concurrently
        tasks = [
            check_policy("api_call", {"endpoint": "https://api.example.com"}),
            check_policy("database_query", {"query": "SELECT * FROM users"}),
            check_policy("file_upload", {"path": "/uploads/file.txt"})
        ]
        
        results = await asyncio.gather(*tasks)
        for result in results:
            print(f"  📋 {result}")
        
        # Async tool execution
        print("\n🔄 Async execution...")
        try:
            async def async_processor(tool_name: str, args: dict):
                await asyncio.sleep(0.1)  # Simulate async work
                return f"Async processed: {tool_name}"
            
            result = await client.execute_tool(
                "async_operation",
                {"task": "process_data"},
                executor=async_processor
            )
            print(f"✅ Async result: {result.result}")
        except Exception as e:
            print(f"❌ Async execution failed: {e}")


def configuration_example():
    """Different ways to configure TameSDK."""
    print("\n⚙️ Configuration Example")
    print("=" * 25)
    
    # Method 1: Environment variables
    print("📝 Configuration methods:")
    print("  1. Environment variables:")
    print("     export TAME_API_URL=http://localhost:8000")
    print("     export TAME_API_KEY=your-secret-key")
    
    # Method 2: Programmatic configuration
    print("  2. Programmatic:")
    print("     tamesdk.configure(api_url='...', api_key='...')")
    
    # Method 3: Per-client configuration
    print("  3. Per-client:")
    print("     client = tamesdk.Client(api_url='...', api_key='...')")
    
    # Show current configuration
    config = tamesdk.get_config()
    print(f"\n📊 Current config:")
    print(f"  API URL: {config.api_url}")
    print(f"  Session ID: {config.session_id}")
    print(f"  Bypass mode: {config.bypass_mode}")


def error_handling_example():
    """How to handle different types of errors."""
    print("\n🚨 Error Handling Example")
    print("=" * 30)
    
    @tamesdk.enforce_policy
    def risky_operation(action: str) -> str:
        if action == "safe":
            return "Operation completed safely"
        elif action == "error":
            raise Exception("Something went wrong")
        else:
            return f"Performed {action}"
    
    test_actions = ["safe", "dangerous", "error"]
    
    for action in test_actions:
        try:
            print(f"🎯 Testing action: {action}")
            result = risky_operation(action)
            print(f"  ✅ Success: {result}")
            
        except tamesdk.PolicyViolationException as e:
            print(f"  ❌ Policy denied: {e.decision.reason}")
            
        except tamesdk.ApprovalRequiredException as e:
            print(f"  ⏳ Approval required: {e.decision.reason}")
            
        except Exception as e:
            print(f"  💥 Execution error: {e}")


def cli_example():
    """How to use the TameSDK CLI."""
    print("\n💻 CLI Usage Example")
    print("=" * 25)
    
    print("🔧 TameSDK CLI commands:")
    print("  # Check API status")
    print("  tamesdk status")
    print()
    print("  # Test a tool call")
    print("  tamesdk test read_file --args '{\"path\": \"/tmp/test.txt\"}'")
    print()
    print("  # View session logs")
    print("  tamesdk logs --format table")
    print()
    print("  # Interactive mode")
    print("  tamesdk interactive")
    print()
    print("  # Policy information")
    print("  tamesdk policy")
    print()
    print("📝 Try running these commands to explore TameSDK!")


def integration_tips():
    """Tips for integrating TameSDK into existing applications."""
    print("\n💡 Integration Tips")
    print("=" * 20)
    
    tips = [
        "🎯 Start with decorators for the simplest integration",
        "🔧 Use bypass_mode=True during development and testing",
        "📊 Check logs regularly to understand policy decisions",
        "⚡ Use AsyncClient for high-performance applications",
        "🛡️ Test your policies thoroughly before production",
        "📈 Monitor session summaries for insights",
        "🔄 Use context managers for fine-grained control",
        "🚨 Handle approval workflows in your application logic"
    ]
    
    for tip in tips:
        print(f"  {tip}")


if __name__ == "__main__":
    print("🚀 TameSDK Quickstart Examples")
    print("=" * 35)
    print("This demo shows the simplest ways to use TameSDK")
    print()
    
    try:
        # Run all examples
        basic_decorator_example()
        client_context_example()
        asyncio.run(async_example())
        configuration_example()
        error_handling_example()
        cli_example()
        integration_tips()
        
        print("\n🎉 Quickstart completed!")
        print("💡 Next steps:")
        print("   1. Install: pip install tamesdk")
        print("   2. Configure your Tame server")
        print("   3. Add @tamesdk.enforce_policy to your functions")
        print("   4. Test with: tamesdk test your_function")
        
    except KeyboardInterrupt:
        print("\n👋 Quickstart interrupted by user")
    except Exception as e:
        print(f"\n❌ Quickstart failed: {e}")
        import traceback
        traceback.print_exc()