# Incident Response ChatOps Assistant

Automated security incident classification and response system built with LLM technology and playbook automation.

## Results Summary

After testing on 50 challenging security incident cases, the system achieved:
- **98.0% classification accuracy** (49 out of 50 cases correct)
- **100% playbook validation** (all 28 multi-playbook scenarios passed)
- Uses a hybrid approach combining rule-based detection, LLM classification, and canonical mapping

The system supports multiple LLM providers (Gemini, OpenAI, Claude) for baseline comparisons.

## Project Structure

```
incidentResponse_Combine/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
├── setup.ps1                   # Quick setup script
├── test_cases.py               # Test case definitions
│
├── src/                        # Core source code
│   ├── phase1_core.py         # Classification pipeline
│   ├── llm_adapter.py         # Multi-LLM integration (Gemini, OpenAI, Claude)
│   ├── explicit_detector.py   # Regex pattern detection (100+ patterns)
│   ├── classification_rules.py # Canonical label mapping (90+ variations)
│   └── baseline_keyword_classifier.py # Baseline classifier
│
├── phase2_engine/             # Playbook execution engine
│   ├── core/                  # Core execution logic
│   └── playbooks/             # OWASP category playbooks (YAML)
│
├── tests/                     # Test suite
│   ├── accuracy/              # Accuracy test cases
│   └── test_*.py              # Various test files
│
├── scripts/                   # Utility scripts
│   ├── experiments/           # Experiment scripts
│   ├── visualization/         # Chart generation
│   ├── testing/               # Test utilities
│   └── setup/                 # Setup helpers
│
├── docs/                      # Documentation
│   ├── guides/                # User guides
│   ├── architecture/          # Architecture docs
│   ├── experiments/           # Experiment docs
│   └── README.md              # Documentation index
│
└── reports/                   # Test results & reports
    ├── papers/                # Paper-ready reports (IEEE format)
    ├── visualizations/         # Charts and images
    ├── results/               # JSON test results
    └── summaries/             # Summary reports
```

## ⚠️ **NEW: Confused about project files?**
**Read `ESSENTIAL_FILES_GUIDE.md` first!** It explains what files you actually need vs what you can ignore.

## Getting Started

### Installation

First, install the required dependencies:

```powershell
pip install -r requirements.txt
```

### Configuration

Set up your API keys. You can either:

1. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your-api-key-here
   ANTHROPIC_API_KEY=your-claude-key-here  # Optional, for baseline comparison
   ```

2. Or set environment variables directly:
   ```powershell
   $env:GEMINI_API_KEY = "your-api-key-here"
   ```

### Running the Application

Start the Streamlit web interface:

```powershell
streamlit run app.py
```

The application will open in your browser where you can interact with the incident classification system.

### Running Tests

Execute the test suite:

```powershell
pytest tests/ -v
```

For baseline comparison experiments:

```powershell
python scripts/experiments/run_llm_baseline_experiment.py --baseline claude
```

## Test Results

### Latest Results (November 2025)

Overall accuracy: **98.0%** (49/50 test cases)

Breakdown by category:
- **A01** - Broken Access Control: 92.3% (12/13)
- **A04** - Cryptographic Failures: 100.0% (12/12) ✅
- **A05** - Injection: 100.0% (13/13) ✅
- **A07** - Authentication Failures: 100.0% (12/12) ✅

### Test Reports

All test reports and results are available in the `reports/` directory:
- `reports/papers/IEEE_Experiment_Report_*.md` - IEEE-formatted results
- `reports/visualizations/accuracy_by_category_ieee.png` - Category accuracy chart
- `reports/visualizations/overall_accuracy_gauge_ieee.png` - Overall accuracy gauge
- `reports/results/accuracy_results_all_50_*.json` - Complete test results

## Technology Stack

- **LLM Models**: Google Gemini 2.5 Pro (primary), Claude 3.5 Sonnet (baseline), OpenAI GPT-4o (baseline)
- **Web Framework**: Streamlit 1.x
- **Testing**: Pytest
- **DAG Processing**: NetworkX 3.0+
- **Visualization**: Matplotlib (IEEE-format charts)
- **Python**: 3.12.4

## Features

- Multi-LLM support (Gemini, OpenAI, Claude)
- Baseline comparison tools for model evaluation
- IEEE-formatted visualizations for academic papers
- Hybrid classification approach (rule-based + LLM + canonical mapping)
- Full OWASP Top 10:2025 category support
- Automated playbook generation using DAG-based approach

## Documentation

See the `docs/` directory for detailed documentation:
- **Getting Started**: `docs/guides/QUICKSTART.md`
- **Architecture**: `docs/architecture/ARCHITECTURE.md`
- **Experiments**: `docs/experiments/D3_EXPERIMENT_PLAN.md`
- **Full Index**: `docs/README.md`

## Repository

GitHub: https://github.com/Satayu47/IncidentResponse_NEW

## License

This project is part of academic research on automated incident response systems.

## Contributing

This is a research project. For questions or contributions, please open an issue on GitHub.
