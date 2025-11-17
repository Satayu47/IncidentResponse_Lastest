# Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 2: Set Up Environment

```powershell
# Copy the example environment file
Copy-Item .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Run the Application

```powershell
streamlit run app.py
```

The app will open at http://localhost:8501

---

## 📝 Try It Out

### Example 1: SQL Injection

**Incident Description:**
```
We detected SQL injection attempts from IP 192.168.1.100 targeting our 
/login endpoint. The attacker used union-based injection with payloads 
like ' UNION SELECT username, password FROM users--
```

**Expected Result:**
- Classification: A03 - Injection (SQL Injection)
- Confidence: High (>70%)
- Playbook: A03_injection
- Response plan with 6 phases

---

### Example 2: Broken Access Control

**Incident Description:**
```
User account u12345 accessed admin panel without proper authorization. 
Logs show privilege escalation attempt via IDOR vulnerability at 
/api/users/{user_id}/profile endpoint.
```

**Expected Result:**
- Classification: A01 - Broken Access Control
- Confidence: High
- Playbook: A01_broken_access_control

---

### Example 3: Cryptographic Failure

**Incident Description:**
```
Database backup found on public S3 bucket containing plaintext passwords 
and credit card numbers. No encryption was applied. Affected records: ~5000 users.
CVE-2023-1234 related to weak cipher implementation.
```

**Expected Result:**
- Classification: A02 - Cryptographic Failures
- Confidence: High
- Extracted CVE: CVE-2023-1234
- Playbook: A02_cryptographic_failures

---

## 🎯 Understanding the Workflow

### Phase-1: Classification
1. Paste incident description
2. Click "Classify Incident"
3. System extracts IOCs (IPs, URLs, CVEs)
4. LLM classifies into OWASP category
5. Confidence score calculated

### Phase-2: Response Plan
1. When confidence ≥ 65%, "Generate Response Plan" appears
2. Click button to generate plan
3. System maps incident → playbook
4. DAG builds execution flow
5. Plan displayed by NIST IR phases

---

## ⚙️ Settings

### Sidebar Controls
- **LLM Model:** Choose between gpt-4o-mini, gpt-4o, gpt-4-turbo
- **Fast Mode:** Use keyword-based detection (faster, less accurate)
- **Reset:** Clear conversation and start over

### Phase-2 Options
- **Dry Run:** Simulate actions (default: ON)
  - **⚠️ Turn OFF only in sandbox environments!**
- **Multi-Incident:** Merge multiple incidents (optional)

---

## 🔍 What to Look For

### Good Classification
- ✅ Confidence > 70%
- ✅ Correct OWASP category
- ✅ IOCs extracted (IPs, URLs, CVEs)
- ✅ Relevant rationale

### Phase-2 Success
- ✅ Playbook mapped correctly
- ✅ Steps organized by phase
- ✅ All 6 NIST phases present
- ✅ Mix of manual + automated steps

---

## 🐛 Troubleshooting

### "OpenAI API Key missing"
→ Set `OPENAI_API_KEY` in `.env` file

### "No suitable playbook found"
→ Check that incident type maps to a playbook in `runner_bridge.py`

### Low Confidence (<65%)
→ Add more details to incident description
→ Include specific attack patterns, IPs, CVEs

### Module Import Errors
→ Ensure all dependencies installed: `pip install -r requirements.txt`

---

## 📚 Next Steps

1. **Customize Playbooks:** Edit YAML files in `phase2_engine/playbooks/`
2. **Add Mappings:** Update `INCIDENT_TO_PLAYBOOK` in `runner_bridge.py`
3. **Add Actions:** Extend `automation.py` with new automation actions
4. **Configure Policies:** Adjust approval levels in `policy.py`
5. **Run Tests:** `pytest tests/`

---

## 🎓 Learn More

- Read `README.md` for full documentation
- Check docstrings in each module
- Review playbook YAML structure
- Explore `runner_bridge.py` for mapping logic

---

**Happy Incident Response! 🛡️**
