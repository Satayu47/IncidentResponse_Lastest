"""Test cases for the Incident Response ChatOps Bot
Focus: A01 (Broken Access Control), A04 (Cryptographic Failures), 
       A05 (Injection), A07 (Authentication Failures)
50 test cases total: 10 per category + 10 ambiguous cases
"""

TEST_CASES = [
    # ===== A01: BROKEN ACCESS CONTROL (10 cases) =====
    {
        "id": "BAC-01",
        "category": "Broken Access Control",
        "user_input": "I changed the number in the URL and saw someone else's profile. Is that normal?",
        "expected": "broken_access_control",
        "difficulty": "hard",
        "note": "Ambiguous - could be normal feature or vulnerability"
    },
    {
        "id": "BAC-02",
        "category": "Broken Access Control",
        "user_input": "My friend logged into my account using their own password. That shouldn't work right?",
        "expected": "broken_access_control",
        "difficulty": "hard",
        "note": "Confusing - sounds like authentication but is access control"
    },
    {
        "id": "BAC-03",
        "category": "Broken Access Control",
        "user_input": "I can see all customer orders even though I'm just a regular employee.",
        "expected": "broken_access_control",
        "difficulty": "medium",
        "note": "Clear but uses business terms"
    },
    {
        "id": "BAC-04",
        "category": "Broken Access Control",
        "user_input": "When I delete my account, I can still access it by direct link.",
        "expected": "broken_access_control",
        "difficulty": "hard",
        "note": "Soft-delete issue, ambiguous phrasing"
    },
    {
        "id": "BAC-05",
        "category": "Broken Access Control",
        "user_input": "I'm a viewer but I can approve transactions somehow.",
        "expected": "broken_access_control",
        "difficulty": "medium",
        "note": "Role-based access control violation"
    },
    {
        "id": "BAC-06",
        "category": "Broken Access Control",
        "user_input": "I can access the admin panel even though I'm not an admin. I just typed /admin in the URL.",
        "expected": "broken_access_control",
        "difficulty": "medium",
        "note": "Direct URL access without authorization check"
    },
    {
        "id": "BAC-07",
        "category": "Broken Access Control",
        "user_input": "When I click on a link from my email, I can see other people's private messages.",
        "expected": "broken_access_control",
        "difficulty": "hard",
        "note": "Token-based access control failure, could be confused with session issues"
    },
    {
        "id": "BAC-08",
        "category": "Broken Access Control",
        "user_input": "I can edit other users' posts by changing the post ID in the URL.",
        "expected": "broken_access_control",
        "difficulty": "medium",
        "note": "IDOR in edit functionality"
    },
    {
        "id": "BAC-09",
        "category": "Broken Access Control",
        "user_input": "As a customer, I can see invoices from other companies by changing the company ID.",
        "expected": "broken_access_control",
        "difficulty": "hard",
        "note": "Multi-tenant isolation failure, business context"
    },
    {
        "id": "BAC-10",
        "category": "Broken Access Control",
        "user_input": "I can download files that belong to other users. I just need to know the file ID.",
        "expected": "broken_access_control",
        "difficulty": "medium",
        "note": "File access control bypass"
    },
    
    # ===== A04: CRYPTOGRAPHIC FAILURES (10 cases) =====
    {
        "id": "CRY-01",
        "category": "Cryptographic Failures",
        "user_input": "Our passwords are stored in plain text in the database. Is that bad?",
        "expected": "cryptographic_failures",
        "difficulty": "medium",
        "note": "Clear but user unsure if it's a problem"
    },
    {
        "id": "CRY-02",
        "category": "Cryptographic Failures",
        "user_input": "I found credit card numbers in the logs without any encryption.",
        "expected": "cryptographic_failures",
        "difficulty": "medium",
        "note": "Sensitive data exposure via logging"
    },
    {
        "id": "CRY-03",
        "category": "Cryptographic Failures",
        "user_input": "The website doesn't use HTTPS. Users are sending passwords over HTTP.",
        "expected": "cryptographic_failures",
        "difficulty": "medium",
        "note": "Missing TLS/encryption in transit"
    },
    {
        "id": "CRY-04",
        "category": "Cryptographic Failures",
        "user_input": "I can see user data when I look at the network traffic. It's not encrypted.",
        "expected": "cryptographic_failures",
        "difficulty": "hard",
        "note": "Ambiguous - could be misconfiguration or crypto failure"
    },
    {
        "id": "CRY-05",
        "category": "Cryptographic Failures",
        "user_input": "Our API returns user emails and phone numbers without any protection.",
        "expected": "cryptographic_failures",
        "difficulty": "medium",
        "note": "Sensitive data exposure"
    },
    {
        "id": "CRY-06",
        "category": "Cryptographic Failures",
        "user_input": "The system stores social security numbers in plain text. I can see them in the database.",
        "expected": "cryptographic_failures",
        "difficulty": "medium",
        "note": "PII stored without encryption"
    },
    {
        "id": "CRY-07",
        "category": "Cryptographic Failures",
        "user_input": "When I check the API response, I can see passwords in the JSON. They're not hashed or anything.",
        "expected": "cryptographic_failures",
        "difficulty": "hard",
        "note": "API exposing sensitive data, could be confused with access control"
    },
    {
        "id": "CRY-08",
        "category": "Cryptographic Failures",
        "user_input": "Our backup files contain unencrypted customer data. Anyone with access to the backup can read everything.",
        "expected": "cryptographic_failures",
        "difficulty": "medium",
        "note": "Data at rest not encrypted"
    },
    {
        "id": "CRY-09",
        "category": "Cryptographic Failures",
        "user_input": "The mobile app sends user location data over HTTP instead of HTTPS.",
        "expected": "cryptographic_failures",
        "difficulty": "hard",
        "note": "Mobile app context, could be confused with misconfiguration"
    },
    {
        "id": "CRY-10",
        "category": "Cryptographic Failures",
        "user_input": "I found medical records in the database that are stored without encryption. This seems wrong.",
        "expected": "cryptographic_failures",
        "difficulty": "medium",
        "note": "HIPAA-related, sensitive health data"
    },
    
    # ===== A05: INJECTION (10 cases) =====
    {
        "id": "INJ-01",
        "category": "Injection",
        "user_input": "Weird syntax appear on login page. Looks like code but I'm not sure.",
        "expected": "injection",
        "difficulty": "hard",
        "note": "Very vague, needs semantic understanding"
    },
    {
        "id": "INJ-02",
        "category": "Injection",
        "user_input": "My table disappeared from the database. Could someone have deleted it?",
        "expected": "injection",
        "difficulty": "very_hard",
        "note": "Could be SQL injection OR admin mistake OR database issue"
    },
    {
        "id": "INJ-03",
        "category": "Injection",
        "user_input": "When I type special characters in the search box, the page breaks.",
        "expected": "injection",
        "difficulty": "hard",
        "note": "Vague - could be XSS, SQL injection, or just a bug"
    },
    {
        "id": "INJ-04",
        "category": "Injection",
        "user_input": "I saw error messages that show database structure. Is that dangerous?",
        "expected": "injection",
        "difficulty": "hard",
        "note": "Error disclosure - could be injection or misconfiguration"
    },
    {
        "id": "INJ-05",
        "category": "Injection",
        "user_input": "Someone entered JavaScript code in a comment and it executed on other users' browsers.",
        "expected": "injection",
        "difficulty": "medium",
        "note": "XSS - clear but uses technical terms"
    },
    {
        "id": "INJ-06",
        "category": "Injection",
        "user_input": "The login form accepts strange characters and then the database shows errors.",
        "expected": "injection",
        "difficulty": "hard",
        "note": "Indirect description of SQL injection"
    },
    {
        "id": "INJ-07",
        "category": "Injection",
        "user_input": "I'm worried! The website is showing database errors when I search for things.",
        "expected": "injection",
        "difficulty": "hard",
        "note": "Emotional + vague - needs context understanding"
    },
    {
        "id": "INJ-08",
        "category": "Injection",
        "user_input": "When I paste code snippets into the contact form, they appear on other users' screens as actual code.",
        "expected": "injection",
        "difficulty": "medium",
        "note": "XSS stored, indirect description"
    },
    {
        "id": "INJ-09",
        "category": "Injection",
        "user_input": "The system crashed after someone entered a weird command in the file upload field.",
        "expected": "injection",
        "difficulty": "very_hard",
        "note": "Could be command injection, file upload issue, or system crash"
    },
    {
        "id": "INJ-10",
        "category": "Injection",
        "user_input": "I noticed that when users type certain characters in the search, the page shows SQL errors with table names.",
        "expected": "injection",
        "difficulty": "medium",
        "note": "SQL injection with error disclosure"
    },
    
    # ===== A07: AUTHENTICATION FAILURES (10 cases) =====
    {
        "id": "AUTH-01",
        "category": "Authentication Failures",
        "user_input": "I can log in with password '12345'. That seems too easy.",
        "expected": "broken_authentication",
        "difficulty": "medium",
        "note": "Weak password policy"
    },
    {
        "id": "AUTH-02",
        "category": "Authentication Failures",
        "user_input": "My session never expires. I logged in last week and I'm still logged in.",
        "expected": "broken_authentication",
        "difficulty": "medium",
        "note": "Session management issue"
    },
    {
        "id": "AUTH-03",
        "category": "Authentication Failures",
        "user_input": "I tried wrong passwords many times but the system didn't lock me out.",
        "expected": "broken_authentication",
        "difficulty": "medium",
        "note": "No brute force protection"
    },
    {
        "id": "AUTH-04",
        "category": "Authentication Failures",
        "user_input": "I forgot my password but I can still access my account somehow.",
        "expected": "broken_authentication",
        "difficulty": "hard",
        "note": "Ambiguous - could be session hijacking or broken auth"
    },
    {
        "id": "AUTH-05",
        "category": "Authentication Failures",
        "user_input": "The system doesn't require two-factor authentication for admin accounts.",
        "expected": "broken_authentication",
        "difficulty": "medium",
        "note": "Missing MFA"
    },
    {
        "id": "AUTH-06",
        "category": "Authentication Failures",
        "user_input": "I logged out but when I go back to the site, I'm still logged in.",
        "expected": "broken_authentication",
        "difficulty": "hard",
        "note": "Session invalidation failure"
    },
    {
        "id": "AUTH-07",
        "category": "Authentication Failures",
        "user_input": "Users can set their password to anything, even just one character.",
        "expected": "broken_authentication",
        "difficulty": "medium",
        "note": "Weak password policy"
    },
    {
        "id": "AUTH-08",
        "category": "Authentication Failures",
        "user_input": "The system allows me to use my username as my password. That can't be secure.",
        "expected": "broken_authentication",
        "difficulty": "medium",
        "note": "Password policy allows username as password"
    },
    {
        "id": "AUTH-09",
        "category": "Authentication Failures",
        "user_input": "I can reset anyone's password if I know their email address. There's no verification.",
        "expected": "broken_authentication",
        "difficulty": "hard",
        "note": "Password reset without proper verification, could be confused with access control"
    },
    {
        "id": "AUTH-10",
        "category": "Authentication Failures",
        "user_input": "The system shows me if a username exists or not when I try to log in. That seems like it helps attackers.",
        "expected": "broken_authentication",
        "difficulty": "hard",
        "note": "Username enumeration vulnerability, information disclosure"
    },
    
    # ===== AMBIGUOUS / BORDERLINE CASES (10 cases) =====
    # These relate to multiple categories but have a primary correct classification
    {
        "id": "AMBIG-01",
        "category": "Injection",
        "user_input": "The website crashed after someone entered weird text. Now it shows database errors.",
        "expected": "injection",
        "difficulty": "very_hard",
        "note": "Multiple issues - injection likely but could be other causes"
    },
    {
        "id": "AMBIG-02",
        "category": "Broken Access Control",
        "user_input": "I can see other people's data when I shouldn't be able to. The URL changes when I click around.",
        "expected": "broken_access_control",
        "difficulty": "hard",
        "note": "IDOR - indirect description"
    },
    {
        "id": "AMBIG-03",
        "category": "Cryptographic Failures",
        "user_input": "I found user information in log files. It includes passwords and credit cards.",
        "expected": "cryptographic_failures",
        "difficulty": "hard",
        "note": "Could be logging issue or crypto failure - crypto is primary"
    },
    {
        "id": "AMBIG-04",
        "category": "Authentication Failures",
        "user_input": "Users can set their password to anything, even just one character.",
        "expected": "broken_authentication",
        "difficulty": "medium",
        "note": "Weak password policy"
    },
    {
        "id": "AMBIG-05",
        "category": "Broken Access Control",
        "user_input": "I can access admin functions by changing my role in the cookie. The system doesn't check if I'm really an admin.",
        "expected": "broken_access_control",
        "difficulty": "hard",
        "note": "Could be session/auth issue but primary is access control bypass"
    },
    {
        "id": "AMBIG-06",
        "category": "Injection",
        "user_input": "When I enter HTML tags in my profile, they show up as actual HTML on other users' pages.",
        "expected": "injection",
        "difficulty": "medium",
        "note": "XSS - could be confused with data exposure but is injection"
    },
    {
        "id": "AMBIG-07",
        "category": "Cryptographic Failures",
        "user_input": "The API endpoint returns sensitive data without checking if I'm authorized, and it's all in plain text.",
        "expected": "cryptographic_failures",
        "difficulty": "hard",
        "note": "Both access control and crypto failure - crypto is primary issue"
    },
    {
        "id": "AMBIG-08",
        "category": "Authentication Failures",
        "user_input": "I can bypass the login by manipulating the session token. The system doesn't verify it properly.",
        "expected": "broken_authentication",
        "difficulty": "hard",
        "note": "Session manipulation - auth failure, could be confused with access control"
    },
    {
        "id": "AMBIG-09",
        "category": "Injection",
        "user_input": "The search function breaks when I enter database commands. It shows me table names and column structures.",
        "expected": "injection",
        "difficulty": "hard",
        "note": "SQL injection with info disclosure - injection is primary"
    },
    {
        "id": "AMBIG-10",
        "category": "Broken Access Control",
        "user_input": "I can see deleted posts by changing the status parameter. They're marked as deleted but I can still view them.",
        "expected": "broken_access_control",
        "difficulty": "hard",
        "note": "Soft-delete bypass - access control issue, could be confused with data integrity"
    },
]


def get_test_case(test_id: str):
    """Get a test case by ID"""
    for tc in TEST_CASES:
        if tc["id"] == test_id:
            return tc
    return None


def get_test_cases_by_category(category: str = None):
    """Get test cases filtered by category"""
    if category:
        return [tc for tc in TEST_CASES if tc["category"] == category]
    return TEST_CASES


def get_hard_test_cases():
    """Get only hard/very_hard test cases"""
    return [tc for tc in TEST_CASES if tc.get("difficulty") in ["hard", "very_hard"]]


def get_test_cases_by_expected(expected_label: str = None):
    """Get test cases filtered by expected label"""
    if expected_label:
        return [tc for tc in TEST_CASES if tc["expected"] == expected_label]
    return TEST_CASES
