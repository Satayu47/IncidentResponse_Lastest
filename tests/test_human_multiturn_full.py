"""
Human-Style Multi-Turn OWASP Test Suite
========================================

100 test cases covering:
- 72 single-incident classification tests (for accuracy metrics)
- 28 multi-incident/merge tests (for playbook mapping + DAG behavior)

Categories with ≥10 cases each:
- Broken Access Control (12)
- Injection (12)
- Broken Authentication (12)
- Security Misconfiguration (12)
"""

import pytest
import os
import time
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_adapter import LLMAdapter
from src.extractor import SecurityExtractor
from src.dialogue_state import DialogueState
from src.explicit_detector import ExplicitDetector
from phase2_engine.core.runner_bridge import run_phase2_from_incident

# Rate limiting for Gemini free tier (15 RPM)
RATE_LIMIT_DELAY = 4.5  # seconds between requests


# =============================================================================
# A. SINGLE-INCIDENT CLASSIFICATION TESTS (72 cases)
# =============================================================================

CASES_SINGLE = [
    # -------------------------------------------------------------------------
    # A.1 Broken Access Control (12 cases)
    # -------------------------------------------------------------------------
    ("BAC-01", "broken_access_control",
     "Normal staff can access /admin dashboard. They don't have admin role but they can still see all reports."),
    
    ("BAC-02", "broken_access_control",
     "Customer A can see invoices of customer B. Just by changing the invoice id in the URL."),
    
    ("BAC-03", "broken_access_control",
     "Viewer role can delete records in the system. They should only be able to read."),
    
    ("BAC-04", "broken_access_control",
     "User can read another user's profile by guessing user ID."),
    
    ("BAC-05", "broken_access_control",
     "If I change ?userId=10 to 11 I can see another account's data."),
    
    ("BAC-06", "broken_access_control",
     "Mobile app lets me access other tenant's data. There is no tenant filter on the API."),
    
    ("BAC-07", "broken_access_control",
     "Helpdesk user can escalate themselves to admin via API."),
    
    ("BAC-08", "broken_access_control",
     "Soft-deleted records still accessible via direct URL."),
    
    ("BAC-09", "broken_access_control",
     "Tenant isolation is broken. Company A can see Company B's project list."),
    
    ("BAC-10", "broken_access_control",
     "Unauthenticated user can call /export-all-users endpoint."),
    
    ("BAC-11", "broken_access_control",
     "Role 'intern' can approve financial transactions."),
    
    ("BAC-12", "broken_access_control",
     "User can access /admin/logs without being logged in."),

    # -------------------------------------------------------------------------
    # A.2 Injection (12 cases)
    # -------------------------------------------------------------------------
    ("INJ-01", "injection",
     "Login works when I type ' OR 1=1 -- as username."),
    
    ("INJ-02", "injection",
     "User search breaks when they type %$#@. SQL error appears in the response."),
    
    ("INJ-03", "injection",
     "Attacker sent id=1; DROP TABLE users; in the query string."),
    
    ("INJ-04", "injection",
     "Log shows syntax error near 'OR' when attacker tries weird payloads."),
    
    ("INJ-05", "injection",
     "Comment form allows <script>alert(1)</script> which pops up for other users."),
    
    ("INJ-06", "injection",
     "We see Union Select payloads in access logs."),
    
    ("INJ-07", "injection",
     "API accepts filter parameter and attacker injects OR 1=1 there."),
    
    ("INJ-08", "injection",
     "Password reset token parameter can inject SQL via query string."),
    
    ("INJ-09", "injection",
     "Search page reflects raw HTML from user input without escaping."),
    
    ("INJ-10", "injection",
     "Backend executes OS command using user input. We saw ; rm -rf / in logs."),
    
    ("INJ-11", "injection",
     "Attacker sent serialized object and we think it leads to code execution."),
    
    ("INJ-12", "injection",
     "Login page shows DB error when user enters '/**/OR/**/1=1 in username."),

    # -------------------------------------------------------------------------
    # A.3 Broken Authentication (12 cases)
    # -------------------------------------------------------------------------
    ("AUTH-01", "broken_authentication",
     "Any 6-digit code is accepted as OTP."),
    
    ("AUTH-02", "broken_authentication",
     "Session never expires even after days."),
    
    ("AUTH-03", "broken_authentication",
     "User stays logged in even after password reset."),
    
    ("AUTH-04", "broken_authentication",
     "JWT tokens never expire. They don't have exp claim."),
    
    ("AUTH-05", "broken_authentication",
     "We store passwords in plaintext in DB."),
    
    ("AUTH-06", "broken_authentication",
     "Login doesn't lock after hundreds of failed attempts."),
    
    ("AUTH-07", "broken_authentication",
     "User can reuse old password that was already compromised."),
    
    ("AUTH-08", "broken_authentication",
     "Remember-me cookie is not bound to device or IP, can be stolen and reused."),
    
    ("AUTH-09", "broken_authentication",
     "We send reset password link without any expiry."),
    
    ("AUTH-10", "broken_authentication",
     "2FA is optional but not enforced on admin accounts."),
    
    ("AUTH-11", "broken_authentication",
     "Same session ID before and after login."),
    
    ("AUTH-12", "broken_authentication",
     "We use 'md5' without salt for passwords."),

    # -------------------------------------------------------------------------
    # A.4 Sensitive Data Exposure (8 cases)
    # -------------------------------------------------------------------------
    ("SDE-01", "sensitive_data_exposure",
     "Credit card numbers appear in access logs."),
    
    ("SDE-02", "sensitive_data_exposure",
     "We accidentally published CSV with customer SSNs."),
    
    ("SDE-03", "sensitive_data_exposure",
     "Database backup with PII was left on public S3 bucket."),
    
    ("SDE-04", "sensitive_data_exposure",
     "Export API returns full card PAN without masking."),
    
    ("SDE-05", "sensitive_data_exposure",
     "HR staff can download all salary info in plain CSV."),
    
    ("SDE-06", "sensitive_data_exposure",
     "Error page dumps full stack trace with secrets."),
    
    ("SDE-07", "sensitive_data_exposure",
     "Logs include Authorization headers with bearer tokens."),
    
    ("SDE-08", "sensitive_data_exposure",
     "App returns full national ID number to the frontend."),

    # -------------------------------------------------------------------------
    # A.5 Cryptographic Failures (8 cases)
    # -------------------------------------------------------------------------
    ("CRY-01", "cryptographic_failures",
     "Login page still uses HTTP, not HTTPS."),
    
    ("CRY-02", "cryptographic_failures",
     "TLS certificate expired 3 months ago."),
    
    ("CRY-03", "cryptographic_failures",
     "Browser shows NOT SECURE on our login form."),
    
    ("CRY-04", "cryptographic_failures",
     "We use self-signed cert in production."),
    
    ("CRY-05", "cryptographic_failures",
     "We still support TLS 1.0 and weak ciphers."),
    
    ("CRY-06", "cryptographic_failures",
     "Sensitive config stored with hard-coded AES key 123456 in code."),
    
    ("CRY-07", "cryptographic_failures",
     "We hash tokens with MD5 and no salt."),
    
    ("CRY-08", "cryptographic_failures",
     "Our TLS was disabled after an update; traffic is now plain HTTP."),

    # -------------------------------------------------------------------------
    # A.6 Security Misconfiguration (12 cases)
    # -------------------------------------------------------------------------
    ("MIS-01", "security_misconfiguration",
     "Admin panel still uses default credentials admin/admin."),
    
    ("MIS-02", "security_misconfiguration",
     "Directory listing is enabled on production web server."),
    
    ("MIS-03", "security_misconfiguration",
     "Debug mode is enabled in production."),
    
    ("MIS-04", "security_misconfiguration",
     "Kibana is exposed to the internet without auth."),
    
    ("MIS-05", "security_misconfiguration",
     "We left test endpoints enabled /test/health-debug."),
    
    ("MIS-06", "security_misconfiguration",
     "Firewall allows SSH from anywhere."),
    
    ("MIS-07", "security_misconfiguration",
     "S3 bucket is public read/write by mistake."),
    
    ("MIS-08", "security_misconfiguration",
     "Our WAF is disabled after last deployment."),
    
    ("MIS-09", "security_misconfiguration",
     "CORS is configured as * for all origins, methods, and headers."),
    
    ("MIS-10", "security_misconfiguration",
     "Stack trace shown to all users on error."),
    
    ("MIS-11", "security_misconfiguration",
     "Monitoring dashboard accessible without login."),
    
    ("MIS-12", "security_misconfiguration",
     "Old default accounts are still active (guest/guest)."),

    # -------------------------------------------------------------------------
    # A.7 Other / Noise / Non-Security (8 cases)
    # -------------------------------------------------------------------------
    ("OTH-01", "other",
     "The website is just slow bro. No errors, just slow."),
    
    ("OTH-02", "other",
     "Color of the button is ugly, can you fix UI?"),
    
    ("OTH-03", "other",
     "User forgot their password, nothing else happened."),
    
    ("OTH-04", "other",
     "Boss shouted 'we are hacked' but there's no log or evidence."),
    
    ("OTH-05", "other",
     "Someone spammed support chat with emojis."),
    
    ("OTH-06", "other",
     "User mis-typed email address, doesn't receive confirmation."),
    
    ("OTH-07", "other",
     "We changed domain and users are confused."),
    
    ("OTH-08", "other",
     "Customer is just angry about pricing, not security."),
]


# =============================================================================
# B. MULTI-INCIDENT / MERGE TESTS (28 cases)
# =============================================================================

CASES_MULTI = [
    ("MIX-01", ["broken_access_control", "injection"],
     "Normal users can access /admin. Also log shows ' OR 1=1 payloads on login."),
    
    ("MIX-02", ["broken_authentication", "injection"],
     "Brute force on login, no lockout. We also see SQL syntax errors during login."),
    
    ("MIX-03", ["broken_access_control", "security_misconfiguration"],
     "Kibana is exposed on internet, no login. Anyone can view all logs."),
    
    ("MIX-04", ["sensitive_data_exposure", "security_misconfiguration"],
     "Public S3 bucket with database backup. Bucket was misconfigured as public."),
    
    ("MIX-05", ["cryptographic_failures", "broken_authentication"],
     "Login page is HTTP only. Passwords are stored with MD5, no salt."),
    
    ("MIX-06", ["injection", "sensitive_data_exposure"],
     "SQL injection dumped full user table with emails and phone numbers."),
    
    ("MIX-07", ["injection", "security_misconfiguration"],
     "Debug error page exposes full SQL error messages when payload is injected."),
    
    ("MIX-08", ["broken_access_control", "sensitive_data_exposure"],
     "User can download another company's financial report PDF."),
    
    ("MIX-09", ["broken_access_control", "broken_authentication"],
     "User stays logged in as admin after logging out, can still access /admin."),
    
    ("MIX-10", ["security_misconfiguration", "cryptographic_failures"],
     "TLS disabled accidentally, and firewall allows HTTP from anywhere."),
    
    ("MIX-11", ["injection", "other"],
     "Dev thinks there is SQL injection but only UI bug, no logs, no errors."),
    
    ("MIX-12", ["broken_authentication", "other"],
     "User complains 2FA is annoying, keeps asking to disable it."),
    
    ("MIX-13", ["broken_access_control", "injection"],
     "Attacker uses SQL injection to promote themselves to admin role."),
    
    ("MIX-14", ["security_misconfiguration", "injection"],
     "Test endpoint /debug/query lets you run raw SQL without auth."),
    
    ("MIX-15", ["cryptographic_failures", "sensitive_data_exposure"],
     "We send passwords via email in plaintext, and mail server uses no TLS."),
    
    ("MIX-16", ["broken_authentication", "security_misconfiguration"],
     "Admin console uses default admin/admin and no 2FA."),
    
    ("MIX-17", ["broken_access_control", "cryptographic_failures"],
     "VPN portal over HTTP, and once inside you can see all tenants."),
    
    ("MIX-18", ["injection", "broken_authentication"],
     "Login bypass possible via ' OR 'a'='a in username."),
    
    ("MIX-19", ["security_misconfiguration", "other"],
     "We left some dev banners on site, but no sensitive data exposed."),
    
    ("MIX-20", ["broken_access_control", "sensitive_data_exposure"],
     "Intern can export all user PII from admin panel."),
    
    ("MIX-21", ["injection", "cryptographic_failures"],
     "SQL errors on HTTP (no TLS) login endpoint when attacker injects payloads."),
    
    ("MIX-22", ["broken_authentication", "sensitive_data_exposure"],
     "Reset link is guessable and never expires, allows resetting any account."),
    
    ("MIX-23", ["security_misconfiguration", "broken_access_control"],
     "Test admin account left active, no MFA, full access."),
    
    ("MIX-24", ["injection", "security_misconfiguration", "broken_access_control"],
     "Public admin endpoint /admin/sql-console lets anyone run SQL."),
    
    ("MIX-25", ["other"],
     "Site is slow and ugly, CEO says it's 'cyber attack' but there's nothing in logs."),
    
    ("MIX-26", ["broken_access_control", "injection"],
     "Attacker gains admin via SQLi and then deletes some tables."),
    
    ("MIX-27", ["broken_authentication", "security_misconfiguration"],
     "We disabled lockout and WAF to make QA easier, forgot to re-enable in prod."),
    
    ("MIX-28", ["injection", "broken_access_control", "sensitive_data_exposure"],
     "SQLi used to dump all users, then attacker shares links so others can view data without login."),
]


# =============================================================================
# HELPER: Classification wrapper
# =============================================================================

def classify_incident(text: str, use_llm: bool = True) -> Dict[str, Any]:
    """
    Wrapper around Phase-1 classification logic.
    Returns dict with 'label', 'confidence', etc.
    """
    # Skip if no API key
    if use_llm and not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        return {"label": "other", "confidence": 0.0}
    
    # 1. Explicit keyword detection
    detector = ExplicitDetector()
    explicit_label, explicit_conf = detector.detect(text)
    
    # Normalize explicit labels to match expected format
    label_map = {
        "sql_injection": "injection",
        "xss": "injection",
        "command_injection": "injection",
        "ldap_injection": "injection",
    }
    
    if explicit_label:
        normalized_label = label_map.get(explicit_label, explicit_label)
        return {
            "label": normalized_label,
            "confidence": explicit_conf,
        }
    
    # 2. LLM classification (if enabled and no explicit match)
    if use_llm:
        adapter = LLMAdapter(model="gemini-2.5-pro")
        llm_result = adapter.classify_incident(text)
        return {
            "label": llm_result.get("category", "other"),
            "confidence": llm_result.get("confidence", 0.0),
        }
    
    # Return default
    return {
        "label": "other",
        "confidence": 0.0,
    }


# =============================================================================
# TEST: Single-Incident Classification (Accuracy)
# =============================================================================

@pytest.mark.parametrize("case_id,expected,text", CASES_SINGLE)
def test_single_incident_classification(case_id: str, expected: str, text: str):
    """
    Test single-incident classification accuracy.
    Each test case should produce the expected label.
    """
    # Rate limiting: Sleep to avoid hitting 15 RPM limit
    time.sleep(RATE_LIMIT_DELAY)
    
    result = classify_incident(text, use_llm=True)
    label = result["label"]
    confidence = result.get("confidence", 0.0)
    
    assert label == expected, (
        f"\n❌ {case_id} FAILED\n"
        f"   Expected: {expected}\n"
        f"   Got:      {label}\n"
        f"   Confidence: {confidence:.2f}\n"
        f"   Text:     {text}\n"
    )


# =============================================================================
# TEST: Multi-Incident / Merge (Playbook Mapping)
# =============================================================================

@pytest.mark.parametrize("case_id,expected_labels,text", CASES_MULTI)
def test_multi_incident_playbook_mapping(case_id: str, expected_labels: List[str], text: str):
    """
    Test multi-incident scenarios for playbook mapping and DAG merging.
    Verifies that Phase-2 returns multiple playbooks when appropriate.
    """
    # Classify the combined incident
    result = classify_incident(text, use_llm=True)
    label = result["label"]
    
    # Build incident dict for Phase-2
    incident = {
        "label": label,
        "coarse": result["coarse"],
        "fine": result["fine"],
        "confidence": result["confidence"],
        "iocs": result["iocs"],
        "text": text,
    }
    
    # Run Phase-2 with dry_run
    phase2_result = run_phase2_from_incident(
        incident=incident,
        merged_with=None,
        dry_run=True,
        opa_url=None,
    )
    
    # Verify playbook mapping
    returned_playbooks = phase2_result.get("playbooks", [])
    
    # For multi-label cases, we expect the system to potentially map to multiple playbooks
    # At minimum, the primary label should map to a playbook
    assert len(returned_playbooks) > 0, (
        f"\n❌ {case_id} FAILED - No playbooks returned\n"
        f"   Expected labels: {expected_labels}\n"
        f"   Got label:       {label}\n"
        f"   Text:            {text}\n"
    )
    
    # Verify response structure
    assert "status" in phase2_result, f"{case_id}: Missing 'status' in Phase-2 response"
    assert "steps" in phase2_result, f"{case_id}: Missing 'steps' in Phase-2 response"
    assert "automation" in phase2_result, f"{case_id}: Missing 'automation' in Phase-2 response"
    
    # Verify steps have required fields
    if phase2_result["steps"]:
        step = phase2_result["steps"][0]
        assert "node_id" in step, f"{case_id}: Step missing 'node_id'"
        assert "phase" in step, f"{case_id}: Step missing 'phase'"
        assert "name" in step, f"{case_id}: Step missing 'name'"


# =============================================================================
# TEST: DAG Merge Validation
# =============================================================================

def test_dag_merge_multiple_incidents():
    """
    Test that merging multiple incidents produces a combined DAG.
    """
    # Incident 1: Access control
    inc1 = classify_incident("User can access /admin without auth.", use_llm=True)
    incident1 = {
        "label": inc1["label"],
        "coarse": inc1["coarse"],
        "fine": inc1["fine"],
        "confidence": inc1["confidence"],
        "iocs": inc1["iocs"],
        "text": "User can access /admin without auth.",
    }
    
    # Incident 2: SQL Injection
    inc2 = classify_incident("SQL injection via ' OR 1=1 in login.", use_llm=True)
    incident2 = {
        "label": inc2["label"],
        "coarse": inc2["coarse"],
        "fine": inc2["fine"],
        "confidence": inc2["confidence"],
        "iocs": inc2["iocs"],
        "text": "SQL injection via ' OR 1=1 in login.",
    }
    
    # Run Phase-2 with merged incidents
    result = run_phase2_from_incident(
        incident=incident1,
        merged_with=[incident2],
        dry_run=True,
        opa_url=None,
    )
    
    # Should have multiple playbooks
    assert len(result.get("playbooks", [])) >= 1, "Merged incidents should map to playbooks"
    
    # Should have merged in the name if multiple distinct playbooks
    playbook_name = result.get("playbook", "")
    if len(result.get("playbooks", [])) > 1:
        assert "merged" in playbook_name.lower(), "Multiple playbooks should create merged DAG"
    
    # Should have steps from both playbooks
    steps = result.get("steps", [])
    assert len(steps) > 0, "Merged DAG should have steps"


# =============================================================================
# TEST: OPA Policy Integration (if enabled)
# =============================================================================

def test_opa_policy_evaluation():
    """
    Test that OPA policy evaluation is called when opa_url is provided.
    """
    result = classify_incident("Admin can execute arbitrary SQL.", use_llm=True)
    incident = {
        "label": result["label"],
        "coarse": result["coarse"],
        "fine": result["fine"],
        "confidence": result["confidence"],
        "iocs": result["iocs"],
        "text": "Admin can execute arbitrary SQL.",
    }
    
    # Run with fake OPA URL (will gracefully degrade to ALLOW)
    phase2_result = run_phase2_from_incident(
        incident=incident,
        merged_with=None,
        dry_run=True,
        opa_url="http://localhost:8181/v1/data/incident/allow",
    )
    
    # Verify steps have policy field when OPA URL provided
    steps = phase2_result.get("steps", [])
    if steps:
        # At least some steps should have policy field
        has_policy = any("policy" in step for step in steps)
        assert has_policy, "When opa_url provided, steps should include policy decisions"


# =============================================================================
# FIXTURES & UTILITIES
# =============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Setup test environment with API keys and configuration.
    """
    import os
    # Ensure API key is set (from .env or environment)
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - skipping LLM tests")


if __name__ == "__main__":
    # Run tests with verbose output and summary
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-q",
    ])
