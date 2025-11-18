# Project Organization Plan

## Current Issues:
1. Too many .md files in root directory
2. Duplicate/old reports
3. Scripts not categorized
4. Documentation scattered

## New Structure:
```
incidentResponse_Combine/
├── app.py                    # Main application
├── README.md                 # Main readme
├── requirements.txt          # Dependencies
├── setup.ps1                 # Setup script
├── LICENSE                   # License
├── CONTRIBUTING.md           # Contributing guide
│
├── src/                      # Core source code
│   ├── phase1_core.py
│   ├── llm_adapter.py
│   ├── baseline_keyword_classifier.py
│   └── ...
│
├── phase2_engine/           # Playbook engine
│   ├── core/
│   └── playbooks/
│
├── tests/                    # Test suite
│   ├── accuracy/
│   └── ...
│
├── scripts/                  # Utility scripts
│   ├── experiments/         # Experiment scripts
│   ├── visualization/       # Visualization scripts
│   ├── testing/             # Test utilities
│   └── setup/               # Setup utilities
│
├── docs/                     # Documentation
│   ├── guides/              # User guides
│   ├── architecture/        # Architecture docs
│   ├── experiments/         # Experiment docs
│   └── api/                # API docs
│
├── reports/                  # Results & reports
│   ├── results/             # JSON results
│   ├── visualizations/      # Charts/images
│   ├── papers/              # Paper-ready reports
│   └── summaries/           # Summary reports
│
└── test_cases.py            # Test cases
```

