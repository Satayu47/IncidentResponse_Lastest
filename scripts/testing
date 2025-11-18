#!/usr/bin/env python3
"""Test the improved ambiguous case handling"""

import os
import sys
import io
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

load_dotenv()

from src.phase1_core import run_phase1_classification

print("=" * 70)
print("Testing Improved Ambiguous Case Handling")
print("=" * 70)
print()

test_cases = [
    {
        "id": "CRY-05",
        "input": "Our API returns user emails and phone numbers without any protection.",
        "expected": "cryptographic_failures",
        "note": "Ambiguous - 'without any protection' could mean encryption or authorization"
    },
    {
        "id": "AMBIG-07",
        "input": "The API endpoint returns sensitive data without checking if I'm authorized, and it's all in plain text.",
        "expected": "cryptographic_failures",
        "note": "Both access control and crypto issues - should prioritize crypto"
    },
    {
        "id": "CRY-07",
        "input": "When I check the API response, I can see passwords in the JSON. They're not hashed or anything.",
        "expected": "cryptographic_failures",
        "note": "Passwords in plain text - clear crypto failure"
    }
]

for test in test_cases:
    print(f"Testing: {test['id']}")
    print(f"Input: {test['input']}")
    print(f"Expected: {test['expected']}")
    print(f"Note: {test['note']}")
    print()
    
    try:
        result = run_phase1_classification(test['input'])
        predicted = result.get("label", "unknown")
        confidence = result.get("score", 0.0)
        rationale = result.get("rationale", "No rationale")
        
        is_correct = predicted == test['expected']
        status = "✅ CORRECT" if is_correct else "❌ WRONG"
        
        print(f"Predicted: {predicted}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Status: {status}")
        print(f"Rationale: {rationale[:150]}...")
        print()
        print("-" * 70)
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        print("-" * 70)
        print()

print("=" * 70)
print("Test Complete")
print("=" * 70)

