"""
Visualize Accuracy Test Results
================================

Creates visualizations from accuracy test JSON results.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Try to import matplotlib, fallback if not available
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib not installed. Install with: pip install matplotlib numpy")
    print("   Generating text-based report instead...")


def load_results(json_file: str) -> Dict[str, Any]:
    """Load test results from JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)


def create_category_accuracy_chart(results: Dict[str, Any], output_file: str = None):
    """Create IEEE-style bar chart showing accuracy by category."""
    if not MATPLOTLIB_AVAILABLE:
        return create_text_report(results)
    
    categories = []
    accuracies = []
    
    # Handle different JSON structures
    if "summary" in results:
        category_data = results["summary"].get("by_category", {})
    else:
        category_data = results.get("by_category", {})
    
    # Map category codes to full names for IEEE format
    category_names = {
        "A01": "A01: Broken\nAccess Control",
        "A04": "A04: Cryptographic\nFailures",
        "A05": "A05: Injection",
        "A07": "A07: Authentication\nFailures"
    }
    
    for cat, data in sorted(category_data.items()):
        if data.get("total", 0) > 0:
            categories.append(category_names.get(cat, cat))
            accuracy = (data.get("correct", 0) / data.get("total", 1)) * 100
            accuracies.append(accuracy)
    
    # IEEE-style figure: clean, professional, high contrast
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14,
        'axes.linewidth': 1.0,
        'grid.linewidth': 0.5,
        'lines.linewidth': 1.5,
        'patch.linewidth': 0.5
    })
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Use grayscale-friendly colors with patterns for IEEE
    # Blue gradient for professional look
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']
    if len(accuracies) > len(colors):
        colors = colors * (len(accuracies) // len(colors) + 1)
    colors = colors[:len(accuracies)]
    
    bars = ax.bar(categories, accuracies, color=colors, alpha=0.85, 
                   edgecolor='black', linewidth=1.0, width=0.6)
    
    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('OWASP Top 10:2025 Category', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.set_yticks(range(0, 111, 10))
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Add reference lines
    ax.axhline(y=95, color='gray', linestyle=':', alpha=0.5, linewidth=1.0)
    ax.axhline(y=80, color='gray', linestyle=':', alpha=0.5, linewidth=1.0)
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.0)
    ax.spines['bottom'].set_linewidth(1.0)
    
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', format='png')
        print(f"[OK] IEEE chart saved to {output_file}")
    else:
        plt.savefig('reports/accuracy_by_category_ieee.png', dpi=300, bbox_inches='tight', format='png')
        print("[OK] IEEE chart saved to reports/accuracy_by_category_ieee.png")
    
    plt.close()


def create_overall_accuracy_gauge(results: Dict[str, Any], output_file: str = None):
    """Create IEEE-style gauge chart for overall accuracy."""
    if not MATPLOTLIB_AVAILABLE:
        return
    
    # Handle different JSON structures
    if "summary" in results:
        summary = results["summary"]
        accuracy = summary.get("overall_accuracy", 0.0)
        correct = summary.get("total_correct", 0)
        total = summary.get("total_tests", 0)
    else:
        overall = results.get("overall", {})
        accuracy = overall.get("accuracy", 0.0)
        correct = overall.get("correct", 0)
        total = overall.get("total", 0)
    
    # IEEE-style figure settings
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14
    })
    
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
    
    # Create gauge with IEEE-style colors (grayscale-friendly)
    theta = np.linspace(0, np.pi, 100)
    r = np.ones_like(theta)
    
    # Color zones with professional colors
    colors = []
    for t in theta:
        angle_deg = np.degrees(t)
        if angle_deg <= 60:  # 0-60% = light red
            colors.append('#ffcccc')
        elif angle_deg <= 80:  # 60-80% = light orange
            colors.append('#ffe6cc')
        else:  # 80-100% = light green
            colors.append('#ccffcc')
    
    ax.bar(theta, r, width=np.pi/100, color=colors, alpha=0.4, edgecolor='none')
    
    # Draw accuracy indicator line (thick black for visibility)
    accuracy_angle = (accuracy / 100) * np.pi
    ax.plot([accuracy_angle, accuracy_angle], [0, 1.05], 'k-', linewidth=3.5, label='Accuracy')
    ax.plot([accuracy_angle, accuracy_angle], [0, 1.05], 'w-', linewidth=1.5)
    
    # Add tick marks at 0, 25, 50, 75, 100
    for tick_val in [0, 25, 50, 75, 100]:
        tick_angle = (tick_val / 100) * np.pi
        ax.plot([tick_angle, tick_angle], [0.95, 1.05], 'k-', linewidth=1.5)
        ax.text(tick_angle, 1.15, f'{tick_val}%', ha='center', va='center',
                fontsize=9, fontweight='bold')
    
    # Add main accuracy text (large and bold)
    ax.text(0, 0.35, f'{accuracy:.1f}%', ha='center', va='center', 
            fontsize=42, fontweight='bold', color='black',
            family='serif')
    
    # Add subtitle with test details
    ax.text(0, 0.15, f'{correct}/{total} test cases', ha='center', va='center',
            fontsize=14, color='#333333', family='serif')
    
    # Add model info
    ax.text(0, 0.05, 'Gemini 2.5 Pro', ha='center', va='center',
            fontsize=11, color='#666666', style='italic', family='serif')
    
    ax.set_ylim(0, 1.3)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', format='png')
        print(f"[OK] IEEE gauge chart saved to {output_file}")
    else:
        plt.savefig('reports/overall_accuracy_gauge_ieee.png', dpi=300, bbox_inches='tight', format='png')
        print("[OK] IEEE gauge chart saved to reports/overall_accuracy_gauge_ieee.png")
    
    plt.close()


def create_comparison_chart(gemini_results: Dict[str, Any], openai_results: Dict[str, Any] = None, output_file: str = None):
    """Create IEEE-style comparison chart between Gemini and OpenAI."""
    if not MATPLOTLIB_AVAILABLE:
        return
    
    if not openai_results:
        return
    
    categories = []
    gemini_acc = []
    openai_acc = []
    
    # Handle different JSON structures
    if "summary" in gemini_results:
        gemini_cats = gemini_results["summary"].get("by_category", {})
    else:
        gemini_cats = gemini_results.get("by_category", {})
    
    if "summary" in openai_results:
        openai_cats = openai_results["summary"].get("by_category", {})
    else:
        openai_cats = openai_results.get("by_category", {})
    
    # Map category codes to full names for IEEE format
    category_names = {
        "A01": "A01: Broken\nAccess Control",
        "A04": "A04: Cryptographic\nFailures",
        "A05": "A05: Injection",
        "A07": "A07: Authentication\nFailures"
    }
    
    all_cats = set(gemini_cats.keys()) | set(openai_cats.keys())
    
    for cat in sorted(all_cats):
        if gemini_cats.get(cat, {}).get("total", 0) > 0:
            categories.append(category_names.get(cat, cat))
            gemini_accuracy = (gemini_cats[cat].get("correct", 0) / gemini_cats[cat].get("total", 1)) * 100
            gemini_acc.append(gemini_accuracy)
            
            if openai_cats.get(cat):
                openai_accuracy = (openai_cats[cat].get("correct", 0) / openai_cats[cat].get("total", 1)) * 100
                openai_acc.append(openai_accuracy)
            else:
                openai_acc.append(0)
    
    # IEEE-style figure settings
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14,
        'axes.linewidth': 1.0,
        'grid.linewidth': 0.5,
        'lines.linewidth': 1.5,
        'patch.linewidth': 0.5
    })
    
    x = np.arange(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # IEEE-style colors (professional, grayscale-friendly)
    bars1 = ax.bar(x - width/2, gemini_acc, width, label='Gemini 2.5 Pro', 
                   color='#1f77b4', alpha=0.85, edgecolor='black', linewidth=1.0)
    bars2 = ax.bar(x + width/2, openai_acc, width, label='OpenAI GPT-4o', 
                   color='#ff7f0e', alpha=0.85, edgecolor='black', linewidth=1.0)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('OWASP Top 10:2025 Category', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=0, ha='center')
    ax.legend(loc='upper right', fontsize=10, frameon=True, fancybox=False, edgecolor='black')
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_ylim(0, 110)
    ax.set_yticks(range(0, 111, 10))
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.0)
    ax.spines['bottom'].set_linewidth(1.0)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', format='png')
        print(f"[OK] IEEE comparison chart saved to {output_file}")
    else:
        plt.savefig('reports/baseline_comparison_chart_ieee.png', dpi=300, bbox_inches='tight', format='png')
        print("[OK] IEEE comparison chart saved to reports/baseline_comparison_chart_ieee.png")
    
    plt.close()


def create_text_report(results: Dict[str, Any]) -> str:
    """Create text-based report if matplotlib not available."""
    report = []
    report.append("=" * 70)
    report.append("ACCURACY TEST RESULTS - TEXT REPORT")
    report.append("=" * 70)
    report.append("")
    
    overall = results.get("overall", {})
    report.append(f"Overall Accuracy: {overall.get('accuracy', 0):.2f}%")
    report.append(f"Correct: {overall.get('correct', 0)}/{overall.get('total', 0)}")
    report.append("")
    
    report.append("Category-Wise Results:")
    report.append("-" * 70)
    
    category_data = results.get("by_category", {})
    for cat, data in sorted(category_data.items()):
        if data.get("total", 0) > 0:
            accuracy = (data.get("correct", 0) / data.get("total", 1)) * 100
            report.append(f"{cat:30s} {accuracy:6.2f}% ({data.get('correct', 0)}/{data.get('total', 0)})")
    
    report.append("")
    report.append("=" * 70)
    
    report_text = "\n".join(report)
    print(report_text)
    
    # Save to file
    output_file = 'reports/accuracy_text_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"\n[OK] Text report saved to {output_file}")
    
    return report_text


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize accuracy test results")
    parser.add_argument("input", help="Input JSON file with test results")
    parser.add_argument("--baseline", help="Baseline (OpenAI) results JSON file for comparison")
    parser.add_argument("--output-dir", default="reports", help="Output directory for charts")
    
    args = parser.parse_args()
    
    # Load results
    print(f"Loading results from {args.input}...")
    results = load_results(args.input)
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    print("\nGenerating IEEE-format visualizations...")
    
    # Category accuracy chart (IEEE format)
    create_category_accuracy_chart(results, f"{args.output_dir}/accuracy_by_category_ieee.png")
    
    # Overall accuracy gauge (IEEE format)
    create_overall_accuracy_gauge(results, f"{args.output_dir}/overall_accuracy_gauge_ieee.png")
    
    # Comparison chart if baseline provided
    if args.baseline:
        print(f"Loading baseline results from {args.baseline}...")
        baseline_results = load_results(args.baseline)
        create_comparison_chart(results, baseline_results, f"{args.output_dir}/baseline_comparison_chart.png")
    
    print("\n[OK] All visualizations generated!")


if __name__ == "__main__":
    main()

