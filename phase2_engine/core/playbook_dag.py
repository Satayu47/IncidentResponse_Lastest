# phase2_engine/core/playbook_dag.py
"""
Playbook DAG (Directed Acyclic Graph) construction and manipulation.
Converts playbook phases into executable DAG structures.
"""

from __future__ import annotations
import networkx as nx
from typing import Dict, Any, List
import hashlib


def build_playbook_dag(playbook: Dict[str, Any]) -> nx.DiGraph:
    """
    Build a directed acyclic graph from a playbook.
    
    Args:
        playbook: Playbook dict with phases and steps
    
    Returns:
        NetworkX DiGraph representing the playbook execution flow
    """
    dag = nx.DiGraph()
    playbook_id = playbook.get("id", "unknown")
    
    # Standard NIST IR phases in order
    phase_order = [
        "preparation",
        "detection_analysis",
        "containment",
        "eradication",
        "recovery",
        "post_incident",
    ]
    
    phases = playbook.get("phases", {})
    prev_phase_nodes = []
    
    for phase_name in phase_order:
        steps = phases.get(phase_name, [])
        if not steps:
            continue
        
        phase_nodes = []
        
        for idx, step in enumerate(steps):
            # Generate unique node ID
            node_id = _generate_node_id(playbook_id, phase_name, idx, step)
            
            # Add node with metadata
            dag.add_node(
                node_id,
                meta={
                    "phase": phase_name,
                    "action": step.get("action", "unknown"),
                    "name": step.get("name", step.get("action", "Unnamed")),
                    "message": step.get("message", ""),
                    "ui_description": step.get("ui_description", ""),
                    "automated": step.get("automated", False),
                    "playbook_id": playbook_id,
                }
            )
            
            # Connect to previous phase nodes
            if prev_phase_nodes:
                for prev_node in prev_phase_nodes:
                    dag.add_edge(prev_node, node_id)
            
            phase_nodes.append(node_id)
        
        # Update previous phase nodes for next iteration
        prev_phase_nodes = phase_nodes
    
    return dag


def merge_graphs(dags: List[nx.DiGraph]) -> nx.DiGraph:
    """
    Merge multiple playbook DAGs into a single unified DAG.
    
    Args:
        dags: List of NetworkX DiGraphs to merge
    
    Returns:
        Merged DiGraph with all nodes and edges
    """
    if not dags:
        return nx.DiGraph()
    
    if len(dags) == 1:
        return dags[0]
    
    # Create a new merged graph
    merged = nx.DiGraph()
    
    # Add all nodes and edges from all DAGs
    for dag in dags:
        merged.add_nodes_from(dag.nodes(data=True))
        merged.add_edges_from(dag.edges())
    
    # Group nodes by phase for inter-playbook dependencies
    phase_groups: Dict[str, List[str]] = {}
    
    for node, data in merged.nodes(data=True):
        phase = data.get("meta", {}).get("phase", "unknown")
        phase_groups.setdefault(phase, []).append(node)
    
    # Add cross-playbook dependencies based on phase order
    phase_order = [
        "preparation",
        "detection_analysis",
        "containment",
        "eradication",
        "recovery",
        "post_incident",
    ]
    
    for i in range(len(phase_order) - 1):
        current_phase = phase_order[i]
        next_phase = phase_order[i + 1]
        
        current_nodes = phase_groups.get(current_phase, [])
        next_nodes = phase_groups.get(next_phase, [])
        
        # Connect last nodes of current phase to first nodes of next phase
        # Only if they're from different playbooks
        for curr_node in current_nodes:
            curr_playbook = merged.nodes[curr_node].get("meta", {}).get("playbook_id")
            
            for next_node in next_nodes:
                next_playbook = merged.nodes[next_node].get("meta", {}).get("playbook_id")
                
                # Add edge if playbooks differ and no path exists
                if curr_playbook != next_playbook and not nx.has_path(merged, curr_node, next_node):
                    merged.add_edge(curr_node, next_node)
    
    return merged


def _generate_node_id(
    playbook_id: str,
    phase: str,
    idx: int,
    step: Dict[str, Any]
) -> str:
    """
    Generate a unique node ID for a playbook step.
    
    Args:
        playbook_id: Playbook identifier
        phase: Phase name
        idx: Step index within phase
        step: Step dict
    
    Returns:
        Unique node identifier
    """
    # Create a deterministic ID based on content
    action = step.get("action", "unknown")
    name = step.get("name", action)
    
    # Use hash for uniqueness while keeping it readable
    content = f"{playbook_id}:{phase}:{idx}:{name}"
    hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
    
    return f"{playbook_id}_{phase}_{idx}_{hash_suffix}"


def topological_sort_dag(dag: nx.DiGraph) -> List[str]:
    """
    Get topological ordering of DAG nodes for execution.
    
    Args:
        dag: NetworkX DiGraph
    
    Returns:
        List of node IDs in topological order
    """
    try:
        return list(nx.topological_sort(dag))
    except nx.NetworkXError as e:
        print(f"Error in topological sort (cycle detected?): {e}")
        return list(dag.nodes)
