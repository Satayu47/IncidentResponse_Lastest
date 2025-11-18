"""Test accuracy for 50 classification test cases
Focus: A01, A04, A05, A07 (10 cases each) + 10 ambiguous cases

Usage:
    python tests/accuracy/test_accuracy_50_cases.py          # Test all 50 cases
    python tests/accuracy/test_accuracy_50_cases.py --hard  # Test only hard/very_hard cases (27 cases)
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from datetime import datetime
import json

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path (go up 2 levels from tests/accuracy/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.phase1_core import run_phase1_classification
from test_cases import TEST_CASES, get_hard_test_cases

load_dotenv()

def test_classification_accuracy(hard_only=False):
    """Test classification accuracy on test cases
    
    Args:
        hard_only: If True, only test hard/very_hard cases (27 cases)
                   If False, test all 50 cases
    """
    
    # Select test cases
    if hard_only:
        test_cases = get_hard_test_cases()
        test_type = "HARD CASES ONLY"
        case_count = len(test_cases)
    else:
        test_cases = TEST_CASES
        test_type = "ALL 50 CASES"
        case_count = len(test_cases)
    
    print("=" * 70)
    print(f"CLASSIFICATION ACCURACY TEST - {test_type}")
    print(f"Total Cases: {case_count}")
    print("Focus: A01, A04, A05, A07")
    print("=" * 70)
    print()
    
    results = {
        "A01": {"correct": 0, "total": 0, "cases": []},
        "A04": {"correct": 0, "total": 0, "cases": []},
        "A05": {"correct": 0, "total": 0, "cases": []},
        "A07": {"correct": 0, "total": 0, "cases": []},
        "ambiguous": {"correct": 0, "total": 0, "cases": []},
    }
    
    all_results = []
    
    for test_case in test_cases:
        test_id = test_case["id"]
        user_input = test_case["user_input"]
        expected = test_case["expected"]
        category = test_case["category"]
        difficulty = test_case.get("difficulty", "medium")
        
        print(f"Testing: {test_id} ({difficulty})")
        print(f"Input: {user_input[:80]}...")
        
        try:
            # Run classification
            result = run_phase1_classification(user_input)
            
            # Extract results - phase1_core returns "label", "score", "rationale"
            predicted_label = result.get("label", "unknown")
            confidence = result.get("score", 0.0)
            rationale = result.get("rationale", "No rationale")
            
            # Get incident type from label using classification rules
            from src.classification_rules import ClassificationRules
            incident_type = ClassificationRules.get_owasp_display_name(predicted_label, show_specific=False, version="2025")
            
            # Check if correct
            is_correct = False
            if isinstance(expected, list):
                is_correct = predicted_label in expected
            else:
                is_correct = predicted_label == expected
            
            # Store result
            case_result = {
                "id": test_id,
                "input": user_input,
                "expected": expected,
                "predicted": predicted_label,
                "incident_type": incident_type,
                "confidence": confidence,
                "rationale": rationale,
                "correct": is_correct,
                "difficulty": difficulty,
                "category": category
            }
            
            all_results.append(case_result)
            
            # Update category stats
            if category == "Broken Access Control":
                results["A01"]["total"] += 1
                if is_correct:
                    results["A01"]["correct"] += 1
                results["A01"]["cases"].append(case_result)
            elif category == "Cryptographic Failures":
                results["A04"]["total"] += 1
                if is_correct:
                    results["A04"]["correct"] += 1
                results["A04"]["cases"].append(case_result)
            elif category == "Injection":
                results["A05"]["total"] += 1
                if is_correct:
                    results["A05"]["correct"] += 1
                results["A05"]["cases"].append(case_result)
            elif category == "Authentication Failures":
                results["A07"]["total"] += 1
                if is_correct:
                    results["A07"]["correct"] += 1
                results["A07"]["cases"].append(case_result)
            else:
                results["ambiguous"]["total"] += 1
                if is_correct:
                    results["ambiguous"]["correct"] += 1
                results["ambiguous"]["cases"].append(case_result)
            
            # Print result
            status = "[CORRECT]" if is_correct else "[WRONG]"
            print(f"Expected: {expected} | Predicted: {predicted_label} | Confidence: {confidence:.2f}")
            if not is_correct:
                print(f"Rationale: {rationale[:100]}...")
            print(f"Result: {status}")
            print()
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            print()
            continue
    
    # Print summary
    print("=" * 70)
    print("ACCURACY SUMMARY")
    print("=" * 70)
    print()
    
    total_correct = 0
    total_tests = 0
    
    for category, stats in results.items():
        if stats["total"] > 0:
            accuracy = (stats["correct"] / stats["total"]) * 100
            total_correct += stats["correct"]
            total_tests += stats["total"]
            
            status_icon = "[OK]" if accuracy >= 80 else "[NEEDS IMPROVEMENT]"
            print(f"{category}: {status_icon}")
            print(f"  Correct: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
            print()
    
    overall_accuracy = (total_correct / total_tests) * 100 if total_tests > 0 else 0
    overall_status = "[EXCELLENT]" if overall_accuracy >= 90 else "[GOOD]" if overall_accuracy >= 70 else "[NEEDS IMPROVEMENT]"
    print(f"OVERALL ACCURACY: {total_correct}/{total_tests} ({overall_accuracy:.1f}%) {overall_status}")
    print()
    
    # Save detailed results to reports directory
    reports_dir = os.path.join(project_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    suffix = "hard_only" if hard_only else "all_50"
    output_file = os.path.join(reports_dir, f"accuracy_results_{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "total_correct": total_correct,
                "overall_accuracy": overall_accuracy,
                "by_category": {
                    cat: {
                        "correct": stats["correct"],
                        "total": stats["total"],
                        "accuracy": (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
                    }
                    for cat, stats in results.items() if stats["total"] > 0
                }
            },
            "detailed_results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Detailed results saved to: {output_file}")
    print()
    
    # Show wrong predictions
    wrong_cases = [r for r in all_results if not r["correct"]]
    if wrong_cases:
        print("=" * 70)
        print("INCORRECT PREDICTIONS")
        print("=" * 70)
        print()
        for case in wrong_cases:
            print(f"ID: {case['id']} ({case['difficulty']})")
            print(f"Input: {case['input']}")
            print(f"Expected: {case['expected']} | Predicted: {case['predicted']}")
            print(f"Confidence: {case['confidence']:.2f}")
            print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test classification accuracy")
    parser.add_argument(
        "--hard",
        action="store_true",
        help="Test only hard/very_hard cases (27 cases) instead of all 50 cases"
    )
    args = parser.parse_args()
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY not set in .env file")
        sys.exit(1)
    
    test_classification_accuracy(hard_only=args.hard)

