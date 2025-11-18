"""
Baseline Keyword Matching Classifier

A simple rule-based classifier used as a baseline for comparison.
Uses basic pattern matching to classify security incidents.

Pattern examples:
- SQL injection patterns (' OR '1'='1) → A05 Injection
- Session-related keywords → A07 Authentication Failure
- Access control keywords → A01 Broken Access Control
- Encryption-related terms → A04 Cryptographic Failure
"""

import re
from typing import Dict, Optional, Tuple


class BaselineKeywordClassifier:
    """
    Simple keyword-matching baseline classifier.
    
    This is intentionally simple to serve as a weak baseline
    for comparison against our hybrid LLM system.
    """
    
    def __init__(self):
        # Define keyword patterns (ordered by specificity)
        self.patterns = [
            # A05: Injection
            (r"' OR ['\"]1['\"]=['\"]1", "injection", 0.8),
            (r"union.*select", "injection", 0.8),
            (r"sql.*injection", "injection", 0.7),
            (r"xss", "injection", 0.7),
            (r"<script>", "injection", 0.7),
            (r"command.*injection", "injection", 0.7),
            
            # A07: Authentication Failures
            (r"session.*timeout", "broken_authentication", 0.7),
            (r"password.*weak", "broken_authentication", 0.6),
            (r"login.*fail", "broken_authentication", 0.6),
            (r"authentication.*fail", "broken_authentication", 0.7),
            (r"2fa.*missing", "broken_authentication", 0.6),
            
            # A01: Broken Access Control
            (r"change.*user.*id", "broken_access_control", 0.6),
            (r"another.*user", "broken_access_control", 0.6),
            (r"unauthorized.*access", "broken_access_control", 0.7),
            (r"admin.*panel", "broken_access_control", 0.6),
            (r"privilege.*escalat", "broken_access_control", 0.6),
            
            # A04: Cryptographic Failures
            (r"base64", "cryptographic_failures", 0.6),
            (r"plaintext", "cryptographic_failures", 0.7),
            (r"unencrypted", "cryptographic_failures", 0.7),
            (r"not.*encrypted", "cryptographic_failures", 0.7),
            (r"weak.*crypto", "cryptographic_failures", 0.6),
            (r"md5.*hash", "cryptographic_failures", 0.6),
        ]
    
    def classify(self, text: str) -> Dict[str, any]:
        """
        Classify incident using simple keyword matching.
        
        Args:
            text: Incident description
            
        Returns:
            Dict with:
                - label: predicted category
                - confidence: fixed 0.7 (baseline doesn't calibrate confidence)
                - rationale: which pattern matched
        """
        text_lower = text.lower()
        
        # Check patterns in order
        for pattern, label, conf in self.patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    "label": label,
                    "confidence": 0.7,  # Fixed confidence (baseline weakness)
                    "rationale": f"Keyword match: {pattern}",
                    "method": "baseline_keyword"
                }
        
        # Default: can't classify
        return {
            "label": "other",
            "confidence": 0.3,  # Low confidence for unknown
            "rationale": "No keyword pattern matched",
            "method": "baseline_keyword"
        }


def run_baseline_classification(text: str) -> Dict[str, any]:
    """
    Convenience function to run baseline classification.
    
    Args:
        text: Incident description
        
    Returns:
        Classification result dict
    """
    classifier = BaselineKeywordClassifier()
    return classifier.classify(text)

