# scripts/dump_cases_csv.py

"""
Export all test cases to CSV for documentation, reports, or slides.

Usage:
    python scripts/dump_cases_csv.py
"""

import csv
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_human_multiturn_single import CASES_SINGLE


def main():
    # Export single-incident cases
    path = Path("test_cases_single.csv")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "expected_label", "turn_index", "text"])
        for case_id, expected, turns in CASES_SINGLE:
            for idx, t in enumerate(turns, start=1):
                writer.writerow([case_id, expected, idx, t])

    print(f"✅ Exported {len(CASES_SINGLE)} test cases to: {path}")
    
    # Also create a summary CSV
    summary_path = Path("test_cases_summary.csv")
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "expected_label", "full_text", "num_turns"])
        for case_id, expected, turns in CASES_SINGLE:
            full_text = " ".join(turns)
            writer.writerow([case_id, expected, full_text, len(turns)])
    
    print(f"✅ Exported summary to: {summary_path}")
    
    # Print category statistics
    from collections import Counter
    categories = Counter(expected for _, expected, _ in CASES_SINGLE)
    
    print("\n" + "="*60)
    print("Test Case Distribution by Category:")
    print("="*60)
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"{cat:30s}: {count:3d} cases")
    print(f"\nTotal: {len(CASES_SINGLE)} test cases")


if __name__ == "__main__":
    main()
