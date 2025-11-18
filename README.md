# Incident Response ChatOps Assistant

Automated incident response system using LLM-based classification and playbook generation.

## 🎯 Key Results
- **98.0% Classification Accuracy** (49/50 hard test cases)
- **100% Playbook Validation** (28/28 multi-playbook tests)
- **Hybrid Approach**: Rule-based + LLM + Canonical Mapping
- **Baseline Comparison**: Supports Gemini, OpenAI, and Claude models

## 📁 Project Structure

```
incidentResponse_Combine/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
├── setup.ps1                   # Quick setup script
│
├── src/                        # Core source code
│   ├── phase1_core.py         # Classification pipeline
│   ├── llm_adapter.py         # Multi-LLM integration (Gemini, OpenAI, Claude)
│   ├── explicit_detector.py   # Regex pattern detection (100+ patterns)
│   ├── classification_rules.py # Canonical label mapping (90+ variations)
│   └── playbook_builder.py    # DAG playbook generator
│
├── phase2_engine/             # Playbook execution engine
│   ├── core/                  # Core execution logic
│   └── playbooks/             # OWASP category playbooks (YAML)
│
├── tests/                     # Test suite
│   ├── accuracy/              # Accuracy test cases
│   ├── test_human_multiturn_single.py  # 50 hard test cases
│   └── test_phase2_multi_playbooks.py  # Multi-playbook tests
│
├── scripts/                   # Utility scripts
│   ├── test_baseline_comparison.py     # Baseline model comparison
│   ├── visualize_accuracy_results.py  # Generate IEEE charts
│   └── generate_ieee_baseline_report.py # IEEE report generator
│
├── docs/                      # Documentation
│   ├── QUICKSTART.md         # Getting started guide
│   ├── ARCHITECTURE.md       # System design
│   ├── BASELINE_COMPARISON_GUIDE.md # Baseline testing guide
│   └── CLAUDE_SETUP.md       # Claude API setup
│
├── reports/                   # Test results & reports
│   ├── accuracy_results_all_50_*.json # Test results
│   ├── IEEE_Test_Results_Table.md     # IEEE-formatted results
│   ├── accuracy_by_category_ieee.png  # Category chart (IEEE)
│   └── overall_accuracy_gauge_ieee.png # Accuracy gauge (IEEE)
│
└── test_scripts/             # Development test files
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   - Create `.env` file in project root
   - Add: `GEMINI_API_KEY=your-api-key-here`
   - Or set environment variable: `$env:GEMINI_API_KEY = "your-api-key-here"`
   - Optional: Add `ANTHROPIC_API_KEY` for Claude baseline comparison

3. **Run the app:**
   ```powershell
   streamlit run app.py
   ```

4. **Run tests:**
   ```powershell
   pytest tests/ -v
   ```

5. **Run baseline comparison:**
   ```powershell
   python scripts/test_baseline_comparison.py --limit 50
   ```

## 📊 Documentation

- **Getting Started**: `docs/QUICKSTART.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Test Results**: `reports/IEEE_Test_Results_Table.md`
- **How It Works**: `docs/HOW_IT_WORK.md`
- **Baseline Comparison**: `docs/BASELINE_COMPARISON_GUIDE.md`

## 🔬 Test Results

### Latest Results (2025-11-18)
- **Overall Accuracy:** 98.0% (49/50 test cases)
- **A01 - Broken Access Control:** 92.3% (12/13)
- **A04 - Cryptographic Failures:** 100.0% (12/12) ✅
- **A05 - Injection:** 100.0% (13/13) ✅
- **A07 - Authentication Failures:** 100.0% (12/12) ✅

### Test Reports
All test reports and results are in the `reports/` folder:
- `accuracy_results_all_50_20251118_152137.json` - Latest test results
- `IEEE_Test_Results_Table.md` - IEEE-formatted results
- `accuracy_by_category_ieee.png` - Category accuracy chart (IEEE format)
- `overall_accuracy_gauge_ieee.png` - Overall accuracy gauge (IEEE format)
- `results_single.csv` - Complete test results

## 🛠️ Technology Stack

- **LLM**: Google Gemini 2.5 Pro (primary), Claude 3.5 Sonnet (baseline), OpenAI GPT-4o (baseline)
- **Web Framework**: Streamlit 1.x
- **Testing**: Pytest
- **DAG Processing**: NetworkX 3.0+
- **Visualization**: Matplotlib (IEEE-format charts)
- **Python**: 3.12.4

## 📊 Features

- ✅ **Multi-LLM Support**: Gemini, OpenAI, Claude
- ✅ **Baseline Comparison**: Compare models on same test cases
- ✅ **IEEE Visualizations**: Publication-ready charts
- ✅ **Hybrid Classification**: Rule-based + LLM + Canonical mapping
- ✅ **OWASP Top 10:2025**: Full category support
- ✅ **Automated Playbooks**: DAG-based response generation

## 🔗 Repository

GitHub: https://github.com/Satayu47/IncidentResponse_NEW

## 📝 License

This project is part of academic research on automated incident response systems.

## 🤝 Contributing

This is a research project. For questions or contributions, please open an issue on GitHub.
