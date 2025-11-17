# Incident Response Platform

**Combined Phase-1 + Phase-2 Incident Response System**

Phase-1 provides LLM-based incident classification with a ChatOps interface.  
Phase-2 delivers DAG-based playbook execution and automation engine.

---

## 🏗️ Project Structure

```
IncidentResponse_Combine/
├── app.py                              # Streamlit UI (Phase-1 + Phase-2)
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment template
├── src/                                # Phase-1 modules
│   ├── llm_adapter.py                 # OpenAI API wrapper
│   ├── extractor.py                   # IOC extraction
│   ├── dialogue_state.py              # Multi-turn conversation
│   ├── explicit_detector.py           # Keyword-based detection
│   ├── classification_rules.py        # OWASP normalization
│   ├── nvd.py                         # NVD API client
│   ├── lc_retriever.py                # Knowledge base retriever
│   └── owasp_display.py               # UI formatting
├── phase2_engine/                      # Phase-2 automation
│   ├── core/
│   │   ├── runner.py                  # Playbook executor
│   │   ├── runner_bridge.py           # Phase-1 → Phase-2 glue
│   │   ├── playbook_loader.py         # YAML playbook loader
│   │   ├── playbook_dag.py            # DAG construction
│   │   ├── automation.py              # Automation actions
│   │   └── policy.py                  # Policy enforcement
│   └── playbooks/                      # OWASP playbooks
│       ├── A01_broken_access_control.yaml
│       ├── A02_cryptographic_failures.yaml
│       ├── A03_injection.yaml
│       ├── A04_insecure_design.yaml
│       ├── A05_misconfiguration.yaml
│       ├── A06_vulnerable_components.yaml
│       ├── A07_authentication_failures.yaml
│       └── A10_ssrf.yaml
└── tests/                              # Test suite
    ├── test_phase1_classification.py
    ├── test_phase2_automation.py
    ├── test_human_multiturn_full.py   # 100-case human-style test suite
    └── generate_accuracy_report.py    # Accuracy report generator
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your OpenAI API key:

```powershell
Copy-Item .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Run the Application

```powershell
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📖 Usage

### Phase-1: Incident Classification

1. **Describe the incident** in the text area
   - Include IPs, URLs, attack patterns, CVEs
   - Be as detailed as possible

2. **Click "Classify Incident"**
   - System extracts IOCs (IPs, URLs, CVEs)
   - LLM classifies into OWASP Top 10 category
   - Confidence score is calculated

3. **Review classification results**
   - See incident type and confidence
   - View extracted indicators
   - Check OWASP category details

### Phase-2: Automated Response

Once confidence reaches 65% or higher:

1. **Click "Generate Response Plan"**
   - System maps incident → playbooks
   - Builds execution DAG
   - Generates step-by-step plan

2. **Review the response plan**
   - Steps grouped by NIST IR phases:
     - 🛡️ Preparation
     - 🔍 Detection & Analysis
     - ⚠️ Containment
     - 🧹 Eradication
     - ♻️ Recovery
     - 📋 Post-Incident Review

3. **Execute automation** (optional)
   - Uncheck "Dry Run" to execute real actions
   - **⚠️ Use with extreme caution in production!**

---

## 🔧 Configuration

### Confidence Threshold

Adjust in `.env`:
```
CONFIDENCE_THRESHOLD=0.65
```

Or modify `THRESH_GO` in `app.py`.

### LLM Model Selection

Choose model in the sidebar:
- `gpt-4o-mini` (fast, cost-effective)
- `gpt-4o` (balanced)
- `gpt-4-turbo` (most capable)

### Automation Settings

Phase-2 automation is disabled by default (dry-run mode).

To enable real automation:
1. Set `ENABLE_AUTOMATION=true` in `.env`
2. Uncheck "Dry Run" in the UI
3. **⚠️ Test thoroughly in a sandbox environment first!**

---

## 🎯 How It Works

### Phase-1 Flow

```
User Description
    ↓
IOC Extraction (IPs, URLs, CVEs)
    ↓
LLM Classification → OWASP Category
    ↓
Confidence Check (≥ 65%?)
    ↓
Ready for Phase-2
```

### Phase-2 Flow

```
Incident Type
    ↓
Map to Playbook IDs
    ↓
Load YAML Playbooks
    ↓
Build DAG (topological order)
    ↓
Policy Validation
    ↓
Execute Actions (dry-run or real)
    ↓
Response Plan Display
```

### Incident → Playbook Mapping

Configured in `phase2_engine/core/runner_bridge.py`:

```python
INCIDENT_TO_PLAYBOOK = {
    "sql_injection": ["A03_injection"],
    "xss": ["A03_injection"],
    "broken_access_control": ["A01_broken_access_control"],
    "cryptographic_failures": ["A02_cryptographic_failures"],
    # ... etc
}
```

---

## 🧪 Testing

Run tests:

```powershell
pytest tests/
```

With coverage:

```powershell
pytest --cov=src --cov=phase2_engine tests/
```

---

## 🛡️ Security Considerations

### Phase-1
- API keys stored in `.env` (never commit!)
- Input sanitization for all user text
- Rate limiting on LLM calls

### Phase-2
- **Dry-run default:** No destructive actions by default
- **Policy engine:** Validates actions before execution
- **Approval levels:** High-risk actions require approval
- **Audit logging:** All actions are logged

### ⚠️ Production Deployment

**DO NOT** run Phase-2 automation in production without:
1. Thorough testing in sandbox
2. Policy configuration review
3. Approval workflows
4. Comprehensive logging/monitoring
5. Rollback procedures

---

## 📚 Playbook Structure

Playbooks are YAML files in `phase2_engine/playbooks/`:

```yaml
id: A03_injection
name: Injection Attack Response
description: Response playbook for injection attacks
severity: critical

phases:
  preparation:
    - action: verify_waf_enabled
      name: Verify WAF Enabled
      automated: false
  
  detection_analysis:
    - action: analyze_injection_payload
      name: Analyze Injection Payload
      automated: true
      params:
        log_sources: ["waf", "application"]
  
  containment:
    - action: enable_waf_rule
      name: Enable WAF Rule
      automated: true
  # ... more phases
```

---

## 🔄 Multi-Incident Merging

To merge multiple incidents:

1. Classify the primary incident
2. Add additional incidents in "Additional incidents to merge" text area
3. Click "Generate Response Plan"
4. System will merge playbooks using DAG composition

---

## 🤝 Contributing

This is an educational/demo project combining two approaches:
- **Your repo:** Phase-1 ChatOps + classification
- **Friend's repo (IR-SANDBOX):** Phase-2 playbook + DAG

To extend:
1. Add new playbooks in `phase2_engine/playbooks/`
2. Update mapping in `runner_bridge.py`
3. Add automation actions in `automation.py`
4. Configure policies in `policy.py`

---

## 🧪 Testing & Accuracy

### 100-Case Human-Style Test Suite

The project includes comprehensive testing with **100 real-world test cases**:

- **72 single-incident tests:** Human-style multi-turn conversations for accuracy metrics
- **28 multi-incident tests:** Complex scenarios for playbook merging and DAG validation

**Run tests:**
```powershell
# Install test dependencies
pip install pytest pytest-json-report

# Run full test suite
pytest tests/test_human_multiturn_full.py -v

# Generate accuracy report
pytest tests/test_human_multiturn_full.py -v --json-report --json-report-file=tests/results.json
python tests/generate_accuracy_report.py tests/results.json

# View results
cat tests/ACCURACY_REPORT.md
```

### Multilabel DAG Merge Tests

Validates Phase-2 playbook merging for multi-vector incidents:

- **22 merge scenarios:** 2-label, 3-label, and stress tests
- **All 8 OWASP playbooks:** Verified individually and in combinations
- **Critical four validation:** A01, A04, A05, A07 merge tested

**Run merge tests:**
```powershell
# Run DAG merge validation
pytest tests/test_multilabel_merge.py -v

# View merge report
cat tests/MULTILABEL_MERGE_REPORT.md
```

**Test categories:**
- Broken Access Control (12 tests)
- Injection (12 tests)
- Broken Authentication (12 tests)
- Security Misconfiguration (12 tests)
- Sensitive Data Exposure (8 tests)
- Cryptographic Failures (8 tests)
- Other/Non-Security (8 tests)

See **[RUN_TESTS.md](RUN_TESTS.md)** for detailed testing guide.

---

## 📄 License

MIT License - Educational purposes

---

## 🙏 Acknowledgments

- Phase-1: LLM-first incident classification
- Phase-2: DAG-based automation engine (IR-SANDBOX concept)
- OWASP Top 10 2021
- NIST Incident Response Framework

---

## 📞 Support

For issues or questions, create a GitHub issue or refer to the documentation in each module's docstrings.

---

**Built with ❤️ for security teams everywhere**
