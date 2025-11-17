# Incident Response ChatOps Assistant

Automated incident response system using LLM-based classification and playbook generation.

## 🎯 Key Results
- **100% Classification Accuracy** (72/72 test cases)
- **100% Playbook Validation** (28/28 multi-playbook tests)
- **Hybrid Approach**: Rule-based + LLM + Canonical Mapping

## 📁 Project Structure

```
incidentResponse_Combine/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
├── setup.ps1                   # Quick setup script
│
├── src/                        # Core source code
│   ├── phase1_core.py         # Classification pipeline
│   ├── llm_adapter.py         # Gemini LLM integration
│   ├── explicit_detector.py   # Regex pattern detection (100+ patterns)
│   ├── classification_rules.py # Canonical label mapping (90+ variations)
│   └── playbook_builder.py    # DAG playbook generator
│
├── tests/                      # Test suite
│   ├── test_human_multiturn_single.py  # 72 incident test cases
│   └── test_phase2_multi_playbooks.py  # 28 DAG validation tests
│
├── scripts/                    # Utilities
│   └── eval_accuracy.py       # Generate accuracy reports
│
├── phase2_engine/             # Playbook templates
│   └── playbooks/             # OWASP category playbooks
│
├── docs/                      # Documentation
│   ├── QUICKSTART.md         # Getting started guide
│   ├── ARCHITECTURE.md       # System design
│   └── HOW_IT_WORKS.md       # Technical details
│
├── reports/                   # Test results & reports
│   ├── results_single.csv    # Complete test results (100% accuracy)
│   ├── IEEE_Test_Results_Table.md  # IEEE-formatted results
│   └── test_report.txt       # Detailed test output
│
└── test_scripts/             # Development test files
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Set API key:**
   ```powershell
   $env:GEMINI_API_KEY = "your-api-key-here"
   ```

3. **Run the app:**
   ```powershell
   streamlit run app.py
   ```

4. **Run tests:**
   ```powershell
   pytest tests/ -v
   ```

## 📊 Documentation

- **Getting Started**: `docs/QUICKSTART.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Test Results**: `reports/IEEE_Test_Results_Table.md`
- **How It Works**: `docs/HOW_IT_WORKS.md`

## 🔬 Test Results

All test reports and CSV results are in the `reports/` folder:
- `results_single.csv` - Complete 72-case test results
- `IEEE_Test_Results_Table.md` - Academic paper format
- `test_report.txt` - Detailed test execution log

## 🔗 Repository

GitHub: https://github.com/Satayu47/IncidentResponse_NEW

## 🛠️ Technology Stack

- **LLM**: Google Gemini 2.5 Pro (temperature=0.0)
- **Web Framework**: Streamlit 1.x
- **Testing**: Pytest
- **DAG Processing**: NetworkX 3.0+
- **Python**: 3.12.4
