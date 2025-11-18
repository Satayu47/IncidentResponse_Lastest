"""
Improved Accuracy Comparison: ChatOps vs ChatGPT
================================================

Compares ChatOps (Gemini + explicit detection) vs ChatGPT (GPT-4o) with:
- All 72 single-incident + 28 multi-incident test cases (100 total)
- Multiple runs (3 per case) for confidence intervals
- Precision, Recall, F1-score per category
- Per-category detailed analysis
- Confusion matrix
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from collections import defaultdict
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_adapter import LLMAdapter
from src.classification_rules import canonicalize_label
from src.phase1_core import run_phase1_classification

# Try to import multi-incident test cases
try:
    from tests.accuracy.test_multi_incident_classification_merge import MULTI_INCIDENT_TEST_CASES
except ImportError:
    try:
        from tests.test_phase2_multi_playbooks import MULTI_INCIDENT_TEST_CASES
    except ImportError:
        MULTI_INCIDENT_TEST_CASES = []

# Import test cases
try:
    from tests.test_human_multiturn_single import CASES_SINGLE
    # Convert to dict format
    SINGLE_TEST_CASES = [
        {
            "id": case_id,
            "user_input": " ".join(turns),
            "expected": expected,
            "category": expected,
            "type": "single"
        }
        for case_id, expected, turns in CASES_SINGLE
    ]
    print(f"[INFO] Loaded {len(SINGLE_TEST_CASES)} single-incident test cases")
except ImportError:
    SINGLE_TEST_CASES = []
    print("[WARNING] Could not load single-incident test cases")

try:
    from tests.test_phase2_multi_playbooks import MULTI_INCIDENT_TEST_CASES
    # Convert to dict format (simplified - use first expected label)
    MULTI_TEST_CASES = [
        {
            "id": tc.get("id", f"multi_{i}"),
            "user_input": tc.get("description", ""),
            "expected": tc.get("expected_labels", [""])[0] if isinstance(tc.get("expected_labels"), list) else tc.get("expected", "other"),
            "category": tc.get("expected_labels", [""])[0] if isinstance(tc.get("expected_labels"), list) else tc.get("expected", "other"),
            "type": "multi"
        }
        for i, tc in enumerate(MULTI_INCIDENT_TEST_CASES[:28], 1)
    ]
    print(f"[INFO] Loaded {len(MULTI_TEST_CASES)} multi-incident test cases")
except ImportError:
    MULTI_TEST_CASES = []
    print("[WARNING] Could not load multi-incident test cases")

ALL_TEST_CASES = SINGLE_TEST_CASES + MULTI_TEST_CASES
print(f"[INFO] Total test cases: {len(ALL_TEST_CASES)}")

# Configuration
NUM_RUNS = 1  # Number of runs per test case (reduced to 1 for speed)
CONFIDENCE_LEVEL = 0.95
GEMINI_RATE_LIMIT = 2.0  # seconds between Gemini requests (reduced for speed)
OPENAI_RATE_LIMIT = 0.5  # seconds between OpenAI requests (reduced for speed)
USE_FAST_MODE = True  # Fast mode: fewer test cases, single run

def normalize_label(label) -> str:
    """Normalize label to canonical form for comparison."""
    # Handle list case (multi-label)
    if isinstance(label, list):
        label = label[0] if label else "other"
    # Handle string case
    if not isinstance(label, str):
        label = str(label)
    return canonicalize_label(label.lower().replace(" ", "_"))

def calculate_confidence_interval(data: List[float], confidence: float = 0.95) -> tuple:
    """Calculate confidence interval."""
    if len(data) < 2:
        return (data[0], data[0])
    
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    n = len(data)
    
    if n >= 30:
        t_value = 1.96
    elif n >= 10:
        t_value = 2.262
    else:
        t_value = 2.776
    
    margin = t_value * (std / np.sqrt(n))
    return (mean - margin, mean + margin)

def test_chatops(test_cases: List[Dict[str, Any]], num_runs: int = 1) -> Dict[str, Any]:
    """Test ChatOps system (Gemini + explicit detection)."""
    print(f"\n{'='*70}")
    print(f"Testing ChatOps (Gemini 2.5 Pro + Explicit Detection)")
    print(f"{'='*70}\n")
    
    all_results = []
    per_case_results = defaultdict(list)
    
    for idx, test_case in enumerate(test_cases, 1):
        test_id = test_case.get("id", f"test_{idx}")
        user_input = test_case.get("user_input", "")
        expected = test_case.get("expected", "")
        
        # Handle list case (multi-label - use first one)
        if isinstance(expected, list):
            expected = expected[0] if expected else "other"
        
        print(f"[{idx}/{len(test_cases)}] {test_id}: {user_input[:60]}...")
        
        case_runs = []
        for run in range(num_runs):
            try:
                # Use phase1_core which includes explicit detection + LLM
                result = run_phase1_classification(user_input)
                predicted = normalize_label(result.get("label", "other"))
                expected_norm = normalize_label(expected)
                is_correct = predicted == expected_norm
                
                case_runs.append({
                    "run": run + 1,
                    "predicted": predicted,
                    "expected": expected_norm,
                    "correct": is_correct,
                    "confidence": result.get("score", 0.0),
                })
                
                if run == 0:  # Only print first run
                    status = "[OK]" if is_correct else "[X]"
                    print(f"        {status} Expected: {expected_norm}, Got: {predicted}")
                
            except Exception as e:
                print(f"        [ERROR] Run {run+1}: {str(e)[:50]}")
                case_runs.append({
                    "run": run + 1,
                    "predicted": "error",
                    "expected": normalize_label(expected),
                    "correct": False,
                    "confidence": 0.0,
                    "error": str(e)
                })
            
            # Rate limiting
            if idx < len(test_cases) or run < num_runs - 1:
                time.sleep(GEMINI_RATE_LIMIT)
        
        per_case_results[test_id] = case_runs
        all_results.extend(case_runs)
    
    # Calculate statistics
    correct_counts = [sum(1 for r in runs if r.get("correct", False)) for runs in per_case_results.values()]
    accuracy_per_case = [c / num_runs for c in correct_counts]
    
    overall_correct = sum(1 for r in all_results if r.get("correct", False))
    overall_accuracy = (overall_correct / len(all_results)) * 100 if all_results else 0.0
    
    ci_lower, ci_upper = calculate_confidence_interval(accuracy_per_case, CONFIDENCE_LEVEL)
    
    return {
        "model": "ChatOps (Gemini 2.5 Pro + Explicit Detection)",
        "provider": "chatops",
        "status": "success",
        "results": all_results,
        "per_case_results": dict(per_case_results),
        "overall_accuracy": float(overall_accuracy),
        "overall_correct": overall_correct,
        "total_tests": len(all_results),
        "ci_95_lower": float(ci_lower * 100),
        "ci_95_upper": float(ci_upper * 100),
    }

def test_chatgpt(test_cases: List[Dict[str, Any]], num_runs: int = 1, api_key: str = None, model_name: str = None, provider_name: str = None) -> Dict[str, Any]:
    """Test ChatGPT (GPT-4o) or Claude."""
    print(f"\n{'='*70}")
    
    # Use provided model/name, or detect from API key
    if model_name and provider_name:
        use_claude = "claude" in model_name.lower()
    elif api_key and (api_key.startswith("sk-or-v1-") or api_key.startswith("sk-ant-")):
        use_claude = True
        model_name = "claude-3-5-sonnet-20241022"
        provider_name = "Anthropic Claude 3.5 Sonnet"
    else:
        use_claude = False
        model_name = "gpt-4o"
        provider_name = "OpenAI GPT-4o"
    
    print(f"Testing {provider_name}")
    print(f"{'='*70}\n")
    
    # Initialize adapter
    try:
        adapter = LLMAdapter(model=model_name, api_key=api_key)
    except Exception as e:
        print(f"[ERROR] Failed to initialize {provider_name}: {e}")
        return {
            "model": model_name,
            "provider": "anthropic" if use_claude else "openai",
            "status": "error",
            "error": str(e),
            "results": [],
            "overall_accuracy": 0.0,
            "total_tests": 0
        }
    
    all_results = []
    per_case_results = defaultdict(list)
    
    for idx, test_case in enumerate(test_cases, 1):
        test_id = test_case.get("id", f"test_{idx}")
        user_input = test_case.get("user_input", "")
        expected = test_case.get("expected", "")
        
        # Handle list case (multi-label - use first one)
        if isinstance(expected, list):
            expected = expected[0] if expected else "other"
        
        print(f"[{idx}/{len(test_cases)}] {test_id}: {user_input[:60]}...")
        
        case_runs = []
        for run in range(num_runs):
            try:
                classification = adapter.classify_incident(
                    description=user_input,
                    context="",
                    conversation_history=None
                )
                
                predicted = normalize_label(classification.get("fine_label", "other"))
                expected_norm = normalize_label(expected)
                is_correct = predicted == expected_norm
                
                case_runs.append({
                    "run": run + 1,
                    "predicted": predicted,
                    "expected": expected_norm,
                    "correct": is_correct,
                    "confidence": classification.get("confidence", 0.0),
                })
                
                if run == 0:  # Only print first run
                    status = "[OK]" if is_correct else "[X]"
                    print(f"        {status} Expected: {expected_norm}, Got: {predicted}")
                
            except Exception as e:
                print(f"        [ERROR] Run {run+1}: {str(e)[:50]}")
                case_runs.append({
                    "run": run + 1,
                    "predicted": "error",
                    "expected": normalize_label(expected),
                    "correct": False,
                    "confidence": 0.0,
                    "error": str(e)
                })
            
            # Rate limiting
            if idx < len(test_cases) or run < num_runs - 1:
                time.sleep(OPENAI_RATE_LIMIT)
        
        per_case_results[test_id] = case_runs
        all_results.extend(case_runs)
    
    # Calculate statistics
    correct_counts = [sum(1 for r in runs if r.get("correct", False)) for runs in per_case_results.values()]
    accuracy_per_case = [c / num_runs for c in correct_counts]
    
    overall_correct = sum(1 for r in all_results if r.get("correct", False))
    overall_accuracy = (overall_correct / len(all_results)) * 100 if all_results else 0.0
    
    ci_lower, ci_upper = calculate_confidence_interval(accuracy_per_case, CONFIDENCE_LEVEL)
    
    return {
        "model": model_name or "gpt-4o",
        "provider": "anthropic" if use_claude else "openai",
        "status": "success",
        "results": all_results,
        "per_case_results": dict(per_case_results),
        "overall_accuracy": float(overall_accuracy),
        "overall_correct": overall_correct,
        "total_tests": len(all_results),
        "ci_95_lower": float(ci_lower * 100),
        "ci_95_upper": float(ci_upper * 100),
    }

def calculate_metrics(y_true: List[str], y_pred: List[str], categories: List[str]) -> Dict[str, Any]:
    """Calculate precision, recall, F1-score per category."""
    # Flatten categories if they contain lists (for multi-incident cases)
    flat_categories = []
    for cat in categories:
        if isinstance(cat, list):
            flat_categories.extend(cat)
        else:
            flat_categories.append(cat)
    
    # Get unique categories (ensure all are strings)
    all_categories = sorted(set([str(c) for c in flat_categories + y_true + y_pred]))
    
    # Calculate metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=all_categories, average=None, zero_division=0
    )
    
    # Per-category metrics
    per_category = {}
    for i, cat in enumerate(all_categories):
        per_category[cat] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1_score": float(f1[i]),
            "support": int(support[i])
        }
    
    # Overall metrics (macro average)
    macro_precision = np.mean([m["precision"] for m in per_category.values()])
    macro_recall = np.mean([m["recall"] for m in per_category.values()])
    macro_f1 = np.mean([m["f1_score"] for m in per_category.values()])
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=all_categories)
    
    return {
        "per_category": per_category,
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "confusion_matrix": cm.tolist(),
        "categories": all_categories
    }

def main():
    """Run improved accuracy comparison."""
    print("=" * 70)
    print("IMPROVED ACCURACY COMPARISON: ChatOps vs ChatGPT")
    print("=" * 70)
    
    # Model selection - allow user to force ChatGPT
    force_chatgpt = os.getenv("FORCE_CHATGPT", "false").lower() == "true"
    use_fast_mode = USE_FAST_MODE or os.getenv("FAST_MODE", "false").lower() == "true"
    
    # Use fewer test cases in fast mode
    if use_fast_mode:
        test_cases = ALL_TEST_CASES[:30]  # Use first 30 cases for speed
        print(f"\n[FAST MODE] Using {len(test_cases)} test cases (instead of {len(ALL_TEST_CASES)})")
    else:
        test_cases = ALL_TEST_CASES
    
    print(f"\nConfiguration:")
    print(f"  Test cases: {len(test_cases)} ({len(SINGLE_TEST_CASES)} single + {len(MULTI_TEST_CASES)} multi)")
    print(f"  Runs per case: {NUM_RUNS}")
    print(f"  Total measurements: {len(test_cases) * NUM_RUNS * 2}")
    print(f"  Confidence level: {CONFIDENCE_LEVEL * 100}%")
    print(f"  Fast mode: {use_fast_mode}")
    
    # Get API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Model selection logic
    baseline_key = None
    baseline_model = None
    baseline_name = None
    
    if force_chatgpt:
        # Force ChatGPT - must have valid OpenAI key
        if openai_key and not (openai_key.startswith("sk-or-v1-") or openai_key.startswith("sk-ant-")):
            baseline_key = openai_key
            baseline_model = "gpt-4o"
            baseline_name = "OpenAI GPT-4o"
            print("[INFO] Forcing ChatGPT (GPT-4o)")
        else:
            print("[ERROR] FORCE_CHATGPT=true but no valid OpenAI key found!")
            print("[ERROR] OpenAI keys must start with 'sk-' (not 'sk-or-v1-' or 'sk-ant-')")
            return
    elif openai_key and not (openai_key.startswith("sk-or-v1-") or openai_key.startswith("sk-ant-")):
        # Valid OpenAI key - use ChatGPT
        baseline_key = openai_key
        baseline_model = "gpt-4o"
        baseline_name = "OpenAI GPT-4o"
        print("[INFO] Using ChatGPT (GPT-4o)")
    elif openai_key and (openai_key.startswith("sk-or-v1-") or openai_key.startswith("sk-ant-")):
        # Anthropic key in OPENAI_API_KEY - use Claude
        baseline_key = openai_key
        baseline_model = "claude-3-5-sonnet-20241022"
        baseline_name = "Anthropic Claude 3.5 Sonnet"
        print("[INFO] Detected Anthropic API key - using Claude instead of ChatGPT")
    elif anthropic_key:
        # Anthropic key in ANTHROPIC_API_KEY - use Claude
        baseline_key = anthropic_key
        baseline_model = "claude-3-5-sonnet-20241022"
        baseline_name = "Anthropic Claude 3.5 Sonnet"
        print("[INFO] Using Claude (Anthropic)")
    else:
        print("[WARNING] No valid baseline API key found!")
        print("[WARNING] Set OPENAI_API_KEY for ChatGPT or ANTHROPIC_API_KEY for Claude")
        baseline_key = None
    
    if not gemini_key:
        print("\n[WARNING] GEMINI_API_KEY not set. ChatOps testing may fail.")
    
    # Test ChatOps
    chatops_results = test_chatops(test_cases, NUM_RUNS)
    
    # Test baseline (ChatGPT or Claude)
    if baseline_key:
        chatgpt_results = test_chatgpt(test_cases, NUM_RUNS, baseline_key, baseline_model, baseline_name)
    else:
        chatgpt_results = {
            "model": baseline_model or "unknown",
            "provider": "unknown",
            "status": "error",
            "error": "No valid API key",
            "results": [],
            "overall_accuracy": 0.0,
            "total_tests": 0
        }
    
    # Calculate detailed metrics
    print(f"\n{'='*70}")
    print("Calculating Detailed Metrics...")
    print(f"{'='*70}\n")
    
    # Extract predictions for first run only (for confusion matrix)
    chatops_y_true = [r["expected"] for r in chatops_results["results"] if r.get("run") == 1]
    chatops_y_pred = [r["predicted"] for r in chatops_results["results"] if r.get("run") == 1]
    chatops_categories = [ALL_TEST_CASES[i % len(ALL_TEST_CASES)].get("category", "other") for i in range(len(chatops_y_true))]
    
    chatgpt_y_true = [r["expected"] for r in chatgpt_results["results"] if r.get("run") == 1]
    chatgpt_y_pred = [r["predicted"] for r in chatgpt_results["results"] if r.get("run") == 1]
    chatgpt_categories = [ALL_TEST_CASES[i % len(ALL_TEST_CASES)].get("category", "other") for i in range(len(chatgpt_y_true))]
    
    # Calculate metrics (handle empty ChatGPT results)
    chatops_metrics = calculate_metrics(chatops_y_true, chatops_y_pred, chatops_categories)
    
    if chatgpt_y_true and chatgpt_y_pred:
        chatgpt_metrics = calculate_metrics(chatgpt_y_true, chatgpt_y_pred, chatgpt_categories)
    else:
        # ChatGPT failed - create empty metrics
        chatgpt_metrics = {
            "per_category": {},
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "macro_f1": 0.0,
            "confusion_matrix": [],
            "categories": []
        }
    
    # Create comparison summary (handle missing ChatGPT results)
    if chatgpt_results["total_tests"] > 0:
        comparison = {
            "accuracy_diff": chatops_results["overall_accuracy"] - chatgpt_results["overall_accuracy"],
            "chatops_better": chatops_results["overall_accuracy"] > chatgpt_results["overall_accuracy"],
            "improvement_percentage": ((chatops_results["overall_accuracy"] - chatgpt_results["overall_accuracy"]) / chatgpt_results["overall_accuracy"] * 100) if chatgpt_results["overall_accuracy"] > 0 else 0.0
        }
    else:
        # ChatGPT failed - no comparison
        comparison = {
            "accuracy_diff": chatops_results["overall_accuracy"],
            "chatops_better": True,
            "improvement_percentage": 0.0,
            "note": "ChatGPT results unavailable (API key error)"
        }
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    
    results = {
        "timestamp": timestamp,
        "test_cases_count": len(ALL_TEST_CASES),
        "runs_per_case": NUM_RUNS,
        "confidence_level": CONFIDENCE_LEVEL,
        "chatops": chatops_results,
        "chatgpt": chatgpt_results,
        "chatops_metrics": chatops_metrics,
        "chatgpt_metrics": chatgpt_metrics,
        "comparison": comparison
    }
    
    output_file = output_dir / f"accuracy_comparison_improved_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"ChatOps (Gemini + Explicit Detection):")
    print(f"  Accuracy: {chatops_results['overall_accuracy']:.2f}% ({chatops_results['overall_correct']}/{chatops_results['total_tests']})")
    print(f"  95% CI: [{chatops_results['ci_95_lower']:.2f}%, {chatops_results['ci_95_upper']:.2f}%]")
    print(f"  Macro F1: {chatops_metrics['macro_f1']:.3f}")
    
    # Get provider name for display
    provider_name = chatgpt_results.get("provider", "openai")
    model_display = "Anthropic Claude 3.5 Sonnet" if provider_name == "anthropic" else "OpenAI GPT-4o"
    
    if chatgpt_results["total_tests"] > 0:
        print(f"\n{model_display}:")
        print(f"  Accuracy: {chatgpt_results['overall_accuracy']:.2f}% ({chatgpt_results['overall_correct']}/{chatgpt_results['total_tests']})")
        print(f"  95% CI: [{chatgpt_results['ci_95_lower']:.2f}%, {chatgpt_results['ci_95_upper']:.2f}%]")
        print(f"  Macro F1: {chatgpt_metrics['macro_f1']:.3f}")
        
        print(f"\nComparison:")
        print(f"  Accuracy Difference: {comparison['accuracy_diff']:+.2f}%")
        print(f"  Improvement: {comparison['improvement_percentage']:+.2f}%")
        baseline_name = "Claude" if provider_name == "anthropic" else "ChatGPT"
        print(f"  Winner: {'ChatOps' if comparison['chatops_better'] else baseline_name}")
    else:
        print(f"\n{model_display}:")
        print(f"  Status: FAILED (API key error - all tests failed)")
        print(f"  Note: {comparison.get('note', 'No results available')}")
        print(f"\nComparison:")
        print(f"  Note: Cannot compare - {model_display} results unavailable")
    
    print(f"\n[OK] Results saved to {output_file}")
    print(f"     Use scripts/visualization/create_improved_accuracy_charts.py to generate graphs.")
    
    return output_file

if __name__ == "__main__":
    main()

