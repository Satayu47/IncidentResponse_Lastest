# phase2_engine/core/runner_bridge.py

from __future__ import annotations

from typing import Any, Dict, List, Optional
import sys
import os

# Add src to path for compatibility module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from .runner import run_playbook  # from IR-SANDBOX core
from .playbook_utils import (
    load_playbook_by_id,
    build_dag,
    merge_graphs,
    evaluate_policy,  # currently optional, but available
)

try:
    from owasp_compatibility import get_playbook_file, normalize_owasp_id
except ImportError:
    # Fallback if module not found - OWASP 2025 only
    def get_playbook_file(owasp_id: str) -> str:
        """Fallback playbook file mapping for OWASP 2025."""
        mapping = {
            "A01": "A01_broken_access_control",
            "A02": "A05_misconfiguration",
            "A03": "A06_vulnerable_components",
            "A04": "A02_cryptographic_failures",
            "A05": "A03_injection",
            "A06": "A04_insecure_design",
            "A07": "A07_authentication_failures",
            "A08": "A08_data_integrity",
            "A09": "A09_logging_failures",
            "A10": "A10_ssrf",
        }
        return mapping.get(owasp_id, f"{owasp_id}_unknown")
    
    def normalize_owasp_id(owasp_id: str) -> tuple:
        """Fallback normalization for OWASP 2025."""
        if ":" in owasp_id:
            owasp_id = owasp_id.split(":")[0].strip()
        if " " in owasp_id:
            owasp_id = owasp_id.split()[0].strip()
        return owasp_id, get_playbook_file(owasp_id)


# Map your Phase-1 labels to concrete playbook IDs
INCIDENT_TO_PLAYBOOK: Dict[str, List[str]] = {
    # Coarse report_category (phase1_output["incident_type"])
    "Injection Attack": ["A03_injection"],
    "Broken Access Control": ["A01_broken_access_control"],
    "Authentication Failures": ["A07_authentication_failures"],
    "Sensitive Data Exposure": ["A02_cryptographic_failures"],
    "Cryptographic Failures": ["A02_cryptographic_failures"],
    "Misconfiguration": ["A05_misconfiguration"],
    "Vulnerable Components": ["A06_vulnerable_components"],
    "Software Supply Chain Failures": ["A06_vulnerable_components"],
    "Insecure Design": ["A06_vulnerable_components"],

    # Fine labels (phase1_output["fine_label"])
    "injection": ["A03_injection"],
    "sql_injection": ["A03_injection"],
    "xss": ["A03_injection"],
    "ssrf": ["A03_injection"],

    "broken_access_control": ["A01_broken_access_control"],

    "broken_authentication": ["A07_authentication_failures"],
    "identification_and_authentication_failures": ["A07_authentication_failures"],

    "sensitive_data_exposure": ["A02_cryptographic_failures"],
    "cryptographic_failures": ["A02_cryptographic_failures"],

    "security_misconfiguration": ["A05_misconfiguration"],
    "misconfig": ["A05_misconfiguration"],

    "vulnerable_components": ["A06_vulnerable_components"],
    "vulnerable_component": ["A06_vulnerable_components"],
    "vulnerable_and_outdated_components": ["A06_vulnerable_components"],
    "outdated_components": ["A06_vulnerable_components"],
    "supply_chain": ["A06_vulnerable_components"],
    "supply_chain_failure": ["A06_vulnerable_components"],
    "supply_chain_compromise": ["A06_vulnerable_components"],
    "insecure_design": ["A06_vulnerable_components"],  # Fallback for supply chain issues
    "Software Supply Chain Failures": ["A06_vulnerable_components"],
    "Insecure Design": ["A06_vulnerable_components"],  # Fallback
    
    # A08:2025 - Software or Data Integrity Failures
    "data_integrity": ["A08_data_integrity"],
    "integrity_failures": ["A08_data_integrity"],
    "Software or Data Integrity Failures": ["A08_data_integrity"],
    
    # A09:2025 - Logging & Alerting Failures
    "logging_failures": ["A09_logging_failures"],
    "monitoring_failures": ["A09_logging_failures"],
    "Logging & Alerting Failures": ["A09_logging_failures"],
    
    # A10:2025 - Mishandling of Exceptional Conditions
    "exceptional_conditions": ["A10_ssrf"],
    "Mishandling of Exceptional Conditions": ["A10_ssrf"],
}


def _playbooks_for_incident(incident: Dict[str, Any]) -> List[str]:
    """
    Decide which playbook IDs to use for ONE incident JSON from Phase-1.

    Expected incident shape (your phase1_output):
      {
        "incident_type": "Injection Attack",
        "fine_label": "sql_injection",
        "labels": ["injection", "broken_access_control"],  # multi-label support
        "confidence": 0.9,
        ...
      }
    """
    playbooks: List[str] = []

    # Support multi-label classification
    labels = incident.get("labels", [])
    for label in labels:
        label_lower = label.lower()
        if label_lower in INCIDENT_TO_PLAYBOOK:
            playbooks.extend(INCIDENT_TO_PLAYBOOK[label_lower])

    fine = (incident.get("fine_label") or "").lower()
    coarse = incident.get("incident_type") or ""

    if fine in INCIDENT_TO_PLAYBOOK:
        playbooks.extend(INCIDENT_TO_PLAYBOOK[fine])

    if coarse in INCIDENT_TO_PLAYBOOK:
        playbooks.extend(INCIDENT_TO_PLAYBOOK[coarse])

    # Deduplicate while preserving order
    seen = set()
    unique: List[str] = []
    for pb in playbooks:
        if pb not in seen:
            seen.add(pb)
            unique.append(pb)

    return unique


def run_phase2_from_incident(
    incident: Dict[str, Any],
    merged_with: List[Dict[str, Any]] | None = None,
    dry_run: bool = True,
    opa_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main entry point for Phase-1 → Phase-2.
    - incident: current Phase-1 JSON (single case)
    - merged_with: optional list of other incidents to merge (for multiple incidents)
    - dry_run: True = don't actually run destructive automations
    - opa_url: Optional URL to OPA policy server for step validation
    Returns a normalized dict for the UI.
    """
    incidents: List[Dict[str, Any]] = [incident]
    if merged_with:
        incidents.extend(merged_with)

    # 1) Collect all playbook IDs across all incidents
    all_playbook_ids: List[str] = []
    for inc in incidents:
        all_playbook_ids.extend(_playbooks_for_incident(inc))

    # If nothing mapped, let caller know
    if not all_playbook_ids:
        return {
            "status": "no_playbook",
            "playbooks": [],
            "description": "No suitable playbook found for this incident.",
            "steps": [],
        }

    # Deduplicate while preserving order
    all_playbook_ids = list(dict.fromkeys(all_playbook_ids))

    # 2) Load playbooks and build DAGs
    dags = []
    loaded = []
    for pb_id in all_playbook_ids:
        pb = load_playbook_by_id(pb_id)
        if not pb:
            continue
        loaded.append(pb)
        dags.append(build_dag(pb))

    if not dags:
        return {
            "status": "no_playbook",
            "playbooks": [],
            "description": "Playbooks were mapped but could not be loaded.",
            "steps": [],
        }

    # 3) Merge DAGs if necessary
    if len(dags) == 1:
        merged_dag = dags[0]
        merged_name = loaded[0].get("id", all_playbook_ids[0])
    else:
        merged_dag = merge_graphs(dags)
        merged_name = "merged_" + "_".join(all_playbook_ids)

    # 4) Topological order → ordered list of steps
    execution_steps: List[Dict[str, Any]] = []
    for node_id in list(merged_dag.nodes):
        meta = merged_dag.nodes[node_id].get("meta", {})
        phase = meta.get("phase", "unknown")

        step_info: Dict[str, Any] = {
            "node_id": node_id,
            "phase": phase,
            "name": meta.get("name") or meta.get("action", "Unnamed step"),
            "message": meta.get("message", ""),
            "ui_description": meta.get("ui_description", ""),
        }

        # Optional: policy decision via OPA
        if opa_url:
            step_info["policy"] = evaluate_policy(opa_url, meta)

        execution_steps.append(step_info)

    # 5) Optional: real automation
    automation_result: Dict[str, Any] = {
        "dry_run": dry_run,
        "executed": False,
        "details": None,
    }

    if not dry_run:
        # For simplicity, we execute the first playbook as the 'main' automation
        main_pb_id = all_playbook_ids[0]
        automation_result["executed"] = True
        automation_result["details"] = run_playbook(
            playbook_id=main_pb_id,
            context={"incident": incident},
        )

    # 6) Final response
    description = loaded[0].get(
        "description", "Respond to the mapped OWASP incident(s)."
    )

    return {
        "status": "success",
        "playbook": merged_name,
        "playbooks": all_playbook_ids,
        "description": description,
        "steps": execution_steps,
        "merged_dag": merged_dag,
        "automation": automation_result,
    }
