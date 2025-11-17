# phase2_engine/core/playbook_utils.py

from __future__ import annotations

from pathlib import Path
from hashlib import sha1
from typing import Any, Dict, List, Optional

import yaml
import networkx as nx
import requests

# Base folder for playbooks (adjust if your layout is different)
PLAYBOOK_ROOT = Path(__file__).resolve().parent.parent / "playbooks"


def load_playbook_by_id(playbook_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a playbook YAML by ID.

    Expected file names (we try in this order):
      - {playbook_id}.yaml
      - {playbook_id}_playbook.yaml
      - lowercase versions of the above

    Example IDs:
      - "A01_broken_access_control"
      - "A03_injection"
    """
    candidates = [
        PLAYBOOK_ROOT / f"{playbook_id}.yaml",
        PLAYBOOK_ROOT / f"{playbook_id}_playbook.yaml",
        PLAYBOOK_ROOT / f"{playbook_id.lower()}.yaml",
        PLAYBOOK_ROOT / f"{playbook_id.lower()}_playbook.yaml",
    ]

    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

    return None


def load_playbook_for_incident_type(incident_type: str) -> Optional[Dict[str, Any]]:
    """
    Optional helper if you want to load by a human-friendly incident_type.
    Uses the 'old' convention: playbooks/{incident_type}_playbook.yaml
    where incident_type is already normalized.

    Example:
        incident_type = "injection_attack" ->
        playbooks/injection_attack_playbook.yaml
    """
    safe = incident_type.replace(" ", "_").lower()
    path = PLAYBOOK_ROOT / f"{safe}_playbook.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_dag(playbook: Dict[str, Any]) -> nx.DiGraph:
    """
    Build a directed acyclic graph (DAG) from a playbook dict.

    Supports two playbook formats:
    1. "nodes" or "steps" format (flat list with 'requires' dependencies)
    2. "phases" format (NIST IR phases with nested steps)

    Expected YAML structure (nodes format):

    id: A03_injection
    description: Respond to injection attacks (SQL, XSS, etc.)
    nodes:
      - id: prep_logging
        phase: preparation
        action: enable_logging
        description: Enable logging for HTTP requests and DB queries.
        requires: []
      - id: detect_sqli
        phase: detection_analysis
        action: detect_sql_injection
        description: Detect suspicious SQL patterns in logs.
        requires: [prep_logging]
      ...

    Expected YAML structure (phases format):

    id: A03_injection
    phases:
      preparation:
        - action: enable_logging
          name: Enable Logging
          ...
      detection_analysis:
        - action: detect_sql_injection
          ...
    """
    G = nx.DiGraph()
    playbook_id = playbook.get("id", "unknown")

    # Support both "nodes" (your snippet) and "steps" (some playbook styles)
    items = playbook.get("nodes") or playbook.get("steps")
    
    if items:
        # Flat format with explicit requires
        for node in items:
            nid = node["id"]
            G.add_node(nid, meta=node)
            for dep in node.get("requires", []):
                G.add_edge(dep, nid)
        return G

    # Otherwise, try phases format (NIST IR structure)
    phases = playbook.get("phases", {})
    
    if phases:
        # Standard NIST IR phases in order
        phase_order = [
            "preparation",
            "detection_analysis",
            "containment",
            "eradication",
            "recovery",
            "post_incident",
        ]
        
        prev_phase_nodes = []
        
        for phase_name in phase_order:
            steps = phases.get(phase_name, [])
            if not steps:
                continue
            
            phase_nodes = []
            
            for idx, step in enumerate(steps):
                # Generate unique node ID
                action = step.get("action", "unknown")
                node_id = f"{playbook_id}_{phase_name}_{idx}_{action}"
                
                # Add node with metadata
                G.add_node(
                    node_id,
                    meta={
                        "phase": phase_name,
                        "action": action,
                        "name": step.get("name", action),
                        "description": step.get("message", ""),
                        "message": step.get("message", ""),
                        "ui_description": step.get("ui_description", ""),
                        "automated": step.get("automated", False),
                        "playbook_id": playbook_id,
                    }
                )
                
                # Connect to previous phase nodes (sequential dependency)
                if prev_phase_nodes:
                    for prev_node in prev_phase_nodes:
                        G.add_edge(prev_node, node_id)
                
                phase_nodes.append(node_id)
            
            # Update previous phase nodes for next iteration
            prev_phase_nodes = phase_nodes

    return G


def normalize_node(node_meta: Dict[str, Any]) -> str:
    """
    Normalize a node for deduplication when merging DAGs.

    We hash the (action, description) pair so that semantically identical
    steps across different playbooks are treated as the same node.
    """
    key_str = f"{node_meta.get('action', '')}:{node_meta.get('description', '')}".lower()
    return sha1(key_str.encode("utf-8")).hexdigest()


def merge_graphs(graph_list: List[nx.DiGraph]) -> nx.DiGraph:
    """
    Merge multiple DAGs into a single DAG, deduplicating nodes by semantic hash.

    If a cycle is introduced by merging, we raise ValueError.
    """
    merged = nx.DiGraph()
    seen_nodes: Dict[str, str] = {}

    for g in graph_list:
        # 1) Add / dedupe nodes
        for nid, data in g.nodes(data=True):
            meta = data["meta"]
            node_hash = normalize_node(meta)
            if node_hash in seen_nodes:
                canonical_id = seen_nodes[node_hash]
            else:
                canonical_id = nid
                seen_nodes[node_hash] = nid
                merged.add_node(canonical_id, meta=meta)

        # 2) Rewire edges using canonical node IDs
        for src, dst in g.edges():
            src_meta = g.nodes[src]["meta"]
            dst_meta = g.nodes[dst]["meta"]
            src_key = normalize_node(src_meta)
            dst_key = normalize_node(dst_meta)
            src_id = seen_nodes[src_key]
            dst_id = seen_nodes[dst_key]
            merged.add_edge(src_id, dst_id)

    if not nx.is_directed_acyclic_graph(merged):
        raise ValueError("Merged DAG contains cycles! Check playbook dependencies.")

    return merged


def evaluate_policy(opa_url: str, meta: Dict[str, Any]) -> str:
    """
    Optional: Ask OPA (Open Policy Agent) whether a step is ALLOW / DENY / REQUIRE_APPROVAL.

    If OPA is unreachable, default to 'ALLOW' so the system degrades gracefully.
    """
    try:
        response = requests.post(opa_url, json={"input": meta}, timeout=3)
        if response.status_code == 200:
            return response.json().get("result", "ALLOW")
        return "ALLOW"
    except requests.exceptions.RequestException:
        return "ALLOW"
