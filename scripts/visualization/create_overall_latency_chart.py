"""
Create Overall System Latency Graph (IEEE Format - Improved)
============================================================

Generates IEEE-compliant line graph showing overall system latency (end-to-end).
Enhanced with better formatting, clearer presentation, and professional appearance.
"""

import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

# IEEE style settings - strict compliance
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0
plt.rcParams['xtick.minor.width'] = 0.5
plt.rcParams['ytick.minor.width'] = 0.5

# Find latest overall latency data file (exclude summary files)
project_root = Path(__file__).parent.parent.parent
reports_dir = project_root / "reports"
latency_files = sorted([f for f in reports_dir.glob("overall_latency_*.json")
                       if "summary" not in f.name], reverse=True)

if not latency_files:
    print("[ERROR] No overall latency measurement files found.")
    print("        Run scripts/measure_overall_latency.py first.")
    exit(1)

# Load data
data_file = latency_files[0]
print(f"[INFO] Loading data from {data_file.name}")

with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Handle different data formats
# If it's a list of measurements, take first 10 unique test cases
# If it's improved format with multiple runs, take first 10 test cases (first run of each)
total_latencies = []
seen_test_cases = set()

for d in data:
    if not isinstance(d, dict):
        continue
    
    # Check if this is a test case we've seen
    test_case = d.get("test_case", None)
    if test_case is not None:
        if test_case in seen_test_cases:
            continue  # Skip if we already have this test case
        seen_test_cases.add(test_case)
    
    latency = d.get("total_latency_ms", 0)
    if latency > 0:
        total_latencies.append(latency)
        if len(total_latencies) >= 10:
            break  # We have 10 points

# If we have less than 10, pad or use what we have
if len(total_latencies) < 10:
    print(f"[WARNING] Only found {len(total_latencies)} valid data points, using all available")
    if len(total_latencies) == 0:
        print(f"[ERROR] No valid latency data found")
        exit(1)

# Calculate statistics (verify correctness)
avg_latency = np.mean(total_latencies)
min_latency = np.min(total_latencies)
max_latency = np.max(total_latencies)
std_latency = np.std(total_latencies)
median_latency = np.median(total_latencies)

print(f"[INFO] Data validation:")
print(f"  Average: {avg_latency:.2f} ms")
print(f"  Min: {min_latency:.2f} ms")
print(f"  Max: {max_latency:.2f} ms")
print(f"  Std Dev: {std_latency:.2f} ms")
print(f"  Median: {median_latency:.2f} ms")

# Create figure with proper IEEE dimensions
# IEEE figures typically: 3.5" (single column) or 7" (double column)
fig, ax = plt.subplots(figsize=(7.5, 5))  # Slightly wider for better readability

# Plot line graph
x = np.arange(1, 11)  # Test cases 1-10

# Use IEEE-friendly colors (works in grayscale)
# Blue line with black markers for B&W printing compatibility
line = ax.plot(x, total_latencies, marker='o', markersize=9, linewidth=2.5, 
               color='#0066CC', markerfacecolor='#0066CC', markeredgecolor='black', 
               markeredgewidth=1.5, label='System Latency', zorder=3, clip_on=False)

# Calculate Y-axis limits with proper padding for labels
y_range = max_latency - min_latency if max_latency > min_latency else max_latency
y_min_plot = max(0, int(min_latency - (y_range * 0.05))) if y_range > 0 else 0
y_max_plot = int(max_latency + (y_range * 0.30)) if y_range > 0 else int(max_latency * 1.30)

# Add value labels on points (with bounds checking)
label_offset = y_range * 0.08 if y_range > 0 else 5
for i, (xi, val) in enumerate(zip(x, total_latencies)):
    # Position label above point, ensure it stays within bounds
    label_y = min(val + label_offset, y_max_plot * 0.98)  # Don't exceed plot area
    ax.text(xi, label_y, f'{val:.0f}', ha='center', va='bottom', 
            fontsize=9, fontweight='normal', family='Times New Roman')

# Add average line (dashed, red - standard for reference lines)
avg_line = ax.axhline(y=avg_latency, color='#CC0000', linestyle='--', linewidth=2, 
           alpha=0.85, label=f'Mean: {avg_latency:.0f} ms', zorder=2)

# Add standard deviation bands (optional, for better visualization)
ax.fill_between([0.5, 10.5], avg_latency - std_latency, avg_latency + std_latency,
                alpha=0.15, color='gray', zorder=1, label=f'±1 Std Dev')

# Customize axes - IEEE standards
ax.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold', labelpad=8)
ax.set_xlabel('Test Case', fontsize=12, fontweight='bold', labelpad=8)
ax.set_title('Overall System Latency Performance', 
             fontsize=13, fontweight='bold', pad=18)

# Set x-axis ticks - cleaner formatting
ax.set_xticks(x)
ax.set_xticklabels([f'{i}' for i in x], fontsize=10)
ax.set_xlim(0.5, 10.5)

# Set y-axis with proper range and ticks (using calculated values)
ax.set_ylim(y_min_plot, y_max_plot)

# Smart y-axis ticks - every 25 ms up to 250, then adjust
if y_max_plot <= 250:
    y_ticks = np.arange(0, y_max_plot + 1, 25)
else:
    y_ticks = np.arange(0, y_max_plot + 1, 50)
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{int(t)}' for t in y_ticks], fontsize=10)

# Grid - subtle, IEEE style
ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, axis='both', zorder=1)
ax.set_axisbelow(True)

# Legend - IEEE style (top right, simple frame, positioned to avoid overflow)
legend = ax.legend(loc='upper right', frameon=True, fancybox=False, 
          edgecolor='black', fontsize=10, framealpha=0.95, 
          handlelength=2.5, handletextpad=0.5,
          bbox_to_anchor=(0.98, 0.98))  # Slightly inside to avoid edge
legend.get_frame().set_linewidth(0.8)
legend.get_frame().set_facecolor('white')

# Add statistics in text box (IEEE style - simple, clear)
stats_text = f'Mean: {avg_latency:.0f} ms\n'
stats_text += f'Min: {min_latency:.0f} ms\n'
stats_text += f'Max: {max_latency:.0f} ms\n'
stats_text += f'Std Dev: {std_latency:.0f} ms\n'
stats_text += f'Median: {median_latency:.0f} ms'

# Position stats box (top left, simple style, zorder to ensure visibility)
stats_box = ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
        fontsize=10, verticalalignment='top', family='Times New Roman',
        bbox=dict(boxstyle='round,pad=0.6', facecolor='white', 
                  alpha=0.95, edgecolor='black', linewidth=1.2),
        zorder=10)  # Ensure it's on top

# Add annotation for outlier (Test Case 7)
if max_latency > avg_latency + 2 * std_latency:
    max_idx = np.argmax(total_latencies) + 1
    ax.annotate('Outlier', xy=(max_idx, max_latency), 
                xytext=(max_idx + 0.5, max_latency - 20),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.2, alpha=0.7),
                fontsize=9, fontweight='bold', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7, edgecolor='black'))

# Ensure proper spacing (increased padding to prevent overflow)
plt.tight_layout(pad=3.0)

# Save with high quality
output_dir = reports_dir / "visualizations"
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "overall_latency_graph_ieee.png"
plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print(f"[OK] Improved IEEE-compliant graph saved to {output_file}")

# Validate and save summary with statistics
summary = {
    "test_cases": len(total_latencies),
    "statistics": {
        "mean_ms": float(avg_latency),
        "mean_seconds": float(avg_latency / 1000),
        "min_ms": float(min_latency),
        "max_ms": float(max_latency),
        "std_dev_ms": float(std_latency),
        "median_ms": float(median_latency),
        "range_ms": float(max_latency - min_latency),
        "coefficient_of_variation": float(std_latency / avg_latency * 100)
    },
    "data_points": [
        {
            "test_case": i+1,
            "total_latency_ms": float(total_latencies[i]),
            "total_latency_seconds": float(total_latencies[i] / 1000)
        }
        for i in range(len(total_latencies))
    ],
    "validation": {
        "data_points_count": len(total_latencies),
        "expected_count": 10,
        "all_valid": all(l > 0 for l in total_latencies),
        "mean_calculated": float(avg_latency),
        "std_calculated": float(std_latency),
        "outlier_detected": bool(max_latency > avg_latency + 2 * std_latency)
    }
}

summary_file = output_dir / "overall_latency_summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"[OK] Summary with validation saved to {summary_file}")

# Print validation results
print(f"\n[VALIDATION]")
print(f"  Data points: {len(total_latencies)}/10")
print(f"  All values > 0: {all(l > 0 for l in total_latencies)}")
print(f"  Mean: {avg_latency:.2f} ms")
print(f"  Std Dev: {std_latency:.2f} ms")
print(f"  Range: {max_latency - min_latency:.2f} ms")
print(f"  Coefficient of Variation: {std_latency/avg_latency*100:.1f}%")
print(f"  Outlier detected: {max_latency > avg_latency + 2 * std_latency}")
print(f"  [OK] Graph improved and IEEE-compliant")

plt.close()
