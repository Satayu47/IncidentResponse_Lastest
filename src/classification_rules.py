# src/classification_rules.py
"""
Classification rules and normalization for incident types.
Maps various labels to standardized OWASP categories.
"""

import re
from typing import Dict, Tuple


# Canonical label mapping
# This fixes the issue where Gemini returns different variations
# like "identification_and_authentication_failures" vs "broken_authentication"
# Took a while to figure out all the variations!

_CANON_MAP = {
    # Broken Access Control
    "broken_access_control": "broken_access_control",
    "access_control": "broken_access_control",
    "access_control_issue": "broken_access_control",
    "authorization_failure": "broken_access_control",
    "authorization_failures": "broken_access_control",
    "improper_access_control": "broken_access_control",
    "privilege_escalation": "broken_access_control",
    "vertical_privilege_escalation": "broken_access_control",
    "horizontal_privilege_escalation": "broken_access_control",
    "insecure_direct_object_reference": "broken_access_control",
    "idor": "broken_access_control",

    # Injection
    "injection": "injection",
    "sql_injection": "injection",
    "xss": "injection",
    "cross_site_scripting": "injection",
    "command_injection": "injection",
    "os_command_injection": "injection",
    "ldap_injection": "injection",
    "nosql_injection": "injection",
    "code_injection": "injection",
    "xml_injection": "injection",

    # Broken Authentication
    "broken_authentication": "broken_authentication",
    "authentication_failures": "broken_authentication",
    "identification_and_authentication_failures": "broken_authentication",
    "auth_failure": "broken_authentication",
    "weak_authentication": "broken_authentication",
    "session_fixation": "broken_authentication",
    "credential_stuffing": "broken_authentication",
    "brute_force": "broken_authentication",

    # Sensitive Data Exposure (maps to Cryptographic Failures in 2025)
    "sensitive_data_exposure": "cryptographic_failures",  # A04:2025
    "data_exposure": "cryptographic_failures",
    "data_leak": "cryptographic_failures",
    "data_breach": "cryptographic_failures",
    "information_disclosure": "cryptographic_failures",
    "pii_exposure": "cryptographic_failures",
    "plaintext": "cryptographic_failures",
    "plaintext_passwords": "cryptographic_failures",
    "unencrypted_data": "cryptographic_failures",

    # Cryptographic Failures (A04:2025)
    "cryptographic_failures": "cryptographic_failures",
    "crypto_failures": "cryptographic_failures",
    "insecure_transport": "cryptographic_failures",
    "tls_failure": "cryptographic_failures",
    "no_tls": "cryptographic_failures",
    "no_https": "cryptographic_failures",
    "http_instead_of_https": "cryptographic_failures",
    "unencrypted": "cryptographic_failures",
    "weak_crypto": "cryptographic_failures",
    "weak_encryption": "cryptographic_failures",
    "insecure_protocol": "cryptographic_failures",
    "missing_encryption": "cryptographic_failures",

    # Security Misconfiguration
    "security_misconfiguration": "security_misconfiguration",
    "misconfiguration": "security_misconfiguration",
    "config_error": "security_misconfiguration",
    "insecure_configuration": "security_misconfiguration",
    "default_credentials": "security_misconfiguration",
    "missing_security_headers": "security_misconfiguration",

    # Vulnerable Components
    "vulnerable_components": "vulnerable_components",
    "vulnerable_and_outdated_components": "vulnerable_components",
    "outdated_components": "vulnerable_components",
    "known_vulnerabilities": "vulnerable_components",

    # Insecure Design (A06:2025) - only for true design flaws
    "insecure_design": "insecure_design",
    "design_flaw": "insecure_design",
    "missing_security_controls": "insecure_design",
    
    # Other
    "other": "other",
    "noise": "other",
    "non_security": "other",
    "unknown": "other",
}


def canonicalize_label(raw: str) -> str:
    """
    Normalize LLM output variations to canonical labels.
    
    Args:
        raw: Raw label from LLM (e.g., "identification_and_authentication_failures")
    
    Returns:
        Canonical label (e.g., "broken_authentication")
    """
    if not raw:
        return "other"
    
    # Normalize: lowercase, replace non-alphanumeric with underscore
    key = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")
    
    # Map to canonical label
    return _CANON_MAP.get(key, "other")


class ClassificationRules:
    """Rules for normalizing and mapping incident classifications."""
    
    # Map fine-grained labels to OWASP Top 10:2025 categories
    LABEL_TO_OWASP = {
        # Injection variants (A05:2025)
        "sql_injection": ("A05", "Injection"),
        "xss": ("A05", "Injection"),
        "cross_site_scripting": ("A05", "Injection"),
        "command_injection": ("A05", "Injection"),
        "ldap_injection": ("A05", "Injection"),
        "nosql_injection": ("A05", "Injection"),
        "injection": ("A05", "Injection"),
        
        # Access control (A01:2025 - same)
        "broken_access_control": ("A01", "Broken Access Control"),
        "privilege_escalation": ("A01", "Broken Access Control"),
        "idor": ("A01", "Broken Access Control"),
        "unauthorized_access": ("A01", "Broken Access Control"),
        
        # Authentication (A07:2025)
        "broken_authentication": ("A07", "Authentication Failures"),
        "authentication_failure": ("A07", "Authentication Failures"),
        "session_hijacking": ("A07", "Authentication Failures"),
        "credential_stuffing": ("A07", "Authentication Failures"),
        
        # Cryptographic failures (A04:2025)
        "cryptographic_failures": ("A04", "Cryptographic Failures"),
        "sensitive_data_exposure": ("A04", "Cryptographic Failures"),
        "weak_encryption": ("A04", "Cryptographic Failures"),
        "data_leak": ("A04", "Cryptographic Failures"),
        
        # Misconfiguration (A02:2025)
        "security_misconfiguration": ("A02", "Security Misconfiguration"),
        "misconfiguration": ("A02", "Security Misconfiguration"),
        "misconfig": ("A02", "Security Misconfiguration"),
        "default_credentials": ("A02", "Security Misconfiguration"),
        
        # Software Supply Chain Failures (A03:2025 - was Vulnerable Components)
        "vulnerable_components": ("A03", "Software Supply Chain Failures"),
        "outdated_components": ("A03", "Software Supply Chain Failures"),
        "known_vulnerability": ("A03", "Software Supply Chain Failures"),
        "supply_chain": ("A03", "Software Supply Chain Failures"),
        
        # Mishandling of Exceptional Conditions (A10:2025 - was SSRF)
        "ssrf": ("A10", "Mishandling of Exceptional Conditions"),
        "exception_handling": ("A10", "Mishandling of Exceptional Conditions"),
        "error_handling": ("A10", "Mishandling of Exceptional Conditions"),
        
        # Insecure design (A06:2025)
        "insecure_design": ("A06", "Insecure Design"),
        
        # Software or Data Integrity Failures (A08:2025 - same)
        "data_integrity": ("A08", "Software or Data Integrity Failures"),
        "integrity_failures": ("A08", "Software or Data Integrity Failures"),
        
        # Logging & Alerting Failures (A09:2025)
        "logging_failures": ("A09", "Logging & Alerting Failures"),
        "monitoring_failures": ("A09", "Logging & Alerting Failures"),
    }
    
    @classmethod
    def normalize_label(cls, label: str) -> str:
        """
        Normalize a classification label using canonical mapping.
        
        Args:
            label: Raw classification label
        
        Returns:
            Canonical label string
        """
        return canonicalize_label(label)
    
    @classmethod
    def get_owasp_display_name(cls, label: str, show_specific: bool = True, version: str = "2025") -> str:
        """
        Get OWASP 2025 display name for a label.
        Note: version parameter kept for API compatibility but only 2025 is supported.
        
        Args:
            label: Classification label
            show_specific: If True, include specific type (e.g., "SQL Injection")
            version: OWASP version (default: "2025", only 2025 is supported)
        
        Returns:
            Display string like "A05:2025 - Injection (SQL Injection)"
        """
        # First canonicalize the label
        canonical = canonicalize_label(label)
        
        # Look up OWASP mapping (always uses 2025 mapping internally)
        if canonical in cls.LABEL_TO_OWASP:
            owasp_id, owasp_name = cls.LABEL_TO_OWASP[canonical]
        elif canonical == "insecure_design":
            # Only use A06 if it's explicitly insecure_design
            owasp_id, owasp_name = ("A06", "Insecure Design")
        else:
            # Default fallback - try to infer from label
            if "access" in canonical or "authorization" in canonical or "privilege" in canonical or "idor" in canonical:
                owasp_id, owasp_name = ("A01", "Broken Access Control")
            elif "crypto" in canonical or "encrypt" in canonical or "plaintext" in canonical or "tls" in canonical or "https" in canonical or "data_exposure" in canonical:
                owasp_id, owasp_name = ("A04", "Cryptographic Failures")
            elif "injection" in canonical or "xss" in canonical or "sql" in canonical:
                owasp_id, owasp_name = ("A05", "Injection")
            elif "authentication" in canonical or "session" in canonical or "password" in canonical or "login" in canonical or "auth" in canonical:
                owasp_id, owasp_name = ("A07", "Authentication Failures")
            else:
                owasp_id, owasp_name = ("A06", "Insecure Design")  # Last resort
        
        # OWASP 2025 only - no version conversion needed
        
        if show_specific and label:
            specific = label.replace("_", " ").title()
            return f"{owasp_id}:{version} - {owasp_name} ({specific})"
        else:
            return f"{owasp_id}:{version} - {owasp_name}"
