# Changelog

## [Latest] - 2025-11-18

### Added
- ✅ **Claude (Anthropic) support** for baseline comparison
- ✅ **IEEE-format visualizations** (category chart, accuracy gauge)
- ✅ **Baseline comparison test script** (`scripts/test_baseline_comparison.py`)
- ✅ **IEEE report generator** (`scripts/generate_ieee_baseline_report.py`)
- ✅ **Visualization script** (`scripts/visualize_accuracy_results.py`)
- ✅ **Multi-LLM support** (Gemini, OpenAI, Claude)

### Updated
- ✅ **Test Results**: 98.0% accuracy (49/50 test cases)
- ✅ **README.md**: Updated with latest results and features
- ✅ **LLMAdapter**: Extended to support multiple providers
- ✅ **Requirements.txt**: Added `anthropic>=0.18.0`

### Security
- ✅ Removed all hardcoded API keys from test scripts
- ✅ All API keys now use environment variables
- ✅ Enhanced `.gitignore` to exclude sensitive files

### Documentation
- ✅ Added `docs/BASELINE_COMPARISON_GUIDE.md`
- ✅ Added `docs/CLAUDE_SETUP.md`
- ✅ Added `docs/ALTERNATIVE_MODELS_GUIDE.md`
- ✅ Added `CONTRIBUTING.md`
- ✅ Added `LICENSE` (MIT)

### Results
- **A01 - Broken Access Control**: 92.3% (12/13)
- **A04 - Cryptographic Failures**: 100.0% (12/12) ✅
- **A05 - Injection**: 100.0% (13/13) ✅
- **A07 - Authentication Failures**: 100.0% (12/12) ✅
- **Overall**: 98.0% (49/50) ✅

---

## Previous Versions

See `CHANGELOG_BASELINE_COMPARISON.md` for detailed baseline comparison feature changelog.

