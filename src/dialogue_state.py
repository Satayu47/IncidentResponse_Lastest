# src/dialogue_state.py
"""
Dialogue state manager for multi-turn conversations.
Tracks confidence and determines when to proceed to Phase-2.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class Turn:
    """Single conversation turn."""
    user_input: str
    classification: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


class DialogueState:
    """Manages multi-turn conversation state and confidence tracking."""
    
    def __init__(self):
        self.turns: List[Turn] = []
        self.current_incident: Optional[Dict[str, Any]] = None
        self.refinement_count: int = 0
        
    def add_turn(self, user_input: str, classification: Dict[str, Any]):
        """Add a new conversation turn."""
        turn = Turn(user_input=user_input, classification=classification)
        self.turns.append(turn)
        self.current_incident = classification
        self.refinement_count += 1
    
    def get_latest_classification(self) -> Optional[Dict[str, Any]]:
        """Get the most recent classification."""
        return self.current_incident
    
    def get_average_confidence(self) -> float:
        """Calculate average confidence across all turns."""
        if not self.turns:
            return 0.0
        confidences = [t.classification.get("confidence", 0.0) for t in self.turns]
        return sum(confidences) / len(confidences)
    
    def get_max_confidence(self) -> float:
        """Get the highest confidence from any turn."""
        if not self.turns:
            return 0.0
        confidences = [t.classification.get("confidence", 0.0) for t in self.turns]
        return max(confidences)
    
    def is_ready_for_phase2(self, thresh: float = 0.7) -> bool:
        """
        Determine if we have enough confidence to proceed to Phase-2.
        
        Args:
            thresh: Minimum confidence threshold (default 0.7)
        
        Returns:
            True if ready for automated response generation
        """
        if not self.current_incident:
            return False
        
        # Check if latest confidence exceeds threshold
        latest_conf = self.current_incident.get("confidence", 0.0)
        
        # Also require at least one turn
        return latest_conf >= thresh and len(self.turns) >= 1
    
    def get_conversation_context(self) -> str:
        """Build a text summary of the conversation history."""
        if not self.turns:
            return ""
        
        context_parts = []
        for i, turn in enumerate(self.turns, 1):
            context_parts.append(f"Turn {i}: {turn.user_input}")
            context_parts.append(f"  → Classified as: {turn.classification.get('fine_label', 'unknown')}")
        
        return "\n".join(context_parts)
    
    def reset(self):
        """Clear all state for a new conversation."""
        self.turns.clear()
        self.current_incident = None
        self.refinement_count = 0
