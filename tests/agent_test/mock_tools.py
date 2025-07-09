"""
Mock tool implementations for testing Runlok policy enforcement.
These simulate realistic tools that an AI agent might call.
"""

import json
import time
import random
import os
from typing import Dict, Any, Optional
from faker import Faker
from fake_useragent import UserAgent

fake = Faker()
ua = UserAgent()


class MockTools:
    """Collection of mock tools for agent testing."""
    
    def __init__(self):
        self.call_count = {}
        self.fake_data = {}
    
    def _track_call(self, tool_name: str):
        """Track tool call for analytics."""
        self.call_count[tool_name] = self.call_count.get(tool_name, 0) + 1
    
    # ========== FILE OPERATIONS ==========
    
    def read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Mock file reading operation."""
        self._track_call("read_file")
        
        # Simulate different file types
        if path.endswith((".yml", ".yaml")):
            content = "version: 1.0\ndata: mock_yaml_content"
        elif path.endswith(".json"):
            content = '{"mock": "json_data", "timestamp": "2024-01-01"}'
        elif path.endswith((".txt", ".md")):
            content = fake.text(max_nb_chars=500)
        else:
            content = fake.binary(length=256).hex()
        
        return {
            "success": True,
            "path": path,
            "content": content,
            "size": len(content),
            "encoding": encoding
        }
    
    def write_file(self, path: str, content: str, mode: str = "w") -> Dict[str, Any]:
        """Mock file writing operation."""
        self._track_call("write_file")
        
        return {
            "success": True,
            "path": path,
            "bytes_written": len(content),
            "mode": mode,
            "timestamp": time.time()
        }
    
    def delete_file(self, path: str, force: bool = False) -> Dict[str, Any]:
        """Mock file deletion operation."""
        self._track_call("delete_file")
        
        # Simulate different outcomes
        if "/system/" in path or "/root/" in path:
            return {
                "success": False,
                "error": "Permission denied",
                "path": path
            }
        
        return {
            "success": True,
            "path": path,
            "force": force,
            "timestamp": time.time()
        }
    
    def list_directory(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """Mock directory listing."""
        self._track_call("list_directory")
        
        # Generate fake file listing
        files = []
        for _ in range(random.randint(3, 10)):
            files.append({
                "name": fake.file_name(),
                "size": random.randint(100, 10000),
                "modified": fake.date_time().isoformat(),
                "type": random.choice(["file", "directory"])
            })
        
        return {
            "success": True,
            "path": path,
            "files": files,
            "recursive": recursive,
            "count": len(files)
        }
    
    # ========== WEB OPERATIONS ==========
    
    def make_web_request(self, url: str, method: str = "GET", headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Mock web request operation."""
        self._track_call("make_web_request")
        
        # Simulate response based on URL
        if "api.github.com" in url:
            data = {"login": fake.user_name(), "public_repos": random.randint(0, 100)}
        elif "httpbin.org" in url:
            data = {"origin": fake.ipv4(), "user-agent": ua.random}
        else:
            data = {"mock_response": True, "timestamp": time.time()}
        
        return {
            "success": True,
            "url": url,
            "method": method,
            "status_code": random.choice([200, 200, 200, 404, 500]),  # Mostly success
            "data": data,
            "headers": headers or {}
        }
    
    def search_web(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Mock web search operation."""
        self._track_call("search_web")
        
        results = []
        for i in range(min(limit, random.randint(3, 8))):
            results.append({
                "title": fake.sentence(),
                "url": fake.url(),
                "snippet": fake.text(max_nb_chars=200),
                "rank": i + 1
            })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total_found": random.randint(100, 10000)
        }
    
    # ========== SYSTEM OPERATIONS ==========
    
    def execute_command(self, command: str, shell: bool = False) -> Dict[str, Any]:
        """Mock system command execution."""
        self._track_call("execute_command")
        
        # Simulate different command outcomes
        if command.startswith(("rm ", "del ", "format")):
            return {
                "success": False,
                "error": "Dangerous command blocked",
                "command": command
            }
        elif command in ["ls", "dir", "pwd"]:
            output = "\n".join([fake.file_name() for _ in range(5)])
        elif command == "whoami":
            output = fake.user_name()
        else:
            output = fake.text(max_nb_chars=200)
        
        return {
            "success": True,
            "command": command,
            "output": output,
            "exit_code": 0,
            "shell": shell
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Mock system information retrieval."""
        self._track_call("get_system_info")
        
        return {
            "success": True,
            "os": random.choice(["Linux", "Windows", "macOS"]),
            "arch": random.choice(["x86_64", "arm64"]),
            "cpu_count": random.randint(2, 16),
            "memory_gb": random.randint(8, 64),
            "disk_usage": {
                "total": random.randint(500, 2000),
                "used": random.randint(100, 800),
                "free": random.randint(200, 1200)
            }
        }
    
    # ========== COMMUNICATION ==========
    
    def send_email(self, to: str, subject: str, body: str, cc: Optional[str] = None) -> Dict[str, Any]:
        """Mock email sending operation."""
        self._track_call("send_email")
        
        # Check for sensitive content
        sensitive_words = ["password", "secret", "token", "key"]
        is_sensitive = any(word in body.lower() for word in sensitive_words)
        
        return {
            "success": True,
            "to": to,
            "subject": subject,
            "message_id": fake.uuid4(),
            "timestamp": time.time(),
            "sensitive_content_detected": is_sensitive,
            "cc": cc
        }
    
    def send_slack_message(self, channel: str, message: str, username: Optional[str] = None) -> Dict[str, Any]:
        """Mock Slack message sending."""
        self._track_call("send_slack_message")
        
        return {
            "success": True,
            "channel": channel,
            "message": message,
            "timestamp": time.time(),
            "message_id": fake.uuid4(),
            "username": username or "runlok-bot"
        }
    
    # ========== DATA ACCESS ==========
    
    def query_database(self, query: str, database: str = "default") -> Dict[str, Any]:
        """Mock database query operation."""
        self._track_call("query_database")
        
        # Generate fake query results
        if "SELECT" in query.upper():
            rows = []
            for _ in range(random.randint(1, 20)):
                rows.append({
                    "id": random.randint(1, 1000),
                    "name": fake.name(),
                    "email": fake.email(),
                    "created_at": fake.date_time().isoformat()
                })
            result = {"rows": rows, "count": len(rows)}
        else:
            result = {"affected_rows": random.randint(1, 5)}
        
        return {
            "success": True,
            "query": query,
            "database": database,
            "result": result,
            "execution_time_ms": random.randint(10, 500)
        }
    
    def access_cloud_storage(self, action: str, path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """Mock cloud storage access."""
        self._track_call("access_cloud_storage")
        
        actions = {
            "read": {"content": fake.text(), "size": random.randint(100, 10000)},
            "write": {"bytes_written": len(content or ""), "version": fake.uuid4()},
            "list": {"files": [fake.file_name() for _ in range(random.randint(1, 10))]},
            "delete": {"deleted": True, "timestamp": time.time()}
        }
        
        return {
            "success": True,
            "action": action,
            "path": path,
            "result": actions.get(action, {}),
            "provider": "mock-cloud"
        }
    
    # ========== UTILITY METHODS ==========
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get statistics about tool usage."""
        return {
            "total_calls": sum(self.call_count.values()),
            "call_count": self.call_count.copy(),
            "most_used": max(self.call_count.items(), key=lambda x: x[1]) if self.call_count else None
        }
    
    def reset_stats(self):
        """Reset tool usage statistics."""
        self.call_count.clear()
        self.fake_data.clear()


# Global instance for easy access
mock_tools = MockTools()


def get_tool_function(tool_name: str):
    """Get a tool function by name."""
    return getattr(mock_tools, tool_name, None) 