"""
Baseline Comparison Experiment - IEEE Format
============================================

Scientific experiment comparing Gemini 2.5 Pro vs baseline models
(Claude, OpenAI) on identical test cases.

This script runs a controlled experiment and generates IEEE-formatted results.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_adapter import LLMAdapter
from src.classification_rules import canonicalize_label
from test_cases import TEST_CASES

# Rate limiting
GEMINI_RATE_LIMIT = 4.5  # seconds
CLAUDE_RATE_LIMIT = 1.0  # seconds
OPENAI_RATE_LIMIT = 1.0  # seconds


def normalize_label(label: str) -> str:
    """Normalize label for comparison."""
    return canonicalize_label(label.lower().replace(" ", "_"))


def run_experiment_for_model(
    model_name: str,
    provider: str,
    test_cases: List[Dict[str, Any]],
    api_key: str = None
) -> Dict[str, Any]:
    """
    Run controlled experiment for a single model.
    
    Returns:
        Dict with detailed results including:
        - Overall accuracy
        - Category-wise accuracy
        - Confidence scores
        - Response times
        - Error analysis
    """
    print(f"\n{'='*70}")
    print(f"EXPERIMENT: Testing {provider.upper()} - {model_name}")
    print(f"{'='*70}\n")
    
    # Initialize adapter
    try:
        adapter = LLMAdapter(model=model_name, api_key=api_key)
    except Exception as e:
        print(f"[ERROR] Failed to initialize {model_name}: {e}")
        return {
            "model": model_name,
            "provider": provider,
            "status": "error",
            "error": str(e),
            "results": [],
            "accuracy": 0.0,
            "total_tests": len(test_cases)
        }
    
    results = []
    correct = 0
    total_time = 0
    confidence_scores = []
    
    # Category-wise tracking
    category_stats = defaultdict(lambda: {"correct": 0, "total": 0, "confidences": []})
    
    rate_limit = {
        "gemini": GEMINI_RATE_LIMIT,
        "anthropic": CLAUDE_RATE_LIMIT,
        "openai": OPENAI_RATE_LIMIT
    }.get(provider, 1.0)
    
    for idx, test_case in enumerate(test_cases, 1):
        test_id = test_case.get("id", f"test_{idx}")
        user_input = test_case.get("user_input", "")
        expected = test_case.get("expected", "")
        category = test_case.get("category", "Other")
        difficulty = test_case.get("difficulty", "medium")
        
        print(f"[{idx:2d}/{len(test_cases)}] {test_id} ({difficulty[:4]})", end=" ... ")
        
        start_time = time.time()
        
        try:
            # Classify incident
            classification = adapter.classify_incident(
                description=user_input,
                context="",
                conversation_history=None
            )
            
            elapsed = time.time() - start_time
            total_time += elapsed
            
            # Extract results
            fine_label = classification.get("fine_label", "")
            incident_type = classification.get("incident_type", "")
            confidence = float(classification.get("confidence", 0.0))
            rationale = classification.get("rationale", "")
            
            # Normalize for comparison
            predicted_normalized = normalize_label(fine_label)
            expected_normalized = normalize_label(expected)
            
            is_correct = predicted_normalized == expected_normalized
            
            if is_correct:
                correct += 1
                status = "[OK]"
            else:
                status = "[X]"
            
            confidence_scores.append(confidence)
            
            # Track by category
            category_stats[category]["total"] += 1
            if is_correct:
                category_stats[category]["correct"] += 1
            category_stats[category]["confidences"].append(confidence)
            
            result = {
                "test_id": test_id,
                "user_input": user_input,
                "expected": expected,
                "expected_normalized": expected_normalized,
                "predicted": fine_label,
                "predicted_normalized": predicted_normalized,
                "incident_type": incident_type,
                "confidence": confidence,
                "rationale": rationale,
                "correct": is_correct,
                "elapsed_time": round(elapsed, 3),
                "difficulty": difficulty,
                "category": category
            }
            
            print(f"{status} {predicted_normalized[:25]:25s} (conf: {confidence:.2f}, {elapsed:.2f}s)")
            
        except Exception as e:
            elapsed = time.time() - start_time
            total_time += elapsed
            result = {
                "test_id": test_id,
                "user_input": user_input,
                "expected": expected,
                "error": str(e)[:200],
                "correct": False,
                "elapsed_time": round(elapsed, 3),
                "difficulty": difficulty,
                "category": category
            }
            print(f"[ERROR] {str(e)[:50]}")
        
        results.append(result)
        
        # Rate limiting
        if idx < len(test_cases):
            time.sleep(rate_limit)
    
    # Calculate statistics
    accuracy = (correct / len(test_cases)) * 100 if test_cases else 0.0
    avg_time = total_time / len(test_cases) if test_cases else 0.0
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    # Category-wise accuracy
    category_accuracy = {}
    for cat, stats in category_stats.items():
        if stats["total"] > 0:
            cat_acc = (stats["correct"] / stats["total"]) * 100
            cat_avg_conf = sum(stats["confidences"]) / len(stats["confidences"]) if stats["confidences"] else 0.0
            category_accuracy[cat] = {
                "accuracy": round(cat_acc, 2),
                "correct": stats["correct"],
                "total": stats["total"],
                "avg_confidence": round(cat_avg_conf, 3)
            }
    
    print(f"\n{'='*70}")
    print(f"RESULTS: {model_name}")
    print(f"  Accuracy: {correct}/{len(test_cases)} ({accuracy:.2f}%)")
    print(f"  Avg Confidence: {avg_confidence:.3f}")
    print(f"  Avg Time: {avg_time:.3f}s")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"{'='*70}\n")
    
    return {
        "model": model_name,
        "provider": provider,
        "status": "success",
        "results": results,
        "accuracy": round(accuracy, 2),
        "correct": correct,
        "total_tests": len(test_cases),
        "avg_confidence": round(avg_confidence, 3),
        "avg_time": round(avg_time, 3),
        "total_time": round(total_time, 2),
        "category_accuracy": category_accuracy
    }


def run_baseline_experiment(
    test_cases: List[Dict[str, Any]] = None,
    gemini_key: str = None,
    claude_key: str = None,
    openai_key: str = None,
    baseline_models: List[str] = None
) -> Dict[str, Any]:
    """
    Run complete baseline comparison experiment.
    
    Args:
        test_cases: List of test cases (uses all if None)
        gemini_key: Gemini API key
        claude_key: Claude API key
        openai_key: OpenAI API key
        baseline_models: List of baseline models to test (e.g., ["claude", "openai"])
    
    Returns:
        Complete experiment results in IEEE format
    """
    if test_cases is None:
        test_cases = TEST_CASES
    
    if baseline_models is None:
        # Default: try Claude, fallback to OpenAI
        baseline_models = []
        if claude_key or os.getenv("ANTHROPIC_API_KEY"):
            baseline_models.append("claude")
        if openai_key or os.getenv("OPENAI_API_KEY"):
            baseline_models.append("openai")
    
    print("\n" + "="*70)
    print("BASELINE COMPARISON EXPERIMENT")
    print("="*70)
    print(f"Test Cases: {len(test_cases)}")
    print(f"Primary Model: Gemini 2.5 Pro")
    print(f"Baseline Models: {', '.join(baseline_models) if baseline_models else 'None'}")
    print("="*70)
    
    # Test primary model (Gemini)
    gemini_results = run_experiment_for_model(
        model_name="gemini-2.5-pro",
        provider="gemini",
        test_cases=test_cases,
        api_key=gemini_key or os.getenv("GEMINI_API_KEY")
    )
    
    # Test baseline models
    baseline_results = {}
    
    if "claude" in baseline_models:
        claude_key = claude_key or os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            baseline_results["claude"] = run_experiment_for_model(
                model_name="claude-3-5-sonnet-20241022",
                provider="anthropic",
                test_cases=test_cases,
                api_key=claude_key
            )
        else:
            print("[WARNING] Claude API key not available")
    
    if "openai" in baseline_models:
        openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        if openai_key:
            baseline_results["openai"] = run_experiment_for_model(
                model_name="gpt-4o",
                provider="openai",
                test_cases=test_cases,
                api_key=openai_key
            )
        else:
            print("[WARNING] OpenAI API key not available")
    
    # Compile experiment results
    experiment = {
        "experiment_metadata": {
            "timestamp": datetime.now().isoformat(),
            "test_cases_count": len(test_cases),
            "primary_model": "gemini-2.5-pro",
            "baseline_models": list(baseline_results.keys()),
            "experiment_type": "baseline_comparison"
        },
        "primary_model": gemini_results,
        "baseline_models": baseline_results,
        "comparison": {}
    }
    
    # Generate comparisons
    for baseline_name, baseline_data in baseline_results.items():
        if baseline_data.get("status") == "success":
            comparison = {
                "accuracy_diff": round(
                    gemini_results.get("accuracy", 0) - baseline_data.get("accuracy", 0), 
                    2
                ),
                "gemini_better": gemini_results.get("accuracy", 0) > baseline_data.get("accuracy", 0),
                "baseline_better": baseline_data.get("accuracy", 0) > gemini_results.get("accuracy", 0),
                "time_diff": round(
                    gemini_results.get("avg_time", 0) - baseline_data.get("avg_time", 0),
                    3
                ),
                "confidence_diff": round(
                    gemini_results.get("avg_confidence", 0) - baseline_data.get("avg_confidence", 0),
                    3
                )
            }
            experiment["comparison"][baseline_name] = comparison
    
    # Print summary
    print("\n" + "="*70)
    print("EXPERIMENT SUMMARY")
    print("="*70)
    print(f"Primary Model (Gemini 2.5 Pro):")
    print(f"  Accuracy: {gemini_results.get('accuracy', 0):.2f}%")
    print(f"  Avg Confidence: {gemini_results.get('avg_confidence', 0):.3f}")
    print(f"  Avg Time: {gemini_results.get('avg_time', 0):.3f}s")
    
    for baseline_name, baseline_data in baseline_results.items():
        if baseline_data.get("status") == "success":
            print(f"\nBaseline Model ({baseline_name.upper()}):")
            print(f"  Accuracy: {baseline_data.get('accuracy', 0):.2f}%")
            print(f"  Avg Confidence: {baseline_data.get('avg_confidence', 0):.3f}")
            print(f"  Avg Time: {baseline_data.get('avg_time', 0):.3f}s")
            
            comp = experiment["comparison"].get(baseline_name, {})
            print(f"\n  Comparison:")
            print(f"    Accuracy Difference: {comp.get('accuracy_diff', 0):+.2f}%")
            print(f"    Winner: {'Gemini' if comp.get('gemini_better') else baseline_name.upper()}")
    
    print("="*70 + "\n")
    
    return experiment


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run baseline comparison experiment")
    parser.add_argument("--limit", type=int, help="Limit number of test cases")
    parser.add_argument("--baseline", nargs="+", choices=["claude", "openai"], 
                       default=["claude"], help="Baseline models to test")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--gemini-key", help="Gemini API key")
    parser.add_argument("--claude-key", help="Claude API key")
    parser.add_argument("--openai-key", help="OpenAI API key")
    
    args = parser.parse_args()
    
    # Get test cases
    test_cases = TEST_CASES
    if args.limit:
        test_cases = test_cases[:args.limit]
        print(f"[INFO] Limiting to first {args.limit} test cases")
    
    # Run experiment
    experiment = run_baseline_experiment(
        test_cases=test_cases,
        gemini_key=args.gemini_key,
        claude_key=args.claude_key,
        openai_key=args.openai_key,
        baseline_models=args.baseline
    )
    
    # Save results
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/baseline_experiment_{timestamp}.json"
    
    os.makedirs("reports", exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(experiment, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Experiment results saved to {output_file}")
    print(f"\n[INFO] Generate IEEE report with:")
    print(f"  python scripts/generate_ieee_experiment_report.py {output_file}")
    
    return experiment


if __name__ == "__main__":
    main()

