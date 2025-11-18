"""
Visualize LLM Baseline Comparison
=================================

Creates IEEE-format visualizations comparing:
- Gemini 2.5 Pro (Your System)
- Baseline LLM (Claude or OpenAI)
"""

import json
import sys
import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# IEEE style settings
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'


def load_comparison_data(json_file: str) -> dict:
    """Load comparison results from JSON."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_comparison_bar_chart(comparison: dict, output_file: str):
    """Create line graph comparing accuracy metrics."""
    
    primary = comparison["primary_model"]["results"]
    baseline = comparison["baseline_model"]["results"]
    baseline_name = comparison["baseline_model"]["name"]
    
    # Data
    metrics = ["Single-Incident\nAccuracy", "Ambiguous Case\nAccuracy", "Overall\nAccuracy"]
    gemini_values = [
        primary.get("single_accuracy", 0),
        primary.get("ambiguous_accuracy", 0),
        primary.get("overall_accuracy", 0)
    ]
    baseline_values = [
        baseline.get("single_accuracy", 0),
        baseline.get("ambiguous_accuracy", 0),
        baseline.get("overall_accuracy", 0)
    ]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x = np.arange(1, len(metrics) + 1)
    
    # Plot lines with markers
    line1 = ax.plot(x, gemini_values, marker='o', markersize=10, linewidth=2.5,
                    color='#2E86AB', markerfacecolor='#2E86AB', markeredgecolor='black',
                    markeredgewidth=1.5, label='Gemini 2.5 Pro (Proposed)', zorder=3)
    
    line2 = ax.plot(x, baseline_values, marker='s', markersize=10, linewidth=2.5,
                    color='#A23B72', markerfacecolor='#A23B72', markeredgecolor='black',
                    markeredgewidth=1.5, label=baseline_name + ' (Baseline)', zorder=3)
    
    # Add value labels
    for i, (xi, g_val, b_val) in enumerate(zip(x, gemini_values, baseline_values)):
        ax.text(xi, g_val + 2, f'{g_val:.1f}%', ha='center', va='bottom', fontsize=9)
        ax.text(xi, b_val - 3, f'{b_val:.1f}%', ha='center', va='top', fontsize=9)
    
    # Customize
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_xlabel('Metric', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_title('Model Comparison: Classification Accuracy', fontsize=13, fontweight='bold', pad=18)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylim(0, 105)
    ax.set_yticks(np.arange(0, 105, 10))
    ax.legend(loc='upper left', frameon=True, fancybox=False, edgecolor='black', fontsize=10, framealpha=0.95)
    ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, axis='both', zorder=1)
    ax.set_axisbelow(True)
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    
    # Add reference line at 50%
    ax.axhline(y=50, color='gray', linestyle=':', linewidth=0.8, alpha=0.5, zorder=2)
    
    plt.tight_layout(pad=2.5)
    plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"[OK] Line chart saved to {output_file}")
    plt.close()


def create_category_comparison_chart(comparison: dict, output_file: str):
    """Create category-wise comparison chart."""
    
    primary = comparison["primary_model"]["results"]
    baseline = comparison["baseline_model"]["results"]
    baseline_name = comparison["baseline_model"]["name"]
    
    # Calculate category accuracy from detailed results
    categories = {
        "A01": {"primary": {"correct": 0, "total": 0}, "baseline": {"correct": 0, "total": 0}},
        "A04": {"primary": {"correct": 0, "total": 0}, "baseline": {"correct": 0, "total": 0}},
        "A05": {"primary": {"correct": 0, "total": 0}, "baseline": {"correct": 0, "total": 0}},
        "A07": {"primary": {"correct": 0, "total": 0}, "baseline": {"correct": 0, "total": 0}}
    }
    
    # Map expected labels to categories
    label_to_cat = {
        "broken_access_control": "A01",
        "cryptographic_failures": "A04",
        "injection": "A05",
        "broken_authentication": "A07"
    }
    
    # Count from detailed results
    for result in primary.get("detailed_results", []):
        if result.get("correct") and "expected" in result:
            cat = label_to_cat.get(result["expected"], None)
            if cat:
                categories[cat]["primary"]["total"] += 1
                if result.get("correct"):
                    categories[cat]["primary"]["correct"] += 1
    
    for result in baseline.get("detailed_results", []):
        if result.get("correct") and "expected" in result:
            cat = label_to_cat.get(result["expected"], None)
            if cat:
                categories[cat]["baseline"]["total"] += 1
                if result.get("correct"):
                    categories[cat]["baseline"]["correct"] += 1
    
    # Calculate accuracies
    cat_names = []
    primary_accs = []
    baseline_accs = []
    
    for cat, data in categories.items():
        if data["primary"]["total"] > 0:
            cat_names.append(cat)
            primary_acc = (data["primary"]["correct"] / data["primary"]["total"]) * 100
            baseline_acc = (data["baseline"]["correct"] / data["baseline"]["total"]) * 100 if data["baseline"]["total"] > 0 else 0
            primary_accs.append(primary_acc)
            baseline_accs.append(baseline_acc)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x = np.arange(1, len(cat_names) + 1)
    
    # Plot lines with markers
    line1 = ax.plot(x, primary_accs, marker='o', markersize=10, linewidth=2.5,
                    color='#2E86AB', markerfacecolor='#2E86AB', markeredgecolor='black',
                    markeredgewidth=1.5, label='Gemini 2.5 Pro', zorder=3)
    
    line2 = ax.plot(x, baseline_accs, marker='s', markersize=10, linewidth=2.5,
                    color='#A23B72', markerfacecolor='#A23B72', markeredgecolor='black',
                    markeredgewidth=1.5, label=baseline_name, zorder=3)
    
    # Add value labels
    for i, (xi, p_val, b_val) in enumerate(zip(x, primary_accs, baseline_accs)):
        ax.text(xi, p_val + 2, f'{p_val:.1f}%', ha='center', va='bottom', fontsize=9)
        ax.text(xi, b_val - 3, f'{b_val:.1f}%', ha='center', va='top', fontsize=9)
    
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_xlabel('OWASP Category', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_title('Category-Wise Accuracy Comparison', fontsize=13, fontweight='bold', pad=18)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_names, fontsize=10)
    ax.set_ylim(0, 105)
    ax.set_yticks(np.arange(0, 105, 10))
    ax.legend(loc='upper left', frameon=True, fancybox=False, edgecolor='black', fontsize=10, framealpha=0.95)
    ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, axis='both', zorder=1)
    ax.set_axisbelow(True)
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    
    plt.tight_layout(pad=2.5)
    plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"[OK] Category line chart saved to {output_file}")
    plt.close()


def create_radar_chart(comparison: dict, output_file: str):
    """Create radar chart comparing multiple metrics."""
    
    primary = comparison["primary_model"]["results"]
    baseline = comparison["baseline_model"]["results"]
    baseline_name = comparison["baseline_model"]["name"]
    
    # Metrics for radar chart
    metrics = ['Single\nIncident', 'Ambiguous\nCase', 'Overall\nAccuracy']
    primary_values = [
        primary.get("single_accuracy", 0) / 100,
        primary.get("ambiguous_accuracy", 0) / 100,
        primary.get("overall_accuracy", 0) / 100
    ]
    baseline_values = [
        baseline.get("single_accuracy", 0) / 100,
        baseline.get("ambiguous_accuracy", 0) / 100,
        baseline.get("overall_accuracy", 0) / 100
    ]
    
    # Number of variables
    N = len(metrics)
    
    # Compute angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the circle
    
    # Add first value to end for closed polygon
    primary_values += primary_values[:1]
    baseline_values += baseline_values[:1]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(projection='polar'))
    
    # Plot
    ax.plot(angles, primary_values, 'o-', linewidth=2, label='Gemini 2.5 Pro', color='#2E86AB')
    ax.fill(angles, primary_values, alpha=0.25, color='#2E86AB')
    
    ax.plot(angles, baseline_values, 'o-', linewidth=2, label=baseline_name, color='#A23B72')
    ax.fill(angles, baseline_values, alpha=0.25, color='#A23B72')
    
    # Customize
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=9)
    ax.grid(True, linestyle='--', linewidth=0.5)
    
    ax.set_title('Model Performance Comparison (Radar Chart)', 
                fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    plt.tight_layout()
    plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
    print(f"[OK] Radar chart saved to {output_file}")
    plt.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Visualize LLM baseline comparison")
    parser.add_argument("input", help="Input JSON file with comparison results")
    parser.add_argument("--output-dir", default="reports", help="Output directory for charts")
    
    args = parser.parse_args()
    
    print(f"Loading comparison data from {args.input}...")
    comparison = load_comparison_data(args.input)
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate all visualizations
    print("\nGenerating visualizations...")
    
    base_name = Path(args.input).stem
    output_vis_dir = Path(args.output_dir) / "visualizations"
    output_vis_dir.mkdir(parents=True, exist_ok=True)
    
    create_comparison_bar_chart(
        comparison,
        str(output_vis_dir / f"{base_name}_bar_chart_ieee.png")
    )
    
    create_category_comparison_chart(
        comparison,
        str(output_vis_dir / f"{base_name}_category_chart_ieee.png")
    )
    
    create_radar_chart(
        comparison,
        str(output_vis_dir / f"{base_name}_radar_chart_ieee.png")
    )
    
    print("\n[OK] All visualizations generated (line graphs)!")
    print(f"Check {output_vis_dir}/ for charts")


if __name__ == "__main__":
    main()

