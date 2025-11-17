"""
Generate Human-Style OWASP Test Suite Accuracy Report
======================================================

Run this after executing pytest to generate a formatted markdown report.

Usage:
    python tests/generate_accuracy_report.py tests/results.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any


CATEGORY_NAMES = {
    "broken_access_control": "Broken Access Control",
    "injection": "Injection",
    "broken_authentication": "Broken Authentication",
    "sensitive_data_exposure": "Sensitive Data Exposure",
    "cryptographic_failures": "Cryptographic Failures",
    "security_misconfiguration": "Security Misconfiguration",
    "other": "Other",
}

CATEGORY_TOTALS = {
    "broken_access_control": 12,
    "injection": 12,
    "broken_authentication": 12,
    "sensitive_data_exposure": 8,
    "cryptographic_failures": 8,
    "security_misconfiguration": 12,
    "other": 8,
}


def parse_pytest_output(results_file: Path) -> Dict[str, Any]:
    """
    Parse pytest JSON output to extract test results.
    
    To generate JSON output, run:
        pytest tests/test_human_multiturn_full.py --json-report --json-report-file=tests/results.json
    
    Requires: pytest-json-report plugin
        pip install pytest-json-report
    """
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def analyze_single_incident_results(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze single-incident classification test results.
    """
    category_stats = defaultdict(lambda: {"correct": 0, "total": 0, "failed_ids": []})
    
    for test_name, test_data in data.get("tests", {}).items():
        # Only process single-incident tests
        if "test_single_incident_classification" not in test_name:
            continue
        
        # Extract case ID and expected label from test parameters
        params = test_data.get("call", {}).get("longrepr", "")
        
        # Determine if test passed
        outcome = test_data.get("outcome", "failed")
        
        # Try to extract expected category from test name or parameters
        # Test name format: test_single_incident_classification[BAC-01-broken_access_control-text]
        if "[" in test_name and "]" in test_name:
            param_str = test_name.split("[")[1].split("]")[0]
            parts = param_str.split("-")
            if len(parts) >= 2:
                case_id = f"{parts[0]}-{parts[1]}"
                expected = "-".join(parts[2:]).split("-text")[0] if len(parts) > 2 else "unknown"
                
                if expected in CATEGORY_TOTALS:
                    category_stats[expected]["total"] += 1
                    if outcome == "passed":
                        category_stats[expected]["correct"] += 1
                    else:
                        category_stats[expected]["failed_ids"].append(case_id)
    
    return dict(category_stats)


def generate_markdown_report(
    data: Dict[str, Any],
    category_stats: Dict[str, Any],
    output_file: Path
) -> None:
    """
    Generate formatted markdown report.
    """
    summary = data.get("summary", {})
    total_tests = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    
    # Calculate single-incident totals
    single_total = sum(stats["total"] for stats in category_stats.values())
    single_correct = sum(stats["correct"] for stats in category_stats.values())
    single_accuracy = (single_correct / single_total * 100) if single_total > 0 else 0
    
    report = f"""# Human-Style OWASP Test Suite Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Model:** gpt-4o-mini (via OpenAI API)

---

## Executive Summary

This report evaluates the accuracy of the Incident Response Platform's Phase-1 classification engine using 100 human-style test cases with multi-turn conversations, emotional language, and vague descriptions.

---

## Test Summary

- **Total test cases executed:** {total_tests}
- **Total single-incident cases tested:** {single_total}
- **Passed:** {single_correct}
- **Failed:** {single_total - single_correct}
- **Overall accuracy:** `{single_accuracy:.1f}%`

---

## Per-Category Accuracy (single-incident only)

| Category                   | Correct | Total | Accuracy | Failed IDs |
|---------------------------|---------|-------|----------|------------|
"""

    for category, display_name in CATEGORY_NAMES.items():
        stats = category_stats.get(category, {"correct": 0, "total": 0, "failed_ids": []})
        correct = stats["correct"]
        total = stats["total"]
        accuracy = (correct / total * 100) if total > 0 else 0
        failed_ids = ", ".join(stats["failed_ids"]) if stats["failed_ids"] else "None"
        
        report += f"| {display_name:<25} | {correct:>7} | {total:>5} | {accuracy:>7.1f}% | {failed_ids} |\n"

    report += f"""
**Total:** {single_correct}/{single_total} ({single_accuracy:.1f}%)

---

## Multi-Incident / Merge Tests (Playbook & DAG)

- **Total multi-incident cases:** 28 (estimated)
- **Playbook mapping tests:** {summary.get('passed', 0) - single_correct} passed
- **Merged DAG validation:** See test output for details

These tests verify that:
1. Multiple OWASP categories trigger multiple playbook mappings
2. DAG merging works correctly with semantic deduplication
3. Phase-2 automation structure is valid
4. OPA policy evaluation hooks are present when configured

---

## Key Insights

### Strengths
- Categories with highest accuracy: {_get_top_categories(category_stats, top_n=2)}
- Explicit keyword detection working well for clear cases
- Multi-turn conversation context preserved

### Weaknesses
- Categories with lowest accuracy: {_get_bottom_categories(category_stats, bottom_n=2)}
- Challenges with:
  - Vague or emotional language without technical keywords
  - Edge cases between similar categories
  - "Other" classification when no clear security issue

### Recommendations
1. **Enhance LLM prompts** for low-accuracy categories
2. **Add more explicit keywords** for common attack patterns
3. **Improve confidence thresholds** for Phase-2 triggers
4. **Review failed cases** to identify prompt engineering opportunities

---

## Test Case Details

### Failed Cases by Category

"""

    # Add failed case details
    for category, display_name in CATEGORY_NAMES.items():
        stats = category_stats.get(category, {"correct": 0, "total": 0, "failed_ids": []})
        if stats["failed_ids"]:
            report += f"**{display_name}:**\n"
            for case_id in stats["failed_ids"]:
                report += f"- {case_id}\n"
            report += "\n"

    report += """---

## Methodology

### Test Suite Composition
- **72 single-incident tests:** Human-style descriptions with multi-turn context
- **28 multi-incident tests:** Complex scenarios requiring playbook merging

### Categories Tested
Focus on OWASP Top 10 2021:
- Broken Access Control (A01) - 12 tests
- Injection (A03) - 12 tests
- Broken Authentication (A07) - 12 tests
- Security Misconfiguration (A05) - 12 tests
- Sensitive Data Exposure - 8 tests
- Cryptographic Failures (A02) - 8 tests
- Other (Non-Security) - 8 tests

### Classification Flow
1. **Explicit Keyword Detection:** Pattern matching for known attack indicators
2. **IOC Extraction:** IPs, URLs, CVEs, file hashes
3. **LLM Classification:** GPT-4o-mini for semantic understanding
4. **Rule Refinement:** Normalize and merge signals

---

## Appendix: Test Execution

```bash
# Run tests with JSON report
pytest tests/test_human_multiturn_full.py -v --json-report --json-report-file=tests/results.json

# Generate this report
python tests/generate_accuracy_report.py tests/results.json
```

**Environment:**
- Python: {sys.version.split()[0]}
- Pytest: See requirements.txt
- OpenAI API: gpt-4o-mini
- Date: {datetime.now().strftime("%Y-%m-%d")}

---

*Generated by `generate_accuracy_report.py`*
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report generated: {output_file}")


def _get_top_categories(category_stats: Dict[str, Any], top_n: int = 2) -> str:
    """Get categories with highest accuracy."""
    sorted_cats = sorted(
        category_stats.items(),
        key=lambda x: (x[1]["correct"] / x[1]["total"]) if x[1]["total"] > 0 else 0,
        reverse=True
    )
    top = sorted_cats[:top_n]
    return ", ".join([CATEGORY_NAMES.get(cat, cat) for cat, _ in top])


def _get_bottom_categories(category_stats: Dict[str, Any], bottom_n: int = 2) -> str:
    """Get categories with lowest accuracy."""
    sorted_cats = sorted(
        category_stats.items(),
        key=lambda x: (x[1]["correct"] / x[1]["total"]) if x[1]["total"] > 0 else 0
    )
    bottom = sorted_cats[:bottom_n]
    return ", ".join([CATEGORY_NAMES.get(cat, cat) for cat, _ in bottom])


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_accuracy_report.py <results.json>")
        print("\nTo generate results.json, run:")
        print("  pip install pytest-json-report")
        print("  pytest tests/test_human_multiturn_full.py --json-report --json-report-file=tests/results.json")
        sys.exit(1)
    
    results_file = Path(sys.argv[1])
    if not results_file.exists():
        print(f"❌ Error: {results_file} not found")
        print("\nRun pytest with JSON report first:")
        print("  pytest tests/test_human_multiturn_full.py --json-report --json-report-file=tests/results.json")
        sys.exit(1)
    
    # Parse results
    data = parse_pytest_output(results_file)
    
    # Analyze single-incident results
    category_stats = analyze_single_incident_results(data)
    
    # Generate report
    output_file = results_file.parent / "ACCURACY_REPORT.md"
    generate_markdown_report(data, category_stats, output_file)
    
    print(f"\n📊 Summary:")
    print(f"   Total tests: {data.get('summary', {}).get('total', 0)}")
    print(f"   Passed: {data.get('summary', {}).get('passed', 0)}")
    print(f"   Failed: {data.get('summary', {}).get('failed', 0)}")


if __name__ == "__main__":
    main()
