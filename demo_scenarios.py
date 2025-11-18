"""
Real-world test scenarios for ChatOps Incident Response system.

These are practical scenarios you can test yourself. Each one is based on
common security incidents that actually happen in organizations.
"""

# Scenario 1: Individual OWASP Categories
SCENARIO_1 = {
    "A01_Broken_Access_Control": {
        "description": "User from marketing department somehow got into the HR system and downloaded employee salary data. They shouldn't have access to that system at all.",
        "expected_category": "broken_access_control"
    },
    "A04_Insecure_Design": {
        "description": "Our payment API doesn't check how many times someone can try to pay. A customer accidentally triggered 10,000 payment attempts in 5 minutes and crashed the system.",
        "expected_category": "insecure_design"
    },
    "A05_Security_Misconfiguration": {
        "description": "Found out our production database is still using the default admin password 'admin123'. Also, error messages are showing full stack traces to users.",
        "expected_category": "security_misconfiguration"
    },
    "A07_Authentication_Failures": {
        "description": "Seeing hundreds of failed login attempts from the same IP address. Our password policy is too weak - people are using 'Password123' and it's being accepted.",
        "expected_category": "broken_authentication"
    }
}

# Scenario 2: Multiple Incidents Combined (A01, A04, A05, A07)
SCENARIO_2 = {
    "multi_incident": {
        "description": """
        We had a major security incident yesterday. Here's what happened:

        1. Someone without proper permissions accessed our customer database and exported personal information. They weren't supposed to have that access.

        2. Our API has no rate limiting, so an attacker was able to send thousands of requests per second and caused a denial of service.

        3. We discovered our staging server is using default admin credentials and it's accessible from the internet. Debug mode is also enabled.

        4. Our login system is being hit with brute force attacks. We're seeing 500+ failed attempts per hour from the same IP. Also, our password requirements are too weak - "password" is still being accepted.

        Need immediate response plan for all of these.
        """,
        "expected_categories": ["broken_access_control", "insecure_design", "security_misconfiguration", "broken_authentication"]
    }
}

# Scenario 3: Other OWASP Categories
SCENARIO_3 = {
    "A02_Cryptographic_Failures": {
        "description": "Our database is storing user passwords in plain text. No hashing, no encryption. Also, we're sending credit card numbers over HTTP instead of HTTPS.",
        "expected_category": "cryptographic_failures"
    },
    "A03_Injection": {
        "description": "Security team found SQL injection in our login form. An attacker was able to run database queries and extract user email addresses. The login form isn't sanitizing input properly.",
        "expected_category": "injection"
    },
    "A06_Vulnerable_Components": {
        "description": "Our application uses an old version of Apache Struts that has a known vulnerability (CVE-2023-50164). It's been flagged by our security scanner. We need to patch it but don't know what else might break.",
        "expected_category": "vulnerable_components"
    },
    "A10_SSRF": {
        "description": "An attacker found a way to make our server make requests to internal services. They tried to access our internal admin panel at 192.168.1.100 through our API endpoint. The API doesn't validate URLs before making requests.",
        "expected_category": "injection"  # SSRF often gets classified as injection
    }
}

# Scenario 4: Automated Playbook Execution
SCENARIO_4 = {
    "automated_playbook": {
        "description": "URGENT: We just discovered an unauthorized admin account was created and used to access our production database. Customer data including credit card numbers may have been exfiltrated. We need an immediate response plan.",
        "expected_category": "broken_access_control",
        "playbook_actions": [
            "Isolate affected systems",
            "Revoke compromised credentials",
            "Enable enhanced logging",
            "Notify security team",
            "Begin forensic investigation"
        ]
    }
}

def print_demo_scenarios():
    """Print all demo scenarios in a formatted way."""
    
    print("=" * 80)
    print("CHATOPS INCIDENT RESPONSE - DEMO SCENARIOS")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("SCENARIO 1: Separate OWASP Categories (A01, A04, A05, A07)")
    print("=" * 80)
    
    for category, data in SCENARIO_1.items():
        print(f"\n{category}:")
        print(f"  Input: {data['description']}")
        print(f"  Expected: {data['expected_category']}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 2: Multiple Incidents Combined (A01, A04, A05, A07)")
    print("=" * 80)
    
    for scenario, data in SCENARIO_2.items():
        print(f"\n{scenario}:")
        print(f"  Input: {data['description'].strip()}")
        print(f"  Expected Categories: {', '.join(data['expected_categories'])}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 3: Outside A01, A04, A05, A07 (A02, A03, A06, A10)")
    print("=" * 80)
    
    for category, data in SCENARIO_3.items():
        print(f"\n{category}:")
        print(f"  Input: {data['description']}")
        print(f"  Expected: {data['expected_category']}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 4: Automated Playbook Execution")
    print("=" * 80)
    
    for scenario, data in SCENARIO_4.items():
        print(f"\n{scenario}:")
        print(f"  Input: {data['description']}")
        print(f"  Expected Category: {data['expected_category']}")
        print(f"  Playbook Actions:")
        for action in data['playbook_actions']:
            print(f"    - {action}")
    
    print("\n" + "=" * 80)
    print("HOW TO USE:")
    print("=" * 80)
    print("1. Open the Streamlit app at http://localhost:8501")
    print("2. Copy and paste each scenario description into the chat")
    print("3. Observe the classification results")
    print("4. For Scenario 2, check if multiple playbooks are merged")
    print("5. For Scenario 4, click 'Generate Response Plan' and review the automated steps")
    print("=" * 80)

if __name__ == "__main__":
    print_demo_scenarios()

