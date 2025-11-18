# src/phase1_core.py

"""
Phase-1 classification core.
Used by tests and can be imported by the Streamlit app.

This is the main entry point for classification - it combines:
- explicit_detector: fast keyword matching
- llm_adapter: AI classification via Gemini
- classification_rules: label normalization

Returns a dict with:
{
    "label": "broken_access_control",   # canonical label
    "score": 0.87,                      # confidence 0-1
    "rationale": "explanation",
    "candidates": [{"label": "...", "score": 0.87}]
}
"""

from typing import Dict, List
import os

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

    # Fast path: try keyword detection first (only for very obvious cases)
    detector = ExplicitDetector()
    explicit_label, explicit_conf = detector.detect(user_text)
    
    # Only skip LLM for very high confidence (exact patterns like "' OR 1=1")
    # For everything else, use LLM semantic understanding
    if explicit_label and explicit_conf >= 0.90:
        # Very high confidence match, skip LLM
        canonical = canonicalize_label(explicit_label)
        return {
            "label": canonical,
            "score": explicit_conf,
            "rationale": f"High-confidence explicit detection: {explicit_label}",
            "candidates": [{"label": canonical, "score": explicit_conf}]
        }

    # Need LLM for semantic classification
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        # No API key available
        return {
            "label": "other",
            "score": 0.5,
            "rationale": "No API key available for LLM classification",
            "candidates": [{"label": "other", "score": 0.5}]
        }

    try:
        adapter = LLMAdapter(model="gemini-2.5-pro")
        raw = adapter.classify_incident(user_text)
        
        # Prefer fine_label over category (fine_label is more specific)
        # The LLM adapter should have normalized incident_type to category, but fine_label is preferred
        label_raw = raw.get("fine_label") or raw.get("category", "other")
        
        # Normalize the label
        label = canonicalize_label(label_raw)
        score = float(raw.get("confidence", 0.0))
        rationale = raw.get("rationale", "LLM-based classification")
        
        # Additional normalization pass
        label = ClassificationRules.normalize_label(label)
        
        # Blend with explicit detection if both found something
        if explicit_label and explicit_conf >= 0.7:
            explicit_canonical = canonicalize_label(explicit_label)
            if explicit_canonical == label:
                # Both agree - boost confidence
                score = max(score, 0.95)
                rationale = f"LLM + explicit detection agreement: {label}"
        
        # Post-processing: Handle ambiguous cases with multiple issues
        # If both crypto and access control keywords present, prioritize crypto when encryption mentioned
        text_lower = user_text.lower()
        crypto_keywords = ["plain text", "plaintext", "unencrypted", "not encrypted", "without encryption", "not hashed", "in plain text"]
        access_control_keywords = ["without authorization", "without checking", "unauthorized", "no authorization"]
        sensitive_data_keywords = ["email", "phone", "password", "ssn", "credit card", "sensitive data", "pii"]
        
        has_crypto_keyword = any(kw in text_lower for kw in crypto_keywords)
        has_access_keyword = any(kw in text_lower for kw in access_control_keywords)
        has_sensitive_data = any(kw in text_lower for kw in sensitive_data_keywords)
        has_protection_phrase = "without any protection" in text_lower or "without protection" in text_lower
        
        # If explicit detector found crypto, prioritize it
        if explicit_label == "cryptographic_failures" and label == "broken_access_control":
            label = "cryptographic_failures"
            rationale = f"{rationale} (Note: Explicit detection found cryptographic failure, prioritizing over access control)"
            score = max(explicit_conf, score * 0.9)  # Use explicit confidence or slightly reduce LLM confidence
        
        # If both present and LLM chose access control, but crypto keywords are explicit, prioritize crypto
        elif has_crypto_keyword and has_access_keyword and label == "broken_access_control":
            # Check if explicit detector found crypto
            if explicit_label == "cryptographic_failures" or any(kw in text_lower for kw in ["plain text", "plaintext", "unencrypted", "not encrypted"]):
                label = "cryptographic_failures"
                rationale = f"{rationale} (Note: Both access control and encryption issues present, prioritizing cryptographic failure due to explicit encryption keywords)"
                # Slightly reduce confidence since it's ambiguous
                score = min(score, 0.90)
        
        # Handle "without any protection" + sensitive data → prioritize crypto (data exposure is crypto issue)
        elif has_protection_phrase and has_sensitive_data and label == "broken_access_control":
            # "without any protection" when returning sensitive data typically means no encryption
            if explicit_label == "cryptographic_failures" or ("returns" in text_lower and has_sensitive_data):
                label = "cryptographic_failures"
                rationale = f"{rationale} (Note: 'Without protection' when returning sensitive data indicates cryptographic failure - data not encrypted)"
                score = min(score, 0.85)  # Lower confidence due to ambiguity
        
        # Additional check: If explicit detector found crypto but LLM didn't, trust explicit detector
        if explicit_label == "cryptographic_failures" and label != "cryptographic_failures":
            # Explicit patterns are very reliable for crypto failures
            if explicit_conf >= 0.85:
                label = "cryptographic_failures"
                rationale = f"{rationale} (Note: Explicit detection found cryptographic failure with high confidence)"
                score = max(explicit_conf, score * 0.9)
        
        # Check for multi-incident scenarios - if multiple explicit patterns match, prioritize the first one
        if explicit_label and explicit_conf >= 0.85:
            # If explicit detection found something with high confidence, trust it
            explicit_canonical = canonicalize_label(explicit_label)
            if explicit_canonical != label and explicit_conf > confidence:
                # Explicit detector is more confident, use it
                label = explicit_canonical
                rationale = f"High-confidence explicit detection: {explicit_label}"
                score = explicit_conf
        
        candidates = [{"label": label, "score": score}]
        
        return {
            "label": label,
            "score": score,
            "rationale": rationale,
            "candidates": candidates,
        }

    except Exception as e:
        # Error handling - return safe fallback
        return {
            "label": "other",
            "score": 0.5,
            "rationale": f"Classification failed: {str(e)[:100]}",
            "candidates": [{"label": "other", "score": 0.5}]
        }
