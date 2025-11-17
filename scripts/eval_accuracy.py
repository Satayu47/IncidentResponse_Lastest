# scripts/eval_accuracy.py

"""
Evaluation script: Run all 72 single-incident test cases,
compute overall and per-category accuracy, and export results to CSV.

Usage:
    python scripts/eval_accuracy.py
"""

import csv
import sys
import time
from collections import Counter
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.phase1_core import run_phase1_classification
from tests.test_human_multiturn_single import CASES_SINGLE


# Rate limiting
RATE_LIMIT_DELAY = 4.5  # seconds


def main():
    results = []
    category_totals = Counter()
    category_correct = Counter()

    print("="*70)
    print("INCIDENT RESPONSE CLASSIFICATION - ACCURACY EVALUATION")
    print("="*70)
    print(f"Total test cases: {len(CASES_SINGLE)}")
    print(f"Rate limit delay: {RATE_LIMIT_DELAY}s between API calls")
    print(f"Estimated time: {len(CASES_SINGLE) * RATE_LIMIT_DELAY / 60:.1f} minutes\n")
    print("Running tests...")
    print("-"*70)

    for i, (case_id, expected, turns) in enumerate(CASES_SINGLE, 1):
        text = " ".join(turns)
        
        # Rate limiting
        if i > 1:
            time.sleep(RATE_LIMIT_DELAY)
        
        try:
            out = run_phase1_classification(text)
            got = out["label"]
            score = out.get("score", 0.0)
            
            # Handle multi-label cases
            if isinstance(expected, list):
                expected_str = " or ".join(expected)
                ok = got in expected
                primary_expected = expected[0]
            else:
                expected_str = expected
                ok = (got == expected)
                primary_expected = expected
            
            status = "✅" if ok else "❌"
            print(f"{status} {case_id:10s} | Expected: {expected_str:30s} | Got: {got:25s} | Score: {score:.2f}")
            
            results.append({
                "case_id": case_id,
                "expected": expected_str,
                "got": got,
                "score": score,
                "correct": int(ok),
                "text": text[:100] + "..." if len(text) > 100 else text,
            })

            category_totals[primary_expected] += 1
            if ok:
                category_correct[primary_expected] += 1
                
        except Exception as e:
            print(f"❌ {case_id:10s} | ERROR: {str(e)[:50]}")
            primary_expected = expected[0] if isinstance(expected, list) else expected
            results.append({
                "case_id": case_id,
                "expected": str(expected),
                "got": "ERROR",
                "score": 0.0,
                "correct": 0,
                "text": text[:100],
            })
            category_totals[primary_expected] += 1

    # Calculate overall accuracy
    total = len(results)
    correct = sum(r["correct"] for r in results)
    acc = (correct / total) * 100 if total else 0.0

    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"Total cases:      {total}")
    print(f"Correct:          {correct}")
    print(f"Incorrect:        {total - correct}")
    print(f"Overall accuracy: {acc:.1f}%")
    print()

    # Per-category accuracy
    print("Per-category accuracy:")
    print("-"*70)
    for cat in sorted(category_totals.keys()):
        t = category_totals[cat]
        c = category_correct[cat]
        a = (c / t) * 100 if t else 0.0
        bar = "█" * int(a / 5)  # Progress bar
        print(f"{cat:30s}: {c:3d}/{t:3d} ({a:5.1f}%) {bar}")

    # Write detailed results CSV
    out_path = Path("results_single.csv")
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["case_id", "expected", "got", "score", "correct", "text"],
        )
        writer.writeheader()
        writer.writerows(results)

    print()
    print("="*70)
    print(f"✅ Detailed results written to: {out_path}")
    print("="*70)


if __name__ == "__main__":
    main()
