# src/nvd.py
"""
NVD (National Vulnerability Database) API integration.
Fetches CVE details and enrichment data.
"""

import requests
from typing import List, Dict, Any, Optional
import time


class NVDClient:
    """Client for querying the NVD API."""
    
    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"apiKey": api_key})
    
    def get_cve_details(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch details for a specific CVE.
        
        Args:
            cve_id: CVE identifier (e.g., "CVE-2023-12345")
        
        Returns:
            CVE details dict or None if not found
        """
        try:
            params = {"cveId": cve_id}
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("totalResults", 0) > 0:
                return data["vulnerabilities"][0]["cve"]
            return None
            
        except Exception as e:
            print(f"Error fetching CVE {cve_id}: {e}")
            return None
    
    def search_cves(
        self, 
        keyword: Optional[str] = None,
        cpe_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for CVEs by keyword or CPE name.
        
        Args:
            keyword: Search keyword
            cpe_name: CPE name filter
            limit: Maximum number of results
        
        Returns:
            List of CVE summaries
        """
        try:
            params = {"resultsPerPage": min(limit, 100)}
            
            if keyword:
                params["keywordSearch"] = keyword
            if cpe_name:
                params["cpeName"] = cpe_name
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            vulnerabilities = data.get("vulnerabilities", [])
            
            # Extract simplified CVE info
            results = []
            for vuln in vulnerabilities[:limit]:
                cve = vuln.get("cve", {})
                results.append({
                    "id": cve.get("id"),
                    "description": self._get_description(cve),
                    "severity": self._get_severity(cve),
                    "published": cve.get("published"),
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching CVEs: {e}")
            return []
    
    def _get_description(self, cve: Dict[str, Any]) -> str:
        """Extract description from CVE data."""
        descriptions = cve.get("descriptions", [])
        for desc in descriptions:
            if desc.get("lang") == "en":
                return desc.get("value", "")
        return ""
    
    def _get_severity(self, cve: Dict[str, Any]) -> str:
        """Extract severity rating from CVE data."""
        metrics = cve.get("metrics", {})
        
        # Try CVSS v3.1 first
        cvss_v31 = metrics.get("cvssMetricV31", [])
        if cvss_v31:
            return cvss_v31[0].get("cvssData", {}).get("baseSeverity", "UNKNOWN")
        
        # Fallback to CVSS v3.0
        cvss_v30 = metrics.get("cvssMetricV30", [])
        if cvss_v30:
            return cvss_v30[0].get("cvssData", {}).get("baseSeverity", "UNKNOWN")
        
        return "UNKNOWN"
