# src/lc_retriever.py
"""
LangChain-based retriever for knowledge base search.
Uses vector embeddings for semantic search over security documentation.
"""

from typing import List, Dict, Any, Optional
import os
from pathlib import Path

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Try older import paths for compatibility
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.embeddings import GoogleGenerativeAIEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.schema import Document
        from langchain.retrievers import BaseRetriever
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        # Fallback types for type hints
        Document = Any
        BaseRetriever = Any


class KnowledgeBaseRetriever:
    """
    Real LangChain-based knowledge base retriever for security documentation.
    Uses FAISS vector store with Google Gemini embeddings for semantic search.
    """
    
    def __init__(self, kb_path: Optional[str] = None, use_cache: bool = True):
        """
        Initialize the knowledge base retriever.
        
        Args:
            kb_path: Optional path to save/load vector store cache
            use_cache: Whether to cache the vector store to disk
        """
        self.kb_path = kb_path or ".kb_cache"
        self.use_cache = use_cache
        self.vector_store = None
        self.embeddings = None
        self.retriever = None
        
        if not LANGCHAIN_AVAILABLE:
            print("WARNING: LangChain not available. Install with: pip install langchain langchain-community langchain-google-genai faiss-cpu")
            print("   Falling back to mock implementation.")
            self._use_mock = True
            self.mock_kb = self._build_mock_kb()
        else:
            self._use_mock = False
            self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the LangChain vector store with embeddings."""
        try:
            # Initialize embeddings using Google Gemini
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("WARNING: GEMINI_API_KEY not found. Using mock implementation.")
                self._use_mock = True
                self.mock_kb = self._build_mock_kb()
                return
            
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
            
            # Try to load cached vector store
            cache_path = Path(self.kb_path)
            if self.use_cache and cache_path.exists() and (cache_path / "index.faiss").exists():
                try:
                    print("Loading cached knowledge base vector store...")
                    self.vector_store = FAISS.load_local(
                        str(cache_path),
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    print("Loaded cached vector store")
                except Exception as e:
                    print(f"WARNING: Failed to load cache: {e}. Rebuilding...")
                    self._build_and_save_vector_store()
            else:
                self._build_and_save_vector_store()
            
            # Create retriever
            if self.vector_store:
                self.retriever = self.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}
                )
                
        except Exception as e:
            print(f"WARNING: Error initializing LangChain: {e}")
            print("   Falling back to mock implementation.")
            self._use_mock = True
            self.mock_kb = self._build_mock_kb()
    
    def _build_and_save_vector_store(self):
        """Build the vector store from knowledge base documents and save it."""
        print("Building knowledge base vector store...")
        
        # Get knowledge base documents
        kb_docs = self._build_mock_kb()
        
        # Convert to LangChain Documents
        documents = []
        for entry in kb_docs:
            doc = Document(
                page_content=entry["content"],
                metadata=entry["metadata"]
            )
            documents.append(doc)
        
        # Split documents into chunks for better retrieval
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Create FAISS vector store
        self.vector_store = FAISS.from_documents(
            split_docs,
            self.embeddings
        )
        
        # Save to disk for future use
        if self.use_cache:
            cache_path = Path(self.kb_path)
            cache_path.mkdir(parents=True, exist_ok=True)
            try:
                self.vector_store.save_local(str(cache_path))
                print(f"Saved vector store to {cache_path}")
            except Exception as e:
                print(f"WARNING: Failed to save cache: {e}")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge base entries using semantic search.
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of relevant KB entries with scores
        """
        if self._use_mock or not self.retriever:
            return self._mock_retrieve(query, top_k)
        
        try:
            # Use LangChain retriever for semantic search
            docs = self.retriever.get_relevant_documents(query)
            
            results = []
            for doc in docs[:top_k]:
                # Extract metadata and content
                metadata = doc.metadata.copy()
                content = doc.page_content
                
                # Calculate relevance score (simplified - LangChain doesn't always return scores)
                # In a real implementation, you might use similarity_search_with_score
                results.append({
                    "content": content,
                    "metadata": metadata,
                    "score": 0.85,  # Default score for semantic matches
                })
            
            return results
            
        except Exception as e:
            print(f"WARNING: Error in LangChain retrieval: {e}")
            print("   Falling back to mock retrieval.")
            return self._mock_retrieve(query, top_k)
    
    def _mock_retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Fallback mock retrieval using keyword matching."""
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
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _compute_relevance(self, query: str, content: str) -> float:
        """Simple relevance scoring based on keyword overlap (fallback)."""
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
