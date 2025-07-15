#!/usr/bin/env python3
"""
TameSDK Command Line Interface

A comprehensive CLI for managing policies, testing tools, and monitoring agent behavior.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import argparse
import logging
from datetime import datetime

import httpx
import yaml

from .client import Client, AsyncClient
from .config import configure, get_config, load_config, save_config
from .exceptions import TameSDKException, PolicyViolationException, ApprovalRequiredException
from .utils import format_policy_error, create_session_summary, validate_tool_call


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tamesdk.cli')


class TameCLI:
    """Main CLI class for TameSDK operations."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.config = None
    
    def setup_client(self, args) -> None:
        """Setup the TameSDK client from CLI arguments."""
        # Configure from CLI args
        config_updates = {}
        
        if hasattr(args, 'api_url') and args.api_url:
            config_updates['api_url'] = args.api_url
        if hasattr(args, 'api_key') and args.api_key:
            config_updates['api_key'] = args.api_key
        if hasattr(args, 'session_id') and args.session_id:
            config_updates['session_id'] = args.session_id
        if hasattr(args, 'agent_id') and args.agent_id:
            config_updates['agent_id'] = args.agent_id
        if hasattr(args, 'user_id') and args.user_id:
            config_updates['user_id'] = args.user_id
        if hasattr(args, 'timeout') and args.timeout:
            config_updates['timeout'] = args.timeout
        if hasattr(args, 'bypass') and args.bypass:
            config_updates['bypass_mode'] = True
        
        # Load config from file if specified
        if hasattr(args, 'config') and args.config:
            self.config = load_config(args.config)
            # Override with CLI args
            for key, value in config_updates.items():
                setattr(self.config, key, value)
        else:
            self.config = configure(**config_updates)
        
        self.client = Client(config=self.config)
    
    def print_json(self, data: Any, indent: int = 2) -> None:
        """Print data as formatted JSON."""
        print(json.dumps(data, indent=indent, default=str))
    
    def print_table(self, headers: List[str], rows: List[List[str]], title: Optional[str] = None) -> None:
        """Print data in table format."""
        if title:
            print(f"\n{title}")
            print("=" * len(title))
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print header
        header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        print(header_line)
        print("-" * len(header_line))
        
        # Print rows
        for row in rows:
            row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
            print(row_line)
        print()
    
    def cmd_status(self, args) -> None:
        """Check the status of the Tame API server."""
        self.setup_client(args)
        
        try:
            # Try to get policy info to test connection
            policy_info = self.client.get_policy_info()
            
            print("✅ Tame API Connection: OK")
            print(f"📋 Policy Version: {policy_info.version}")
            print(f"📊 Rules Count: {policy_info.rules_count}")
            print(f"🕐 Last Updated: {policy_info.last_updated}")
            print(f"🆔 Session ID: {self.client.session_id}")
            
            if self.client.agent_id:
                print(f"🤖 Agent ID: {self.client.agent_id}")
            if self.client.user_id:
                print(f"👤 User ID: {self.client.user_id}")
                
        except Exception as e:
            print(f"❌ Failed to connect to Tame API: {e}")
            sys.exit(1)
    
    def cmd_test_tool(self, args) -> None:
        """Test a tool call against the current policy."""
        self.setup_client(args)
        
        # Parse tool arguments
        tool_args = {}
        if args.args:
            try:
                if args.args.startswith('{'):
                    tool_args = json.loads(args.args)
                else:
                    # Simple key=value format
                    for pair in args.args.split(','):
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            tool_args[key.strip()] = value.strip()
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in tool arguments: {e}")
                sys.exit(1)
        
        try:
            if args.dry_run:
                # Use policy test endpoint
                result = self.client.test_policy(args.tool_name, tool_args)
                print("🧪 Policy Test Result:")
                self.print_json(result)
            else:
                # Actually enforce the policy
                decision = self.client.enforce(
                    args.tool_name, 
                    tool_args,
                    raise_on_deny=False,
                    raise_on_approve=False
                )
                
                action_emoji = {
                    'allow': '✅',
                    'deny': '❌', 
                    'approve': '⏳'
                }
                
                print(f"{action_emoji.get(decision.action.value, '❓')} Policy Decision: {decision.action.value.upper()}")
                print(f"📝 Reason: {decision.reason}")
                if decision.rule_name:
                    print(f"📋 Rule: {decision.rule_name}")
                print(f"🆔 Log ID: {decision.log_id}")
                
                if args.verbose:
                    print("\n📊 Full Decision Details:")
                    self.print_json({
                        "session_id": decision.session_id,
                        "action": decision.action.value,
                        "rule_name": decision.rule_name,
                        "reason": decision.reason,
                        "policy_version": decision.policy_version,
                        "log_id": decision.log_id,
                        "timestamp": decision.timestamp.isoformat(),
                        "tool_name": decision.tool_name,
                        "tool_args": decision.tool_args
                    })
                    
        except (PolicyViolationException, ApprovalRequiredException) as e:
            print(format_policy_error(e))
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error testing tool: {e}")
            sys.exit(1)
    
    def cmd_session_logs(self, args) -> None:
        """Get logs for a session."""
        self.setup_client(args)
        
        try:
            session_id = args.session_id if hasattr(args, 'session_id') else None
            logs = self.client.get_session_logs(session_id)
            
            if not logs:
                print("📝 No logs found for this session")
                return
            
            if args.format == 'json':
                self.print_json([log.__dict__ for log in logs])
            elif args.format == 'summary':
                # Convert logs to dict format for summary
                log_dicts = []
                for log in logs:
                    log_dict = {
                        'tool_name': log.tool_name,
                        'timestamp': log.timestamp.isoformat(),
                        'decision': {
                            'action': log.decision.action.value if log.decision else None
                        },
                        'error': log.error
                    }
                    log_dicts.append(log_dict)
                
                summary = create_session_summary(log_dicts)
                print("📊 Session Summary:")
                self.print_json(summary)
            else:
                # Table format
                headers = ["Timestamp", "Tool", "Action", "Rule", "Status"]
                rows = []
                
                for log in logs:
                    status = "✅ Success" if log.error is None else "❌ Error"
                    action = log.decision.action.value if log.decision else "unknown"
                    rule = log.decision.rule_name if log.decision else ""
                    
                    rows.append([
                        log.timestamp.strftime("%H:%M:%S"),
                        log.tool_name,
                        action,
                        rule or "-",
                        status
                    ])
                
                self.print_table(headers, rows, f"Session Logs ({len(logs)} entries)")
                
        except Exception as e:
            print(f"❌ Error getting session logs: {e}")
            sys.exit(1)
    
    def cmd_policy_info(self, args) -> None:
        """Get information about the current policy."""
        self.setup_client(args)
        
        try:
            policy_info = self.client.get_policy_info()
            
            print("📋 Current Policy Information:")
            print(f"   Version: {policy_info.version}")
            print(f"   Description: {policy_info.description or 'No description'}")
            print(f"   Rules Count: {policy_info.rules_count}")
            print(f"   Last Updated: {policy_info.last_updated}")
            print(f"   Hash: {policy_info.hash}")
            print(f"   Active: {'✅ Yes' if policy_info.active else '❌ No'}")
            
            if args.verbose:
                print("\n📊 Full Policy Details:")
                self.print_json(policy_info.__dict__)
                
        except Exception as e:
            print(f"❌ Error getting policy info: {e}")
            sys.exit(1)
    
    def cmd_config(self, args) -> None:
        """Manage configuration."""
        if args.config_action == 'show':
            config = get_config()
            print("⚙️  Current Configuration:")
            self.print_json(config.__dict__)
            
        elif args.config_action == 'save':
            if not args.file:
                print("❌ Please specify a file path with --file")
                sys.exit(1)
            
            config = get_config()
            save_config(config, args.file)
            print(f"✅ Configuration saved to {args.file}")
            
        elif args.config_action == 'load':
            if not args.file:
                print("❌ Please specify a file path with --file")
                sys.exit(1)
            
            try:
                config = load_config(args.file)
                configure(**config.__dict__)
                print(f"✅ Configuration loaded from {args.file}")
            except Exception as e:
                print(f"❌ Error loading configuration: {e}")
                sys.exit(1)
    
    def cmd_interactive(self, args) -> None:
        """Start interactive mode."""
        self.setup_client(args)
        
        print("🚀 TameSDK Interactive Mode")
        print("Type 'help' for available commands, 'quit' to exit")
        
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
  logs                     - Show session logs
  config                   - Show configuration
  help                     - Show this help
  quit                     - Exit interactive mode
                    """)
                elif command == 'status':
                    self.cmd_status(args)
                elif command == 'policy':
                    self.cmd_policy_info(args)
                elif command == 'logs':
                    self.cmd_session_logs(args)
                elif command == 'config':
                    config = get_config()
                    self.print_json(config.__dict__)
                elif command.startswith('test '):
                    parts = command.split(' ', 2)
                    tool_name = parts[1] if len(parts) > 1 else ""
                    tool_args_str = parts[2] if len(parts) > 2 else ""
                    
                    if not tool_name:
                        print("❌ Please specify a tool name")
                        continue
                    
                    # Create a mock args object for test_tool
                    mock_args = type('Args', (), {
                        'tool_name': tool_name,
                        'args': tool_args_str,
                        'dry_run': False,
                        'verbose': True
                    })()
                    
                    self.cmd_test_tool(mock_args)
                elif command:
                    print(f"❌ Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='tamesdk',
        description='TameSDK CLI - Runtime control for AI agents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tamesdk status                                    # Check API status
  tamesdk test read_file --args '{"path": "/tmp/file.txt"}'  # Test a tool
  tamesdk logs --format table                      # View session logs
  tamesdk policy                                   # Show policy info
  tamesdk interactive                              # Start interactive mode
  
Configuration:
  Set TAME_API_URL, TAME_API_KEY environment variables
  Or use --config to load from file
        """
    )
    
    # Global options
    parser.add_argument('--api-url', help='Tame API URL')
    parser.add_argument('--api-key', help='API key for authentication')
    parser.add_argument('--session-id', help='Session ID')
    parser.add_argument('--agent-id', help='Agent ID')
    parser.add_argument('--user-id', help='User ID')
    parser.add_argument('--timeout', type=float, help='Request timeout')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--bypass', action='store_true', help='Enable bypass mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check API status')
    
    # Test tool command
    test_parser = subparsers.add_parser('test', help='Test a tool call')
    test_parser.add_argument('tool_name', help='Name of the tool to test')
    test_parser.add_argument('--args', help='Tool arguments (JSON or key=value pairs)')
    test_parser.add_argument('--dry-run', action='store_true', help='Test policy without logging')
    
    # Session logs command
    logs_parser = subparsers.add_parser('logs', help='View session logs')
    logs_parser.add_argument('--session-id', help='Specific session ID to view')
    logs_parser.add_argument('--format', choices=['table', 'json', 'summary'], 
                           default='table', help='Output format')
    
    # Policy info command
    policy_parser = subparsers.add_parser('policy', help='Show policy information')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('config_action', choices=['show', 'save', 'load'], 
                             help='Configuration action')
    config_parser.add_argument('--file', help='Configuration file path')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive mode')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Set up logging level
    if args.verbose:
        logging.getLogger('tamesdk').setLevel(logging.DEBUG)
    
    cli = TameCLI()
    
    try:
        # Route to appropriate command handler
        if args.command == 'status':
            cli.cmd_status(args)
        elif args.command == 'test':
            cli.cmd_test_tool(args)
        elif args.command == 'logs':
            cli.cmd_session_logs(args)
        elif args.command == 'policy':
            cli.cmd_policy_info(args)
        elif args.command == 'config':
            cli.cmd_config(args)
        elif args.command == 'interactive':
            cli.cmd_interactive(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if cli.client:
            cli.client.close()


if __name__ == '__main__':
    main()