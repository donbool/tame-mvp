"""
Mock AI Agent for testing tame policy enforcement.
Simulates realistic agent behavior with various tool calls.
"""

import sys
import os
import json
import time
import random
import argparse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Add the SDK to the path
sys.path.append('../../sdk/python')

import tame
from tame import PolicyViolationException, ApprovalRequiredException
from mock_tools import mock_tools, get_tool_function


@dataclass
class AgentTask:
    """Represents a task the agent wants to execute."""
    description: str
    tool_name: str
    tool_args: Dict[str, Any]
    expected_outcome: str  # "allow", "deny", "approve"
    priority: int = 1


class MockAIAgent:
    """
    Mock AI Agent that simulates realistic behavior and integrates with tame.
    """
    
    def __init__(
        self,
        agent_id: str = "test-agent-001",
        user_id: str = "test-user",
        api_url: str = "http://localhost:8000",
        session_id: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.user_id = user_id
        self.session_id = session_id
        
        # Initialize tame client
        self.tame_client = tame.Client(
            api_url=api_url,
            session_id=session_id,
            agent_id=agent_id,
            user_id=user_id
        )
        
        # Task tracking
        self.completed_tasks = []
        self.failed_tasks = []
        self.pending_approvals = []
        
        # Agent state
        self.is_running = False
        self.task_queue = []
        
        print(f"🤖 Mock AI Agent initialized:")
        print(f"   Agent ID: {self.agent_id}")
        print(f"   User ID: {self.user_id}")
        print(f"   Session: {self.session_id or 'auto-generated'}")
        print(f"   tame API: {api_url}")
    
    def add_task(self, task: AgentTask):
        """Add a task to the agent's queue."""
        self.task_queue.append(task)
    
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a single tool with tame policy enforcement.
        """
        start_time = time.time()
        
        try:
            print(f"\n🔧 Attempting to use tool: {tool_name}")
            print(f"   Args: {json.dumps(tool_args, indent=2)}")
            
            # Enforce policy through tame
            decision = self.tame_client.enforce(
                tool_name=tool_name,
                tool_args=tool_args,
                metadata=metadata
            )
            
            print(f"✅ Policy Decision: {decision.action.upper()}")
            print(f"   Rule: {decision.rule_name}")
            print(f"   Reason: {decision.reason}")
            
            # Execute the actual tool
            tool_func = get_tool_function(tool_name)
            if not tool_func:
                raise Exception(f"Tool '{tool_name}' not implemented")
            
            result = tool_func(**tool_args)
            execution_time = (time.time() - start_time) * 1000
            
            # Report result back to tame
            self.tame_client.update_result(
                session_id=decision.session_id,
                log_id=decision.log_id,
                result=result,
                execution_time_ms=execution_time
            )
            
            print(f"✅ Tool executed successfully in {execution_time:.1f}ms")
            
            return {
                "status": "success",
                "decision": decision,
                "result": result,
                "execution_time_ms": execution_time
            }
            
        except PolicyViolationException as e:
            print(f"❌ Policy Violation: {e.decision.reason}")
            print(f"   Rule: {e.decision.rule_name}")
            
            return {
                "status": "denied",
                "decision": e.decision,
                "error": str(e)
            }
            
        except ApprovalRequiredException as e:
            print(f"⏳ Approval Required: {e.decision.reason}")
            print(f"   Rule: {e.decision.rule_name}")
            
            self.pending_approvals.append(e.decision)
            
            return {
                "status": "approval_required",
                "decision": e.decision,
                "approval_id": e.decision.log_id
            }
            
        except Exception as e:
            print(f"💥 Tool execution failed: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e),
                "execution_time_ms": (time.time() - start_time) * 1000
            }
    
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a complete task."""
        print(f"\n📋 Executing Task: {task.description}")
        
        metadata = {
            "task_description": task.description,
            "expected_outcome": task.expected_outcome,
            "priority": task.priority
        }
        
        result = self.execute_tool(task.tool_name, task.tool_args, metadata)
        
        # Track the result
        if result["status"] == "success":
            self.completed_tasks.append((task, result))
        elif result["status"] in ["denied", "error"]:
            self.failed_tasks.append((task, result))
        
        return result
    
    def run_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Run a predefined test scenario."""
        scenarios = self.get_test_scenarios()
        
        if scenario_name not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        print(f"\n🎯 Running Scenario: {scenario_name}")
        print(f"   Description: {scenarios[scenario_name]['description']}")
        
        tasks = scenarios[scenario_name]['tasks']
        results = []
        
        for task_data in tasks:
            task = AgentTask(**task_data)
            result = self.execute_task(task)
            results.append(result)
            
            # Small delay between tasks
            time.sleep(0.5)
        
        return {
            "scenario": scenario_name,
            "total_tasks": len(tasks),
            "results": results,
            "summary": self.get_execution_summary()
        }
    
    def get_test_scenarios(self) -> Dict[str, Dict]:
        """Get predefined test scenarios."""
        return {
            "safe_operations": {
                "description": "Tests safe operations that should be allowed",
                "tasks": [
                    {
                        "description": "Search for Python tutorials",
                        "tool_name": "search_web",
                        "tool_args": {"query": "Python programming tutorials", "limit": 5},
                        "expected_outcome": "allow"
                    },
                    {
                        "description": "Get system information",
                        "tool_name": "get_system_info",
                        "tool_args": {},
                        "expected_outcome": "allow"
                    },
                    {
                        "description": "Read a configuration file",
                        "tool_name": "read_file",
                        "tool_args": {"path": "/home/user/config.yml"},
                        "expected_outcome": "allow"
                    },
                    {
                        "description": "List directory contents",
                        "tool_name": "list_directory",
                        "tool_args": {"path": "/home/user/documents"},
                        "expected_outcome": "allow"
                    }
                ]
            },
            
            "dangerous_operations": {
                "description": "Tests dangerous operations that should be denied",
                "tasks": [
                    {
                        "description": "Delete system file",
                        "tool_name": "delete_file",
                        "tool_args": {"path": "/system/important.conf", "force": True},
                        "expected_outcome": "deny"
                    },
                    {
                        "description": "Execute dangerous command",
                        "tool_name": "execute_command",
                        "tool_args": {"command": "rm -rf /", "shell": True},
                        "expected_outcome": "deny"
                    },
                    {
                        "description": "Access sensitive database",
                        "tool_name": "query_database",
                        "tool_args": {"query": "SELECT * FROM users WHERE role='admin'", "database": "production"},
                        "expected_outcome": "deny"
                    }
                ]
            },
            
            "approval_required": {
                "description": "Tests operations requiring approval",
                "tasks": [
                    {
                        "description": "Send email to external recipient",
                        "tool_name": "send_email",
                        "tool_args": {
                            "to": "external@company.com",
                            "subject": "Automated Report",
                            "body": "Here is the automated report you requested."
                        },
                        "expected_outcome": "approve"
                    },
                    {
                        "description": "Make external API call",
                        "tool_name": "make_web_request",
                        "tool_args": {
                            "url": "https://api.external-service.com/data",
                            "method": "POST",
                            "headers": {"Authorization": "Bearer token123"}
                        },
                        "expected_outcome": "approve"
                    },
                    {
                        "description": "Access cloud storage",
                        "tool_name": "access_cloud_storage",
                        "tool_args": {
                            "action": "write",
                            "path": "/backup/sensitive-data.json",
                            "content": '{"users": ["alice", "bob"]}'
                        },
                        "expected_outcome": "approve"
                    }
                ]
            },
            
            "mixed_scenario": {
                "description": "Mixed scenario with various outcomes",
                "tasks": [
                    {
                        "description": "Safe web search",
                        "tool_name": "search_web",
                        "tool_args": {"query": "weather forecast"},
                        "expected_outcome": "allow"
                    },
                    {
                        "description": "Sensitive email with password",
                        "tool_name": "send_email",
                        "tool_args": {
                            "to": "user@company.com",
                            "subject": "Password Reset",
                            "body": "Your new password is: secret123"
                        },
                        "expected_outcome": "deny"
                    },
                    {
                        "description": "Safe file read",
                        "tool_name": "read_file",
                        "tool_args": {"path": "/home/user/notes.txt"},
                        "expected_outcome": "allow"
                    },
                    {
                        "description": "Approval-required database query",
                        "tool_name": "query_database",
                        "tool_args": {"query": "SELECT COUNT(*) FROM orders WHERE date > '2024-01-01'"},
                        "expected_outcome": "approve"
                    }
                ]
            }
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of task execution."""
        total_tasks = len(self.completed_tasks) + len(self.failed_tasks) + len(self.pending_approvals)
        
        return {
            "total_tasks": total_tasks,
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "pending_approval": len(self.pending_approvals),
            "success_rate": len(self.completed_tasks) / total_tasks if total_tasks > 0 else 0,
            "tool_stats": mock_tools.get_tool_stats()
        }
    
    def get_session_logs(self) -> List[Dict]:
        """Get session logs from tame."""
        try:
            return self.tame_client.get_session_logs()
        except Exception as e:
            print(f"Failed to get session logs: {e}")
            return []
    
    def interactive_mode(self):
        """Run agent in interactive mode."""
        print("\n🎮 Interactive Mode - Type tool commands or 'help' for options")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command in ["exit", "quit", "q"]:
                    break
                elif command == "help":
                    self.print_help()
                elif command == "stats":
                    print(json.dumps(self.get_execution_summary(), indent=2))
                elif command == "logs":
                    logs = self.get_session_logs()
                    print(json.dumps(logs[-5:], indent=2))  # Last 5 logs
                elif command.startswith("tool "):
                    # Parse tool command: tool <name> <args_json>
                    parts = command.split(" ", 2)
                    if len(parts) >= 2:
                        tool_name = parts[1]
                        tool_args = json.loads(parts[2]) if len(parts) > 2 else {}
                        self.execute_tool(tool_name, tool_args)
                elif command.startswith("scenario "):
                    scenario_name = command.split(" ", 1)[1]
                    self.run_scenario(scenario_name)
                else:
                    print("Unknown command. Type 'help' for options.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n👋 Goodbye!")
    
    def print_help(self):
        """Print help information."""
        print("""
Available Commands:
  tool <name> [args_json]  - Execute a specific tool
  scenario <name>          - Run a test scenario
  stats                    - Show execution statistics
  logs                     - Show recent session logs
  help                     - Show this help
  exit/quit/q             - Exit interactive mode

Available Scenarios:
  safe_operations         - Test safe operations
  dangerous_operations    - Test dangerous operations  
  approval_required       - Test approval workflows
  mixed_scenario          - Mixed scenario

Example tool usage:
  tool search_web {"query": "Python tutorials"}
  tool read_file {"path": "/home/user/test.txt"}
  tool send_email {"to": "test@example.com", "subject": "Test", "body": "Hello"}
        """)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Mock AI Agent for tame testing")
    
    parser.add_argument("--agent-id", default="test-agent-001", help="Agent identifier")
    parser.add_argument("--user-id", default="test-user", help="User identifier")
    parser.add_argument("--api-url", default="http://localhost:8000", help="tame API URL")
    parser.add_argument("--session-id", help="Session identifier (auto-generated if not provided)")
    
    parser.add_argument("--tool", help="Tool name to execute")
    parser.add_argument("--args", default="{}", help="Tool arguments as JSON")
    parser.add_argument("--scenario", help="Scenario to run")
    
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create agent
    agent = MockAIAgent(
        agent_id=args.agent_id,
        user_id=args.user_id,
        api_url=args.api_url,
        session_id=args.session_id
    )
    
    try:
        if args.interactive:
            agent.interactive_mode()
        elif args.scenario:
            result = agent.run_scenario(args.scenario)
            print(f"\n📊 Scenario Results:")
            print(json.dumps(result, indent=2, default=str))
        elif args.tool:
            tool_args = json.loads(args.args)
            result = agent.execute_tool(args.tool, tool_args)
            print(f"\n📊 Tool Result:")
            print(json.dumps(result, indent=2, default=str))
        else:
            print("No action specified. Use --interactive, --scenario, or --tool")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"💥 Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main() 