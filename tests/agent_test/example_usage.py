#!/usr/bin/env python3
"""
Example usage of the tame Agent Test Framework.
Demonstrates how to use the testing components programmatically.
"""

import sys
import json
from mock_agent import MockAIAgent, AgentTask
from run_tests import tameTestRunner

def example_single_tool_test():
    """Example of testing a single tool call."""
    print("🔧 Example 1: Single Tool Test")
    print("=" * 40)
    
    # Create an agent
    agent = MockAIAgent(
        agent_id="example-agent",
        user_id="example-user",
        api_url="http://localhost:8000"
    )
    
    # Test a safe tool call
    result = agent.execute_tool(
        tool_name="search_web",
        tool_args={"query": "Python tutorials", "limit": 5}
    )
    
    print(f"Result: {result['status']}")
    if 'decision' in result:
        print(f"Policy Rule: {result['decision'].rule_name}")
        print(f"Reason: {result['decision'].reason}")
    
    print()

def example_custom_scenario():
    """Example of creating and running a custom scenario."""
    print("🎯 Example 2: Custom Scenario")
    print("=" * 40)
    
    agent = MockAIAgent(
        agent_id="example-agent",
        user_id="example-user"
    )
    
    # Create custom tasks
    custom_tasks = [
        AgentTask(
            description="Test safe web search",
            tool_name="search_web",
            tool_args={"query": "weather today"},
            expected_outcome="allow"
        ),
        AgentTask(
            description="Test file deletion (should be denied)",
            tool_name="delete_file", 
            tool_args={"path": "/important/file.txt"},
            expected_outcome="deny"
        ),
        AgentTask(
            description="Test email sending (needs approval)",
            tool_name="send_email",
            tool_args={
                "to": "test@example.com",
                "subject": "Test",
                "body": "Hello world"
            },
            expected_outcome="approve"
        )
    ]
    
    # Execute custom tasks
    results = []
    for task in custom_tasks:
        result = agent.execute_task(task)
        results.append(result)
    
    # Print summary
    print(f"Total tasks: {len(custom_tasks)}")
    print(f"Successful: {len([r for r in results if r['status'] == 'success'])}")
    print(f"Denied: {len([r for r in results if r['status'] == 'denied'])}")
    print(f"Approval required: {len([r for r in results if r['status'] == 'approval_required'])}")
    
    print()

def example_test_runner():
    """Example of using the test runner programmatically."""
    print("📊 Example 3: Test Runner")
    print("=" * 40)
    
    # Create test runner
    runner = tameTestRunner(verbose=False)
    
    # Run a specific scenario
    report = runner.run_single_scenario("safe_operations")
    
    # Extract key metrics
    task_summary = report["task_summary"]
    
    print(f"Test Results:")
    print(f"• Total tasks: {task_summary['total_tasks']}")
    print(f"• Success rate: {task_summary['policy_effectiveness']['success_rate']:.1%}")
    print(f"• Enforcement rate: {task_summary['policy_effectiveness']['enforcement_rate']:.1%}")
    
    # Save detailed report
    filename = runner.save_report("example_test_report.json")
    print(f"• Detailed report saved to: {filename}")
    
    print()

def example_interactive_agent():
    """Example of creating an agent for interactive testing."""
    print("🎮 Example 4: Interactive Agent Setup")
    print("=" * 40)
    
    agent = MockAIAgent(
        agent_id="interactive-agent",
        user_id="test-user"
    )
    
    print("Agent created and ready for interactive use.")
    print("Available scenarios:")
    
    scenarios = agent.get_test_scenarios()
    for name, data in scenarios.items():
        print(f"• {name}: {data['description']}")
    
    print("\nTo use interactively, run:")
    print("python3 mock_agent.py --interactive")
    
    print()

def example_policy_testing():
    """Example of testing different policy configurations."""
    print("📋 Example 5: Policy Configuration Testing")
    print("=" * 40)
    
    # This would test different policy files if the backend supported loading them
    print("Available test policies:")
    print("• policies/test_strict.yml - Strict security policy")
    print("• policies/test_permissive.yml - Development-friendly policy")
    print("• policies/test_conditional.yml - Role-based conditional policy")
    
    print("\nTo test with different policies:")
    print("1. Update the backend to load the desired policy file")
    print("2. Restart the backend")
    print("3. Run tests with: python3 run_tests.py")
    
    print()

def main():
    """Run all examples."""
    print("🚀 tame Agent Test Framework - Usage Examples")
    print("=" * 50)
    print()
    
    try:
        # Run examples
        example_single_tool_test()
        example_custom_scenario()
        example_test_runner()
        example_interactive_agent()
        example_policy_testing()
        
        print("✅ All examples completed successfully!")
        print("\nNext steps:")
        print("• Try running: python3 run_tests.py")
        print("• Explore interactive mode: python3 mock_agent.py --interactive")
        print("• Check the README.md for more detailed documentation")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("\nMake sure the tame backend is running:")
        print("cd ../../backend && python3 -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    main() 