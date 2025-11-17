# phase2_engine/core/runner_bridge.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .runner import run_playbook  # from IR-SANDBOX core
from .playbook_utils import (
    load_playbook_by_id,
    build_dag,
    merge_graphs,
    evaluate_policy,  # currently optional, but available
)


# Map your Phase-1 labels to concrete playbook IDs
INCIDENT_TO_PLAYBOOK: Dict[str, List[str]] = {
    # Coarse report_category (phase1_output["incident_type"])
    "Injection Attack": ["A03_injection"],
    "Broken Access Control": ["A01_broken_access_control"],
    "Authentication Failures": ["A07_authentication_failures"],
    "Sensitive Data Exposure": ["A02_cryptographic_failures"],
    "Cryptographic Failures": ["A02_cryptographic_failures"],
    "Misconfiguration": ["A05_security_misconfiguration"],
    "Vulnerable Components": ["A06_vulnerable_and_outdated_components"],

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

    "security_misconfiguration": ["A05_security_misconfiguration"],
    "misconfig": ["A05_security_misconfiguration"],

    "vulnerable_component": ["A06_vulnerable_and_outdated_components"],
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
