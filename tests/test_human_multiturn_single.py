# tests/test_human_multiturn_single.py

import pytest
import time
from src.phase1_core import run_phase1_classification


# Rate limiting to avoid API quota issues
RATE_LIMIT_DELAY = 4.5  # seconds between API calls


# =====================================================
# FULL SINGLE-INCIDENT HUMAN MULTI-TURN CASES (72)
# =====================================================

CASES_SINGLE = [

# ---------- Broken Access Control (12) ----------
("BAC-01", "broken_access_control", [
    "Normal staff can access the /admin dashboard.",
    "They don't even have admin role but they can still see all reports."
]),
("BAC-02", "broken_access_control", [
    "Customer A can see the invoice of customer B.",
    "Just by changing the invoice ID in the URL."
]),
("BAC-03", "broken_access_control", [
    "Viewer role can delete records.",
    "They should only be able to read, not modify anything."
]),
("BAC-04", "broken_access_control", [
    "User can read another user's profile.",
    "Just by guessing the user ID they get the whole profile data."
]),
("BAC-05", "broken_access_control", [
    "If I change ?userId=10 to 11 I can see another account's data.",
    "There is no permission check."
]),
("BAC-06", "broken_access_control", [
    "Mobile app lets me access other tenant's data.",
    "API does not filter by tenant ID."
]),
("BAC-07", "broken_access_control", [
    "Helpdesk user can escalate themselves to admin via an API call.",
    "That's not supposed to happen."
]),
("BAC-08", "broken_access_control", [
    "Soft-deleted records can still be accessed via direct URL.",
    "The backend does not check if it's deleted."
]),
("BAC-09", "broken_access_control", [
    "Tenant isolation is broken.",
    "Company A can see Company B's project list."
]),
("BAC-10", "broken_access_control", [
    "Unauthenticated user can call /export-all-users.",
    "They can dump all user accounts without login."
]),
("BAC-11", "broken_access_control", [
    "Intern role can approve financial transactions.",
    "They should not have approval permissions."
]),
("BAC-12", "broken_access_control", [
    "User can access /admin/logs without being logged in.",
    "This endpoint is unprotected."
]),

# ---------- Injection (12) ----------
("INJ-01", "injection", [
    "Login works with weird payload.",
    "When I type ' OR 1=1 -- the login bypasses authentication."
]),
("INJ-02", "injection", [
    "Search bar shows weird symbols.",
    "SQL error appears in response when using %$#@."
]),
("INJ-03", "injection", [
    "Attacker sent id=1; DROP TABLE users;",
    "This caused table deletion."
]),
("INJ-04", "injection", [
    "Logs show syntax error near 'OR'.",
    "Attacker keeps sending strange SQL payloads."
]),
("INJ-05", "injection", [
    "Comment form allows <script>alert(1)</script>.",
    "Other users see the popup."
]),
("INJ-06", "injection", [
    "We found UNION SELECT payloads in logs.",
    "Looks like SQL injection."
]),
("INJ-07", "injection", [
    "API filter parameter accepts OR 1=1.",
    "It reveals data that shouldn't be visible."
]),
("INJ-08", "injection", [
    "Password reset parameter can inject SQL.",
    "User added ' OR ''=' in the link."
]),
("INJ-09", "injection", [
    "Search page reflects HTML without escaping.",
    "User injected raw HTML tags."
]),
("INJ-10", "injection", [
    "Backend executes OS commands from user input.",
    "Saw ; rm -rf / in the logs."
]),
("INJ-11", "injection", [
    "Attacker sent malicious serialized Java object.",
    "Possible remote code execution."
]),
("INJ-12", "injection", [
    "Login page throws DB error.",
    "Payload was '/**/OR/**/1=1'."
]),

# ---------- Broken Authentication (12) ----------
("AUTH-01", "broken_authentication", [
    "Any 6 digit code is accepted as OTP.",
    "Even random numbers work."
]),
("AUTH-02", "broken_authentication", [
    "Session never expires.",
    "User stays logged in for days even without activity."
]),
("AUTH-03", "broken_authentication", [
    "User stays logged in even after password reset.",
    "Session is not invalidated."
]),
("AUTH-04", "broken_authentication", [
    "JWT tokens never expire.",
    "They have no exp claim."
]),
("AUTH-05", "broken_authentication", [
    "Passwords stored in plaintext in DB.",
    "No hashing at all."
]),
("AUTH-06", "broken_authentication", [
    "Login doesn't lock after hundreds of failed attempts.",
    "Brute force seems possible."
]),
("AUTH-07", "broken_authentication", [
    "User can reuse previous password.",
    "Old revoked passwords accepted."
]),
("AUTH-08", "broken_authentication", [
    "Remember-me cookie works on every device.",
    "It is not device-bound."
]),
("AUTH-09", "broken_authentication", [
    "Reset password link has no expiration.",
    "Anyone with link can reset any time."
]),
("AUTH-10", "broken_authentication", [
    "2FA is optional for admin accounts.",
    "Admins can skip MFA entirely."
]),
("AUTH-11", "broken_authentication", [
    "Same session ID before and after login.",
    "Session fixation possible."
]),
("AUTH-12", ["broken_authentication", "cryptographic_failures"], [
    "System uses md5 without salt for passwords.",
    "Very weak password storage."
]),

# ---------- Sensitive Data Exposure (8) ----------
("SDE-01", "sensitive_data_exposure", [
    "Credit card numbers appear in access logs.",
    "Full PAN, not masked."
]),
("SDE-02", "sensitive_data_exposure", [
    "Customer SSNs accidentally exposed.",
    "They were in a CSV we emailed."
]),
("SDE-03", "sensitive_data_exposure", [
    "DB backup with PII left in public S3 bucket.",
    "Anyone could download it."
]),
("SDE-04", "sensitive_data_exposure", [
    "Export API returns full card numbers.",
    "No masking applied."
]),
("SDE-05", ["sensitive_data_exposure", "broken_access_control"], [
    "HR staff can download everyone's salary.",
    "No restrictions."
]),
("SDE-06", "sensitive_data_exposure", [
    "Error page prints full stack trace including secrets.",
    "This reveals environment vars."
]),
("SDE-07", "sensitive_data_exposure", [
    "Logs include Authorization headers.",
    "Bearer tokens visible."
]),
("SDE-08", "sensitive_data_exposure", [
    "National ID returned fully in frontend response.",
    "Should be masked."
]),

# ---------- Cryptographic Failures (8) ----------
("CRY-01", "cryptographic_failures", [
    "Login page is HTTP, not HTTPS.",
    "Credentials sent in plain text."
]),
("CRY-02", "cryptographic_failures", [
    "TLS certificate expired 3 months ago.",
    "Browser warning appears."
]),
("CRY-03", "cryptographic_failures", [
    "Browser shows NOT SECURE on login page.",
    "TLS misconfigured."
]),
("CRY-04", "cryptographic_failures", [
    "We use self-signed certificate in production.",
    "Users see warnings."
]),
("CRY-05", "cryptographic_failures", [
    "Server still supports TLS 1.0.",
    "Weak cipher suites."
]),
("CRY-06", "cryptographic_failures", [
    "Hard-coded AES key '123456' in source code.",
    "Extremely weak encryption."
]),
("CRY-07", "cryptographic_failures", [
    "Tokens hashed using md5 without salt.",
    "Not secure."
]),
("CRY-08", "cryptographic_failures", [
    "TLS was disabled after update.",
    "Everything sent over HTTP."
]),

# ---------- Security Misconfiguration (12) ----------
("MIS-01", "security_misconfiguration", [
    "Admin panel still uses default credentials.",
    "Username: admin, password: admin."
]),
("MIS-02", "security_misconfiguration", [
    "Directory listing enabled on production.",
    "Users can browse source files."
]),
("MIS-03", "security_misconfiguration", [
    "Debug mode enabled in production.",
    "Shows stack traces to public."
]),
("MIS-04", "security_misconfiguration", [
    "Kibana is exposed to the internet.",
    "No authentication required."
]),
("MIS-05", "security_misconfiguration", [
    "Test endpoints still active in production.",
    "/test/debug-health."
]),
("MIS-06", "security_misconfiguration", [
    "Firewall allows SSH from anywhere.",
    "0.0.0.0/0 allowed."
]),
("MIS-07", "security_misconfiguration", [
    "S3 bucket is public read/write.",
    "Anyone can upload or delete."
]),
("MIS-08", "security_misconfiguration", [
    "WAF disabled after deployment.",
    "Forgot to turn back on."
]),
("MIS-09", "security_misconfiguration", [
    "CORS set to * for everything.",
    "Very risky."
]),
("MIS-10", "security_misconfiguration", [
    "Stack trace shows to all users.",
    "Happens on every error."
]),
("MIS-11", "security_misconfiguration", [
    "Monitoring dashboard public.",
    "No login required."
]),
("MIS-12", "security_misconfiguration", [
    "Default accounts still active.",
    "guest/guest still works."
]),

# ---------- Other / Non-Security (8) ----------
("OTH-01", "other", [
    "Website is super slow.",
    "No logs, no suspicious activity."
]),
("OTH-02", "other", [
    "UI looks bad.",
    "User wants nicer colors."
]),
("OTH-03", "other", [
    "User forgot password.",
    "No security incident."
]),
("OTH-04", "other", [
    "Boss says we are hacked.",
    "But no logs or evidence."
]),
("OTH-05", "other", [
    "User spamming emojis in support chat.",
    "Annoying but not security."
]),
("OTH-06", "other", [
    "User mistyped email.",
    "No deeper issue."
]),
("OTH-07", "other", [
    "We changed domain; users are confused.",
    "Just usability issue."
]),
("OTH-08", "other", [
    "Customer angry about pricing.",
    "Not a cyber issue."
]),

]


@pytest.mark.parametrize("case_id, expected, turns", CASES_SINGLE)
def test_single_incident_classification(case_id, expected, turns):
    """
    Joins the multi-turn human conversation into a single
    input text (like your chat history window) and verifies
    the final label from Phase-1.
    
    Supports multiple valid labels for ambiguous cases.
    """
    # Rate limiting to avoid API quota
    time.sleep(RATE_LIMIT_DELAY)
    
    text = " ".join(turns)
    result = run_phase1_classification(text)
    got = result["label"]
    score = result.get("score", 0.0)

    # Handle both single label and list of valid labels
    valid_labels = [expected] if isinstance(expected, str) else expected
    
    assert got in valid_labels, (
        f"\n❌ {case_id} FAILED\n"
        f"   Expected: {' or '.join(valid_labels)}\n"
        f"   Got:      {got}\n"
        f"   Score:    {score:.2f}\n"
        f"   Text:     {text}\n"
    )
