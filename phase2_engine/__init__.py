# phase2_engine/__init__.py
"""
Phase-2 automation engine for incident response.
Provides playbook loading, DAG construction, and automated response execution.
"""

from .core.runner_bridge import run_phase2_from_incident
from .core.playbook_loader import load_playbook_by_id
from .core.playbook_dag import build_playbook_dag, merge_graphs

__all__ = [
    "run_phase2_from_incident",
    "load_playbook_by_id",
    "build_playbook_dag",
    "merge_graphs",
]
