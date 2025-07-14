#!/usr/bin/env python3
"""
Comprehensive test runner for tame policy enforcement.
Runs multiple scenarios and provides detailed analysis.
"""

import sys
import os
import json
import time
import argparse
import yaml
from typing import Dict, Any, List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from mock_agent import MockAIAgent, AgentTask


class tameTestRunner:
    """Comprehensive test runner for tame policy enforcement."""
    
    def __init__(self, api_url: str = "http://localhost:8000", verbose: bool = False):
        self.api_url = api_url
        self.verbose = verbose
        self.console = Console()
        
        # Test results
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def run_all_scenarios(self, agent_id: str = "test-runner", user_id: str = "test-user") -> Dict[str, Any]:
        """Run all predefined test scenarios."""
        
        self.console.print("\n🚀 [bold blue]tame Policy Enforcement Test Suite[/bold blue]")
        self.console.print(f"API URL: {self.api_url}")
        self.console.print(f"Agent ID: {agent_id}")
        self.console.print(f"User ID: {user_id}")
        
        self.start_time = datetime.now()
        
        # Create agent for testing
        agent = MockAIAgent(
            agent_id=agent_id,
            user_id=user_id,
            api_url=self.api_url
        )
        
        scenarios = agent.get_test_scenarios()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            for scenario_name, scenario_data in scenarios.items():
                task = progress.add_task(f"Running {scenario_name}...", total=None)
                
                try:
                    result = agent.run_scenario(scenario_name)
                    result["test_status"] = "completed"
                    self.test_results.append(result)
                    
                    progress.update(task, description=f"✅ Completed {scenario_name}")
                    
                except Exception as e:
                    error_result = {
                        "scenario": scenario_name,
                        "test_status": "failed",
                        "error": str(e),
                        "total_tasks": 0,
                        "results": [],
                        "summary": {}
                    }
                    self.test_results.append(error_result)
                    
                    progress.update(task, description=f"❌ Failed {scenario_name}")
                
                # Small delay between scenarios
                time.sleep(1)
        
        self.end_time = datetime.now()
        
        # Generate comprehensive report
        report = self.generate_report()
        
        # Display results
        self.display_results()
        
        return report
    
    def run_single_scenario(self, scenario_name: str, agent_id: str = "test-runner", user_id: str = "test-user") -> Dict[str, Any]:
        """Run a single test scenario."""
        
        self.console.print(f"\n🎯 [bold blue]Running Single Scenario: {scenario_name}[/bold blue]")
        
        self.start_time = datetime.now()
        
        agent = MockAIAgent(
            agent_id=agent_id,
            user_id=user_id,
            api_url=self.api_url
        )
        
        try:
            result = agent.run_scenario(scenario_name)
            result["test_status"] = "completed"
            self.test_results.append(result)
            
        except Exception as e:
            error_result = {
                "scenario": scenario_name,
                "test_status": "failed",
                "error": str(e),
                "total_tasks": 0,
                "results": [],
                "summary": {}
            }
            self.test_results.append(error_result)
        
        self.end_time = datetime.now()
        
        # Generate and display results
        report = self.generate_report()
        self.display_results()
        
        return report
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        
        # Calculate overall statistics
        total_scenarios = len(self.test_results)
        successful_scenarios = len([r for r in self.test_results if r["test_status"] == "completed"])
        
        total_tasks = sum(r.get("total_tasks", 0) for r in self.test_results)
        
        # Aggregate task outcomes
        allowed_count = 0
        denied_count = 0
        approval_required_count = 0
        error_count = 0
        
        policy_rules_triggered = {}
        
        for scenario_result in self.test_results:
            for task_result in scenario_result.get("results", []):
                status = task_result.get("status", "unknown")
                
                if status == "success":
                    allowed_count += 1
                elif status == "denied":
                    denied_count += 1
                elif status == "approval_required":
                    approval_required_count += 1
                elif status == "error":
                    error_count += 1
                
                # Track policy rules
                decision = task_result.get("decision")
                if decision and hasattr(decision, 'rule_name') and decision.rule_name:
                    rule_name = decision.rule_name
                    policy_rules_triggered[rule_name] = policy_rules_triggered.get(rule_name, 0) + 1
        
        # Calculate execution time
        execution_time = None
        if self.start_time and self.end_time:
            execution_time = (self.end_time - self.start_time).total_seconds()
        
        return {
            "test_run": {
                "timestamp": self.start_time.isoformat() if self.start_time else None,
                "execution_time_seconds": execution_time,
                "api_url": self.api_url
            },
            "scenario_summary": {
                "total_scenarios": total_scenarios,
                "successful_scenarios": successful_scenarios,
                "failed_scenarios": total_scenarios - successful_scenarios,
                "success_rate": successful_scenarios / total_scenarios if total_scenarios > 0 else 0
            },
            "task_summary": {
                "total_tasks": total_tasks,
                "allowed": allowed_count,
                "denied": denied_count,
                "approval_required": approval_required_count,
                "errors": error_count,
                "policy_effectiveness": {
                    "enforcement_rate": (denied_count + approval_required_count) / total_tasks if total_tasks > 0 else 0,
                    "success_rate": allowed_count / total_tasks if total_tasks > 0 else 0
                }
            },
            "policy_analysis": {
                "rules_triggered": policy_rules_triggered,
                "most_triggered_rule": max(policy_rules_triggered.items(), key=lambda x: x[1]) if policy_rules_triggered else None
            },
            "detailed_results": self.test_results
        }
    
    def display_results(self):
        """Display test results with rich formatting."""
        
        if not self.test_results:
            self.console.print("❌ No test results to display")
            return
        
        # Overall summary
        report = self.generate_report()
        
        # Scenario summary table
        scenario_table = Table(title="📊 Scenario Results")
        scenario_table.add_column("Scenario", style="cyan")
        scenario_table.add_column("Status", style="green")
        scenario_table.add_column("Tasks", justify="right")
        scenario_table.add_column("Allowed", justify="right", style="green")
        scenario_table.add_column("Denied", justify="right", style="red")
        scenario_table.add_column("Approval Required", justify="right", style="yellow")
        scenario_table.add_column("Errors", justify="right", style="magenta")
        
        for result in self.test_results:
            scenario_name = result.get("scenario", "Unknown")
            status = "✅ Completed" if result.get("test_status") == "completed" else "❌ Failed"
            total_tasks = result.get("total_tasks", 0)
            
            # Count outcomes for this scenario
            allowed = len([r for r in result.get("results", []) if r.get("status") == "success"])
            denied = len([r for r in result.get("results", []) if r.get("status") == "denied"])
            approval = len([r for r in result.get("results", []) if r.get("status") == "approval_required"])
            errors = len([r for r in result.get("results", []) if r.get("status") == "error"])
            
            scenario_table.add_row(
                scenario_name,
                status,
                str(total_tasks),
                str(allowed),
                str(denied),
                str(approval),
                str(errors)
            )
        
        self.console.print("\n")
        self.console.print(scenario_table)
        
        # Overall statistics
        task_summary = report["task_summary"]
        policy_summary = report["policy_analysis"]
        
        stats_panel = Panel(
            f"""
📈 [bold]Overall Statistics[/bold]

• Total Tasks: {task_summary['total_tasks']}
• Allowed: {task_summary['allowed']} ({task_summary['allowed']/task_summary['total_tasks']*100:.1f}%)
• Denied: {task_summary['denied']} ({task_summary['denied']/task_summary['total_tasks']*100:.1f}%)
• Approval Required: {task_summary['approval_required']} ({task_summary['approval_required']/task_summary['total_tasks']*100:.1f}%)
• Errors: {task_summary['errors']} ({task_summary['errors']/task_summary['total_tasks']*100:.1f}%)

🛡️ [bold]Policy Effectiveness[/bold]

• Enforcement Rate: {task_summary['policy_effectiveness']['enforcement_rate']*100:.1f}%
• Success Rate: {task_summary['policy_effectiveness']['success_rate']*100:.1f}%

📋 [bold]Most Triggered Rule[/bold]

• {policy_summary['most_triggered_rule'][0] if policy_summary['most_triggered_rule'] else 'None'}: {policy_summary['most_triggered_rule'][1] if policy_summary['most_triggered_rule'] else 0} times
            """.strip(),
            title="Test Summary",
            border_style="blue"
        )
        
        self.console.print("\n")
        self.console.print(stats_panel)
        
        # Execution time
        if report["test_run"]["execution_time_seconds"]:
            exec_time = report["test_run"]["execution_time_seconds"]
            self.console.print(f"\n⏱️  Total execution time: {exec_time:.2f} seconds")
        
        # Detailed results if verbose
        if self.verbose:
            self.display_detailed_results()
    
    def display_detailed_results(self):
        """Display detailed task-by-task results."""
        
        self.console.print("\n📝 [bold]Detailed Results[/bold]")
        
        for scenario_result in self.test_results:
            scenario_name = scenario_result.get("scenario", "Unknown")
            
            self.console.print(f"\n🎯 [bold cyan]{scenario_name}[/bold cyan]")
            
            for i, task_result in enumerate(scenario_result.get("results", []), 1):
                status = task_result.get("status", "unknown")
                
                status_icons = {
                    "success": "✅",
                    "denied": "❌", 
                    "approval_required": "⏳",
                    "error": "💥"
                }
                
                icon = status_icons.get(status, "❓")
                
                self.console.print(f"  {i}. {icon} {status.upper()}")
                
                if self.verbose and "decision" in task_result:
                    decision = task_result["decision"]
                    if hasattr(decision, 'rule_name'):
                        self.console.print(f"     Rule: {decision.rule_name}")
                        self.console.print(f"     Reason: {decision.reason}")
    
    def save_report(self, filename: str = None):
        """Save test report to file."""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tame_test_report_{timestamp}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.console.print(f"\n💾 Report saved to: {filename}")
        
        return filename


def main():
    """Main function for command-line usage."""
    
    parser = argparse.ArgumentParser(description="tame Policy Enforcement Test Runner")
    
    parser.add_argument("--api-url", default="http://localhost:8000", help="tame API URL")
    parser.add_argument("--agent-id", default="test-runner", help="Agent identifier")
    parser.add_argument("--user-id", default="test-user", help="User identifier")
    
    parser.add_argument("--scenario", help="Run specific scenario only")
    parser.add_argument("--all", action="store_true", help="Run all scenarios (default)")
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--save-report", help="Save report to file")
    
    parser.add_argument("--check-api", action="store_true", help="Check if tame API is running")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = tameTestRunner(api_url=args.api_url, verbose=args.verbose)
    
    try:
        # Check API if requested
        if args.check_api:
            import httpx
            try:
                response = httpx.get(f"{args.api_url}/health", timeout=5)
                if response.status_code == 200:
                    runner.console.print("✅ tame API is running and accessible")
                else:
                    runner.console.print(f"⚠️  tame API responded with status {response.status_code}")
            except Exception as e:
                runner.console.print(f"❌ Cannot connect to tame API: {e}")
                runner.console.print(f"   Make sure the backend is running at {args.api_url}")
                return 1
        
        # Run tests
        if args.scenario:
            report = runner.run_single_scenario(args.scenario, args.agent_id, args.user_id)
        else:
            report = runner.run_all_scenarios(args.agent_id, args.user_id)
        
        # Save report if requested
        if args.save_report:
            runner.save_report(args.save_report)
        
        # Return appropriate exit code
        task_summary = report["task_summary"]
        if task_summary["errors"] > 0:
            return 2  # Errors occurred
        elif task_summary["total_tasks"] == 0:
            return 3  # No tasks executed
        else:
            return 0  # Success
            
    except KeyboardInterrupt:
        runner.console.print("\n👋 Test run interrupted by user")
        return 130
    except Exception as e:
        runner.console.print(f"💥 Test runner failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main()) 