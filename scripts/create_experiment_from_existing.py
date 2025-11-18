"""
Create Experiment Results from Existing Gemini Test Results
===========================================================

Since we have Gemini results but no baseline yet, this creates
an experiment structure that can be updated when baseline results are available.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))


def convert_gemini_results_to_experiment(gemini_json_file: str) -> dict:
    """Convert existing Gemini test results to experiment format."""
    
    with open(gemini_json_file, 'r', encoding='utf-8') as f:
        gemini_data = json.load(f)
    
    summary = gemini_data.get("summary", {})
    detailed = gemini_data.get("detailed_results", [])
    
    # Calculate category-wise accuracy
    category_stats = defaultdict(lambda: {"correct": 0, "total": 0, "confidences": []})
    
    for result in detailed:
        category = result.get("category", "Other")
        is_correct = result.get("correct", False)
        confidence = result.get("confidence", 0.0)
        
        category_stats[category]["total"] += 1
        if is_correct:
            category_stats[category]["correct"] += 1
        category_stats[category]["confidences"].append(confidence)
    
    # Build category accuracy
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
    
    # Calculate average confidence
    all_confidences = [r.get("confidence", 0.0) for r in detailed if r.get("confidence")]
    avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
    
    # Calculate average time (if available)
    all_times = [r.get("elapsed_time", 0.0) for r in detailed if r.get("elapsed_time")]
    avg_time = sum(all_times) / len(all_times) if all_times else 0.0
    
    # Build experiment structure
    experiment = {
        "experiment_metadata": {
            "timestamp": datetime.now().isoformat(),
            "test_cases_count": summary.get("total_tests", len(detailed)),
            "primary_model": "gemini-2.5-pro",
            "baseline_models": [],  # Will be added when baseline tests run
            "experiment_type": "baseline_comparison",
            "source_file": gemini_json_file
        },
        "primary_model": {
            "model": "gemini-2.5-pro",
            "provider": "gemini",
            "status": "success",
            "results": detailed,
            "accuracy": summary.get("overall_accuracy", 0.0),
            "correct": summary.get("total_correct", 0),
            "total_tests": summary.get("total_tests", len(detailed)),
            "avg_confidence": round(avg_confidence, 3),
            "avg_time": round(avg_time, 3),
            "total_time": round(sum(all_times), 2) if all_times else 0.0,
            "category_accuracy": category_accuracy
        },
        "baseline_models": {},
        "comparison": {}
    }
    
    return experiment


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create experiment structure from Gemini results")
    parser.add_argument("input", help="Gemini test results JSON file")
    parser.add_argument("-o", "--output", help="Output experiment JSON file")
    
    args = parser.parse_args()
    
    print(f"Converting Gemini results to experiment format...")
    experiment = convert_gemini_results_to_experiment(args.input)
    
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/baseline_experiment_from_gemini_{timestamp}.json"
    
    import os
    os.makedirs("reports", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(experiment, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Experiment structure saved to {output_file}")
    print(f"\n[INFO] When you have baseline results, you can:")
    print(f"  1. Run: python scripts/run_baseline_experiment.py")
    print(f"  2. Generate IEEE report: python scripts/generate_ieee_experiment_report.py {output_file}")
    
    return experiment


if __name__ == "__main__":
    main()

