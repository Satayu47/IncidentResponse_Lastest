# src/llm_adapter.py
"""
LLM adapter supporting both Google Gemini and OpenAI/ChatGPT APIs.
Handles structured JSON output for classification.
"""

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai

# Optional OpenAI import - only needed if using ChatGPT
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

# Optional Anthropic Claude import - for baseline comparison
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None


class LLMAdapter:
    """Wrapper around Gemini, OpenAI, and Claude APIs for incident classification."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-pro"):
        # Determine provider based on model name or API key
        self.model_name = model
        self.provider = self._detect_provider(model, api_key)
        
        # Try provided key, then env vars
        if api_key is None:
            if self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
            else:
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        # Initialize provider-specific client
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed. Install with: pip install openai")
            self.client = OpenAI(api_key=api_key)
            self.model = model  # OpenAI uses model name directly
        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
            self.client = Anthropic(api_key=api_key)
            self.model = model  # Anthropic uses model name directly
        else:
            # Gemini
            genai.configure(api_key=api_key)
            # Model path handling - Gemini needs "models/" prefix
            if not model.startswith("models/"):
                model = f"models/{model}"
            self.model = genai.GenerativeModel(model)
            self.model_name = model
    
    def _detect_provider(self, model: str, api_key: Optional[str] = None) -> str:
        """Detect which provider to use based on model name or API key format."""
        # Check model name first
        if model.startswith("gpt-") or model.startswith("o1-") or model.startswith("o3-"):
            return "openai"
        elif model.startswith("gemini-") or model.startswith("models/gemini-"):
            return "gemini"
        elif model.startswith("claude-"):
            return "anthropic"
        
        # Check API key format if provided
        if api_key:
            if api_key.startswith("sk-"):
                return "openai"
            elif api_key.startswith("AIza"):
                return "gemini"
            elif api_key.startswith("sk-ant-"):
                return "anthropic"
        
        # Default to gemini for backwards compatibility
        return "gemini"
    
    def classify_incident(
        self, 
        description: str, 
        context: str = "", 
        system_prompt: Optional[str] = None,
        conversation_history: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify an incident description into OWASP categories.
        Returns dict with category, confidence, rationale.
        """
        if system_prompt is None:
            system_prompt = self._get_default_classification_prompt()
        
        # Build the prompt with full conversation context
        prompt_parts = [system_prompt]
        
        # Add conversation history if available (helps with context and emotions)
        if conversation_history:
            prompt_parts.append(f"\nCONVERSATION HISTORY (remember what we've been discussing):\n{conversation_history}")
        
        prompt_parts.append(f"\nCURRENT USER MESSAGE: {description}")
        
        if context:
            prompt_parts.append(f"\nADDITIONAL CONTEXT: {context}")
        
        prompt_parts.append("\n\nAnalyze the CURRENT USER MESSAGE considering the full conversation history. Understand the user's emotions, urgency, and what they're really trying to say.")
        prompt_parts.append("\nRespond with valid JSON only.")
        
        prompt = "\n".join(prompt_parts)
        
        # Call appropriate API based on provider
        if self.provider == "openai":
            # OpenAI/ChatGPT API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "\n".join(prompt_parts[1:])}  # Skip system prompt in user message
                ],
                temperature=0.1,
                top_p=0.95,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
        elif self.provider == "anthropic":
            # Anthropic Claude API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": "\n".join(prompt_parts[1:])}
                ],
                temperature=0.1
            )
            # Claude returns text, need to extract JSON
            content = response.content[0].text
            # Try to extract JSON from response
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If not pure JSON, try to extract JSON block
                import re
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse JSON from Claude response: {content[:200]}")
        else:
            # Gemini API call
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,  # Slight randomness for better semantic understanding
                    top_p=0.95,
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
        
        # Normalize different output formats (LLM sometimes returns different keys)
        # CRITICAL: Prefer fine_label first (it's the most specific and correct)
        if "fine_label" in result:
            result["category"] = result["fine_label"]
        elif "incident_type" in result:
            # Handle "A01:2025 - Broken Access Control" format
            incident_type = result["incident_type"]
            if " - " in incident_type:
                # Extract category name after the dash (e.g., "A01:2025 - Broken Access Control" -> "broken_access_control")
                category = incident_type.split(" - ", 1)[1].strip().lower().replace(" ", "_")
            elif ":" in incident_type:
                # Fallback: extract from after colon (e.g., "A01: Broken Access Control" -> "broken_access_control")
                parts = incident_type.split(":", 1)
                if len(parts) > 1:
                    category = parts[1].strip().lower().replace(" ", "_")
                else:
                    category = incident_type.lower().replace(" ", "_")
            else:
                category = incident_type.lower().replace(" ", "_")
            result["category"] = category
        
        # Ensure category exists
        if "category" not in result:
            result["category"] = "other"
        
        # Ensure owasp_version is set to 2025
        if "owasp_version" not in result:
            result["owasp_version"] = "2025"
            
        return result
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract IOCs and entities from incident description."""
        prompt = """You are an expert at extracting security indicators from incident reports.
Extract IPs, URLs, domains, file hashes, CVEs, and other technical entities.
Return JSON with keys: ips, urls, domains, hashes, cves, emails, filenames.

Text: """ + text + """

Respond with valid JSON only."""
        
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting security indicators from incident reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system="You are an expert at extracting security indicators from incident reports.",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            content = response.content[0].text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"ips": [], "urls": [], "domains": [], "hashes": [], "cves": [], "emails": [], "filenames": []}
        else:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
    
    def generate_clarifying_question(
        self,
        incident_description: str,
        current_classification: Dict[str, Any],
        conversation_history: Optional[str] = None
    ) -> str:
        """
        Generate a clarifying question when confidence is low.
        Makes the conversation feel more natural and empathetic.
        """
        confidence = current_classification.get("confidence", 0.0)
        incident_type = current_classification.get("incident_type", "Unknown")
        
        # Build prompt for question generation - be empathetic
        prompt = f"""You are a helpful, understanding security incident response assistant. 

The user described an incident, but I'm only {int(confidence*100)}% confident about the classification.

IMPORTANT: The user may be:
- Stressed, worried, or frustrated
- Not a technical expert
- In a hurry
- Using emotional or vague language

Be empathetic and understanding. Ask ONE friendly, conversational question that:
1. Shows you understand their situation
2. Helps clarify what happened
3. Doesn't make them feel stupid
4. Is specific and helpful

{f"Here's what we've discussed so far:\n{conversation_history}\n" if conversation_history else ""}

Current understanding: {incident_type}
User's description: {incident_description}

{f"Previous conversation: {conversation_history}" if conversation_history else ""}

Generate ONE friendly, conversational question to help clarify the incident. Be specific and helpful. Ask about:
- What exactly happened (specific symptoms, error messages, attack patterns)
- Where it occurred (which system, endpoint, page)
- When it happened (timing, frequency)
- What was affected (data, users, systems)

Keep it natural and conversational, like you're talking to a colleague. Don't be too technical. Just ask one clear question.

Return only the question text, nothing else."""

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful, understanding security incident response assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    top_p=0.9
                )
                question = response.choices[0].message.content.strip()
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=256,
                    system="You are a helpful, understanding security incident response assistant.",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                question = response.content[0].text.strip()
            else:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,  # More creative for natural questions
                        top_p=0.9,
                    )
                )
                question = response.text.strip()
            # Remove quotes if present
            if question.startswith('"') and question.endswith('"'):
                question = question[1:-1]
            return question
        except Exception as e:
            # Fallback question
            return "Can you provide more details about what exactly happened? For example, what error messages did you see, or what suspicious activity did you notice?"
    
    def _get_default_classification_prompt(self) -> str:
        return """You are a helpful, empathetic security incident analyst. You understand that people reporting incidents may be:
- Stressed, worried, or frustrated
- Using vague or emotional language
- Not technical experts
- In a hurry
- Confused about what happened

Your task: Understand what the user is REALLY trying to say, even if they express it poorly or emotionally.

IMPORTANT: Understand the SEMANTIC MEANING and HUMAN INTENT, not just keywords. Think step by step:
1. What emotions or urgency is the user expressing? (frustrated, worried, confused, urgent)
2. What is the user REALLY trying to describe? (read between the lines)
3. What security issue does this indicate?
4. Which OWASP category best fits?

Examples of good classification (learn from these):

**FOCUS CATEGORIES: A01, A04, A05, A07 (OWASP 2025)**

Example 1 (A01 - Broken Access Control):
Description: "I changed the number in the URL and saw someone else's profile"
Reasoning: Changing URL parameter to access another user's data = IDOR (Insecure Direct Object Reference) = Broken Access Control
Classification: {"incident_type": "A01:2025 - Broken Access Control", "fine_label": "broken_access_control", "confidence": 0.90, "rationale": "IDOR vulnerability - unauthorized access by manipulating URL parameter"}

Example 2 (A01 - Broken Access Control):
Description: "I can see all customer orders even though I'm just a regular employee"
Reasoning: Regular employee accessing restricted data = Broken Access Control
Classification: {"incident_type": "A01:2025 - Broken Access Control", "fine_label": "broken_access_control", "confidence": 0.95, "rationale": "Access control failure - unauthorized data access by low-privilege user"}

Example 3 (A04 - Cryptographic Failures):
Description: "Our passwords are stored in plain text in the database"
Reasoning: Plaintext password storage = Cryptographic Failure (not encrypted/hashed)
Classification: {"incident_type": "A04:2025 - Cryptographic Failures", "fine_label": "cryptographic_failures", "confidence": 0.95, "rationale": "Critical cryptographic failure - passwords not encrypted at rest"}

Example 4 (A04 - Cryptographic Failures):
Description: "The website doesn't use HTTPS. Users are sending passwords over HTTP"
Reasoning: No encryption in transit = Cryptographic Failure
Classification: {"incident_type": "A04:2025 - Cryptographic Failures", "fine_label": "cryptographic_failures", "confidence": 0.98, "rationale": "Cryptographic failure - sensitive data transmitted without encryption"}

Example 4b (A04 - Cryptographic Failures):
Description: "I found credit card numbers in the logs without any encryption"
Reasoning: Sensitive data (credit cards) exposed without encryption = Cryptographic Failure
Classification: {"incident_type": "A04:2025 - Cryptographic Failures", "fine_label": "cryptographic_failures", "confidence": 0.95, "rationale": "Cryptographic failure - sensitive financial data logged without encryption"}

Example 4c (A04 - Cryptographic Failures):
Description: "The API returns user emails and phone numbers without any protection"
Reasoning: "without any protection" when returning sensitive data (PII) = Cryptographic Failure (data not encrypted)
Classification: {"incident_type": "A04:2025 - Cryptographic Failures", "fine_label": "cryptographic_failures", "confidence": 0.90, "rationale": "Cryptographic failure - sensitive PII exposed without encryption protection"}

Example 4d (A04 - Cryptographic Failures):
Description: "I can see user data when I look at the network traffic. It's not encrypted"
Reasoning: Data visible in network traffic without encryption = Cryptographic Failure
Classification: {"incident_type": "A04:2025 - Cryptographic Failures", "fine_label": "cryptographic_failures", "confidence": 0.95, "rationale": "Cryptographic failure - sensitive data transmitted unencrypted over network"}

Example 5 (A05 - Injection):
Description: "Weird syntax appear on login page. Looks like code but I'm not sure"
Reasoning: "weird syntax" + "login" = code injection, likely SQL injection
Classification: {"incident_type": "A05:2025 - Injection", "fine_label": "sql_injection", "confidence": 0.85, "rationale": "Syntax errors on login page typically indicate SQL injection attempts"}

Example 6 (A05 - Injection):
Description: "When I type special characters in the search box, the page breaks"
Reasoning: Special characters causing page break = injection vulnerability
Classification: {"incident_type": "A05:2025 - Injection", "fine_label": "injection", "confidence": 0.85, "rationale": "Input validation failure - special characters causing injection attack"}

Example 7 (A07 - Authentication Failures):
Description: "I can log in with password '12345'. That seems too easy"
Reasoning: Weak password accepted = Authentication Failure (weak password policy)
Classification: {"incident_type": "A07:2025 - Authentication Failures", "fine_label": "broken_authentication", "confidence": 0.95, "rationale": "Authentication failure - weak password policy allows insecure passwords"}

Example 8 (A07 - Authentication Failures):
Description: "I tried wrong passwords many times but the system didn't lock me out"
Reasoning: No account lockout = Authentication Failure (brute force protection missing)
Classification: {"incident_type": "A07:2025 - Authentication Failures", "fine_label": "broken_authentication", "confidence": 0.95, "rationale": "Authentication failure - missing brute force protection"}

Example 9 (A05 - Injection):
Description: "My table disappeared from the database. Could someone have deleted it?"
Reasoning: Could be SQL injection (DROP TABLE), but ambiguous - use lower confidence
Classification: {"incident_type": "A05:2025 - Injection", "fine_label": "sql_injection", "confidence": 0.55, "rationale": "Table missing could indicate SQL injection (DROP TABLE), but could also be admin mistake or database issue - needs clarification"}

**OWASP Top 10:2025 Categories (ALWAYS USE 2025 VERSION):**

**PRIMARY FOCUS CATEGORIES:**
- **A01:2025 - Broken Access Control**: Unauthorized access, IDOR, privilege escalation, tenant isolation, role-based access violations, accessing deleted resources
- **A04:2025 - Cryptographic Failures**: Weak encryption, plaintext storage, missing TLS/HTTPS, unencrypted data in transit/at rest, weak hashing algorithms
- **A05:2025 - Injection**: SQL injection, XSS, command injection, code injection, LDAP injection, NoSQL injection, input validation failures
- **A07:2025 - Authentication Failures**: Weak passwords, session management issues, MFA bypass, no account lockout, session never expires, password policy failures

**OTHER CATEGORIES:**
- A02:2025 - Security Misconfiguration (default credentials, exposed services, verbose errors)
- A03:2025 - Software Supply Chain Failures (vulnerable dependencies, unpatched software, supply chain attacks)
- A06:2025 - Insecure Design (design flaws, missing security controls) - **ONLY use this when it's truly a design flaw, NOT when it's a specific vulnerability like IDOR, injection, crypto failure, or auth failure**
- A08:2025 - Software or Data Integrity Failures (insecure deserialization, integrity violations)
- A09:2025 - Logging & Alerting Failures (missing logs, no alerts, insufficient monitoring)
- A10:2025 - Mishandling of Exceptional Conditions (error handling flaws, SSRF, exception disclosure)

**CRITICAL: Do NOT classify as A06 (Insecure Design) when the issue is:**
- IDOR or unauthorized access → Use A01 (Broken Access Control)
- Plaintext passwords or missing encryption → Use A04 (Cryptographic Failures)
- SQL injection, XSS, or code injection → Use A05 (Injection)
- Weak passwords or session issues → Use A07 (Authentication Failures)

Guidelines:
1. **Understand human nature**: People express things differently:
   - Emotional: "I'm worried", "This is bad", "Help!"
   - Vague: "Something weird", "Not working", "Errors"
   - Urgent: "ASAP", "Critical", "Right now"
   - Technical: Direct descriptions
   - ALL are valid - understand the intent behind the words

2. **Remember conversation context**: If user said "weird syntax" earlier and now says "it's getting worse", they're talking about the same incident

3. **Think semantically and use correct OWASP 2025 categories**:
   - "changed URL number" + "saw another user's data" = A01 (Broken Access Control / IDOR)
   - "plaintext passwords" or "no HTTPS" = A04 (Cryptographic Failures)
   - "weird syntax" + "login" or "special characters" + "database errors" = A05 (Injection)
   - "weak password" or "session never expires" or "no lockout" = A07 (Authentication Failures)
   - "frustrated" + "errors" = likely security issue (determine which category)

4. **Handle ambiguity and multiple issues**: Some incidents can have MULTIPLE causes:
   - "Table missing" = could be SQL injection OR admin mistake OR database issue
   - "Errors on website" = could be injection OR misconfiguration OR attack
   - When ambiguous, classify as the MOST LIKELY security issue but mention other possibilities in rationale
   
   **IMPORTANT: When BOTH encryption and authorization issues are present:**
   - If the description mentions "plain text", "unencrypted", "not encrypted", "without encryption", "not hashed", "in plain text" → Prioritize A04 (Cryptographic Failures)
   - Examples:
     * "API returns sensitive data without authorization, and it's all in plain text" → A04 (Cryptographic Failures) - encryption is the primary issue
     * "API returns user data without any protection" (ambiguous) → If "plain text" or "unencrypted" mentioned → A04, else A01
     * "Passwords in JSON response, not hashed" → A04 (Cryptographic Failures)
     * "I can see passwords in the logs" → A04 (Cryptographic Failures) - sensitive data exposure
     * "Network traffic is not encrypted" → A04 (Cryptographic Failures) - missing encryption in transit
   
   **IMPORTANT: When MULTIPLE security issues are described:**
   - If the description mentions multiple distinct issues (e.g., "XSS" AND "admin access", "SQL injection" AND "weak password"), classify as the FIRST/MOST EXPLICIT issue mentioned
   - Examples:
     * "JavaScript code executed on browsers AND I can access admin panel" → A05 (Injection) - XSS is explicit
     * "System crashed after weird command AND session doesn't expire" → A05 (Injection) - command injection is explicit
   - However, if encryption keywords are present, prioritize A04 even if mentioned second
   
   **CRITICAL: When MULTIPLE security issues are mentioned in one description:**
   - Look for connecting words: "and", "also", "plus", "combined with", "as well as"
   - If multiple issues are explicitly mentioned, classify as the FIRST or MOST SEVERE issue
   - Examples:
     * "I can access admin panel AND login form has SQL injection" → A01 (Broken Access Control) - access control mentioned first
     * "XSS in comments AND I can access admin" → A05 (Injection) - injection mentioned first, or A01 if access control is more severe
     * "JavaScript executed in browser AND admin access" → A05 (Injection) - code execution is the attack vector
     * "Command injection in upload AND session doesn't expire" → A05 (Injection) - injection is the active attack

5. **Incidents can be related**: One incident can lead to another or be a subset:
   - SQL injection can lead to data breach (subset relationship)
   - Broken authentication can lead to unauthorized access
   - Consider the primary issue first, but note relationships

6. **Context is key**: Where did it happen? What was the impact? How does the user feel?

7. **Confidence levels**:
   - 0.9-1.0: Very clear, explicit description, no ambiguity
   - 0.7-0.89: Clear pattern, good context, minor ambiguity
   - 0.5-0.69: Somewhat vague, pattern recognizable, some ambiguity (common with emotional/vague descriptions)
   - 0.3-0.49: Very vague, multiple possibilities, low confidence
   
8. **When vague or ambiguous**: Classify as the most likely security issue, but use lower confidence and mention other possibilities in rationale. The system will ask clarifying questions.

Return JSON with:
{
  "incident_type": "<OWASP 2025 category like 'A05:2025 - Injection' or 'A01:2025 - Broken Access Control' or 'A04:2025 - Cryptographic Failures' or 'A07:2025 - Authentication Failures'>",
  "fine_label": "<specific type: broken_access_control, sql_injection, xss, broken_authentication, cryptographic_failures, etc.>",
  "confidence": <float 0-1>,
  "rationale": "<brief step-by-step explanation. If ambiguous, mention other possibilities like 'could be SQL injection, but might also be admin mistake or database issue'>",
  "owasp_version": "2025"
}

**IMPORTANT RULES:**
1. ALWAYS use "2025" in incident_type (e.g., "A01:2025 - Broken Access Control")
2. ALWAYS set "owasp_version": "2025"
3. Use fine_label values: "broken_access_control", "injection", "sql_injection", "xss", "broken_authentication", "cryptographic_failures"
4. Do NOT use "insecure_design" unless it's truly a design flaw that doesn't fit A01, A04, A05, or A07
5. When in doubt between categories, choose the MOST SPECIFIC one:
   - IDOR/unauthorized access → A01 (NOT A06)
   - Plaintext/missing encryption → A04 (NOT A06)
   - Code injection/SQL/XSS → A05 (NOT A06)
   - Password/session issues → A07 (NOT A06)

IMPORTANT: In your rationale, if the incident could have multiple causes, mention them. For example:
- "Table missing could be SQL injection (DROP TABLE), but might also be admin mistake or database corruption"
- "Errors on login could be injection attack, but could also be misconfiguration"
This helps users understand the ambiguity and provides better context."""
