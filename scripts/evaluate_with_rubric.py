"""
Comprehensive Evaluation with 7-Dimension Rubric (35 Points)
============================================================

Evaluates classification system using the academic rubric:
- Dimension 1: Correct Category Detection (0-5)
- Dimension 2: Confidence Calibration (0-5)
- Dimension 3: Clarification Behavior (0-5)
- Dimension 4: Ambiguity Resolution (0-5)
- Dimension 5: Reasoning Quality (0-5)
- Dimension 6: Stability Across Inputs (0-5)
- Dimension 7: Error Handling (0-5)

Total: 0-35 points per test case
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.phase1_core import run_phase1_classification
from src.baseline_keyword_classifier import BaselineKeywordClassifier
from src.classification_rules import canonicalize_label
from test_cases import TEST_CASES


class RubricEvaluator:
    """Evaluates predictions using 7-dimension rubric."""
    
    def __init__(self):
        self.baseline = BaselineKeywordClassifier()
    
    def evaluate_dimension_1(self, predicted: str, expected: str) -> int:
        """
        Dimension 1: Correct Category Detection (0-5)
        - 5 = correct primary OWASP category
        - 3 = partially correct, wrong secondary category
        - 0 = wrong category completely
        """
        predicted_norm = canonicalize_label(predicted)
        expected_norm = canonicalize_label(expected)
        
        if predicted_norm == expected_norm:
            return 5
        elif self._is_partially_correct(predicted_norm, expected_norm):
            return 3
        else:
            return 0
    
    def evaluate_dimension_2(self, confidence: float, is_correct: bool) -> int:
        """
        Dimension 2: Confidence Calibration (0-5)
        - 5 = High confidence when correct; low when unsure
        - 0 = Always high confidence even when wrong (overconfidence)
        """
        if is_correct:
            # Correct prediction: higher confidence = better
            if confidence >= 0.8:
                return 5
            elif confidence >= 0.6:
                return 4
            elif confidence >= 0.4:
                return 3
            else:
                return 2
        else:
            # Wrong prediction: lower confidence = better (shows awareness)
            if confidence < 0.5:
                return 4  # Good: knew it was uncertain
            elif confidence < 0.7:
                return 2  # Medium: somewhat overconfident
            else:
                return 0  # Bad: very overconfident when wrong
    
    def evaluate_dimension_3(self, clarification_asked: bool, needed_clarification: bool) -> int:
        """
        Dimension 3: Clarification Behavior (0-5)
        - 5 = Clarifies missing info with correct questions
        - 0 = Does not ask when input is unclear
        """
        if needed_clarification:
            if clarification_asked:
                return 5
            else:
                return 0
        else:
            # No clarification needed
            if clarification_asked:
                return 3  # Asked when not needed (acceptable)
            else:
                return 5  # Correctly didn't ask
    
    def evaluate_dimension_4(self, predicted: str, expected: str, is_ambiguous: bool) -> int:
        """
        Dimension 4: Ambiguity Resolution (0-5)
        - 5 = Correct primary category chosen in multi-symptom input
        - 0 = Confused or switches categories incorrectly
        """
        if not is_ambiguous:
            # Single incident: just check correctness
            return 5 if canonicalize_label(predicted) == canonicalize_label(expected) else 0
        
        # Ambiguous case: check if primary category is correct
        predicted_norm = canonicalize_label(predicted)
        expected_norm = canonicalize_label(expected)
        
        if predicted_norm == expected_norm:
            return 5
        elif self._is_partially_correct(predicted_norm, expected_norm):
            return 3
        else:
            return 0
    
    def evaluate_dimension_5(self, rationale: str, predicted: str, expected: str) -> int:
        """
        Dimension 5: Reasoning Quality (0-5)
        - 5 = Correct logic (auth vs access vs crypto vs injection)
        - 0 = Wrong reasoning path
        """
        predicted_norm = canonicalize_label(predicted)
        expected_norm = canonicalize_label(expected)
        
        if predicted_norm == expected_norm:
            # Check if rationale mentions correct concepts
            rationale_lower = rationale.lower()
            expected_keywords = {
                "broken_access_control": ["access", "authorization", "permission", "privilege"],
                "injection": ["injection", "sql", "xss", "command"],
                "cryptographic_failures": ["encrypt", "crypto", "hash", "plaintext"],
                "broken_authentication": ["authentication", "login", "password", "session"]
            }
            
            keywords = expected_keywords.get(expected_norm, [])
            if any(kw in rationale_lower for kw in keywords):
                return 5
            else:
                return 4  # Correct but rationale could be better
        else:
            return 0
    
    def evaluate_dimension_6(self, predictions: List[str]) -> int:
        """
        Dimension 6: Stability Across Inputs (0-5)
        - 5 = Small changes in input → similar reasoning
        - 0 = Very unstable answers
        """
        if len(predictions) < 2:
            return 5  # Can't evaluate stability with single prediction
        
        # Check consistency
        normalized = [canonicalize_label(p) for p in predictions]
        unique = len(set(normalized))
        
        if unique == 1:
            return 5  # Perfectly stable
        elif unique == 2:
            return 3  # Some variation
        else:
            return 1  # Very unstable
    
    def evaluate_dimension_7(self, error_occurred: bool, recovered: bool) -> int:
        """
        Dimension 7: Error Handling (0-5)
        - 5 = Recovers from unclear cases with clarification
        - 0 = Fails silently / gives nonsense
        """
        if error_occurred:
            if recovered:
                return 5
            else:
                return 0
        else:
            return 5  # No error = good handling
    
    def _is_partially_correct(self, predicted: str, expected: str) -> bool:
        """Check if prediction is partially correct (related categories)."""
        # Related category pairs
        related = {
            "broken_access_control": ["broken_authentication"],
            "broken_authentication": ["broken_access_control"],
            "cryptographic_failures": ["sensitive_data_exposure"],
            "sensitive_data_exposure": ["cryptographic_failures"]
        }
        
        return predicted in related.get(expected, [])
    
    def evaluate_case(
        self,
        test_case: Dict[str, Any],
        prediction: Dict[str, Any],
        clarification_asked: bool = False,
        is_ambiguous: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate a single test case using full rubric.
        
        Returns:
            Dict with scores for all 7 dimensions + total
        """
        predicted_label = prediction.get("label", "other")
        expected_label = test_case.get("expected", "other")
        confidence = prediction.get("score", 0.0)
        rationale = prediction.get("rationale", "")
        is_correct = canonicalize_label(predicted_label) == canonicalize_label(expected_label)
        
        scores = {
            "dimension_1": self.evaluate_dimension_1(predicted_label, expected_label),
            "dimension_2": self.evaluate_dimension_2(confidence, is_correct),
            "dimension_3": self.evaluate_dimension_3(clarification_asked, test_case.get("needs_clarification", False)),
            "dimension_4": self.evaluate_dimension_4(predicted_label, expected_label, is_ambiguous),
            "dimension_5": self.evaluate_dimension_5(rationale, predicted_label, expected_label),
            "dimension_6": 5,  # Will be evaluated across multiple runs
            "dimension_7": self.evaluate_dimension_7(
                "error" in prediction or prediction.get("label") == "other",
                clarification_asked
            )
        }
        
        scores["total"] = sum(scores.values())
        scores["is_correct"] = is_correct
        scores["predicted"] = predicted_label
        scores["expected"] = expected_label
        scores["confidence"] = confidence
        
        return scores


def split_test_cases(test_cases: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Split test cases into:
    - Single incident (40 cases: 10 per category)
    - Ambiguous/multiple (10 cases)
    """
    single_cases = []
    ambiguous_cases = []
    
    # Count by category
    category_counts = defaultdict(int)
    
    for case in test_cases:
        category = case.get("category", "Other")
        difficulty = case.get("difficulty", "medium")
        is_ambiguous = case.get("note", "").lower().find("ambiguous") >= 0 or difficulty == "hard"
        
        # First 10 per category go to single, rest ambiguous
        if category_counts[category] < 10 and not is_ambiguous:
            single_cases.append(case)
            category_counts[category] += 1
        else:
            ambiguous_cases.append(case)
    
    # Ensure we have 40 single and 10 ambiguous
    # If not enough ambiguous, take from single
    while len(ambiguous_cases) < 10 and len(single_cases) > 40:
        ambiguous_cases.append(single_cases.pop())
    
    return single_cases[:40], ambiguous_cases[:10]


def evaluate_system(
    test_cases: List[Dict],
    use_baseline: bool = False,
    system_name: str = "Proposed System"
) -> Dict[str, Any]:
    """
    Evaluate system on all test cases with full rubric.
    
    Returns:
        Complete evaluation results
    """
    print(f"\n{'='*70}")
    print(f"Evaluating: {system_name}")
    print(f"{'='*70}\n")
    
    # Split cases
    single_cases, ambiguous_cases = split_test_cases(test_cases)
    
    print(f"Single Incident Cases: {len(single_cases)}")
    print(f"Ambiguous Cases: {len(ambiguous_cases)}")
    print()
    
    all_results = []
    rubric_scores = []
    
    # Evaluate single cases
    print("Evaluating Single Incident Cases...")
    for i, case in enumerate(single_cases, 1):
        print(f"[{i:2d}/{len(single_cases)}] {case.get('id', 'UNKNOWN')}", end=" ... ")
        
        try:
            if use_baseline:
                from src.baseline_keyword_classifier import BaselineKeywordClassifier
                classifier = BaselineKeywordClassifier()
                prediction = classifier.classify(case["user_input"])
                prediction["label"] = canonicalize_label(prediction["label"])
            else:
                prediction = run_phase1_classification(case["user_input"])
            
            evaluator = RubricEvaluator()
            scores = evaluator.evaluate_case(prediction, case, clarification_asked=False, is_ambiguous=False)
            
            rubric_scores.append(scores["total"])
            all_results.append({
                "test_id": case.get("id"),
                "type": "single",
                "category": case.get("category"),
                "prediction": prediction,
                "rubric_scores": scores
            })
            
            status = "✓" if scores["is_correct"] else "✗"
            print(f"{status} Score: {scores['total']}/35")
            
        except Exception as e:
            print(f"ERROR: {str(e)[:50]}")
            all_results.append({
                "test_id": case.get("id"),
                "type": "single",
                "error": str(e),
                "rubric_scores": {"total": 0}
            })
    
    # Evaluate ambiguous cases
    print(f"\nEvaluating Ambiguous Cases...")
    for i, case in enumerate(ambiguous_cases, 1):
        print(f"[{i:2d}/{len(ambiguous_cases)}] {case.get('id', 'UNKNOWN')}", end=" ... ")
        
        try:
            if use_baseline:
                from src.baseline_keyword_classifier import BaselineKeywordClassifier
                classifier = BaselineKeywordClassifier()
                prediction = classifier.classify(case["user_input"])
                prediction["label"] = canonicalize_label(prediction["label"])
            else:
                prediction = run_phase1_classification(case["user_input"])
            
            evaluator = RubricEvaluator()
            scores = evaluator.evaluate_case(prediction, case, clarification_asked=False, is_ambiguous=True)
            
            rubric_scores.append(scores["total"])
            all_results.append({
                "test_id": case.get("id"),
                "type": "ambiguous",
                "category": case.get("category"),
                "prediction": prediction,
                "rubric_scores": scores
            })
            
            status = "✓" if scores["is_correct"] else "✗"
            print(f"{status} Score: {scores['total']}/35")
            
        except Exception as e:
            print(f"ERROR: {str(e)[:50]}")
            all_results.append({
                "test_id": case.get("id"),
                "type": "ambiguous",
                "error": str(e),
                "rubric_scores": {"total": 0}
            })
    
    # Calculate metrics
    single_results = [r for r in all_results if r.get("type") == "single"]
    ambiguous_results = [r for r in all_results if r.get("type") == "ambiguous"]
    
    single_correct = sum(1 for r in single_results if r.get("rubric_scores", {}).get("is_correct", False))
    ambiguous_correct = sum(1 for r in ambiguous_results if r.get("rubric_scores", {}).get("is_correct", False))
    
    single_accuracy = (single_correct / len(single_results)) * 100 if single_results else 0
    ambiguous_accuracy = (ambiguous_correct / len(ambiguous_results)) * 100 if ambiguous_results else 0
    overall_accuracy = ((single_correct + ambiguous_correct) / len(all_results)) * 100 if all_results else 0
    
    avg_rubric = sum(rubric_scores) / len(rubric_scores) if rubric_scores else 0
    
    # Overconfidence errors (high confidence when wrong)
    overconfidence_errors = sum(
        1 for r in all_results
        if not r.get("rubric_scores", {}).get("is_correct", False)
        and r.get("prediction", {}).get("score", 0) > 0.7
    )
    
    results = {
        "system_name": system_name,
        "timestamp": datetime.now().isoformat(),
        "single_incident": {
            "total": len(single_results),
            "correct": single_correct,
            "accuracy": round(single_accuracy, 2)
        },
        "ambiguous_incident": {
            "total": len(ambiguous_results),
            "correct": ambiguous_correct,
            "accuracy": round(ambiguous_accuracy, 2)
        },
        "overall": {
            "total": len(all_results),
            "correct": single_correct + ambiguous_correct,
            "accuracy": round(overall_accuracy, 2)
        },
        "rubric": {
            "average_score": round(avg_rubric, 2),
            "max_score": 35,
            "total_cases": len(all_results)
        },
        "overconfidence_errors": overconfidence_errors,
        "detailed_results": all_results
    }
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Results: {system_name}")
    print(f"{'='*70}")
    print(f"Single-Incident Accuracy: {single_accuracy:.2f}% ({single_correct}/{len(single_results)})")
    print(f"Ambiguous Case Accuracy: {ambiguous_accuracy:.2f}% ({ambiguous_correct}/{len(ambiguous_results)})")
    print(f"Overall Accuracy: {overall_accuracy:.2f}%")
    print(f"Average Rubric Score: {avg_rubric:.2f}/35")
    print(f"Overconfidence Errors: {overconfidence_errors}")
    print(f"{'='*70}\n")
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate system with 7-dimension rubric")
    parser.add_argument("--baseline", action="store_true", help="Evaluate baseline keyword classifier")
    parser.add_argument("--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    # Load test cases
    test_cases = TEST_CASES
    
    # Evaluate
    if args.baseline:
        results = evaluate_system(test_cases, use_baseline=True, system_name="Baseline Keyword Classifier")
    else:
        results = evaluate_system(test_cases, use_baseline=False, system_name="Proposed System (Gemini 2.5 Pro)")
    
    # Save results
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        system_type = "baseline" if args.baseline else "proposed"
        output_file = f"reports/rubric_evaluation_{system_type}_{timestamp}.json"
    
    os.makedirs("reports", exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Results saved to {output_file}")
    
    return results


if __name__ == "__main__":
    main()

