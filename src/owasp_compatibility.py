"""
OWASP Top 10:2025 Support
Simplified version - 2025 only, no 2021 compatibility
"""

from typing import Dict, Tuple, Optional

# OWASP Top 10: 2025 Categories
OWASP_2025 = {
    "A01": "Broken Access Control",
    "A02": "Security Misconfiguration",
    "A03": "Software Supply Chain Failures",
    "A04": "Cryptographic Failures",
    "A05": "Injection",
    "A06": "Insecure Design",
    "A07": "Authentication Failures",
    "A08": "Software or Data Integrity Failures",
    "A09": "Logging & Alerting Failures",
    "A10": "Mishandling of Exceptional Conditions",
}

# Playbook file mapping: OWASP 2025 category -> playbook file name
# Note: Playbook files use legacy naming but represent 2025 categories
PLAYBOOK_FILE_MAPPING: Dict[str, str] = {
    "A01": "A01_broken_access_control",  # A01:2025 - Broken Access Control
    "A02": "A05_misconfiguration",  # A02:2025 - Security Misconfiguration
    "A03": "A06_vulnerable_components",  # A03:2025 - Software Supply Chain Failures
    "A04": "A02_cryptographic_failures",  # A04:2025 - Cryptographic Failures
    "A05": "A03_injection",  # A05:2025 - Injection
    "A06": "A04_insecure_design",  # A06:2025 - Insecure Design
    "A07": "A07_authentication_failures",  # A07:2025 - Authentication Failures
    "A08": "A08_data_integrity",  # A08:2025 - Software or Data Integrity Failures
    "A09": "A09_logging_failures",  # A09:2025 - Logging & Alerting Failures
    "A10": "A10_ssrf",  # A10:2025 - Mishandling of Exceptional Conditions
}


def get_playbook_file(owasp_id: str) -> str:
    """
    Get playbook file name for an OWASP 2025 category.
    
    Args:
        owasp_id: OWASP 2025 category ID (e.g., "A05")
    
    Returns:
        Playbook file name (e.g., "A03_injection")
    """
    # Extract just the ID part (e.g., "A05" from "A05:2025 - Injection")
    if ":" in owasp_id:
        owasp_id = owasp_id.split(":")[0].strip()
    if " " in owasp_id:
        owasp_id = owasp_id.split()[0].strip()
    
    return PLAYBOOK_FILE_MAPPING.get(owasp_id, f"{owasp_id}_unknown")


def normalize_owasp_id(owasp_id: str) -> Tuple[str, str]:
    """
    Normalize OWASP ID and return playbook file.
    
    Args:
        owasp_id: OWASP category ID (e.g., "A05" or "A05:2025 - Injection")
    
    Returns:
        Tuple of (normalized_owasp_id, playbook_file_name)
    """
    # Extract just the ID part
    if ":" in owasp_id:
        owasp_id = owasp_id.split(":")[0].strip()
    if " " in owasp_id:
        owasp_id = owasp_id.split()[0].strip()
    
    playbook_file = get_playbook_file(owasp_id)
    return owasp_id, playbook_file


def is_valid_owasp_category(owasp_id: str) -> bool:
    """Check if OWASP 2025 category ID is valid."""
    # Extract just the ID part
    if ":" in owasp_id:
        owasp_id = owasp_id.split(":")[0].strip()
    if " " in owasp_id:
        owasp_id = owasp_id.split()[0].strip()
    
    return owasp_id in OWASP_2025
