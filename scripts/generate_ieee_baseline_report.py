"""
Generate IEEE-Formatted Baseline Comparison Report
==================================================

Converts baseline comparison test results into IEEE paper format.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

def load_comparison_results(json_file: str) -> Dict[str, Any]:
    """Load comparison results from JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)


def categorize_test_cases(test_cases: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Categorize test cases by OWASP category."""
    categories = defaultdict(list)
    for tc in test_cases:
        category = tc.get("category", "Other")
        categories[category].append(tc.get("id", ""))
    return categories


def calculate_category_accuracy(
    results: List[Dict[str, Any]],
    test_cases: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Calculate accuracy per category."""
    # Create mapping from test_id to expected category
    test_id_to_category = {tc.get("id"): tc.get("category", "Other") for tc in test_cases}
    
    # Group results by category
    category_stats = defaultdict(lambda: {"correct": 0, "total": 0, "details": []})
    
    for result in results:
        test_id = result.get("test_id", "")
        expected = result.get("expected_normalized", "")
        predicted = result.get("predicted_normalized", "")
        is_correct = result.get("correct", False)
        
        # Get category from test cases
        category = test_id_to_category.get(test_id, "Other")
        
        category_stats[category]["total"] += 1
        if is_correct:
            category_stats[category]["correct"] += 1
        
        category_stats[category]["details"].append({
            "test_id": test_id,
            "expected": expected,
            "predicted": predicted,
            "correct": is_correct
        })
    
    # Calculate accuracy for each category
    category_accuracy = {}
    for category, stats in category_stats.items():
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
        category_accuracy[category] = {
            "correct": stats["correct"],
            "total": stats["total"],
            "accuracy": round(accuracy, 2),
            "details": stats["details"]
        }
    
    return category_accuracy


def generate_ieee_report(comparison_results: Dict[str, Any], output_file: str = None) -> str:
    """Generate IEEE-formatted report from comparison results."""
    
    gemini_results = comparison_results.get("gemini", {})
    openai_results = comparison_results.get("openai", {})
    comparison = comparison_results.get("comparison", {})
    timestamp = comparison_results.get("timestamp", datetime.now().isoformat())
    
    gemini_model = gemini_results.get("model", "gemini-2.5-pro")
    openai_model = openai_results.get("model", "gpt-4o")
    total_tests = comparison_results.get("test_cases_count", 0)
    
    gemini_accuracy = gemini_results.get("accuracy", 0.0)
    openai_accuracy = openai_results.get("accuracy", 0.0)
    gemini_correct = gemini_results.get("correct", 0)
    openai_correct = openai_results.get("correct", 0)
    
    gemini_avg_time = gemini_results.get("avg_time", 0.0)
    openai_avg_time = openai_results.get("avg_time", 0.0)
    
    # Get test cases from results (if available)
    gemini_test_results = gemini_results.get("results", [])
    openai_test_results = openai_results.get("results", [])
    
    # Load test cases to get categories
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from test_cases import TEST_CASES
        test_cases = TEST_CASES[:total_tests] if total_tests else TEST_CASES
    except:
        test_cases = []
    
    # Calculate category-wise accuracy
    gemini_category_acc = calculate_category_accuracy(gemini_test_results, test_cases)
    openai_category_acc = calculate_category_accuracy(openai_test_results, test_cases)
    
    # Generate report
    report = []
    report.append("# Baseline Model Comparison Report - IEEE Format")
    report.append("")
    report.append(f"**Date:** {datetime.fromisoformat(timestamp).strftime('%B %d, %Y')}")
    report.append(f"**Test Suite:** Baseline Comparison (Gemini vs OpenAI)")
    report.append(f"**Total Test Cases:** {total_tests}")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append(f"This report compares the classification accuracy and performance of two baseline models:")
    report.append(f"- **Gemini {gemini_model}**: {gemini_accuracy:.2f}% accuracy ({gemini_correct}/{total_tests} correct)")
    report.append(f"- **OpenAI {openai_model}**: {openai_accuracy:.2f}% accuracy ({openai_correct}/{total_tests} correct)")
    report.append("")
    if comparison.get("gemini_better"):
        report.append(f"**Result:** Gemini outperforms OpenAI by {abs(comparison.get('accuracy_diff', 0)):.2f} percentage points.")
    elif comparison.get("openai_better"):
        report.append(f"**Result:** OpenAI outperforms Gemini by {abs(comparison.get('accuracy_diff', 0)):.2f} percentage points.")
    else:
        report.append("**Result:** Both models achieve identical accuracy.")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## Table I: Overall Performance Comparison")
    report.append("")
    report.append("| Metric | Gemini | OpenAI | Difference |")
    report.append("|--------|--------|--------|------------|")
    report.append(f"| **Accuracy (%)** | {gemini_accuracy:.2f} | {openai_accuracy:.2f} | {comparison.get('accuracy_diff', 0):+.2f} |")
    report.append(f"| **Correct Predictions** | {gemini_correct}/{total_tests} | {openai_correct}/{total_tests} | {gemini_correct - openai_correct:+d} |")
    report.append(f"| **Average Response Time (s)** | {gemini_avg_time:.2f} | {openai_avg_time:.2f} | {comparison.get('time_diff', 0):+.2f} |")
    report.append("")
    
    # Category-wise comparison
    if gemini_category_acc or openai_category_acc:
        report.append("## Table II: Category-Wise Accuracy Comparison")
        report.append("")
        report.append("| Category | Gemini Accuracy (%) | OpenAI Accuracy (%) | Difference |")
        report.append("|----------|---------------------|---------------------|------------|")
        
        # Get all unique categories
        all_categories = set(gemini_category_acc.keys()) | set(openai_category_acc.keys())
        
        # Map category names to display names
        category_display = {
            "Broken Access Control": "A01 - Broken Access Control",
            "Cryptographic Failures": "A04 - Cryptographic Failures",
            "Injection": "A05 - Injection",
            "Authentication Failures": "A07 - Authentication Failures",
            "Security Misconfiguration": "A02 - Security Misconfiguration",
            "Other": "Other"
        }
        
        for category in sorted(all_categories):
            gemini_acc = gemini_category_acc.get(category, {}).get("accuracy", 0.0)
            openai_acc = openai_category_acc.get(category, {}).get("accuracy", 0.0)
            diff = gemini_acc - openai_acc
            display_name = category_display.get(category, category)
            report.append(f"| {display_name} | {gemini_acc:.2f} | {openai_acc:.2f} | {diff:+.2f} |")
        
        report.append("")
    
    # Detailed results table
    report.append("## Table III: Sample Test Case Results")
    report.append("")
    report.append("| Case ID | Expected | Gemini Prediction | OpenAI Prediction | Gemini Correct | OpenAI Correct |")
    report.append("|---------|----------|-------------------|-------------------|----------------|----------------|")
    
    # Show first 20 results or all if less than 20
    sample_size = min(20, len(gemini_test_results))
    for i in range(sample_size):
        gemini_result = gemini_test_results[i]
        openai_result = openai_test_results[i] if i < len(openai_test_results) else {}
        
        test_id = gemini_result.get("test_id", "")
        expected = gemini_result.get("expected_normalized", "")
        gemini_pred = gemini_result.get("predicted_normalized", "")
        openai_pred = openai_result.get("predicted_normalized", "")
        gemini_correct = "✓" if gemini_result.get("correct", False) else "✗"
        openai_correct = "✓" if openai_result.get("correct", False) else "✗"
        
        report.append(f"| {test_id} | {expected} | {gemini_pred} | {openai_pred} | {gemini_correct} | {openai_correct} |")
    
    if len(gemini_test_results) > sample_size:
        report.append(f"| ... | ... | ... | ... | ... | ... |")
        report.append(f"| *(Total: {len(gemini_test_results)} cases)* | | | | | |")
    
    report.append("")
    
    # Performance analysis
    report.append("## Table IV: Performance Metrics")
    report.append("")
    report.append("| Metric | Gemini | OpenAI | Winner |")
    report.append("|--------|--------|--------|--------|")
    
    # Accuracy winner
    if gemini_accuracy > openai_accuracy:
        acc_winner = "Gemini"
    elif openai_accuracy > gemini_accuracy:
        acc_winner = "OpenAI"
    else:
        acc_winner = "Tie"
    report.append(f"| **Accuracy** | {gemini_accuracy:.2f}% | {openai_accuracy:.2f}% | {acc_winner} |")
    
    # Speed winner
    if gemini_avg_time < openai_avg_time:
        speed_winner = "Gemini"
    elif openai_avg_time < gemini_avg_time:
        speed_winner = "OpenAI"
    else:
        speed_winner = "Tie"
    report.append(f"| **Average Response Time** | {gemini_avg_time:.2f}s | {openai_avg_time:.2f}s | {speed_winner} |")
    
    # Calculate category wins
    gemini_category_wins = sum(1 for cat in all_categories 
                              if gemini_category_acc.get(cat, {}).get("accuracy", 0) > 
                                 openai_category_acc.get(cat, {}).get("accuracy", 0))
    openai_category_wins = sum(1 for cat in all_categories 
                               if openai_category_acc.get(cat, {}).get("accuracy", 0) > 
                                  gemini_category_acc.get(cat, {}).get("accuracy", 0))
    
    if gemini_category_wins > openai_category_wins:
        cat_winner = f"Gemini ({gemini_category_wins} categories)"
    elif openai_category_wins > gemini_category_wins:
        cat_winner = f"OpenAI ({openai_category_wins} categories)"
    else:
        cat_winner = "Tie"
    report.append(f"| **Category Wins** | {gemini_category_wins} | {openai_category_wins} | {cat_winner} |")
    
    report.append("")
    
    # Methodology section
    report.append("## Methodology")
    report.append("")
    report.append("### A. Test Configuration")
    report.append("")
    report.append(f"- **Test Cases:** {total_tests} incident descriptions covering OWASP Top 10 2025 categories")
    report.append(f"- **Gemini Model:** {gemini_model}")
    report.append(f"- **OpenAI Model:** {openai_model}")
    report.append("- **Evaluation Metric:** Classification accuracy (exact match on normalized labels)")
    report.append("- **Rate Limiting:** Applied to respect API rate limits")
    report.append("")
    
    report.append("### B. Classification Process")
    report.append("")
    report.append("Both models were tested on identical test cases with the following process:")
    report.append("1. Input: Incident description text")
    report.append("2. Processing: LLM-based classification with OWASP Top 10 2025 context")
    report.append("3. Output: Normalized OWASP category label")
    report.append("4. Evaluation: Exact match comparison with expected labels")
    report.append("")
    
    # Results analysis
    report.append("## Results Analysis")
    report.append("")
    
    if gemini_accuracy > openai_accuracy:
        report.append(f"**Gemini {gemini_model}** demonstrates superior classification accuracy, achieving {gemini_accuracy:.2f}% compared to OpenAI's {openai_accuracy:.2f}%.")
    elif openai_accuracy > gemini_accuracy:
        report.append(f"**OpenAI {openai_model}** demonstrates superior classification accuracy, achieving {openai_accuracy:.2f}% compared to Gemini's {gemini_accuracy:.2f}%.")
    else:
        report.append(f"Both models achieve identical accuracy of {gemini_accuracy:.2f}%.")
    
    report.append("")
    
    # Category analysis
    if gemini_category_acc or openai_category_acc:
        report.append("### Category-Wise Analysis")
        report.append("")
        
        for category in sorted(all_categories):
            gemini_cat = gemini_category_acc.get(category, {})
            openai_cat = openai_category_acc.get(category, {})
            
            gemini_acc = gemini_cat.get("accuracy", 0.0)
            openai_acc = openai_cat.get("accuracy", 0.0)
            gemini_total = gemini_cat.get("total", 0)
            openai_total = openai_cat.get("total", 0)
            
            display_name = category_display.get(category, category)
            report.append(f"- **{display_name}**: Gemini {gemini_acc:.2f}% ({gemini_cat.get('correct', 0)}/{gemini_total}), OpenAI {openai_acc:.2f}% ({openai_cat.get('correct', 0)}/{openai_total})")
        
        report.append("")
    
    # Performance analysis
    report.append("### Performance Analysis")
    report.append("")
    if gemini_avg_time < openai_avg_time:
        report.append(f"Gemini demonstrates faster response times ({gemini_avg_time:.2f}s vs {openai_avg_time:.2f}s), providing a {((openai_avg_time - gemini_avg_time) / openai_avg_time * 100):.1f}% speed improvement.")
    elif openai_avg_time < gemini_avg_time:
        report.append(f"OpenAI demonstrates faster response times ({openai_avg_time:.2f}s vs {gemini_avg_time:.2f}s), providing a {((gemini_avg_time - openai_avg_time) / gemini_avg_time * 100):.1f}% speed improvement.")
    else:
        report.append(f"Both models demonstrate similar response times ({gemini_avg_time:.2f}s).")
    report.append("")
    
    # Conclusion
    report.append("## Conclusion")
    report.append("")
    report.append("This baseline comparison provides empirical evidence for model selection in production deployment.")
    if gemini_accuracy > openai_accuracy:
        report.append(f"Based on accuracy metrics, **Gemini {gemini_model}** is recommended as the primary model.")
    elif openai_accuracy > gemini_accuracy:
        report.append(f"Based on accuracy metrics, **OpenAI {openai_model}** is recommended as the primary model.")
    else:
        report.append("Both models demonstrate equivalent accuracy, allowing selection based on other factors (cost, latency, availability).")
    report.append("")
    report.append("---")
    report.append("")
    report.append("**Note:** This report is generated automatically from baseline comparison test results.")
    report.append("For detailed results, refer to the JSON output file.")
    
    report_text = "\n".join(report)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"✅ IEEE report saved to {output_file}")
    
    return report_text


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate IEEE-formatted baseline comparison report")
    parser.add_argument("input", help="Input JSON file with comparison results")
    parser.add_argument("-o", "--output", help="Output markdown file (default: reports/IEEE_Baseline_Comparison.md)")
    
    args = parser.parse_args()
    
    # Load results
    print(f"Loading comparison results from {args.input}...")
    comparison_results = load_comparison_results(args.input)
    
    # Generate report
    print("Generating IEEE-formatted report...")
    output_file = args.output or "reports/IEEE_Baseline_Comparison.md"
    
    # Ensure reports directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    report = generate_ieee_report(comparison_results, output_file)
    
    print(f"\n✅ Report generated successfully!")
    print(f"📄 Output: {output_file}")
    print(f"\nPreview (first 500 chars):")
    print("-" * 60)
    print(report[:500] + "...")
    print("-" * 60)


if __name__ == "__main__":
    main()

