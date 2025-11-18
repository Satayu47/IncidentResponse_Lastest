"""
CVE/NVD Integration Service
Fetches vulnerability information from National Vulnerability Database
"""

import requests
import time
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class CVEService:
    """
    Service for querying CVE/NVD database
    Uses NVD REST API v2.0
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = api_key or os.getenv("NVD_API_KEY")
        
        # Rate limiting: 6s without API key, 0.5s with API key
        if self.api_key:
            self.rate_limit_delay = 0.5  # With API key: 50 requests per 30 seconds
        else:
            self.rate_limit_delay = 6  # Without API key: 6 seconds between requests
        
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"apiKey": self.api_key})
        
        self.last_request_time = None
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=24)
    
    def search_vulnerabilities(self, keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for vulnerabilities by keyword
        Returns list of CVE entries
        """
        # Check cache first
        cache_key = f"search_{keyword}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_data
        
        # Rate limiting
        self._apply_rate_limit()
        
        try:
            params = {
                "keywordSearch": keyword,
                "resultsPerPage": max_results
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            vulnerabilities = self._parse_cve_response(data)
            
            # Cache results
            self.cache[cache_key] = (vulnerabilities, datetime.now())
            
            return vulnerabilities
            
        except requests.exceptions.RequestException as e:
            # Return mock data if API fails (for demo purposes)
            return self._get_mock_vulnerabilities(keyword)
    
    def get_cve_by_id(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific CVE by ID (e.g., CVE-2024-1234)
        """
        # Check cache
        if cve_id in self.cache:
            cached_data, cached_time = self.cache[cve_id]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_data
        
        # Rate limiting
        self._apply_rate_limit()
        
        try:
            url = f"{self.base_url}?cveId={cve_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            vulnerabilities = self._parse_cve_response(data)
            
            if vulnerabilities:
                cve_data = vulnerabilities[0]
                self.cache[cve_id] = (cve_data, datetime.now())
                return cve_data
            
            return None
            
        except requests.exceptions.RequestException:
            return self._get_mock_cve(cve_id)
    
    def search_by_software(self, software: str, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search vulnerabilities affecting specific software/version
        """
        search_term = f"{software} {version}" if version else software
        return self.search_vulnerabilities(search_term)
    
    def _parse_cve_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse NVD API response into simplified format"""
        vulnerabilities = []
        
        cve_items = data.get("vulnerabilities", [])
        
        for item in cve_items:
            cve = item.get("cve", {})
            cve_id = cve.get("id", "Unknown")
            
            # Extract description
            descriptions = cve.get("descriptions", [])
            description = ""
            for desc in descriptions:
                if desc.get("lang") == "en":
                    description = desc.get("value", "")
                    break
            
            # Extract CVSS scores
            metrics = cve.get("metrics", {})
            cvss_v3 = metrics.get("cvssMetricV31", [])
            cvss_score = None
            severity = "Unknown"
            
            if cvss_v3:
                cvss_data = cvss_v3[0].get("cvssData", {})
                cvss_score = cvss_data.get("baseScore")
                severity = cvss_data.get("baseSeverity", "Unknown")
            
            # Extract dates
            published = cve.get("published", "")
            modified = cve.get("lastModified", "")
            
            vulnerabilities.append({
                "cve_id": cve_id,
                "description": description[:200] + "..." if len(description) > 200 else description,
                "cvss_score": cvss_score,
                "severity": severity,
                "published": published.split("T")[0] if published else "Unknown",
                "modified": modified.split("T")[0] if modified else "Unknown"
            })
        
        return vulnerabilities
    
    def _apply_rate_limit(self):
        """Apply rate limiting to avoid hitting API limits"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        
        self.last_request_time = datetime.now()
    
    def _get_mock_vulnerabilities(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Return mock vulnerability data for demo purposes
        Used when API is unavailable
        """
        mock_data = {
            "sql": [
                {
                    "cve_id": "CVE-2024-1234",
                    "description": "SQL injection vulnerability in web application allows attackers to execute arbitrary SQL commands",
                    "cvss_score": 9.8,
                    "severity": "CRITICAL",
                    "published": "2024-01-15",
                    "modified": "2024-02-20"
                }
            ],
            "xss": [
                {
                    "cve_id": "CVE-2024-5678",
                    "description": "Cross-site scripting (XSS) vulnerability allows injection of malicious scripts",
                    "cvss_score": 6.1,
                    "severity": "MEDIUM",
                    "published": "2024-03-10",
                    "modified": "2024-03-15"
                }
            ],
            "authentication": [
                {
                    "cve_id": "CVE-2024-9012",
                    "description": "Authentication bypass vulnerability allows unauthorized access",
                    "cvss_score": 8.1,
                    "severity": "HIGH",
                    "published": "2024-05-20",
                    "modified": "2024-06-01"
                }
            ],
            "apache": [
                {
                    "cve_id": "CVE-2024-3456",
                    "description": "Apache HTTP Server vulnerability allows remote code execution",
                    "cvss_score": 9.8,
                    "severity": "CRITICAL",
                    "published": "2024-04-01",
                    "modified": "2024-04-15"
                }
            ]
        }
        
        # Find matching mock data
        keyword_lower = keyword.lower()
        for key, cves in mock_data.items():
            if key in keyword_lower:
                return cves
        
        # Default mock CVE
        return [{
            "cve_id": "CVE-2024-0000",
            "description": f"Vulnerability related to {keyword} - Mock data for demonstration",
            "cvss_score": 7.5,
            "severity": "HIGH",
            "published": "2024-01-01",
            "modified": "2024-01-15"
        }]
    
    def _get_mock_cve(self, cve_id: str) -> Dict[str, Any]:
        """Return mock data for specific CVE ID"""
        return {
            "cve_id": cve_id,
            "description": f"Mock vulnerability data for {cve_id} - Demonstration purposes",
            "cvss_score": 7.5,
            "severity": "HIGH",
            "published": "2024-01-01",
            "modified": "2024-01-15"
        }
    
    def format_cve_summary(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Format CVE list into readable summary"""
        if not vulnerabilities:
            return "No vulnerabilities found."
        
        summary = f"**Found {len(vulnerabilities)} relevant CVE(s):**\n\n"
        
        for cve in vulnerabilities:
            severity_emoji = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }.get(cve["severity"], "⚪")
            
            summary += f"{severity_emoji} **{cve['cve_id']}** "
            summary += f"(CVSS: {cve['cvss_score']}, {cve['severity']})\n"
            summary += f"   {cve['description']}\n"
            summary += f"   Published: {cve['published']}\n\n"
        
        return summary


# Example usage
if __name__ == "__main__":
    cve_service = CVEService()
    
    print("🔍 Searching for SQL injection vulnerabilities...\n")
    results = cve_service.search_vulnerabilities("SQL injection")
    
    print(cve_service.format_cve_summary(results))
