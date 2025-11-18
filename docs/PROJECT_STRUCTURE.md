# Project Structure

## 📁 Directory Organization

```
incidentResponse_Combine/
├── app.py                          # Main Streamlit application
├── test_cases.py                   # Test case definitions (50 hard cases)
├── test_system_connection.py       # System connection test
├── requirements.txt                # Python dependencies
├── setup.ps1                       # Setup script
├── .env                            # Environment variables (API keys)
├── .gitignore                      # Git ignore rules
│
├── src/                            # Phase-1: Classification Engine
│   ├── __init__.py
│   ├── llm_adapter.py              # Gemini API adapter
│   ├── phase1_core.py              # Main classification logic
│   ├── classification_rules.py    # OWASP mapping & rules
│   ├── explicit_detector.py        # Keyword-based detection
│   ├── extractor.py                # Security entity extraction
│   ├── dialogue_state.py           # Conversation management
│   ├── cve_service.py              # CVE/NVD integration
│   ├── execution_simulator.py      # Playbook execution simulator
│   ├── owasp_display.py            # OWASP display utilities
│   ├── owasp_compatibility.py      # OWASP 2021/2025 conversion
│   ├── lc_retriever.py             # Knowledge base retriever
│   └── nvd.py                      # NVD API client
│
├── phase2_engine/                  # Phase-2: Playbook Execution
│   ├── __init__.py
│   ├── core/
│   │   ├── runner.py               # Playbook runner
│   │   ├── runner_bridge.py        # Phase-1 to Phase-2 bridge
│   │   ├── playbook_loader.py      # YAML playbook loader
│   │   ├── playbook_dag.py         # DAG construction
│   │   ├── automation.py           # Automation engine
│   │   ├── policy.py               # Policy enforcement
│   │   └── playbook_utils.py       # Utility functions
│   └── playbooks/                  # YAML playbook definitions
│       ├── A01_broken_access_control.yaml
│       ├── A02_cryptographic_failures.yaml
│       ├── A03_injection.yaml
│       ├── A04_insecure_design.yaml
│       ├── A05_misconfiguration.yaml
│       ├── A06_vulnerable_components.yaml
│       ├── A07_authentication_failures.yaml
│       ├── A08_data_integrity.yaml
│       ├── A09_logging_failures.yaml
│       └── A10_ssrf.yaml
│
├── tests/                          # Test Suites
│   ├── __init__.py
│   ├── accuracy/                   # Accuracy testing
│   │   └── test_accuracy_hard_cases.py  # 50 hard test cases
│   ├── test_phase1_classification.py
│   ├── test_phase2_automation.py
│   ├── test_phase2_multi_playbooks.py
│   ├── test_human_multiturn_full.py
│   ├── test_human_multiturn_single.py
│   ├── test_multilabel_merge.py
│   └── generate_accuracy_report.py
│
├── test_scripts/                   # Additional test scripts
│   ├── test_full_integration.py
│   ├── test_system.py
│   ├── test_gemini.py
│   ├── test_gemini_flash.py
│   └── test_gemini_2_5_flash.py
│
├── scripts/                        # Utility scripts
│   ├── test_api_key.py             # API key validation
│   ├── debug_llm_response.py       # LLM debugging
│   ├── dump_cases_csv.py           # Export test cases
│   └── eval_accuracy.py            # Accuracy evaluation
│
├── backup/                         # Backup files
│   ├── app_backup.py
│   ├── app_chat.py
│   └── app_hybrid.py
│
├── reports/                        # Test results & reports
│   ├── ACCURACY_REPORT_50_CASES.md
│   ├── accuracy_results_*.json     # Accuracy test results
│   ├── TEST_SUITE_STATUS.md
│   ├── TEST_SUITE_SUMMARY.md
│   ├── MERGE_TEST_RESULTS.md
│   └── IEEE_Test_Results_Table.md
│
└── docs/                          # Documentation
    ├── README.md
    ├── QUICKSTART.md
    ├── HOW_IT_WORKS.md
    ├── ARCHITECTURE.md
    ├── SYSTEM_VALIDATION_REPORT.md
    └── ... (other documentation files)
```

## 🔑 Environment Variables (.env)

```bash
# Required
GEMINI_API_KEY=AIzaSyAWDwuQvKMfRacmYgtKVQGmGhqCb-9uRi4

# Optional
NVD_API_KEY=your_nvd_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   - Create `.env` file in project root
   - Add `GEMINI_API_KEY=your_key_here`

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Run tests:**
   ```bash
   # System connection test
   python test_system_connection.py
   
   # Accuracy test (50 hard cases)
   python tests/accuracy/test_accuracy_hard_cases.py
   ```

## 📊 Key Features

- **Phase-1**: Incident classification using Gemini 2.5 Pro
- **Phase-2**: Automated playbook execution (DAG-based)
- **OWASP Support**: Both 2021 and 2025 versions
- **Focus Categories**: A01, A04, A05, A07 (with playbooks)
- **Test Suite**: 50 hard test cases for accuracy validation
- **CVE Integration**: NVD API for vulnerability information

## 📝 Notes

- All accuracy test results are saved to `reports/` directory
- Backup files are stored in `backup/` directory
- Test scripts are organized in `tests/` and `test_scripts/`
- Utility scripts are in `scripts/` directory

