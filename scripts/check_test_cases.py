#!/usr/bin/env python3
"""Check test case statistics"""

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from test_cases import TEST_CASES, get_hard_test_cases

print("=" * 70)
print("Test Case Statistics")
print("=" * 70)
print()

total = len(TEST_CASES)
hard_cases = get_hard_test_cases()
hard_count = len(hard_cases)

print(f"Total test cases: {total}")
print(f"Hard/very_hard cases: {hard_count}")
print(f"Medium cases: {total - hard_count}")
print()

# Count by difficulty
from collections import Counter
difficulties = Counter(tc.get("difficulty", "medium") for tc in TEST_CASES)
print("By difficulty:")
for diff, count in sorted(difficulties.items()):
    print(f"  {diff}: {count}")

print()
print("=" * 70)
print("Current test script uses: ALL 50 CASES")
print("(not just hard cases, despite the filename)")
print("=" * 70)

