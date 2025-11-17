# src/llm_adapter.py
"""
LLM adapter for Google Gemini API calls.
Handles chat completion with structured JSON output for classification.
"""

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai


class LLMAdapter:
    """Wrapper for Google Gemini API with structured output support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-pro"):
        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
        # Use full model path if not already specified
        if not model.startswith("models/"):
            model = f"models/{model}"
        self.model = genai.GenerativeModel(model)
        self.model_name = model
    
    def classify_incident(
        self, 
        description: str, 
        context: str = "", 
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify incident using structured JSON output.
        Returns dict with category, confidence, rationale.
        """
        if system_prompt is None:
            system_prompt = self._get_default_classification_prompt()
        
        prompt = f"""{system_prompt}

Description: {description}

Context: {context}

Respond with valid JSON only."""
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.0,  # Deterministic for consistent classification
                top_p=1.0,
                response_mime_type="application/json"
            )
        )
        
        result = json.loads(response.text)
        
        # Normalize output format for compatibility
        if "incident_type" in result and "category" not in result:
            # Extract category from "A01: Broken Access Control" format
            incident_type = result["incident_type"]
            if ":" in incident_type:
                category = incident_type.split(":", 1)[1].strip().lower().replace(" ", "_")
            else:
                category = incident_type.lower().replace(" ", "_")
            result["category"] = category
        
        # Use fine_label if available, otherwise use category
        if "fine_label" in result and not result.get("category"):
            result["category"] = result["fine_label"]
            
        return result
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract IOCs and entities from incident description."""
        prompt = """You are an expert at extracting security indicators from incident reports.
Extract IPs, URLs, domains, file hashes, CVEs, and other technical entities.
Return JSON with keys: ips, urls, domains, hashes, cves, emails, filenames.

Text: """ + text + """

Respond with valid JSON only."""
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
    
    def _get_default_classification_prompt(self) -> str:
        return """You are a security incident classifier specializing in OWASP Top 10 categories.

Analyze the incident description and classify it into ONE primary category:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable and Outdated Components
- A07: Identification and Authentication Failures
- A08: Software and Data Integrity Failures
- A09: Security Logging and Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)

Return JSON with:
{
  "incident_type": "<high-level category>",
  "fine_label": "<specific type like sql_injection, xss, broken_authentication>",
  "confidence": <float 0-1>,
  "rationale": "<brief explanation>"
}"""
