# src/explicit_detector.py
"""
Explicit keyword/pattern-based detection for common security incidents.
Fast path before expensive LLM calls.
Enhanced with high-confidence human phrase patterns.
"""

import re
from typing import Tuple, Optional


class ExplicitDetector:
    """Fast keyword-based detection for obvious security patterns."""
    
    def __init__(self):
        # regex patterns for quick detection
        # tried to order by specificity but might need adjustment
        # confidence scores based on testing - some patterns more reliable than others
        self.patterns = [
            
            # ===== OTHER / NON-SECURITY (check first to avoid false positives) =====
            (r"\buser (forgot|mistyped|typo)", "other", 0.95),
            (r"\bno (security|deeper) issue", "other", 0.95),
            (r"\bannoy.*not security", "other", 0.95),
            (r"\bno logs.*no evidence", "other", 0.90),
            
            # ===== BROKEN ACCESS CONTROL (high confidence patterns) =====
            (r"\bnormal (staff|users?) can access.*/admin\b", "broken_access_control", 0.95),
            (r"\bviewer role can delete\b", "broken_access_control", 0.95),
            (r"\bcan see (another|other) (customer|user|tenant)'?s", "broken_access_control", 0.95),
            (r"\bchange.*(user|invoice|account).*id.*url\b", "broken_access_control", 0.90),
            (r"\btenant isolation.*broken\b", "broken_access_control", 0.95),
            (r"\bescalate.*to admin\b", "broken_access_control", 0.95),
            (r"\bunauthenticated.*can (call|access|export)\b", "broken_access_control", 0.95),
            (r"\bsoft[- ]deleted.*still accessible\b", "broken_access_control", 0.90),
            (r"\bintern.*approve.*financial\b", "broken_access_control", 0.90),
            (r"\baccess.*/admin.*without.*log(ged|ging) in\b", "broken_access_control", 0.95),
            (r"\bprivileges?.*escalat", "broken_access_control", 0.85),
            (r"\bidor\b", "broken_access_control", 0.85),
            (r"\bunauthorized access", "broken_access_control", 0.80),
            
            # ===== INJECTION (high confidence patterns) =====
            (r"'\s*or\s+'?1'?\s*=\s*'?1", "injection", 0.98),
            (r"'\s*or\s+1\s*=\s*1", "injection", 0.98),
            (r"\bdrop\s+table\b", "injection", 0.98),
            (r"<script>.*alert.*</script>", "injection", 0.98),
            (r"\bunion\s+select\b", "injection", 0.98),
            (r"\bsql\s+injection\b", "injection", 0.95),
            (r"\bsql\s+error", "injection", 0.85),
            (r"\bsyntax error.*near.*or\b", "injection", 0.90),
            (r";.*rm\s+-rf", "injection", 0.95),
            (r"\bcommand\s+injection\b", "injection", 0.95),
            (r"\bxss\b", "injection", 0.95),
            (r"\breflects?\s+html\s+without\s+escaping", "injection", 0.90),
            (r"\bsqli\b", "injection", 0.90),
            (r"\bmalicious.*serialized.*(object|data)", "injection", 0.90),
            (r"\bremote code execution", "injection", 0.90),
            (r"\bdeserialization", "injection", 0.85),
            
            # ===== BROKEN AUTHENTICATION (high confidence patterns) =====
            (r"\bany\s+\d+\s*digit.*code.*accepted", "broken_authentication", 0.95),
            (r"\bsession.*never.*expire", "broken_authentication", 0.95),
            (r"\bjwt.*never.*expire", "broken_authentication", 0.95),
            (r"\bno.*exp.*claim", "broken_authentication", 0.90),
            (r"\bpassword.*plaintext", "broken_authentication", 0.98),
            (r"\bno.*account.*lockout", "broken_authentication", 0.90),
            (r"\bno.*lock.*after.*fail", "broken_authentication", 0.90),
            (r"\breset.*link.*no.*expir", "broken_authentication", 0.95),
            (r"\bsame session id.*before.*after.*login", "broken_authentication", 0.95),
            (r"\bpassword.*md5.*without.*salt", "broken_authentication", 0.90),
            (r"\b2fa.*optional", "broken_authentication", 0.85),
            (r"\bsession hijack", "broken_authentication", 0.85),
            (r"\bcredential stuffing", "broken_authentication", 0.90),
            
            # ===== SENSITIVE DATA EXPOSURE (high confidence patterns) =====
            (r"\bcredit card.*log", "sensitive_data_exposure", 0.95),
            (r"\bssn.*exposed", "sensitive_data_exposure", 0.95),
            (r"\bpii.*public.*s3", "sensitive_data_exposure", 0.95),
            (r"\bfull.*card.*number.*unmask", "sensitive_data_exposure", 0.95),
            (r"\bexport.*full card number", "sensitive_data_exposure", 0.95),
            (r"\bno masking", "sensitive_data_exposure", 0.85),
            (r"\bsalary.*download", "sensitive_data_exposure", 0.90),
            (r"\bstack trace.*secret", "sensitive_data_exposure", 0.90),
            (r"\bauthorization.*header.*log", "sensitive_data_exposure", 0.90),
            (r"\bbearer token.*visible", "sensitive_data_exposure", 0.90),
            (r"\bnational id.*full.*frontend", "sensitive_data_exposure", 0.90),
            (r"\bdata leak", "sensitive_data_exposure", 0.85),
            (r"\bsensitive data", "sensitive_data_exposure", 0.80),
            
            # ===== CRYPTOGRAPHIC FAILURES (high confidence patterns) =====
            (r"\btokens?.*md5.*without salt", "cryptographic_failures", 0.95),
            (r"\bhashed.*md5.*without salt", "cryptographic_failures", 0.95),
            (r"\blogin.*http.*not.*https", "cryptographic_failures", 0.95),
            (r"\btls.*certificate.*expired", "cryptographic_failures", 0.95),
            (r"\bnot secure.*login", "cryptographic_failures", 0.90),
            (r"\bself[- ]signed.*certificate.*production", "cryptographic_failures", 0.95),
            (r"\btls\s+1\.0", "cryptographic_failures", 0.90),
            (r"\bweak.*cipher", "cryptographic_failures", 0.85),
            (r"\bhard[- ]coded.*aes.*key", "cryptographic_failures", 0.95),
            (r"\btls.*disabled", "cryptographic_failures", 0.95),
            (r"\bhttp\s+only.*password", "cryptographic_failures", 0.95),
            (r"\bweak encryption", "cryptographic_failures", 0.85),
            
            # ===== SECURITY MISCONFIGURATION (high confidence patterns) =====
            (r"\bdefault.*credential", "security_misconfiguration", 0.95),
            (r"\badmin/admin", "security_misconfiguration", 0.95),
            (r"\bguest/guest", "security_misconfiguration", 0.95),
            (r"\bdirectory listing.*enabled", "security_misconfiguration", 0.95),
            (r"\bdebug.*mode.*production", "security_misconfiguration", 0.95),
            (r"\bkibana.*exposed.*internet", "security_misconfiguration", 0.95),
            (r"\btest.*endpoint.*production", "security_misconfiguration", 0.90),
            (r"\bfirewall.*ssh.*anywhere", "security_misconfiguration", 0.90),
            (r"\bs3.*bucket.*public", "security_misconfiguration", 0.95),
            (r"\bwaf.*disabled", "security_misconfiguration", 0.90),
            (r"\bcors.*\*", "security_misconfiguration", 0.85),
            (r"\bstack trace.*all users", "security_misconfiguration", 0.90),
            (r"\bmonitoring dashboard.*public", "security_misconfiguration", 0.95),
            (r"\b(dashboard|panel|admin).*public.*no login", "security_misconfiguration", 0.90),
            (r"\bmisconfiguration\b", "security_misconfiguration", 0.80),
            
            # ===== CVE / VULNERABLE COMPONENTS =====
            (r"\bcve-\d{4}-\d{4,}", "vulnerable_components", 0.90),
            (r"\boutdated (library|component)", "vulnerable_components", 0.85),
            (r"\bknown vulnerability", "vulnerable_components", 0.85),
        ]
    
    def detect(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect incident type using regex pattern matching.
        Returns first match with highest confidence.
        
        Args:
            text: Incident description
        
        Returns:
            Tuple of (detected_type, confidence_score)
            Returns (None, 0.0) if no match found
        """
        text_lower = text.lower()
        
        # Find all matches
        matches = []
        for pattern, label, confidence in self.patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matches.append((label, confidence))
        
        if not matches:
            return None, 0.0
        
        # Return highest confidence match
        best_match = max(matches, key=lambda x: x[1])
        return best_match[0], best_match[1]
    
    def quick_check(self, text: str, threshold: float = 0.6) -> bool:
        """
        Quick check if text contains security-related keywords.
        
        Args:
            text: Text to check
            threshold: Minimum confidence threshold
        
        Returns:
            True if security incident detected with confidence above threshold
        """
        _, confidence = self.detect(text)
        return confidence >= threshold
