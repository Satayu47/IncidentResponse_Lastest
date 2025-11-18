"""
OWASP Top 10 2021/2025 Compatibility Layer
Handles mapping between both versions for backward compatibility
"""

from typing import Dict, Tuple, Optional

# OWASP Top 10: 2021 Categories
OWASP_2021 = {
    "A01": "Broken Access Control",
    "A02": "Cryptographic Failures",
    "A03": "Injection",
    "A04": "Insecure Design",
    "A05": "Security Misconfiguration",
    "A06": "Vulnerable and Outdated Components",
    "A07": "Identification and Authentication Failures",
    "A08": "Software and Data Integrity Failures",
    "A09": "Security Logging and Monitoring Failures",
    "A10": "Server-Side Request Forgery (SSRF)",
}

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

# Mapping: 2021 category -> 2025 category
OWASP_2021_TO_2025: Dict[str, str] = {
    "A01": "A01",  # Same
    "A02": "A04",  # Cryptographic Failures: 2021 A02 -> 2025 A04
    "A03": "A05",  # Injection: 2021 A03 -> 2025 A05
    "A04": "A06",  # Insecure Design: 2021 A04 -> 2025 A06
    "A05": "A02",  # Security Misconfiguration: 2021 A05 -> 2025 A02
    "A06": "A03",  # Vulnerable Components: 2021 A06 -> 2025 A03 (Supply Chain)
    "A07": "A07",  # Authentication: 2021 A07 -> 2025 A07 (same name change)
    "A08": "A08",  # Data Integrity: 2021 A08 -> 2025 A08 (same)
    "A09": "A09",  # Logging: 2021 A09 -> 2025 A09 (same)
    "A10": "A10",  # SSRF: 2021 A10 -> 2025 A10 (now Exceptional Conditions)
}

# Reverse mapping: 2025 category -> 2021 category
OWASP_2025_TO_2021: Dict[str, str] = {v: k for k, v in OWASP_2021_TO_2025.items()}

# Playbook file naming (uses 2021 convention for backward compatibility)
# Maps 2025 category to actual playbook file name
PLAYBOOK_FILE_MAPPING: Dict[str, str] = {
    # 2025 A01 -> 2021 A01 (same)
    "A01": "A01_broken_access_control",
    
    # 2025 A02 (Misconfiguration) -> 2021 A05
    "A02": "A05_misconfiguration",
    
    # 2025 A03 (Supply Chain) -> 2021 A06
    "A03": "A06_vulnerable_components",
    
    # 2025 A04 (Cryptographic) -> 2021 A02
    "A04": "A02_cryptographic_failures",
    
    # 2025 A05 (Injection) -> 2021 A03
    "A05": "A03_injection",
    
    # 2025 A06 (Insecure Design) -> 2021 A04
    "A06": "A04_insecure_design",
    
    # 2025 A07 (Authentication) -> 2021 A07
    "A07": "A07_authentication_failures",
    
    # 2025 A08 (Data Integrity) -> 2021 A08
    "A08": "A08_data_integrity",
    
    # 2025 A09 (Logging) -> 2021 A09
    "A09": "A09_logging_failures",
    
    # 2025 A10 (Exceptional Conditions) -> 2021 A10
    "A10": "A10_ssrf",
}


def convert_2021_to_2025(category_2021: str) -> str:
    """Convert OWASP 2021 category to 2025 category."""
    return OWASP_2021_TO_2025.get(category_2021, category_2021)


def convert_2025_to_2021(category_2025: str) -> str:
    """Convert OWASP 2025 category to 2021 category."""
    return OWASP_2025_TO_2021.get(category_2025, category_2025)


def get_playbook_file(owasp_id: str, version: str = "2025") -> str:
    """
    Get playbook file name for an OWASP category.
    
    Args:
        owasp_id: OWASP category ID (e.g., "A05")
        version: "2021" or "2025" (default: "2025")
    
    Returns:
        Playbook file name (e.g., "A03_injection")
    """
    if version == "2021":
        # Direct mapping for 2021
        return PLAYBOOK_FILE_MAPPING.get(convert_2021_to_2025(owasp_id), f"{owasp_id}_unknown")
    else:
        # 2025: use mapping to get playbook file
        return PLAYBOOK_FILE_MAPPING.get(owasp_id, f"{owasp_id}_unknown")


def normalize_owasp_id(owasp_id: str, target_version: str = "2025") -> Tuple[str, str]:
    """
    Normalize OWASP ID to target version and return playbook file.
    
    Args:
        owasp_id: OWASP category ID (e.g., "A03" or "A05")
        target_version: "2021" or "2025" (default: "2025")
    
    Returns:
        Tuple of (normalized_owasp_id, playbook_file_name)
    """
    # Extract just the ID part (e.g., "A05" from "A05:2025 - Injection")
    if ":" in owasp_id:
        owasp_id = owasp_id.split(":")[0].strip()
    if " " in owasp_id:
        owasp_id = owasp_id.split()[0].strip()
    
    # Determine source version (if it's a 2021 category, convert it)
    if target_version == "2025":
        # If it's already 2025 format, use it; otherwise convert from 2021
        normalized = owasp_id
        playbook_file = get_playbook_file(owasp_id, "2025")
    else:
        # Target is 2021
        normalized = convert_2025_to_2021(owasp_id) if owasp_id in OWASP_2025 else owasp_id
        playbook_file = get_playbook_file(normalized, "2021")
    
    return normalized, playbook_file


def is_valid_owasp_category(owasp_id: str, version: Optional[str] = None) -> bool:
    """Check if OWASP category ID is valid."""
    # Extract just the ID part
    if ":" in owasp_id:
        owasp_id = owasp_id.split(":")[0].strip()
    if " " in owasp_id:
        owasp_id = owasp_id.split()[0].strip()
    
    if version == "2021":
        return owasp_id in OWASP_2021
    elif version == "2025":
        return owasp_id in OWASP_2025
    else:
        # Check both versions
        return owasp_id in OWASP_2021 or owasp_id in OWASP_2025

