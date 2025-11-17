# phase2_engine/core/playbook_loader.py
"""
Playbook loader for YAML-based incident response playbooks.
Handles loading and validation of playbook definitions.
"""

from __future__ import annotations
import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path


# Default playbooks directory
PLAYBOOKS_DIR = Path(__file__).parent.parent / "playbooks"


def load_playbook_by_id(playbook_id: str, playbooks_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Load a playbook by its ID.
    
    Args:
        playbook_id: Playbook identifier (e.g., "A03_injection")
        playbooks_dir: Optional custom playbooks directory
    
    Returns:
        Playbook dict or None if not found
    """
    if playbooks_dir is None:
        playbooks_dir = PLAYBOOKS_DIR
    
    # Try exact match first
    playbook_path = playbooks_dir / f"{playbook_id}.yaml"
    
    if not playbook_path.exists():
        # Try with .yml extension
        playbook_path = playbooks_dir / f"{playbook_id}.yml"
    
    if not playbook_path.exists():
        print(f"Playbook not found: {playbook_id}")
        return None
    
    try:
        with open(playbook_path, "r", encoding="utf-8") as f:
            playbook = yaml.safe_load(f)
        
        # Validate basic structure
        if not isinstance(playbook, dict):
            print(f"Invalid playbook format: {playbook_id}")
            return None
        
        # Ensure ID is set
        if "id" not in playbook:
            playbook["id"] = playbook_id
        
        return playbook
        
    except Exception as e:
        print(f"Error loading playbook {playbook_id}: {e}")
        return None


def load_all_playbooks(playbooks_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Load all playbooks from the playbooks directory.
    
    Args:
        playbooks_dir: Optional custom playbooks directory
    
    Returns:
        List of playbook dicts
    """
    if playbooks_dir is None:
        playbooks_dir = PLAYBOOKS_DIR
    
    playbooks = []
    
    if not playbooks_dir.exists():
        print(f"Playbooks directory not found: {playbooks_dir}")
        return playbooks
    
    for yaml_file in playbooks_dir.glob("*.yaml"):
        playbook_id = yaml_file.stem
        playbook = load_playbook_by_id(playbook_id, playbooks_dir)
        if playbook:
            playbooks.append(playbook)
    
    for yml_file in playbooks_dir.glob("*.yml"):
        playbook_id = yml_file.stem
        # Skip if already loaded as .yaml
        if not any(pb.get("id") == playbook_id for pb in playbooks):
            playbook = load_playbook_by_id(playbook_id, playbooks_dir)
            if playbook:
                playbooks.append(playbook)
    
    return playbooks


def validate_playbook(playbook: Dict[str, Any]) -> bool:
    """
    Validate playbook structure.
    
    Args:
        playbook: Playbook dict to validate
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["id", "name", "phases"]
    
    for field in required_fields:
        if field not in playbook:
            print(f"Missing required field: {field}")
            return False
    
    # Validate phases structure
    phases = playbook.get("phases", {})
    if not isinstance(phases, dict):
        print("Phases must be a dictionary")
        return False
    
    for phase_name, steps in phases.items():
        if not isinstance(steps, list):
            print(f"Phase '{phase_name}' must contain a list of steps")
            return False
        
        for step in steps:
            if not isinstance(step, dict):
                print(f"Step in phase '{phase_name}' must be a dictionary")
                return False
            
            if "action" not in step:
                print(f"Step in phase '{phase_name}' missing 'action' field")
                return False
    
    return True
