# src/owasp_display.py
"""
OWASP display utilities for the UI.
Provides formatted strings and descriptions for OWASP categories.
"""

from typing import Dict


# OWASP Top 10 2021 full descriptions
OWASP_DESCRIPTIONS = {
    "A01": {
        "name": "Broken Access Control",
        "description": "Access control enforces policy such that users cannot act outside of their intended permissions. "
                      "Failures typically lead to unauthorized information disclosure, modification, or destruction of data.",
        "examples": ["IDOR", "Privilege escalation", "Missing access controls"],
    },
    "A02": {
        "name": "Cryptographic Failures",
        "description": "Failures related to cryptography which often lead to exposure of sensitive data. "
                      "Previously known as Sensitive Data Exposure.",
        "examples": ["Weak encryption", "Plaintext storage", "Missing TLS"],
    },
    "A03": {
        "name": "Injection",
        "description": "Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. "
                      "The attacker's hostile data can trick the interpreter into executing unintended commands.",
        "examples": ["SQL injection", "XSS", "Command injection"],
    },
    "A04": {
        "name": "Insecure Design",
        "description": "Risks related to design and architectural flaws. Calls for more use of threat modeling, "
                      "secure design patterns, and reference architectures.",
        "examples": ["Missing rate limiting", "Weak business logic", "No threat modeling"],
    },
    "A05": {
        "name": "Security Misconfiguration",
        "description": "Security misconfiguration is the most commonly seen issue. This is commonly a result of insecure default "
                      "configurations, incomplete configurations, or misconfigured HTTP headers.",
        "examples": ["Default credentials", "Unnecessary features enabled", "Directory listing"],
    },
    "A06": {
        "name": "Vulnerable and Outdated Components",
        "description": "Components run with the same privileges as the application itself, so flaws in any component can result in "
                      "serious impact. Using components with known vulnerabilities may undermine application defenses.",
        "examples": ["Unpatched software", "Outdated libraries", "Known CVEs"],
    },
    "A07": {
        "name": "Identification and Authentication Failures",
        "description": "Confirmation of the user's identity, authentication, and session management is critical to protect against "
                      "authentication-related attacks.",
        "examples": ["Credential stuffing", "Weak passwords", "Session hijacking"],
    },
    "A08": {
        "name": "Software and Data Integrity Failures",
        "description": "Software and data integrity failures relate to code and infrastructure that does not protect against "
                      "integrity violations, such as insecure CI/CD pipelines.",
        "examples": ["Unsigned updates", "Insecure deserialization", "Supply chain attacks"],
    },
    "A09": {
        "name": "Security Logging and Monitoring Failures",
        "description": "Without logging and monitoring, breaches cannot be detected. Insufficient logging and monitoring, coupled with "
                      "missing or ineffective integration with incident response, allows attackers to persist.",
        "examples": ["No audit logs", "Insufficient monitoring", "Late detection"],
    },
    "A10": {
        "name": "Server-Side Request Forgery (SSRF)",
        "description": "SSRF flaws occur whenever a web application is fetching a remote resource without validating the user-supplied "
                      "URL. It allows an attacker to coerce the application to send requests to an unexpected destination.",
        "examples": ["Cloud metadata access", "Internal port scanning", "Bypass firewall"],
    },
}


def get_owasp_display_name(label: str, show_specific: bool = True) -> str:
    """
    Get formatted OWASP display name.
    
    Args:
        label: Classification label
        show_specific: Include specific subtype
    
    Returns:
        Formatted string like "A03 - Injection (SQL Injection)"
    """
    from .classification_rules import ClassificationRules
    return ClassificationRules.get_owasp_display_name(label, show_specific)


def get_owasp_description(owasp_id: str) -> Dict[str, str]:
    """Get full OWASP category description."""
    return OWASP_DESCRIPTIONS.get(owasp_id, {
        "name": "Unknown",
        "description": "No description available.",
        "examples": [],
    })


def format_confidence_badge(confidence: float) -> str:
    """
    Format confidence as a colored badge string.
    
    Args:
        confidence: Confidence score 0-1
    
    Returns:
        Badge text like "High (85%)"
    """
    pct = int(confidence * 100)
    
    if pct >= 70:
        return f"High ({pct}%)"
    elif pct >= 60:
        return f"Medium ({pct}%)"
    else:
        return f"Low ({pct}%)"
