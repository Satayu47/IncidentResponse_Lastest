# src/extractor.py
"""
Entity extraction for security incidents.
Extracts IOCs (IPs, URLs, hashes, CVEs) from text.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ExtractedEntities:
    """Container for extracted security entities."""
    ips: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    hashes: List[str] = field(default_factory=list)
    cves: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    filenames: List[str] = field(default_factory=list)
    
    def __dict__(self):
        return {
            "ips": self.ips,
            "urls": self.urls,
            "domains": self.domains,
            "hashes": self.hashes,
            "cves": self.cves,
            "emails": self.emails,
            "filenames": self.filenames,
        }


class SecurityExtractor:
    """Extract security indicators and entities from text."""
    
    # Regex patterns for common IOCs
    IP_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'
    CVE_PATTERN = r'CVE-\d{4}-\d{4,7}'
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    HASH_MD5_PATTERN = r'\b[a-fA-F0-9]{32}\b'
    HASH_SHA256_PATTERN = r'\b[a-fA-F0-9]{64}\b'
    
    def extract(self, text: str) -> ExtractedEntities:
        """Extract all entities from text using regex patterns."""
        entities = ExtractedEntities()
        
        entities.ips = self._extract_ips(text)
        entities.urls = self._extract_urls(text)
        entities.cves = self._extract_cves(text)
        entities.emails = self._extract_emails(text)
        entities.hashes = self._extract_hashes(text)
        
        return entities
    
    def _extract_ips(self, text: str) -> List[str]:
        """Extract IP addresses."""
        ips = re.findall(self.IP_PATTERN, text)
        # Filter out invalid IPs (e.g., 999.999.999.999)
        valid_ips = []
        for ip in ips:
            parts = ip.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                valid_ips.append(ip)
        return list(set(valid_ips))
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs."""
        return list(set(re.findall(self.URL_PATTERN, text)))
    
    def _extract_cves(self, text: str) -> List[str]:
        """Extract CVE identifiers."""
        return list(set(re.findall(self.CVE_PATTERN, text, re.IGNORECASE)))
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses."""
        return list(set(re.findall(self.EMAIL_PATTERN, text)))
    
    def _extract_hashes(self, text: str) -> List[str]:
        """Extract MD5 and SHA256 hashes."""
        md5_hashes = re.findall(self.HASH_MD5_PATTERN, text)
        sha256_hashes = re.findall(self.HASH_SHA256_PATTERN, text)
        return list(set(md5_hashes + sha256_hashes))
