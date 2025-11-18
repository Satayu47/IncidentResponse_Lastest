# 🎯 ChatOps Demo Guide

## Demo Scenarios

### Scenario 1: Separate OWASP Categories (A01, A04, A05, A07)

Test each category individually:

#### A01 - Broken Access Control
```
Unauthorized user accessed admin panel and modified user permissions
```

#### A04 - Insecure Design
```
Application lacks proper input validation, allowing malicious data to be processed
```

#### A05 - Security Misconfiguration
```
Default credentials still active on production server, debug mode enabled
```

#### A07 - Authentication Failures
```
Multiple failed login attempts detected, weak password policy allows common passwords
```

---

### Scenario 2: Multiple Incidents Combined (A01, A04, A05, A07)

**Single input with multiple incidents:**

```
Security incident report:
1. Unauthorized access detected - user without admin privileges accessed sensitive customer data (A01)
2. Application design flaw - no rate limiting on API endpoints allows brute force attacks (A04)
3. Server misconfiguration - default admin password still active, debug logs exposed publicly (A05)
4. Authentication failure - 500+ failed login attempts from same IP, weak password policy (A07)
```

**Expected Result:**
- System should detect all 4 categories
- Multiple playbooks should be loaded and merged
- DAG should contain steps from all 4 playbooks

---

### Scenario 3: Outside A01, A04, A05, A07

Test other OWASP categories:

#### A02 - Cryptographic Failures
```
Database stores passwords in plaintext, no encryption for sensitive data transmission
```

#### A03 - Injection
```
SQL injection detected in login form, attacker attempted to extract user credentials
```

#### A06 - Vulnerable Components
```
Outdated library with known CVE-2023-12345 vulnerability detected in production
```

#### A10 - SSRF
```
Server-side request forgery attack attempted, attacker tried to access internal services
```

---

### Scenario 4: Automated Playbook Execution (Optional)

**Critical incident for automated response:**

```
Critical security breach: Unauthorized admin access, data exfiltration detected, immediate response required
```

**Steps to test:**
1. Enter the description above
2. Wait for classification (should detect A01 - Broken Access Control)
3. Click "Generate Response Plan" button
4. Review the generated playbook steps
5. (Optional) Click "Execute Step" buttons to simulate automated actions

**Expected Playbook Actions:**
- Isolate affected systems
- Revoke compromised credentials
- Enable enhanced logging
- Notify security team
- Begin forensic investigation

---

## How to Run the Demo

1. **Start the app** (if not already running):
   ```bash
   streamlit run app.py
   ```

2. **Open browser** at http://localhost:8501

3. **Test each scenario:**
   - Copy the description from each scenario
   - Paste into the chat input
   - Press Enter or click Send
   - Observe classification results
   - For Scenario 2, verify multiple playbooks are detected
   - For Scenario 4, generate and review the playbook

4. **Check results:**
   - Classification accuracy
   - Confidence scores
   - Playbook selection
   - DAG merging (for multi-incident)
   - Automated steps (for playbook execution)

---

## Expected Outcomes

### Scenario 1 (Separate Categories)
- ✅ Each incident correctly classified
- ✅ Confidence > 65% for each
- ✅ Correct playbook selected

### Scenario 2 (Multiple Incidents)
- ✅ All 4 categories detected
- ✅ 4 playbooks loaded
- ✅ DAG merged successfully
- ✅ No circular dependencies

### Scenario 3 (Other Categories)
- ✅ Correct category classification
- ✅ Appropriate playbook selected
- ✅ CVE information retrieved (if applicable)

### Scenario 4 (Automated Playbook)
- ✅ Critical incident detected
- ✅ Response plan generated
- ✅ Steps are actionable
- ✅ Execution simulation works

---

## Tips

- **For better results:** Provide detailed descriptions
- **Multi-incident:** Clearly separate incidents with numbers or bullet points
- **CVE lookup:** Include CVE IDs for automatic vulnerability information
- **Playbook execution:** Review steps before executing in production

---

## Troubleshooting

**If classification fails:**
- Check API key is set in sidebar
- Verify description is clear and detailed
- Try rephrasing the incident description

**If playbook doesn't generate:**
- Ensure confidence score > 65%
- Check that playbook exists for the category
- Verify classification is correct

**If multi-incident merge fails:**
- Ensure all categories are clearly stated
- Check that all playbooks exist
- Verify DAG merging logic is working

