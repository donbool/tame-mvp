from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.services.policy_engine import policy_engine
from app.models.policy_version import PolicyVersion

logger = structlog.get_logger()
router = APIRouter()

class PolicyInfo(BaseModel):
    """Current policy information."""
    version: str
    hash: str
    rules_count: int
    rules: List[Dict[str, Any]]

class PolicyValidationRequest(BaseModel):
    """Request to validate a policy configuration."""
    policy_content: str
    description: Optional[str] = None

class PolicyValidationResponse(BaseModel):
    """Response from policy validation."""
    is_valid: bool
    errors: List[str]
    rules_count: int
    version: Optional[str] = None

@router.get("/policy/current", response_model=PolicyInfo)
async def get_current_policy():
    """Get information about the currently loaded policy."""
    
    try:
        policy_info = policy_engine.get_policy_info()
        
        return PolicyInfo(
            version=policy_info["version"],
            hash=policy_info["hash"],
            rules_count=policy_info["rules_count"],
            rules=policy_info["rules"]
        )
        
    except Exception as e:
        logger.error("Failed to get current policy info", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/policy/validate", response_model=PolicyValidationResponse)
async def validate_policy(request: PolicyValidationRequest):
    """Validate a policy configuration without applying it."""
    
    try:
        import yaml
        import tempfile
        import os
        
        # Parse the YAML content
        try:
            policy_data = yaml.safe_load(request.policy_content)
        except yaml.YAMLError as e:
            return PolicyValidationResponse(
                is_valid=False,
                errors=[f"Invalid YAML syntax: {str(e)}"],
                rules_count=0
            )
        
        # Validate policy structure
        errors = []
        
        if not isinstance(policy_data, dict):
            errors.append("Policy must be a YAML object")
            return PolicyValidationResponse(
                is_valid=False,
                errors=errors,
                rules_count=0
            )
        
        # Check required fields
        if "version" not in policy_data:
            errors.append("Policy must have a 'version' field")
        
        if "rules" not in policy_data:
            errors.append("Policy must have a 'rules' field")
        elif not isinstance(policy_data["rules"], list):
            errors.append("'rules' must be a list")
        else:
            # Validate each rule
            rules = policy_data["rules"]
            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    errors.append(f"Rule {i} must be an object")
                    continue
                
                # Check required rule fields
                if "name" not in rule:
                    errors.append(f"Rule {i} must have a 'name' field")
                
                if "action" not in rule:
                    errors.append(f"Rule {i} must have an 'action' field")
                elif rule["action"] not in ["allow", "deny", "approve"]:
                    errors.append(f"Rule {i} action must be 'allow', 'deny', or 'approve'")
                
                if "tools" in rule and not isinstance(rule["tools"], list):
                    errors.append(f"Rule {i} 'tools' field must be a list")
        
        # If no errors so far, try to load the policy in a temporary engine
        if not errors:
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
                    f.write(request.policy_content)
                    temp_file = f.name
                
                # Try to load policy
                from app.services.policy_engine import PolicyEngine
                temp_engine = PolicyEngine()
                temp_engine.load_policy(temp_file)
                
                # Clean up
                os.unlink(temp_file)
                
            except Exception as e:
                errors.append(f"Failed to load policy: {str(e)}")
        
        is_valid = len(errors) == 0
        rules_count = len(policy_data.get("rules", [])) if is_valid else 0
        version = policy_data.get("version") if is_valid else None
        
        return PolicyValidationResponse(
            is_valid=is_valid,
            errors=errors,
            rules_count=rules_count,
            version=version
        )
        
    except Exception as e:
        logger.error("Failed to validate policy", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/policy/reload")
async def reload_policy():
    """Reload the policy from the configuration file."""
    
    try:
        old_version = policy_engine.policy_version
        policy_engine.load_policy()
        new_version = policy_engine.policy_version
        
        logger.info("Policy reloaded", 
                   old_version=old_version,
                   new_version=new_version)
        
        return {
            "status": "reloaded",
            "old_version": old_version,
            "new_version": new_version,
            "rules_count": len(policy_engine.rules)
        }
        
    except Exception as e:
        logger.error("Failed to reload policy", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to reload policy")

@router.get("/policy/versions")
async def list_policy_versions(
    db: AsyncSession = Depends(get_db)
):
    """List all stored policy versions."""
    
    try:
        from sqlalchemy import select, desc
        
        query = select(PolicyVersion).order_by(desc(PolicyVersion.created_at))
        result = await db.execute(query)
        versions = result.scalars().all()
        
        return [
            {
                "id": str(version.id),
                "version": version.version,
                "created_at": version.created_at,
                "description": version.description,
                "created_by": version.created_by,
                "is_active": version.is_active,
                "is_valid": version.is_valid,
                "policy_hash": version.policy_hash
            }
            for version in versions
        ]
        
    except Exception as e:
        logger.error("Failed to list policy versions", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/policy/test")
async def test_policy_rule(
    tool_name: str,
    tool_args: Optional[str] = None,
    session_context: Optional[str] = None
):
    """Test a tool call against the current policy (dry run)."""
    
    try:
        import json
        
        # Parse arguments
        parsed_args = {}
        if tool_args:
            try:
                parsed_args = json.loads(tool_args)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in tool_args")
        
        parsed_context = {}
        if session_context:
            try:
                parsed_context = json.loads(session_context)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in session_context")
        
        # Evaluate against policy
        decision = policy_engine.evaluate(
            tool_name=tool_name,
            tool_args=parsed_args,
            session_context=parsed_context
        )
        
        return {
            "tool_name": tool_name,
            "tool_args": parsed_args,
            "session_context": parsed_context,
            "decision": {
                "action": decision.action,
                "rule_name": decision.rule_name,
                "reason": decision.reason,
                "policy_version": decision.policy_version
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to test policy rule", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") 