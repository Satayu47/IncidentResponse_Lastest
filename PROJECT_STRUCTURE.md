# Project Structure

## 📁 Clean, Organized Structure

```
incidentResponse_Combine/
│
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── setup.ps1                 # Quick setup script
├── README.md                 # Main project documentation
├── START_HERE.md             # Quick start guide
├── LICENSE                   # License file
├── CONTRIBUTING.md           # Contribution guidelines
│
├── src/                      # Core source code
│   ├── phase1_core.py        # Classification pipeline
│   ├── llm_adapter.py        # LLM integration (Gemini, OpenAI, Claude)
│   ├── explicit_detector.py  # Pattern detection (100+ patterns)
│   ├── classification_rules.py # Label normalization
│   ├── classification_validator.py # Safety validation
│   ├── dialogue_state.py     # Multi-turn conversation management
│   ├── lc_retriever.py       # LangChain knowledge base
│   ├── cve_service.py        # NVD CVE integration
│   └── ...
│
├── phase2_engine/            # Playbook execution engine
│   ├── core/                 # Core execution logic
│   ├── playbooks/            # OWASP 2025 playbooks (YAML)
│   └── policies/             # OPA policy files
│
├── tests/                    # Test suite
│   ├── test_cases.py         # Test case definitions
│   ├── test_*.py             # Various test files
│   └── accuracy/             # Accuracy test cases
│
├── scripts/                   # Utility scripts
│   ├── test_presentation_owasp_1_4_5_7.py  # Presentation test
│   ├── experiments/          # Experiment scripts
│   ├── visualization/        # Chart generation
│   └── ...
│
├── docs/                      # Documentation (organized)
│   ├── presentation/         # Presentation materials
│   │   ├── PRESENTATION_TEST_GUIDE.md
│   │   └── PRESENTATION_NOTES.md
│   │
│   ├── thresholds/          # Threshold documentation
│   │   ├── THRESHOLD_CONFIGURATION.md
│   │   ├── THRESHOLD_65_VS_70_ANALYSIS.md
│   │   └── THRESHOLD_CHANGE_CHECKLIST.md
│   │
│   ├── setup/                # Setup guides
│   │   ├── API_KEY_SECURITY.md
│   │   ├── GET_*.md
│   │   └── SET_API_KEYS*.ps1
│   │
│   ├── status/               # Project status files
│   │   ├── PROJECT_VALIDATION.md
│   │   ├── AI_DETECTION_COMPLIANCE.md
│   │   └── GITHUB_PUSH_SUMMARY.md
│   │
│   ├── experiments/          # Experiment documentation
│   │   ├── EXPERIMENT_RUNNING.md
│   │   ├── RUN_IMPROVED_EXPERIMENTS.md
│   │   └── ...
│   │
│   ├── HOW_IT_WORKS.md       # Main documentation
│   ├── ARCHITECTURE_VERIFICATION.md
│   ├── SAFETY_MECHANISMS.md
│   ├── CONVERSATION_HANDLING.md
│   ├── DEMO_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── ...
│
└── reports/                   # Test results & reports
    ├── visualizations/        # Charts and graphs
    ├── data/                  # Test data
    └── *.md                   # Report files
```

---

## 🎯 Quick Navigation

### **For Users:**
- **Start Here:** `START_HERE.md`
- **Setup:** `docs/setup/`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`

### **For Developers:**
- **Architecture:** `docs/ARCHITECTURE_VERIFICATION.md`
- **How It Works:** `docs/HOW_IT_WORKS.md`
- **Code Structure:** `src/`

### **For Presentation:**
- **Test Guide:** `docs/presentation/PRESENTATION_TEST_GUIDE.md`
- **Test Script:** `scripts/test_presentation_owasp_1_4_5_7.py`

### **For Configuration:**
- **Thresholds:** `docs/thresholds/`
- **API Keys:** `docs/setup/`

---

## ✅ Organization Benefits

- ✅ **Clean root directory** - Only essential files
- ✅ **Logical grouping** - Related files together
- ✅ **Easy navigation** - Clear folder structure
- ✅ **Professional** - Standard project layout
- ✅ **Maintainable** - Easy to find files

---

**Last Updated:** Project reorganized for clarity and maintainability

