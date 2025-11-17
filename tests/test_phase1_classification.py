# tests/test_phase1_classification.py
"""
Tests for Phase-1 classification functionality.
"""

import pytest
from src import (
    LLMAdapter,
    SecurityExtractor,
    ExplicitDetector,
    ClassificationRules,
    DialogueState,
)


def test_security_extractor():
    """Test IOC extraction."""
    extractor = SecurityExtractor()
    
    text = "Attack from 192.168.1.100 targeting http://example.com with CVE-2023-12345"
    entities = extractor.extract(text)
    
    assert "192.168.1.100" in entities.ips
    assert "http://example.com" in entities.urls
    assert "CVE-2023-12345" in entities.cves


def test_explicit_detector():
    """Test keyword-based detection."""
    detector = ExplicitDetector()
    
    text = "SQL injection attack using UNION SELECT"
    incident_type, confidence = detector.detect(text)
    
    assert incident_type == "sql_injection"
    assert confidence > 0.5


def test_classification_rules():
    """Test label normalization."""
    owasp_id, owasp_name = ClassificationRules.normalize_label("sql_injection")
    
    assert owasp_id == "A03"
    assert "Injection" in owasp_name


def test_dialogue_state():
    """Test conversation state management."""
    state = DialogueState()
    
    classification = {
        "fine_label": "sql_injection",
        "confidence": 0.85,
        "incident_type": "Injection Attack"
    }
    
    state.add_turn("Test incident", classification)
    
    assert len(state.turns) == 1
    assert state.is_ready_for_phase2(thresh=0.7)
    assert not state.is_ready_for_phase2(thresh=0.9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
