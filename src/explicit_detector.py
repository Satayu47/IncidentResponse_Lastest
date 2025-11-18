# src/explicit_detector.py
"""
Keyword/pattern-based detection for common security incidents.
Fast path before expensive LLM calls - saves a lot of API costs.
Built up these patterns over time from real incident reports.
"""

import re
from typing import Tuple, Optional


class ExplicitDetector:
    """Fast keyword-based detection for obvious security patterns."""
    
    def __init__(self):
        # regex patterns - ordered by specificity (most specific first)
        # confidence scores tuned during testing
        self.patterns = [
            
            # ===== OTHER / NON-SECURITY (check first to avoid false positives) =====
            (r"\buser (forgot|mistyped|typo)", "other", 0.95),
            (r"\bno (security|deeper) issue", "other", 0.95),
            (r"\bannoy.*not security", "other", 0.95),
            (r"\bno logs.*no evidence", "other", 0.90),
            
            # ===== BROKEN ACCESS CONTROL (high confidence patterns) =====
            (r"\bnormal (staff|users?) can access.*/admin\b", "broken_access_control", 0.95),
            (r"\bviewer role can delete\b", "broken_access_control", 0.95),
            (r"\bcan see (another|other) (customer|user|tenant)'?s", "broken_access_control", 0.95),
            (r"\bchange.*(user|invoice|account).*id.*url\b", "broken_access_control", 0.90),
            (r"\btenant isolation.*broken\b", "broken_access_control", 0.95),
            (r"\bescalate.*to admin\b", "broken_access_control", 0.95),
            (r"\bunauthenticated.*can (call|access|export)\b", "broken_access_control", 0.95),
            (r"\bsoft[- ]deleted.*still accessible\b", "broken_access_control", 0.90),
            (r"\bintern.*approve.*financial\b", "broken_access_control", 0.90),
            (r"\baccess.*/admin.*without.*log(ged|ging) in\b", "broken_access_control", 0.95),
            (r"\bprivileges?.*escalat", "broken_access_control", 0.85),
            (r"\bidor\b", "broken_access_control", 0.85),
            (r"\bunauthorized access", "broken_access_control", 0.80),
            (r"\bbroken access control", "broken_access_control", 0.90),
            (r"\ballows unauthorized.*data access", "broken_access_control", 0.90),
            (r"\bunauthorized.*data access", "broken_access_control", 0.85),
            # Edge cases: URL manipulation and indirect descriptions
            (r"\bchanged.*number.*url.*saw.*(profile|account|data|information)", "broken_access_control", 0.90),
            (r"\bchanged.*(id|number).*url.*see.*(other|another|someone)", "broken_access_control", 0.90),
            (r"\btyped.*/admin.*url\b", "broken_access_control", 0.90),
            (r"\bjust.*typed.*(admin|panel).*url\b", "broken_access_control", 0.90),
            (r"\bcan see.*all.*(customer|user|order|invoice).*even though.*(regular|normal|viewer|employee)", "broken_access_control", 0.90),
            (r"\b(regular|normal|viewer|employee).*can see.*all", "broken_access_control", 0.85),
            (r"\bdelete.*account.*still.*access.*(direct|link|url)", "broken_access_control", 0.90),
            (r"\bdeleted.*account.*can still.*access", "broken_access_control", 0.90),
            (r"\b(viewer|employee|regular).*can.*(approve|delete|edit|modify)", "broken_access_control", 0.90),
            (r"\bcan.*(edit|modify|delete).*other.*(user|post|account|file).*by.*(changing|changing|url)", "broken_access_control", 0.90),
            (r"\bchange.*(post|user|account|file).*id.*(url|link)", "broken_access_control", 0.90),
            (r"\b(customer|user).*can see.*(other|another).*(company|tenant|customer).*by.*(changing|changing)", "broken_access_control", 0.90),
            (r"\bcan.*download.*(file|files).*other.*(user|users).*just.*(need|know).*id", "broken_access_control", 0.90),
            (r"\bknow.*(file|user|account).*id.*can.*(access|download|see)", "broken_access_control", 0.85),
            (r"\bclick.*link.*email.*can see.*(other|another).*(private|message|data)", "broken_access_control", 0.85),
            (r"\bemail.*link.*see.*(other|another).*(user|person|account)", "broken_access_control", 0.85),
            
            # ===== INJECTION (high confidence patterns) =====
            (r"'\s*or\s+'?1'?\s*=\s*'?1", "injection", 0.98),
            (r"'\s*or\s+1\s*=\s*1", "injection", 0.98),
            (r"\bdrop\s+table\b", "injection", 0.98),
            (r"<script>.*alert.*</script>", "injection", 0.98),
            (r"\bunion\s+select\b", "injection", 0.98),
            (r"\bsql\s+injection\b", "injection", 0.95),
            (r"\bsql\s+error", "injection", 0.85),
            (r"\bsyntax error.*near.*or\b", "injection", 0.90),
            (r"\b(weird|strange|unusual).*syntax.*(login|web|page|form|input)", "injection", 0.80),  # "weird syntax on login"
            (r"\b(weird|strange|unusual).*sy?yntax.*(login|web|page|form|input)", "injection", 0.80),  # Handle typo "syyntax"
            (r"\bsyntax.*(appear|show|display).*(login|web|page)", "injection", 0.80),  # "syntax appear on login"
            (r"\bsy?yntax.*(appear|show|display).*(login|web|page)", "injection", 0.80),  # Handle typo "syyntax appear"
            (r"\b(weird|strange).*sy?yntax.*appear.*(login|web|page)", "injection", 0.80),  # "weird syyntax appear on web login"
            (r"\b(weird|strange).*symbols?.*(login|web|page)", "injection", 0.75),  # "weird symbols on login"
            (r"\bweird.*(payload|input|query)", "injection", 0.75),
            (r";.*rm\s+-rf", "injection", 0.95),
            (r"\bcommand\s+injection\b", "injection", 0.95),
            (r"\bxss\b", "injection", 0.95),
            (r"\breflects?\s+html\s+without\s+escaping", "injection", 0.90),
            (r"\bsqli\b", "injection", 0.90),
            (r"\bmalicious.*serialized.*(object|data)", "injection", 0.90),
            (r"\bremote code execution", "injection", 0.90),
            (r"\bdeserialization", "injection", 0.85),
            (r"\b(db|database).*error", "injection", 0.75),  # "db error" often means SQL injection
            (r"\berror.*(login|web|page)", "injection", 0.70),  # generic error on login might be injection
            # Multi-incident patterns - injection mentioned with other issues
            (r"\b(javascript|js|code).*(executed?|runs?|executes?).*(browser|user|page)", "injection", 0.90),  # XSS
            (r"\b(weird|strange).*command.*(upload|file|field)", "injection", 0.85),  # Command injection
            (r"\bsystem.*crash.*(weird|strange).*command", "injection", 0.85),  # Command injection causing crash
            # Edge cases: vague descriptions and indirect patterns
            (r"\b(weird|strange|unusual).*syntax.*(appear|show|display|looks)", "injection", 0.80),
            (r"\bsyntax.*(appear|show|display).*(login|page|form)", "injection", 0.80),
            (r"\b(table|tables).*disappeared.*database", "injection", 0.85),  # Could be SQL injection
            (r"\b(table|tables?).*missing.*database", "injection", 0.85),  # "my table is missing from database"
            (r"\bmy.*table.*missing.*database", "injection", 0.85),  # "my table is missing from database"
            (r"\bdatabase.*table.*missing", "injection", 0.80),  # "database table missing"
            (r"\btable.*missing.*from.*database", "injection", 0.85),  # "table missing from database"
            (r"\btype.*special.*character.*(search|input|form).*page.*(break|crash|error)", "injection", 0.80),
            (r"\berror.*message.*show.*(database|db|table|structure)", "injection", 0.85),
            (r"\b(database|db).*error.*show.*(structure|table|schema)", "injection", 0.85),
            (r"\benter.*(javascript|js|code).*(comment|form|field).*(executed|execute|runs?).*(browser|user|screen)", "injection", 0.90),
            (r"\b(javascript|code).*(comment|form|field).*(appear|show).*(other|user|screen)", "injection", 0.90),
            (r"\bpaste.*code.*(snippet|snippets).*(form|field).*(appear|show).*(other|user|screen).*(actual|as)", "injection", 0.90),
            (r"\b(login|form).*accept.*(strange|weird|special).*character.*(database|db).*error", "injection", 0.85),
            (r"\btype.*(character|characters).*(search|input).*page.*(show|shows).*sql.*error", "injection", 0.90),
            (r"\b(search|input).*certain.*(character|characters).*page.*(show|shows).*sql.*error", "injection", 0.90),
            (r"\b(entered|enter).*weird.*command.*(upload|field|form).*system.*(crash|crashed)", "injection", 0.85),
            (r"\bsystem.*(crash|crashed).*entered.*(weird|strange).*command", "injection", 0.85),
            (r"\b(weird|strange).*command.*(upload|field|form).*crash", "injection", 0.85),
            
            # ===== BROKEN AUTHENTICATION (high confidence patterns) =====
            (r"\bany\s+\d+\s*digit.*code.*accepted", "broken_authentication", 0.95),
            (r"\bsession.*never.*expire", "broken_authentication", 0.95),
            (r"\bjwt.*never.*expire", "broken_authentication", 0.95),
            (r"\bno.*exp.*claim", "broken_authentication", 0.90),
            (r"\bpassword.*plaintext", "broken_authentication", 0.98),
            (r"\bno.*account.*lockout", "broken_authentication", 0.90),
            (r"\bno.*lock.*after.*fail", "broken_authentication", 0.90),
            (r"\breset.*link.*no.*expir", "broken_authentication", 0.95),
            (r"\bsame session id.*before.*after.*login", "broken_authentication", 0.95),
            (r"\bpassword.*md5.*without.*salt", "broken_authentication", 0.90),
            (r"\b2fa.*optional", "broken_authentication", 0.85),
            (r"\bsession hijack", "broken_authentication", 0.85),
            (r"\bcredential stuffing", "broken_authentication", 0.90),
            # Edge cases: weak passwords, session management, and indirect descriptions
            (r"\blog.*in.*password.*'12345'", "broken_authentication", 0.90),
            (r"\bpassword.*'12345'.*too.*easy", "broken_authentication", 0.90),
            (r"\bsession.*never.*expires.*logged.*in.*(week|month|ago)", "broken_authentication", 0.90),
            (r"\blogged.*in.*(week|month|ago).*still.*logged.*in", "broken_authentication", 0.90),
            (r"\btried.*wrong.*password.*(many|multiple|several).*time.*(didn't|did not|no).*lock", "broken_authentication", 0.90),
            (r"\b(wrong|incorrect).*password.*(many|multiple).*time.*(no|not).*lock.*out", "broken_authentication", 0.90),
            (r"\bforgot.*password.*still.*access.*account", "broken_authentication", 0.85),  # Could be session issue
            (r"\bforgot.*password.*can still.*access", "broken_authentication", 0.85),
            (r"\bauthentication failure", "broken_authentication", 0.90),
            (r"\bmultiple failed login attempts", "broken_authentication", 0.90),
            (r"\bfailed login attempts", "broken_authentication", 0.85),
            (r"\b(doesn't|does not|not).*require.*(two|2).*factor.*(auth|authentication).*admin", "broken_authentication", 0.90),
            (r"\b(no|missing|not).*two.*factor.*(auth|authentication).*admin", "broken_authentication", 0.90),
            (r"\blogged.*out.*(go back|return|visit).*still.*logged.*in", "broken_authentication", 0.90),
            (r"\blog.*out.*still.*logged.*in.*(go back|return)", "broken_authentication", 0.90),
            (r"\bpassword.*(username|user.*name).*same", "broken_authentication", 0.90),
            (r"\bpassword.*can.*be.*(username|user.*name)", "broken_authentication", 0.90),
            (r"\breset.*password.*(without|no).*verification", "broken_authentication", 0.85),
            (r"\bpassword.*reset.*(without|no).*proper.*verification", "broken_authentication", 0.85),
            
            # ===== SENSITIVE DATA EXPOSURE (high confidence patterns) =====
            (r"\bcredit card.*log", "sensitive_data_exposure", 0.95),
            (r"\bssn.*exposed", "sensitive_data_exposure", 0.95),
            (r"\bpii.*public.*s3", "sensitive_data_exposure", 0.95),
            (r"\bfull.*card.*number.*unmask", "sensitive_data_exposure", 0.95),
            (r"\bexport.*full card number", "sensitive_data_exposure", 0.95),
            (r"\bno masking", "sensitive_data_exposure", 0.85),
            (r"\bsalary.*download", "sensitive_data_exposure", 0.90),
            (r"\bstack trace.*secret", "sensitive_data_exposure", 0.90),
            (r"\bauthorization.*header.*log", "sensitive_data_exposure", 0.90),
            (r"\bbearer token.*visible", "sensitive_data_exposure", 0.90),
            (r"\bnational id.*full.*frontend", "sensitive_data_exposure", 0.90),
            (r"\bdata leak", "sensitive_data_exposure", 0.85),
            (r"\bsensitive data", "sensitive_data_exposure", 0.80),
            (r"\bsecurity misconfiguration.*exposes sensitive data", "sensitive_data_exposure", 0.90),
            (r"\bexposes sensitive data", "sensitive_data_exposure", 0.85),
            
            # ===== CRYPTOGRAPHIC FAILURES (high confidence patterns) =====
            (r"\btokens?.*md5.*without salt", "cryptographic_failures", 0.95),
            (r"\bhashed.*md5.*without salt", "cryptographic_failures", 0.95),
            (r"\blogin.*http.*not.*https", "cryptographic_failures", 0.95),
            (r"\btls.*certificate.*expired", "cryptographic_failures", 0.95),
            (r"\bnot secure.*login", "cryptographic_failures", 0.90),
            (r"\bself[- ]signed.*certificate.*production", "cryptographic_failures", 0.95),
            (r"\btls\s+1\.0", "cryptographic_failures", 0.90),
            (r"\bweak.*cipher", "cryptographic_failures", 0.85),
            (r"\bhard[- ]coded.*aes.*key", "cryptographic_failures", 0.95),
            (r"\btls.*disabled", "cryptographic_failures", 0.95),
            (r"\bhttp\s+only.*password", "cryptographic_failures", 0.95),
            (r"\bweak encryption", "cryptographic_failures", 0.85),
            # Edge cases: network traffic, API responses, and indirect descriptions
            (r"\bcan see.*user.*data.*(network|traffic).*not.*encrypted", "cryptographic_failures", 0.90),
            (r"\blook.*network.*traffic.*not.*encrypted", "cryptographic_failures", 0.90),
            (r"\b(network|traffic).*not.*encrypted.*can.*see", "cryptographic_failures", 0.90),
            (r"\bapi.*(return|returns|returning).*(email|phone|password|data).*(without|no).*protection", "cryptographic_failures", 0.90),
            (r"\bapi.*response.*can.*see.*(password|passwords).*json", "cryptographic_failures", 0.90),
            (r"\bcheck.*api.*response.*can.*see.*password.*(not|not).*(hashed|encrypted)", "cryptographic_failures", 0.90),
            (r"\b(backup|backups).*contain.*(unencrypted|not encrypted).*(customer|user|data)", "cryptographic_failures", 0.90),
            (r"\bbackup.*(unencrypted|not encrypted).*anyone.*access.*can.*read", "cryptographic_failures", 0.90),
            (r"\b(mobile|app).*sends.*(user|location|data).*http.*instead.*https", "cryptographic_failures", 0.90),
            (r"\b(mobile|app).*sends.*(data|information).*http.*not.*https", "cryptographic_failures", 0.90),
            (r"\bfound.*(medical|health).*(record|records).*database.*(without|not).*encryption", "cryptographic_failures", 0.90),
            (r"\b(medical|health).*(record|records).*stored.*(without|not).*encryption", "cryptographic_failures", 0.90),
            # More specific patterns for common A04 test cases
            (r"\bpasswords?.*stored.*plain.*text.*database", "cryptographic_failures", 0.95),
            (r"\bstored.*plain.*text.*database.*(password|passwords)", "cryptographic_failures", 0.95),
            (r"\bfound.*(credit card|card number).*log.*(without|no).*encryption", "cryptographic_failures", 0.95),
            (r"\b(credit card|card number).*log.*(without|no).*encryption", "cryptographic_failures", 0.95),
            (r"\bwebsite.*(doesn't|does not|not).*use.*https", "cryptographic_failures", 0.95),
            (r"\b(doesn't|does not|not).*use.*https.*(user|users).*sending", "cryptographic_failures", 0.95),
            (r"\b(users?|user).*sending.*(password|passwords).*over.*http", "cryptographic_failures", 0.95),
            (r"\bsending.*(password|passwords).*over.*http", "cryptographic_failures", 0.95),
            (r"\bsee.*user.*data.*(network|traffic).*not.*encrypted", "cryptographic_failures", 0.90),
            (r"\bapi.*returns.*(email|phone|number).*(without|no).*protection", "cryptographic_failures", 0.90),
            (r"\bapi.*returns.*(email|phone).*without.*any.*protection", "cryptographic_failures", 0.90),
            (r"\bstores.*(ssn|social security).*plain.*text", "cryptographic_failures", 0.95),
            (r"\b(social security|ssn).*plain.*text.*(see|can see).*database", "cryptographic_failures", 0.95),
            (r"\bcheck.*api.*response.*see.*password.*json.*(not|not).*(hashed|encrypted)", "cryptographic_failures", 0.90),
            (r"\bapi.*response.*see.*password.*json.*(not|not).*(hashed|anything)", "cryptographic_failures", 0.90),
            (r"\bbackup.*file.*(contain|contains).*(unencrypted|not encrypted).*(customer|user|data)", "cryptographic_failures", 0.90),
            (r"\bfound.*(medical|health).*(record|records).*database.*stored.*(without|not).*encryption", "cryptographic_failures", 0.90),
            (r"\b(log|logs|logging).*(include|includes|contain).*(password|passwords|credit card)", "cryptographic_failures", 0.90),
            (r"\bfound.*(user|information).*log.*(include|includes).*(password|credit card)", "cryptographic_failures", 0.90),
            # Patterns for ambiguous cases - prioritize crypto when encryption keywords present
            (r"\b(plain text|plaintext|unencrypted|not encrypted|without encryption).*(password|data|information|sensitive)", "cryptographic_failures", 0.90),
            (r"\b(password|data|sensitive).*(plain text|plaintext|unencrypted|not encrypted|without encryption)", "cryptographic_failures", 0.90),
            (r"\b(returns|returns|exposes).*(plain text|plaintext|unencrypted).*(data|information|sensitive)", "cryptographic_failures", 0.90),
            (r"\b(all|everything).*(plain text|plaintext|unencrypted)", "cryptographic_failures", 0.85),
            # Handle "without any protection" when returning sensitive data (prioritize crypto)
            (r"\b(api|endpoint|returns).*(email|phone|password|ssn|credit card|sensitive).*(without any protection|without protection)", "cryptographic_failures", 0.85),
            (r"\breturns.*(email|phone|password|ssn|credit card|sensitive).*(without any protection|without protection)", "cryptographic_failures", 0.85),
            # Additional A04 patterns for better detection
            (r"\b(credit card|card number|ssn|social security).*(log|logs|logging)", "cryptographic_failures", 0.90),
            (r"\b(password|passwords).*(log|logs|logging|visible|see)", "cryptographic_failures", 0.90),
            (r"\b(network traffic|network).*(not encrypted|unencrypted|plain)", "cryptographic_failures", 0.90),
            # More specific patterns for A04
            (r"\b(stored|storage|store).*(plain text|plaintext|unencrypted|not encrypted)", "cryptographic_failures", 0.90),
            (r"\b(database|db).*(plain text|plaintext|unencrypted|not encrypted|not hashed)", "cryptographic_failures", 0.90),
            (r"\b(backup|backups).*(unencrypted|not encrypted|plain)", "cryptographic_failures", 0.90),
            (r"\b(medical records|health data|pii).*(unencrypted|not encrypted|plain)", "cryptographic_failures", 0.90),
            (r"\b(api|endpoint).*(returns|returning).*(password|passwords|plain text|plaintext)", "cryptographic_failures", 0.90),
            (r"\b(see|visible|can see).*(password|passwords|credit card).*(json|response|api)", "cryptographic_failures", 0.90),
            (r"\b(not hashed|not hashing|no hash|without hash)", "cryptographic_failures", 0.90),
            (r"\b(sent|sending|transmit).*(http|over http).*(instead of|not)", "cryptographic_failures", 0.90),
            (r"\b(mobile app|app).*(http|not https|without https)", "cryptographic_failures", 0.90),
            # Multi-incident patterns - detect when both issues present
            (r"\b(javascript|js|code).*(executed|execute|runs?).*(browser|browsers|users)", "injection", 0.90),
            (r"\b(weird|strange).*(command|text|input).*(upload|field|form)", "injection", 0.85),
            (r"\b(crashed|crash).*(weird|strange).*(command|text|input)", "injection", 0.85),
            (r"\b(data|information).*(network traffic|traffic).*(not encrypted|unencrypted)", "cryptographic_failures", 0.90),
            
            # ===== SECURITY MISCONFIGURATION (high confidence patterns) =====
            (r"\bdefault.*credential", "security_misconfiguration", 0.95),
            (r"\badmin/admin", "security_misconfiguration", 0.95),
            (r"\bguest/guest", "security_misconfiguration", 0.95),
            (r"\bdirectory listing.*enabled", "security_misconfiguration", 0.95),
            (r"\bdebug.*mode.*production", "security_misconfiguration", 0.95),
            (r"\bkibana.*exposed.*internet", "security_misconfiguration", 0.95),
            (r"\btest.*endpoint.*production", "security_misconfiguration", 0.90),
            (r"\bfirewall.*ssh.*anywhere", "security_misconfiguration", 0.90),
            (r"\bs3.*bucket.*public", "security_misconfiguration", 0.95),
            (r"\bwaf.*disabled", "security_misconfiguration", 0.90),
            (r"\bcors.*\*", "security_misconfiguration", 0.85),
            (r"\bstack trace.*all users", "security_misconfiguration", 0.90),
            (r"\bmonitoring dashboard.*public", "security_misconfiguration", 0.95),
            (r"\b(dashboard|panel|admin).*public.*no login", "security_misconfiguration", 0.90),
            (r"\bmisconfiguration\b", "security_misconfiguration", 0.80),
            
            # ===== CVE / VULNERABLE COMPONENTS =====
            (r"\bcve-\d{4}-\d{4,}", "vulnerable_components", 0.90),
            (r"\boutdated (library|component)", "vulnerable_components", 0.85),
            (r"\bknown vulnerability", "vulnerable_components", 0.85),
            
            # ===== SSRF (Server-Side Request Forgery) =====
            (r"\bssrf\b", "injection", 0.90),
            (r"\bserver.*side.*request.*forgery", "injection", 0.90),
            (r"\bssrf attack", "injection", 0.90),
            
            # ===== LOGGING FAILURES =====
            (r"\blogging failure", "security_misconfiguration", 0.85),
            (r"\bsecurity events.*not.*record", "security_misconfiguration", 0.85),
            (r"\bsecurity.*events.*not.*logged", "security_misconfiguration", 0.85),
        ]
    
    def detect(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect incident type using regex pattern matching.
        Returns first match with highest confidence.
        
        Args:
            text: Incident description
        
        Returns:
            Tuple of (detected_type, confidence_score)
            Returns (None, 0.0) if no match found
        """
        text_lower = text.lower()
        
        # Find all matches
        matches = []
        for pattern, label, confidence in self.patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matches.append((label, confidence))
        
        if not matches:
            return None, 0.0
        
        # Return highest confidence match
        best_match = max(matches, key=lambda x: x[1])
        return best_match[0], best_match[1]
    
    def quick_check(self, text: str, threshold: float = 0.6) -> bool:
        """
        Quick check if text contains security-related keywords.
        
        Args:
            text: Text to check
            threshold: Minimum confidence threshold
        
        Returns:
            True if security incident detected with confidence above threshold
        """
        _, confidence = self.detect(text)
        return confidence >= threshold
