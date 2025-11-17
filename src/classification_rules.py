# src/classification_rules.py
"""
Classification rules and normalization for incident types.
Maps various labels to standardized OWASP categories.
"""

import re
from typing import Dict, Tuple


# ============================================================================
# CANONICAL LABEL MAPPING - Fixes LLM synonym variations
# ============================================================================

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

    # Sensitive Data Exposure
    "sensitive_data_exposure": "sensitive_data_exposure",
    "data_exposure": "sensitive_data_exposure",
    "data_leak": "sensitive_data_exposure",
    "data_breach": "sensitive_data_exposure",
    "information_disclosure": "sensitive_data_exposure",
    "pii_exposure": "sensitive_data_exposure",

    # Cryptographic Failures
    "cryptographic_failures": "cryptographic_failures",
    "crypto_failures": "cryptographic_failures",
    "insecure_transport": "cryptographic_failures",
    "tls_failure": "cryptographic_failures",
    "no_tls": "cryptographic_failures",
    "unencrypted": "cryptographic_failures",
    "weak_crypto": "cryptographic_failures",
    "weak_encryption": "cryptographic_failures",
    "insecure_protocol": "cryptographic_failures",

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
    
    # Map fine-grained labels to OWASP Top 10 categories
    LABEL_TO_OWASP = {
        # Injection variants
        "sql_injection": ("A03", "Injection"),
        "xss": ("A03", "Injection"),
        "cross_site_scripting": ("A03", "Injection"),
        "command_injection": ("A03", "Injection"),
        "ldap_injection": ("A03", "Injection"),
        "nosql_injection": ("A03", "Injection"),
        "injection": ("A03", "Injection"),
        
        # Access control
        "broken_access_control": ("A01", "Broken Access Control"),
        "privilege_escalation": ("A01", "Broken Access Control"),
        "idor": ("A01", "Broken Access Control"),
        "unauthorized_access": ("A01", "Broken Access Control"),
        
        # Authentication
        "broken_authentication": ("A07", "Identification and Authentication Failures"),
        "authentication_failure": ("A07", "Identification and Authentication Failures"),
        "session_hijacking": ("A07", "Identification and Authentication Failures"),
        "credential_stuffing": ("A07", "Identification and Authentication Failures"),
        
        # Cryptographic failures
        "cryptographic_failures": ("A02", "Cryptographic Failures"),
        "sensitive_data_exposure": ("A02", "Cryptographic Failures"),
        "weak_encryption": ("A02", "Cryptographic Failures"),
        "data_leak": ("A02", "Cryptographic Failures"),
        
        # Misconfiguration
        "security_misconfiguration": ("A05", "Security Misconfiguration"),
        "misconfiguration": ("A05", "Security Misconfiguration"),
        "misconfig": ("A05", "Security Misconfiguration"),
        "default_credentials": ("A05", "Security Misconfiguration"),
        
        # Vulnerable components
        "vulnerable_components": ("A06", "Vulnerable and Outdated Components"),
        "outdated_components": ("A06", "Vulnerable and Outdated Components"),
        "known_vulnerability": ("A06", "Vulnerable and Outdated Components"),
        
        # SSRF
        "ssrf": ("A10", "Server-Side Request Forgery"),
        
        # Insecure design
        "insecure_design": ("A04", "Insecure Design"),
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
    def get_owasp_display_name(cls, label: str, show_specific: bool = True) -> str:
        """
        Get human-readable display name for a classification.
        
        Args:
            label: Classification label
            show_specific: If True, include specific type (e.g., "SQL Injection")
        
        Returns:
            Display string like "A03 - Injection (SQL Injection)"
        """
        # First canonicalize the label
        canonical = canonicalize_label(label)
        
        # Look up OWASP mapping
        if canonical in cls.LABEL_TO_OWASP:
            owasp_id, owasp_name = cls.LABEL_TO_OWASP[canonical]
        else:
            owasp_id, owasp_name = ("A04", "Insecure Design")
        
        if show_specific and label:
            specific = label.replace("_", " ").title()
            return f"{owasp_id} - {owasp_name} ({specific})"
        else:
            return f"{owasp_id} - {owasp_name}"
