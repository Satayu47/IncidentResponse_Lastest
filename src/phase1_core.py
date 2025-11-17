# src/phase1_core.py

"""
Phase-1 core helper used by:
- Streamlit app (optional)
- pytest (human-style test suites)
- evaluation scripts

Central wrapper that connects to the existing pipeline:
- extractor for IOC extraction
- llm_adapter for AI classification
- classification_rules for label normalization
- explicit_detector for keyword-based detection

Return format (dict) expected by tests:

{
    "label": "broken_access_control",   # final canonical label
    "score": 0.87,                      # confidence 0-1
    "rationale": "why it classified so",
    "candidates": [
        {"label": "broken_access_control", "score": 0.87},
        {"label": "other", "score": 0.13},
    ]
}
"""

from typing import Dict, List
import os

# Import existing modules
from src.llm_adapter import LLMAdapter
from src.explicit_detector import ExplicitDetector
from src.classification_rules import ClassificationRules, canonicalize_label


def run_phase1_classification(user_text: str) -> Dict:
    """
    Single-entry function for Phase-1 classification used in tests.

    This mirrors the logic from the Streamlit app but simplified for testing.
    
    Args:
        user_text: User incident description (multi-turn conversation joined)
    
    Returns:
        Dict with label, score, rationale, candidates
    """
    user_text = (user_text or "").strip()
    if not user_text:
        return {
            "label": "other",
            "score": 0.0,
            "rationale": "Empty input.",
            "candidates": []
        }

    # 1) Try explicit keyword detection first (fast path)
    detector = ExplicitDetector()
    explicit_label, explicit_conf = detector.detect(user_text)
    
    if explicit_label and explicit_conf >= 0.85:
        # High-confidence explicit match - use it directly
        canonical = canonicalize_label(explicit_label)
        return {
            "label": canonical,
            "score": explicit_conf,
            "rationale": f"High-confidence explicit detection: {explicit_label}",
            "candidates": [{"label": canonical, "score": explicit_conf}]
        }

    # 2) Use LLM for semantic classification
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        # Fallback if no API key
        return {
            "label": "other",
            "score": 0.5,
            "rationale": "No API key available for LLM classification",
            "candidates": [{"label": "other", "score": 0.5}]
        }

    try:
        adapter = LLMAdapter(model="gemini-2.5-pro")
        raw = adapter.classify_incident(user_text)
        
        # Extract and normalize with canonical mapping
        label = canonicalize_label(raw.get("category", "other"))
        score = float(raw.get("confidence", 0.0))
        rationale = raw.get("rationale", "LLM-based classification")
        
        # Apply additional normalization rules
        label = ClassificationRules.normalize_label(label)
        
        # If explicit detection found something with lower confidence, blend it
        if explicit_label and explicit_conf >= 0.7:
            explicit_canonical = canonicalize_label(explicit_label)
            # Boost score if LLM agrees with explicit detection
            if explicit_canonical == label:
                score = max(score, 0.95)
                rationale = f"LLM + explicit detection agreement: {label}"
        
        # Build candidates list
        candidates = [{"label": label, "score": score}]
        
        return {
            "label": label,
            "score": score,
            "rationale": rationale,
            "candidates": candidates,
        }

    except Exception as e:
        # Fallback on error
        return {
            "label": "other",
            "score": 0.5,
            "rationale": f"Classification failed: {str(e)[:100]}",
            "candidates": [{"label": "other", "score": 0.5}]
        }
