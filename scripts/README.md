# Scripts Directory

## 📁 Organization

### `experiments/` - Experiment Scripts
- `run_llm_baseline_experiment.py` - Compare Gemini vs Claude/OpenAI
- `run_baseline_experiment.py` - Run baseline comparison
- `run_full_experiment.py` - Full D3 experiment with rubric
- `evaluate_with_rubric.py` - 7-dimension rubric evaluation
- `generate_ieee_experiment_report.py` - Generate IEEE reports

### `visualization/` - Visualization Scripts
- `visualize_llm_comparison.py` - LLM comparison charts
- `visualize_existing_comparison.py` - Charts from existing results
- `visualize_accuracy_results.py` - Accuracy charts

### `testing/` - Test Utilities
- `test_ambiguous_cases.py` - Test ambiguous cases
- `check_test_cases.py` - Validate test cases
- `eval_accuracy.py` - Accuracy evaluation
- `quick_baseline_test.py` - Quick baseline test

### `setup/` - Setup Helpers
- `test_claude_key.py` - Test Claude API key
- `test_api_key.py` - Test any API key
- `check_and_run_experiment.py` - Check keys and run
- `setup_baseline_experiment.ps1` - PowerShell setup

## 🚀 Quick Commands

### Run Experiment:
```powershell
python scripts/experiments/run_llm_baseline_experiment.py --baseline claude
```

### Generate Visualizations:
```powershell
python scripts/visualization/visualize_llm_comparison.py reports/results/llm_baseline_*.json
```

### Test API Keys:
```powershell
python scripts/setup/test_claude_key.py
```

