"""
Analyze Latency Consistency
===========================

Analyzes why latency is inconsistent and suggests improvements.
"""

import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import ExplicitDetector

# Load latest latency data
reports_dir = project_root / "reports"
latency_files = sorted(reports_dir.glob("overall_latency_*.json"), reverse=True)

if not latency_files:
    print("[ERROR] No latency data found")
    sys.exit(1)

with open(latency_files[0], 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("LATENCY CONSISTENCY ANALYSIS")
print("=" * 70)

# Analyze each test case
fast_path_cases = []
llm_path_cases = []

for entry in data:
    test_case = entry.get("test_case", 0)
    description = entry.get("description", "")
    total_ms = entry.get("total_latency_ms", 0)
    llm_ms = entry.get("step4_llm_classification_ms", 0)
    
    # Check if fast path was used
    if llm_ms == 0.0:
        fast_path_cases.append({
            "test_case": test_case,
            "description": description,
            "latency": total_ms,
            "path": "FAST PATH"
        })
    else:
        llm_path_cases.append({
            "test_case": test_case,
            "description": description,
            "latency": total_ms,
            "llm_time": llm_ms,
            "path": "LLM PATH"
        })

print(f"\nFast Path Cases: {len(fast_path_cases)}/{len(data)} ({len(fast_path_cases)*100/len(data):.0f}%)")
print("-" * 70)
for case in fast_path_cases:
    print(f"  Test {case['test_case']}: {case['latency']:.1f}ms - {case['description'][:50]}...")

print(f"\nLLM Path Cases: {len(llm_path_cases)}/{len(data)} ({len(llm_path_cases)*100/len(data):.0f}%)")
print("-" * 70)
for case in llm_path_cases:
    print(f"  Test {case['test_case']}: {case['latency']:.1f}ms (LLM: {case['llm_time']:.1f}ms) - {case['description'][:50]}...")

# Check why LLM cases didn't use fast path
print(f"\n{'='*70}")
print("WHY LLM CASES DIDN'T USE FAST PATH")
print("=" * 70)

detector = ExplicitDetector()
for case in llm_path_cases:
    desc = case['description']
    explicit_label, explicit_conf = detector.detect(desc)
    
    print(f"\nTest {case['test_case']}: {desc[:60]}...")
    if explicit_label:
        print(f"  Explicit detection: {explicit_label} (conf: {explicit_conf:.2f})")
        if explicit_conf < 0.85:
            print(f"  [REASON] Confidence {explicit_conf:.2f} < 0.85 threshold")
        else:
            print(f"  [WARNING] Should have used fast path! (conf >= 0.85)")
    else:
        print(f"  Explicit detection: None")
        print(f"  [REASON] No pattern matched")

print(f"\n{'='*70}")
print("RECOMMENDATIONS")
print("=" * 70)
print("\nTo improve consistency:")
print("  1. Add more explicit detection patterns for LLM cases")
print("  2. Lower threshold to 0.80 (more cases use fast path)")
print("  3. Add API timeout to prevent very slow responses")
print("  4. Use connection pooling for API calls")
print(f"\n{'='*70}\n")

