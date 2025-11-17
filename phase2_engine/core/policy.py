# phase2_engine/core/policy.py
"""
Policy enforcement for automated actions.
Validates that automation actions comply with organizational policies.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from enum import Enum


class ApprovalLevel(Enum):
    """Required approval level for actions."""
    NONE = "none"
    ANALYST = "analyst"
    MANAGER = "manager"
    CISO = "ciso"


class ActionPolicy:
    """Policy definition for an action type."""
    
    def __init__(
        self,
        action: str,
        approval_required: ApprovalLevel = ApprovalLevel.NONE,
        max_automated_count: Optional[int] = None,
        business_hours_only: bool = False,
        requires_backup: bool = False,
    ):
        self.action = action
        self.approval_required = approval_required
        self.max_automated_count = max_automated_count
        self.business_hours_only = business_hours_only
        self.requires_backup = requires_backup


class PolicyEngine:
    """
    Enforces organizational policies for automated actions.
    """
    
    def __init__(self):
        self.policies: Dict[str, ActionPolicy] = self._load_default_policies()
        self.execution_counts: Dict[str, int] = {}
    
    def _load_default_policies(self) -> Dict[str, ActionPolicy]:
        """Load default action policies."""
        return {
            # Low-risk actions (no approval needed)
            "send_alert": ActionPolicy("send_alert", ApprovalLevel.NONE),
            "create_ticket": ActionPolicy("create_ticket", ApprovalLevel.NONE),
            "enable_waf_rule": ActionPolicy("enable_waf_rule", ApprovalLevel.NONE, max_automated_count=10),
            
            # Medium-risk actions (analyst approval)
            "block_ip": ActionPolicy("block_ip", ApprovalLevel.ANALYST, max_automated_count=50),
            "block_url": ActionPolicy("block_url", ApprovalLevel.ANALYST, max_automated_count=100),
            "quarantine_file": ActionPolicy("quarantine_file", ApprovalLevel.ANALYST),
            "scan_system": ActionPolicy("scan_system", ApprovalLevel.ANALYST, business_hours_only=True),
            
            # High-risk actions (manager approval)
            "isolate_host": ActionPolicy("isolate_host", ApprovalLevel.MANAGER, max_automated_count=5),
            "rotate_credentials": ActionPolicy("rotate_credentials", ApprovalLevel.MANAGER, requires_backup=True),
        }
    
    def validate_action(
        self,
        action: str,
        params: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate if an action can be executed according to policy.
        
        Args:
            action: Action type
            params: Action parameters
            context: Execution context
        
        Returns:
            Validation result with status and reasons
        """
        policy = self.policies.get(action)
        
        if not policy:
            return {
                "allowed": False,
                "reason": f"No policy defined for action: {action}",
                "approval_required": ApprovalLevel.CISO,
            }
        
        # Check execution count limits
        if policy.max_automated_count is not None:
            current_count = self.execution_counts.get(action, 0)
            if current_count >= policy.max_automated_count:
                return {
                    "allowed": False,
                    "reason": f"Max automated executions reached: {policy.max_automated_count}",
                    "approval_required": policy.approval_required,
                }
        
        # Check business hours requirement
        if policy.business_hours_only:
            if not self._is_business_hours():
                return {
                    "allowed": False,
                    "reason": "Action only allowed during business hours",
                    "approval_required": policy.approval_required,
                }
        
        # Check if backup is required
        if policy.requires_backup:
            if not params.get("backup_completed"):
                return {
                    "allowed": False,
                    "reason": "Backup must be completed before executing this action",
                    "approval_required": policy.approval_required,
                }
        
        # If approval required, return status
        if policy.approval_required != ApprovalLevel.NONE:
            return {
                "allowed": False,
                "reason": f"Approval required: {policy.approval_required.value}",
                "approval_required": policy.approval_required,
                "can_proceed_with_approval": True,
            }
        
        # All checks passed
        return {
            "allowed": True,
            "reason": "Policy validation passed",
            "approval_required": ApprovalLevel.NONE,
        }
    
    def record_execution(self, action: str):
        """Record that an action was executed."""
        self.execution_counts[action] = self.execution_counts.get(action, 0) + 1
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours."""
        # Simplified check - in production, this would check actual time and calendar
        return True
    
    def get_execution_stats(self) -> Dict[str, int]:
        """Get execution count statistics."""
        return self.execution_counts.copy()
    
    def reset_counts(self):
        """Reset execution counts (e.g., daily reset)."""
        self.execution_counts.clear()
