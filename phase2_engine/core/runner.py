# phase2_engine/core/runner.py
"""
Playbook runner - executes playbooks against incidents.
Main execution engine for Phase-2 automation.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
import time

from .playbook_loader import load_playbook_by_id
from .playbook_dag import build_playbook_dag, topological_sort_dag
from .automation import AutomationEngine
from .policy import PolicyEngine


def run_playbook(
    playbook_id: str,
    context: Optional[Dict[str, Any]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Execute a playbook against an incident.
    
    Args:
        playbook_id: ID of playbook to execute
        context: Execution context (incident data, etc.)
        dry_run: If True, simulate actions without executing
    
    Returns:
        Execution result with summary and logs
    """
    start_time = time.time()
    
    # Load playbook
    playbook = load_playbook_by_id(playbook_id)
    if not playbook:
        return {
            "status": "error",
            "message": f"Playbook not found: {playbook_id}",
            "execution_time": 0,
        }
    
    # Build DAG
    dag = build_playbook_dag(playbook)
    if not dag.nodes:
        return {
            "status": "error",
            "message": "Playbook has no executable steps",
            "execution_time": 0,
        }
    
    # Initialize engines
    automation = AutomationEngine(dry_run=dry_run)
    policy = PolicyEngine()
    
    # Get execution order
    execution_order = topological_sort_dag(dag)
    
    # Execute steps
    results = []
    for node_id in execution_order:
        meta = dag.nodes[node_id].get("meta", {})
        
        # Check if step is automated
        if not meta.get("automated", False):
            results.append({
                "node_id": node_id,
                "status": "skipped",
                "message": "Manual step - requires human interaction",
                "meta": meta,
            })
            continue
        
        # Get action and params
        action = meta.get("action", "unknown")
        params = meta.get("params", {})
        
        # Validate policy
        policy_result = policy.validate_action(action, params, context)
        
        if not policy_result.get("allowed", False):
            results.append({
                "node_id": node_id,
                "status": "blocked",
                "message": policy_result.get("reason", "Policy violation"),
                "meta": meta,
                "policy": policy_result,
            })
            continue
        
        # Execute action
        try:
            exec_result = automation.execute_action(action, params, context)
            policy.record_execution(action)
            
            results.append({
                "node_id": node_id,
                "status": exec_result.get("status", "unknown"),
                "message": exec_result.get("message", ""),
                "meta": meta,
                "result": exec_result,
            })
            
        except Exception as e:
            results.append({
                "node_id": node_id,
                "status": "error",
                "message": f"Execution failed: {str(e)}",
                "meta": meta,
            })
    
    # Calculate summary
    execution_time = time.time() - start_time
    total = len(results)
    succeeded = sum(1 for r in results if r["status"] in ["success", "simulated"])
    failed = sum(1 for r in results if r["status"] == "error")
    blocked = sum(1 for r in results if r["status"] == "blocked")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    
    return {
        "status": "completed",
        "playbook_id": playbook_id,
        "playbook_name": playbook.get("name", playbook_id),
        "execution_time": round(execution_time, 2),
        "summary": {
            "total_steps": total,
            "succeeded": succeeded,
            "failed": failed,
            "blocked": blocked,
            "skipped": skipped,
        },
        "results": results,
        "dry_run": dry_run,
    }
