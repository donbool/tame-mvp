#!/usr/bin/env python3
"""
TameSDK CLI - Command-line interface for policy enforcement and session management.
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

from .client import Client
from .config import get_config
from .exceptions import TameSDKException


def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display."""
    try:
        if hasattr(timestamp_str, 'isoformat'):
            timestamp_str = timestamp_str.isoformat()
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp_str)


def format_decision(decision) -> str:
    """Format enforcement decision for display."""
    color_map = {
        "allow": "\033[92m",  # Green
        "deny": "\033[91m",   # Red
        "approve": "\033[93m" # Yellow
    }
    reset_color = "\033[0m"
    
    action_value = decision.action.value if hasattr(decision.action, 'value') else decision.action
    color = color_map.get(action_value, "")
    
    return f"""
{color}Decision: {action_value.upper()}{reset_color}
Session ID: {decision.session_id}
Tool: {decision.tool_name}
Rule: {decision.rule_name or 'N/A'}
Reason: {decision.reason}
Policy Version: {decision.policy_version}
Log ID: {decision.log_id}
Timestamp: {format_timestamp(decision.timestamp)}
"""


def cmd_status(args):
    """Handle status command."""
    try:
        with Client(api_url=args.api_url) as client:
            policy_info = client.get_policy_info()
            
            print("✅ TameSDK Connection: OK")
            print(f"📋 Policy Version: {policy_info.version}")
            print(f"📊 Rules Count: {policy_info.rules_count}")
            print(f"🕐 Last Updated: {format_timestamp(policy_info.last_updated)}")
            print(f"🆔 Session ID: {client.session_id}")
            
            if client.agent_id:
                print(f"🤖 Agent ID: {client.agent_id}")
            if client.user_id:
                print(f"👤 User ID: {client.user_id}")
                
        return 0
        
    except Exception as e:
        print(f"❌ Failed to connect to Tame API: {e}")
        return 1


def cmd_test(args):
    """Handle test command."""
    try:
        # Parse tool arguments
        tool_args = {}
        if args.args:
            try:
                tool_args = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in --args: {e}")
                return 1
        
        with Client(api_url=args.api_url) as client:
            decision = client.enforce(
                tool_name=args.tool,
                tool_args=tool_args,
                raise_on_deny=False,
                raise_on_approve=False
            )
            
            print(format_decision(decision))
            
            return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_policy(args):
    """Handle policy info command."""
    try:
        with Client(api_url=args.api_url) as client:
            policy_info = client.get_policy_info()
            
            print("\nCurrent Policy Information:")
            print("=" * 40)
            print(f"Version: {policy_info.version}")
            print(f"Hash: {policy_info.hash}")
            print(f"Rules Count: {policy_info.rules_count}")
            print(f"Last Updated: {format_timestamp(policy_info.last_updated)}")
            print(f"Active: {'Yes' if policy_info.active else 'No'}")
            
            if policy_info.description:
                print(f"Description: {policy_info.description}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_interactive(args):
    """Handle interactive mode."""
    print("🚀 TameSDK Interactive Mode")
    print("Type 'help' for available commands, 'quit' to exit")
    
    try:
        with Client(api_url=args.api_url) as client:
            while True:
                try:
                    command = input("\ntamesdk> ").strip()
                    
                    if command in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    elif command == 'help':
                        print("""
Available commands:
  test <tool_name> [args]  - Test a tool call
  status                   - Check API status  
  policy                   - Show policy info
  config                   - Show configuration
  help                     - Show this help
  quit                     - Exit interactive mode
                        """)
                    elif command == 'status':
                        cmd_status(args)
                    elif command == 'policy':
                        cmd_policy(args)
                    elif command == 'config':
                        config = get_config()
                        print(f"API URL: {config.api_url}")
                        print(f"Session ID: {config.session_id}")
                        print(f"Bypass mode: {config.bypass_mode}")
                    elif command.startswith('test '):
                        parts = command.split(' ', 2)
                        tool_name = parts[1] if len(parts) > 1 else ""
                        tool_args_str = parts[2] if len(parts) > 2 else ""
                        
                        if not tool_name:
                            print("❌ Please specify a tool name")
                            continue
                        
                        # Parse args
                        tool_args = {}
                        if tool_args_str:
                            try:
                                tool_args = json.loads(tool_args_str)
                            except json.JSONDecodeError:
                                # Try simple key=value format
                                for pair in tool_args_str.split(','):
                                    if '=' in pair:
                                        key, value = pair.split('=', 1)
                                        tool_args[key.strip()] = value.strip()
                        
                        decision = client.enforce(
                            tool_name,
                            tool_args,
                            raise_on_deny=False,
                            raise_on_approve=False
                        )
                        print(format_decision(decision))
                        
                    elif command:
                        print(f"❌ Unknown command: {command}")
                        print("Type 'help' for available commands")
                        
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return 1
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TameSDK CLI - Policy enforcement and session management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tamesdk status
  tamesdk test read_file --args '{"path": "/tmp/file.txt"}'
  tamesdk interactive
        """
    )
    
    # Global options
    parser.add_argument(
        "--api-url",
        default=os.getenv("TAME_API_URL", "http://localhost:8000"),
        help="Tame API URL (default: http://localhost:8000)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check API connection status")
    status_parser.set_defaults(func=cmd_status)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a tool call against policy")
    test_parser.add_argument("tool", help="Tool name")
    test_parser.add_argument("--args", help="Tool arguments as JSON")
    test_parser.set_defaults(func=cmd_test)
    
    # Policy command
    policy_parser = subparsers.add_parser("policy", help="Show current policy information")
    policy_parser.set_defaults(func=cmd_policy)
    
    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive mode")
    interactive_parser.set_defaults(func=cmd_interactive)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())