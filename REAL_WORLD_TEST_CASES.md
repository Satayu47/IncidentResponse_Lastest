# Real-World Security Incident Test Cases

These are actual scenarios you can test yourself. Each one is based on common security incidents that happen in real organizations.

## Test 1: Individual OWASP Categories

### A01 - Broken Access Control
**Scenario:** 
```
User from marketing department somehow got into the HR system and downloaded employee salary data. They shouldn't have access to that system at all.
```

**What to look for:**
- Should classify as broken_access_control
- Confidence should be high (above 70%)
- Playbook should include access revocation steps

---

### A04 - Insecure Design
**Scenario:**
```
Our payment API doesn't check how many times someone can try to pay. A customer accidentally triggered 10,000 payment attempts in 5 minutes and crashed the system.
```

**What to look for:**
- Should detect insecure_design
- Should mention rate limiting as a solution
- Playbook should include API protection steps

---

### A05 - Security Misconfiguration
**Scenario:**
```
Found out our production database is still using the default admin password "admin123". Also, error messages are showing full stack traces to users.
```

**What to look for:**
- Should identify security_misconfiguration
- Should flag default credentials as critical
- Playbook should include credential rotation

---

### A07 - Authentication Failures
**Scenario:**
```
Seeing hundreds of failed login attempts from the same IP address. Our password policy is too weak - people are using "Password123" and it's being accepted.
```

**What to look for:**
- Should detect broken_authentication
- Should identify brute force pattern
- Playbook should include account lockout and password policy updates

---

## Test 2: Multiple Incidents at Once

**Scenario:**
```
We had a major security incident yesterday. Here's what happened:

1. Someone without proper permissions accessed our customer database and exported personal information. They weren't supposed to have that access.

2. Our API has no rate limiting, so an attacker was able to send thousands of requests per second and caused a denial of service.

3. We discovered our staging server is using default admin credentials and it's accessible from the internet. Debug mode is also enabled.

4. Our login system is being hit with brute force attacks. We're seeing 500+ failed attempts per hour from the same IP. Also, our password requirements are too weak - "password" is still being accepted.

Need immediate response plan for all of these.
```

**What to look for:**
- Should detect all 4 categories: broken_access_control, insecure_design, security_misconfiguration, broken_authentication
- Should load 4 different playbooks
- Should merge them into one unified response plan
- Check that the merged plan has steps from all categories

---

## Test 3: Other Security Issues

### A02 - Cryptographic Failures
**Scenario:**
```
Our database is storing user passwords in plain text. No hashing, no encryption. Also, we're sending credit card numbers over HTTP instead of HTTPS.
```

**What to look for:**
- Should classify as cryptographic_failures
- Should flag both storage and transmission issues
- Playbook should include encryption implementation

---

### A03 - Injection Attack
**Scenario:**
```
Security team found SQL injection in our login form. An attacker was able to run database queries and extract user email addresses. The login form isn't sanitizing input properly.
```

**What to look for:**
- Should detect injection category
- Should identify SQL injection specifically
- Playbook should include input validation steps

---

### A06 - Vulnerable Components
**Scenario:**
```
Our application uses an old version of Apache Struts that has a known vulnerability (CVE-2023-50164). It's been flagged by our security scanner. We need to patch it but don't know what else might break.
```

**What to look for:**
- Should classify as vulnerable_components
- Should retrieve CVE information if available
- Playbook should include patch management steps

---

### A10 - SSRF Attack
**Scenario:**
```
An attacker found a way to make our server make requests to internal services. They tried to access our internal admin panel at 192.168.1.100 through our API endpoint. The API doesn't validate URLs before making requests.
```

**What to look for:**
- Should detect SSRF (might classify as injection or security_misconfiguration)
- Should identify the internal network access attempt
- Playbook should include URL validation steps

---

## Test 4: Critical Incident - Automated Response

**Scenario:**
```
URGENT: We just discovered an unauthorized admin account was created and used to access our production database. Customer data including credit card numbers may have been exfiltrated. We need an immediate response plan.
```

**What to look for:**
- Should classify as broken_access_control (critical)
- Should generate a comprehensive response plan
- Should include steps like:
  - Isolate affected systems
  - Revoke compromised credentials
  - Enable enhanced logging
  - Notify security team
  - Begin forensic investigation
  - Notify affected customers (if data breach confirmed)

---

## Additional Realistic Scenarios

### Scenario: Phishing Incident
```
Several employees received phishing emails that looked like they came from our IT department. Three people clicked the link and entered their credentials. We need to reset their passwords and check if their accounts were accessed.
```

**Expected:** Might classify as broken_authentication or other, should generate response plan

---

### Scenario: Ransomware Detection
```
Our backup server started encrypting files and showing a ransom note. The attacker claims they've been in our system for 2 weeks. We need to isolate everything and figure out how they got in.
```

**Expected:** Should detect security breach, generate isolation and investigation plan

---

### Scenario: API Key Leak
```
Found one of our API keys in a public GitHub repository. It was committed 3 days ago and the repo is public. The key has access to our customer database. We've already revoked it but need to check for unauthorized access.
```

**Expected:** Should classify as security_misconfiguration or sensitive_data_exposure

---

### Scenario: DDoS Attack
```
Our website is down. We're getting hit with millions of requests per second from thousands of different IP addresses. It's been going on for 2 hours and our servers can't handle it.
```

**Expected:** Might classify as insecure_design (lack of DDoS protection) or other

---

## Testing Tips

1. **Be specific:** Include details like IP addresses, system names, or specific vulnerabilities
2. **Use natural language:** Write like you're reporting to a colleague, not like a formal report
3. **Include context:** Mention what happened, when, and what the impact is
4. **Test edge cases:** Try vague descriptions, multiple incidents, or unusual scenarios
5. **Check the results:** Verify the classification makes sense and the playbook steps are relevant

---

## What Makes a Good Test Case

- **Realistic:** Based on actual security incidents
- **Specific:** Includes enough detail for accurate classification
- **Natural:** Written in conversational language
- **Actionable:** Results in a useful response plan
- **Diverse:** Covers different types of incidents and severity levels

---

## Notes for Your Testing

- Test each scenario individually first
- Then try combining multiple scenarios
- Pay attention to confidence scores - they should be reasonable
- Check that playbook steps are relevant to the incident
- For multi-incident scenarios, verify all categories are detected
- Test edge cases like vague descriptions or unusual incidents

Good luck with your testing!

