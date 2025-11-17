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
        """Build a mock knowledge base for demonstration."""
        return [
            {
                "content": "SQL injection is a code injection technique that might destroy your database. "
                          "It occurs when user input is inserted into SQL queries without proper validation. "
                          "Common prevention: use parameterized queries and prepared statements.",
                "metadata": {"category": "injection", "owasp": "A03"},
            },
            {
                "content": "Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web pages. "
                          "Three types exist: reflected, stored, and DOM-based XSS. "
                          "Prevention: sanitize user input, use Content Security Policy.",
                "metadata": {"category": "injection", "owasp": "A03"},
            },
            {
                "content": "Broken Access Control allows unauthorized users to access resources they shouldn't. "
                          "This includes IDOR, privilege escalation, and bypassing authorization. "
                          "Prevention: implement proper authorization checks at every level.",
                "metadata": {"category": "access_control", "owasp": "A01"},
            },
            {
                "content": "Authentication failures occur when authentication mechanisms are implemented incorrectly. "
                          "This includes weak passwords, session fixation, and credential stuffing. "
                          "Prevention: use MFA, strong password policies, and secure session management.",
                "metadata": {"category": "authentication", "owasp": "A07"},
            },
            {
                "content": "Cryptographic failures involve weak or missing encryption of sensitive data. "
                          "This includes using outdated algorithms like MD5 or storing passwords in plaintext. "
                          "Prevention: use strong encryption (AES-256), TLS 1.3, and proper key management.",
                "metadata": {"category": "crypto", "owasp": "A02"},
            },
            {
                "content": "Security misconfigurations are the most common security issue. "
                          "This includes default credentials, unnecessary services, and verbose error messages. "
                          "Prevention: harden configurations, disable unused features, implement secure defaults.",
                "metadata": {"category": "misconfiguration", "owasp": "A05"},
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
