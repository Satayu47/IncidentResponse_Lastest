"""
Baseline Comparison Test: Gemini vs ChatGPT
============================================

Tests both Gemini and ChatGPT models on the same test cases
to compare classification accuracy and performance.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_adapter import LLMAdapter
from src.classification_rules import canonicalize_label
from test_cases import TEST_CASES

# Rate limiting
GEMINI_RATE_LIMIT = 4.5  # seconds between Gemini requests
OPENAI_RATE_LIMIT = 1.0  # seconds between OpenAI requests


def normalize_label(label: str) -> str:
    """Normalize label to canonical form for comparison."""
    return canonicalize_label(label.lower().replace(" ", "_"))


def test_model(
    model_name: str,
    provider: str,
    test_cases: List[Dict[str, Any]],
    api_key: str = None
) -> Dict[str, Any]:
    """
    Test a model on all test cases.
    
    Args:
        model_name: Model identifier (e.g., "gemini-2.5-pro", "gpt-4o")
        provider: "gemini" or "openai"
        test_cases: List of test case dicts
        api_key: Optional API key (uses env var if not provided)
    
    Returns:
        Dict with results, accuracy metrics, and timing
    """
    print(f"\n{'='*60}")
    print(f"Testing {provider.upper()}: {model_name}")
    print(f"{'='*60}\n")
    
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
    rate_limit = GEMINI_RATE_LIMIT if provider == "gemini" else OPENAI_RATE_LIMIT
    
    for idx, test_case in enumerate(test_cases, 1):
        test_id = test_case.get("id", f"test_{idx}")
        user_input = test_case.get("user_input", "")
        expected = test_case.get("expected", "")
        category = test_case.get("category", "")
        
        print(f"[{idx}/{len(test_cases)}] {test_id}: {user_input[:60]}...")
        
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
            
            # Extract predicted label
            fine_label = classification.get("fine_label", "")
            incident_type = classification.get("incident_type", "")
            confidence = classification.get("confidence", 0.0)
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
                "elapsed_time": round(elapsed, 2)
            }
            
            print(f"  {status} Expected: {expected_normalized}, Got: {predicted_normalized} (conf: {confidence:.2f}, {elapsed:.2f}s)")
            
        except Exception as e:
            elapsed = time.time() - start_time
            total_time += elapsed
            result = {
                "test_id": test_id,
                "user_input": user_input,
                "expected": expected,
                "error": str(e),
                "correct": False,
                "elapsed_time": round(elapsed, 2)
            }
            print(f"  [ERROR] {str(e)[:100]}")
        
        results.append(result)
        
        # Rate limiting
        if idx < len(test_cases):
            time.sleep(rate_limit)
    
    accuracy = (correct / len(test_cases)) * 100 if test_cases else 0.0
    avg_time = total_time / len(test_cases) if test_cases else 0.0
    
    print(f"\n{'='*60}")
    print(f"Results for {model_name}:")
    print(f"  Accuracy: {correct}/{len(test_cases)} ({accuracy:.2f}%)")
    print(f"  Average time per test: {avg_time:.2f}s")
    print(f"  Total time: {total_time:.2f}s")
    print(f"{'='*60}\n")
    
    return {
        "model": model_name,
        "provider": provider,
        "status": "success",
        "results": results,
        "accuracy": accuracy,
        "correct": correct,
        "total_tests": len(test_cases),
        "avg_time": round(avg_time, 2),
        "total_time": round(total_time, 2)
    }


def compare_models(
    gemini_model: str = "gemini-2.5-pro",
    baseline_model: str = "claude-3-5-sonnet-20241022",
    baseline_provider: str = "claude",
    test_cases: List[Dict[str, Any]] = None,
    gemini_key: str = None,
    baseline_key: str = None
) -> Dict[str, Any]:
    """
    Compare Gemini and ChatGPT on the same test cases.
    
    Args:
        gemini_model: Gemini model name
        openai_model: OpenAI model name
        test_cases: List of test cases (uses all from test_cases.py if None)
        gemini_key: Optional Gemini API key
        openai_key: Optional OpenAI API key
    
    Returns:
        Comparison results dict
    """
    if test_cases is None:
        test_cases = TEST_CASES
    
    baseline_name = "Claude" if baseline_provider == "claude" else "OpenAI"
    
    print(f"\n{'='*60}")
    print(f"BASELINE COMPARISON TEST")
    print(f"Test Cases: {len(test_cases)}")
    print(f"Gemini Model: {gemini_model}")
    print(f"Baseline Model: {baseline_model} ({baseline_name})")
    print(f"{'='*60}\n")
    
    # Test Gemini
    gemini_results = test_model(
        model_name=gemini_model,
        provider="gemini",
        test_cases=test_cases,
        api_key=gemini_key or os.getenv("GEMINI_API_KEY")
    )
    
    # Test Baseline (Claude or OpenAI)
    baseline_results = test_model(
        model_name=baseline_model,
        provider=baseline_provider,
        test_cases=test_cases,
        api_key=baseline_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    )
    
    # Compare results
    baseline_label = baseline_name.lower()
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "test_cases_count": len(test_cases),
        "gemini": gemini_results,
        "baseline": baseline_results,
        "baseline_provider": baseline_provider,
        "comparison": {
            "accuracy_diff": round(gemini_results.get("accuracy", 0) - baseline_results.get("accuracy", 0), 2),
            "gemini_better": gemini_results.get("accuracy", 0) > baseline_results.get("accuracy", 0),
            "baseline_better": baseline_results.get("accuracy", 0) > gemini_results.get("accuracy", 0),
            "time_diff": round(gemini_results.get("avg_time", 0) - baseline_results.get("avg_time", 0), 2),
            "gemini_faster": gemini_results.get("avg_time", 0) < baseline_results.get("avg_time", 0),
            "baseline_faster": baseline_results.get("avg_time", 0) < gemini_results.get("avg_time", 0)
        }
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"Gemini ({gemini_model}):")
    print(f"  Accuracy: {gemini_results.get('accuracy', 0):.2f}% ({gemini_results.get('correct', 0)}/{gemini_results.get('total_tests', 0)})")
    print(f"  Avg Time: {gemini_results.get('avg_time', 0):.2f}s")
    print(f"\n{baseline_name} ({baseline_model}):")
    print(f"  Accuracy: {baseline_results.get('accuracy', 0):.2f}% ({baseline_results.get('correct', 0)}/{baseline_results.get('total_tests', 0)})")
    print(f"  Avg Time: {baseline_results.get('avg_time', 0):.2f}s")
    print(f"\nDifference:")
    print(f"  Accuracy: {comparison['comparison']['accuracy_diff']:+.2f}% ({'Gemini' if comparison['comparison']['gemini_better'] else baseline_name} better)")
    print(f"  Speed: {comparison['comparison']['time_diff']:+.2f}s ({'Gemini' if comparison['comparison']['gemini_faster'] else baseline_name} faster)")
    print(f"{'='*60}\n")
    
    return comparison


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare Gemini vs ChatGPT baseline")
    parser.add_argument("--gemini-model", default="gemini-2.5-pro", help="Gemini model name")
    parser.add_argument("--openai-model", default="gpt-4o", help="OpenAI model name")
    parser.add_argument("--claude-model", default="claude-3-5-sonnet-20241022", help="Claude model name")
    parser.add_argument("--baseline", choices=["openai", "claude"], default="claude", help="Which baseline model to use")
    parser.add_argument("--limit", type=int, help="Limit number of test cases")
    parser.add_argument("--output", help="Output JSON file for results")
    parser.add_argument("--gemini-key", help="Gemini API key (overrides env var)")
    parser.add_argument("--openai-key", help="OpenAI API key (overrides env var)")
    parser.add_argument("--claude-key", help="Claude API key (overrides env var)")
    
    args = parser.parse_args()
    
    # Determine baseline model
    if args.baseline == "claude":
        baseline_model = args.claude_model
        baseline_key = args.claude_key or os.getenv("ANTHROPIC_API_KEY")
        baseline_provider = "anthropic"
    else:
        baseline_model = args.openai_model
        baseline_key = args.openai_key or os.getenv("OPENAI_API_KEY")
        baseline_provider = "openai"
    
    # Check API keys
    gemini_key = args.gemini_key or os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        print("[WARNING] GEMINI_API_KEY not set. Gemini tests will fail.")
    if not baseline_key:
        baseline_name = "Claude" if args.baseline == "claude" else "OpenAI"
        print(f"[WARNING] {baseline_name.upper()}_API_KEY not set. Baseline tests will fail.")
    
    # Get test cases
    test_cases = TEST_CASES
    if args.limit:
        test_cases = test_cases[:args.limit]
        print(f"[INFO] Limiting to first {args.limit} test cases")
    
    # Run comparison
    results = compare_models(
        gemini_model=args.gemini_model,
        baseline_model=baseline_model,
        baseline_provider=baseline_provider,
        test_cases=test_cases,
        gemini_key=gemini_key,
        baseline_key=baseline_key
    )
    
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to {args.output}")
    else:
        # Default output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/baseline_comparison_{timestamp}.json"
        os.makedirs("reports", exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"[OK] Results saved to {output_file}")


if __name__ == "__main__":
    main()

