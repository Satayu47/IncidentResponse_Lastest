"""
Quick Baseline Test (No API Key Needed)
======================================

Simple test of baseline keyword classifier.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.baseline_keyword_classifier import BaselineKeywordClassifier
from test_cases import TEST_CASES

# Test a few cases
classifier = BaselineKeywordClassifier()

print("Testing Baseline Keyword Classifier (No API Key Needed)\n")
print("="*70)

correct = 0
total = 0

for case in TEST_CASES[:10]:  # Test first 10
    result = classifier.classify(case["user_input"])
    predicted = result["label"]
    expected = case["expected"]
    
    is_correct = predicted == expected
    if is_correct:
        correct += 1
    total += 1
    
    status = "[OK]" if is_correct else "[X]"
    print(f"{status} {case['id']:10s} | Expected: {expected:25s} | Got: {predicted:25s}")

print("="*70)
print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
print("\n[OK] Baseline works! (No API key needed)")

