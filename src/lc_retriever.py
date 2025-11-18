# src/lc_retriever.py
"""
LangChain-based retriever for knowledge base search.
Uses vector embeddings for semantic search over security documentation.
"""

from typing import List, Dict, Any, Optional
import os


class KnowledgeBaseRetriever:
    """
    Simple knowledge base retriever for security documentation.
    In production, this would use a vector store like FAISS or Chroma.
    """
    
    def __init__(self, kb_path: Optional[str] = None):
        self.kb_path = kb_path
        # In a real implementation, you'd load and index documents here
        self.mock_kb = self._build_mock_kb()
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge base entries.
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of relevant KB entries with scores
        """
        # Simple keyword-based mock retrieval
        query_lower = query.lower()
        results = []
        
        for entry in self.mock_kb:
            score = self._compute_relevance(query_lower, entry["content"].lower())
            if score > 0:
                results.append({
                    "content": entry["content"],
                    "metadata": entry["metadata"],
                    "score": score,
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _compute_relevance(self, query: str, content: str) -> float:
        """Simple relevance scoring based on keyword overlap."""
        query_words = set(query.split())
        content_words = set(content.split())
        
        overlap = query_words & content_words
        if not query_words:
            return 0.0
        
        return len(overlap) / len(query_words)
    
    def _build_mock_kb(self) -> List[Dict[str, Any]]:
        """Build a comprehensive knowledge base with real-world security information."""
        return [
            # A03: Injection Attacks
            {
                "content": "SQL injection (SQLi) is a code injection attack where malicious SQL code is inserted into application queries. "
                          "Common attack vectors include: ' OR 1=1 --, UNION SELECT, time-based blind SQLi. "
                          "Impact: data breach, authentication bypass, data manipulation. "
                          "Prevention: parameterized queries, input validation, least privilege database accounts, WAF rules. "
                          "Detection: monitor for unusual database query patterns, error messages containing SQL syntax.",
                "metadata": {"category": "injection", "owasp": "A03", "severity": "critical"},
            },
            {
                "content": "Cross-Site Scripting (XSS) occurs when untrusted data is included in web pages without sanitization. "
                          "Types: Reflected XSS (URL parameters), Stored XSS (database), DOM-based XSS (client-side). "
                          "Impact: session hijacking, credential theft, defacement. "
                          "Prevention: output encoding, Content Security Policy (CSP), input validation, HttpOnly cookies. "
                          "Detection: scan for script tags in user-generated content, monitor for suspicious JavaScript execution.",
                "metadata": {"category": "injection", "owasp": "A03", "severity": "high"},
            },
            {
                "content": "Command injection allows attackers to execute arbitrary system commands on the server. "
                          "Common vectors: shell metacharacters (; | &), command chaining, path traversal. "
                          "Impact: full system compromise, data exfiltration, lateral movement. "
                          "Prevention: avoid shell execution, use parameterized APIs, whitelist allowed commands, sanitize input. "
                          "Detection: monitor for unusual system commands, failed command executions, privilege escalation attempts.",
                "metadata": {"category": "injection", "owasp": "A03", "severity": "critical"},
            },
            {
                "content": "LDAP injection targets applications that construct LDAP queries from user input. "
                          "Attack pattern: inject LDAP filter syntax like )(|(cn=*)) to bypass authentication. "
                          "Impact: unauthorized access, information disclosure, privilege escalation. "
                          "Prevention: parameterized LDAP queries, input validation, least privilege LDAP bindings. "
                          "Detection: monitor LDAP query logs for unusual filter patterns.",
                "metadata": {"category": "injection", "owasp": "A03", "severity": "high"},
            },
            # A01: Broken Access Control
            {
                "content": "Broken Access Control (BAC) allows unauthorized access to resources or functionality. "
                          "Common issues: IDOR (Insecure Direct Object Reference), missing authorization checks, privilege escalation. "
                          "Impact: unauthorized data access, account takeover, data modification. "
                          "Prevention: enforce authorization at every endpoint, use access control lists, implement RBAC/ABAC. "
                          "Detection: monitor for unauthorized access attempts, failed authorization checks, privilege escalation.",
                "metadata": {"category": "access_control", "owasp": "A01", "severity": "critical"},
            },
            {
                "content": "IDOR (Insecure Direct Object Reference) occurs when applications expose internal object references. "
                          "Attack: manipulate URLs/parameters to access other users' data (e.g., /api/user/123 → /api/user/456). "
                          "Impact: unauthorized data access, privacy violations. "
                          "Prevention: use indirect references, verify ownership, implement access control checks. "
                          "Detection: monitor for access to resources outside user's scope.",
                "metadata": {"category": "access_control", "owasp": "A01", "severity": "high"},
            },
            # A07: Identification and Authentication Failures
            {
                "content": "Authentication failures occur when authentication mechanisms are weak or misconfigured. "
                          "Common issues: weak passwords, credential stuffing, session fixation, missing MFA. "
                          "Impact: account takeover, unauthorized access, identity theft. "
                          "Prevention: enforce strong password policies, implement MFA, rate limit login attempts, secure session management. "
                          "Detection: monitor for brute force attacks, failed login spikes, suspicious authentication patterns.",
                "metadata": {"category": "authentication", "owasp": "A07", "severity": "high"},
            },
            {
                "content": "Session management vulnerabilities include session fixation, hijacking, and insecure session storage. "
                          "Attack vectors: predictable session IDs, missing HttpOnly flags, session timeout issues. "
                          "Impact: account takeover, unauthorized access. "
                          "Prevention: use secure random session IDs, set secure cookie flags, implement session timeout, regenerate on login. "
                          "Detection: monitor for unusual session activity, concurrent sessions from different locations.",
                "metadata": {"category": "authentication", "owasp": "A07", "severity": "high"},
            },
            # A02: Cryptographic Failures
            {
                "content": "Cryptographic failures involve weak or missing encryption of sensitive data. "
                          "Common issues: weak algorithms (MD5, SHA1), hardcoded keys, plaintext storage, weak TLS configuration. "
                          "Impact: data breach, credential theft, man-in-the-middle attacks. "
                          "Prevention: use strong encryption (AES-256), TLS 1.3, proper key management, encrypt data at rest and in transit. "
                          "Detection: scan for weak cipher suites, monitor for unencrypted sensitive data transmission.",
                "metadata": {"category": "crypto", "owasp": "A02", "severity": "high"},
            },
            # A05: Security Misconfiguration
            {
                "content": "Security misconfigurations are the most common security issue. "
                          "Common problems: default credentials, unnecessary services enabled, verbose error messages, missing security headers. "
                          "Impact: unauthorized access, information disclosure, system compromise. "
                          "Prevention: harden configurations, disable unused features, implement secure defaults, regular security audits. "
                          "Detection: scan for default credentials, check for unnecessary open ports, review error message content.",
                "metadata": {"category": "misconfiguration", "owasp": "A05", "severity": "medium"},
            },
            {
                "content": "Insecure deserialization allows attackers to execute arbitrary code or manipulate application logic. "
                          "Attack: send malicious serialized objects that execute code when deserialized. "
                          "Impact: remote code execution, denial of service, data manipulation. "
                          "Prevention: avoid deserialization of untrusted data, use safe serialization formats (JSON), implement integrity checks. "
                          "Detection: monitor for deserialization errors, unusual object structures, code execution attempts.",
                "metadata": {"category": "injection", "owasp": "A08", "severity": "critical"},
            },
            {
                "content": "Server-Side Request Forgery (SSRF) forces a server to make requests to unintended locations. "
                          "Attack: manipulate URL parameters to make server request internal resources or external malicious sites. "
                          "Impact: internal network scanning, data exfiltration, cloud metadata access. "
                          "Prevention: validate and sanitize URLs, use allowlists for allowed domains, disable internal network access. "
                          "Detection: monitor for unusual outbound requests, requests to internal IPs, cloud metadata access attempts.",
                "metadata": {"category": "ssrf", "owasp": "A10", "severity": "high"},
            },
            {
                "content": "XML External Entity (XXE) attacks exploit XML parsers that process external entity references. "
                          "Attack: inject malicious XML entities to read local files or perform SSRF. "
                          "Impact: local file disclosure, SSRF, denial of service. "
                          "Prevention: disable external entity processing, use safe XML parsers, validate XML input. "
                          "Detection: monitor for file read attempts, unusual XML parsing errors.",
                "metadata": {"category": "xxe", "owasp": "A05", "severity": "high"},
            },
        ]
    
    def get_context_for_label(self, label: str) -> str:
        """Get relevant context excerpt for a classification label."""
        results = self.retrieve(label, top_k=2)
        
        if not results:
            return "No additional context available."
        
        context_parts = []
        for r in results:
            context_parts.append(r["content"][:300])  # Truncate
        
        return " | ".join(context_parts)
