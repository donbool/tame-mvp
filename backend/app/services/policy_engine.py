import yaml
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import structlog
import re

from app.core.config import settings

logger = structlog.get_logger()

@dataclass
class PolicyRule:
    """Represents a single policy rule."""
    name: str
    action: str  # allow, deny, approve
    tools: List[str]  # Tool name patterns
    conditions: Dict[str, Any]  # Additional conditions
    description: Optional[str] = None

@dataclass
class PolicyDecision:
    """Result of policy evaluation."""
    action: str  # allow, deny, approve
    rule_name: Optional[str]
    reason: str
    policy_version: str

class PolicyEngine:
    """Evaluates tool calls against YAML-defined policies."""
    
    def __init__(self):
        self.rules: List[PolicyRule] = []
        self.policy_version: str = "unknown"
        self.policy_hash: str = ""
        self.load_policy()
    
    def load_policy(self, policy_file: Optional[str] = None):
        """Load policy from YAML file."""
        if policy_file is None:
            policy_file = settings.POLICY_FILE
        
        policy_path = Path(policy_file)
        
        if not policy_path.exists():
            logger.warning("Policy file not found, using default allow-all policy", 
                         policy_file=policy_file)
            self._load_default_policy()
            return
        
        try:
            with open(policy_path, 'r') as f:
                policy_content = f.read()
                policy_data = yaml.safe_load(policy_content)
            
            # Calculate policy hash
            self.policy_hash = hashlib.sha256(policy_content.encode()).hexdigest()
            
            # Extract metadata
            self.policy_version = policy_data.get('version', 'unknown')
            
            # Parse rules
            self.rules = []
            for rule_data in policy_data.get('rules', []):
                rule = PolicyRule(
                    name=rule_data['name'],
                    action=rule_data['action'],
                    tools=rule_data.get('tools', ['*']),
                    conditions=rule_data.get('conditions', {}),
                    description=rule_data.get('description')
                )
                self.rules.append(rule)
            
            logger.info("Policy loaded successfully", 
                       version=self.policy_version, 
                       rules_count=len(self.rules),
                       policy_hash=self.policy_hash[:8])
            
        except Exception as e:
            logger.error("Failed to load policy file", 
                        policy_file=policy_file, error=str(e))
            self._load_default_policy()
    
    def _load_default_policy(self):
        """Load a default allow-all policy."""
        self.policy_version = "default-v1"
        self.policy_hash = "default"
        self.rules = [
            PolicyRule(
                name="default_allow_all",
                action="allow",
                tools=["*"],
                conditions={},
                description="Default allow-all policy"
            )
        ]
        logger.info("Loaded default allow-all policy")
    
    def evaluate(self, tool_name: str, tool_args: Dict[str, Any], 
                session_context: Optional[Dict[str, Any]] = None) -> PolicyDecision:
        """Evaluate a tool call against the policy rules."""
        
        session_context = session_context or {}
        
        logger.debug("Evaluating tool call", 
                    tool_name=tool_name, 
                    args_keys=list(tool_args.keys()),
                    session_context=session_context)
        
        # Evaluate rules in order
        for rule in self.rules:
            if self._rule_matches(rule, tool_name, tool_args, session_context):
                logger.info("Policy rule matched", 
                          rule_name=rule.name, 
                          action=rule.action,
                          tool_name=tool_name)
                
                return PolicyDecision(
                    action=rule.action,
                    rule_name=rule.name,
                    reason=f"Matched rule: {rule.name}",
                    policy_version=self.policy_version
                )
        
        # No rules matched - default deny
        logger.warning("No policy rules matched, defaulting to deny", 
                      tool_name=tool_name)
        
        return PolicyDecision(
            action="deny",
            rule_name=None,
            reason="No matching policy rule found",
            policy_version=self.policy_version
        )
    
    def _rule_matches(self, rule: PolicyRule, tool_name: str, 
                     tool_args: Dict[str, Any], 
                     session_context: Dict[str, Any]) -> bool:
        """Check if a rule matches the given tool call."""
        
        # Check tool name patterns
        tool_matches = False
        for tool_pattern in rule.tools:
            if tool_pattern == "*" or self._pattern_matches(tool_pattern, tool_name):
                tool_matches = True
                break
        
        if not tool_matches:
            return False
        
        # Check additional conditions
        return self._evaluate_conditions(rule.conditions, tool_args, session_context)
    
    def _pattern_matches(self, pattern: str, value: str) -> bool:
        """Check if a pattern matches a value (supports wildcards)."""
        # Convert shell-style wildcards to regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        return re.match(f"^{regex_pattern}$", value) is not None
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], 
                           tool_args: Dict[str, Any], 
                           session_context: Dict[str, Any]) -> bool:
        """Evaluate rule conditions."""
        
        for condition_key, condition_value in conditions.items():
            
            if condition_key == "arg_contains":
                # Check if tool args contain specific keys/values
                for arg_key, expected_value in condition_value.items():
                    if arg_key not in tool_args:
                        return False
                    if expected_value != "*" and tool_args[arg_key] != expected_value:
                        return False
            
            elif condition_key == "arg_not_contains":
                # Check that tool args don't contain specific keys/values
                for arg_key, forbidden_value in condition_value.items():
                    if arg_key in tool_args and tool_args[arg_key] == forbidden_value:
                        return False
            
            elif condition_key == "session_context":
                # Check session context conditions
                for context_key, expected_value in condition_value.items():
                    if context_key not in session_context:
                        return False
                    if expected_value != "*" and session_context[context_key] != expected_value:
                        return False
            
            # Add more condition types as needed
            
        return True
    
    def get_policy_info(self) -> Dict[str, Any]:
        """Get current policy information."""
        return {
            "version": self.policy_version,
            "hash": self.policy_hash,
            "rules_count": len(self.rules),
            "rules": [
                {
                    "name": rule.name,
                    "action": rule.action,
                    "tools": rule.tools,
                    "description": rule.description
                }
                for rule in self.rules
            ]
        }

# Global policy engine instance
policy_engine = PolicyEngine() 