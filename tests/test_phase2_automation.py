# tests/test_phase2_automation.py
"""
Tests for Phase-2 automation functionality.
"""

import pytest
from phase2_engine.core import (
    load_playbook_by_id,
    build_playbook_dag,
    merge_graphs,
    run_playbook,
)
from phase2_engine.core.runner_bridge import (
    run_phase2_from_incident,
    _playbooks_for_incident,
)


def test_load_playbook():
    """Test playbook loading."""
    playbook = load_playbook_by_id("A03_injection")
    
    if playbook:  # Only test if playbook file exists
        assert playbook["id"] == "A03_injection"
        assert "phases" in playbook
        assert "preparation" in playbook["phases"]


def test_build_dag():
    """Test DAG construction."""
    playbook = {
        "id": "test_playbook",
        "name": "Test",
        "phases": {
            "preparation": [
                {"action": "step1", "name": "Step 1"}
            ],
            "containment": [
                {"action": "step2", "name": "Step 2"}
            ]
        }
    }
    
    dag = build_playbook_dag(playbook)
    
    assert dag.number_of_nodes() == 2
    assert dag.number_of_edges() == 1  # step1 → step2


def test_incident_to_playbook_mapping():
    """Test incident → playbook mapping."""
    incident = {
        "incident_type": "Injection Attack",
        "fine_label": "sql_injection",
        "confidence": 0.85
    }
    
    playbooks = _playbooks_for_incident(incident)
    
    assert "A03_injection" in playbooks


def test_run_phase2_from_incident():
    """Test Phase-1 → Phase-2 bridge."""
    incident = {
        "incident_type": "Injection Attack",
        "fine_label": "sql_injection",
        "confidence": 0.85,
        "rationale": "SQL injection detected"
    }
    
    result = run_phase2_from_incident(incident, dry_run=True)
    
    # Should successfully map to playbook
    assert result["status"] == "success"
    assert "A03_injection" in result["playbooks"]
    assert len(result["steps"]) > 0


def test_run_playbook_dry_run():
    """Test playbook execution in dry-run mode."""
    playbook_id = "A03_injection"
    
    # Only run if playbook exists
    from phase2_engine.core.playbook_loader import load_playbook_by_id
    if load_playbook_by_id(playbook_id):
        result = run_playbook(playbook_id, dry_run=True)
        
        assert result["status"] == "completed"
        assert result["dry_run"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
