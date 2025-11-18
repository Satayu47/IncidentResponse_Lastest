"""
Create Latency Graph (IEEE Format)
===================================

Generates IEEE-format latency graph with 10 data points.
"""

import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
import glob

# IEEE style settings
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Find latest latency data file
project_root = Path(__file__).parent.parent.parent
reports_dir = project_root / "reports"
latency_files = sorted(reports_dir.glob("latency_measurements_*.json"), reverse=True)

if not latency_files:
    print("[ERROR] No latency measurement files found.")
    print("        Run scripts/measure_latency.py first.")
    exit(1)

# Load data
data_file = latency_files[0]
print(f"[INFO] Loading data from {data_file.name}")

with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract data points (10 test cases)
test_cases = [f"Case {i+1}" for i in range(len(data))]
total_latencies = [d["total_system_ms"] for d in data]
llm_latencies = [d["llm_classification_ms"] for d in data]
phase2_latencies = [d["phase2_execution_ms"] for d in data]
extraction_latencies = [d["extraction_ms"] for d in data]

# Create figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Chart 1: Total System Latency (Line Graph)
x = np.arange(1, len(test_cases) + 1)  # 1 to 10

# Plot line with markers
line1 = ax1.plot(x, total_latencies, marker='o', markersize=8, linewidth=2.5, 
                 color='#2E86AB', markerfacecolor='#2E86AB', markeredgecolor='black', 
                 markeredgewidth=1.5, label='Total System Latency', zorder=3)

# Add value labels on points
for i, (xi, val) in enumerate(zip(x, total_latencies)):
    ax1.text(xi, val + 15, f'{val:.0f}', ha='center', va='bottom', 
             fontsize=9, fontweight='bold')

ax1.set_ylabel('Latency (ms)', fontsize=11, fontweight='bold')
ax1.set_xlabel('Test Case', fontsize=11, fontweight='bold')
ax1.set_title('Total System Latency Across 10 Test Cases', fontsize=12, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels([f'Case {i}' for i in x], fontsize=9)
ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='both')
ax1.set_axisbelow(True)

# Add average line
avg_latency = np.mean(total_latencies)
ax1.axhline(y=avg_latency, color='red', linestyle='--', linewidth=1.5, 
            alpha=0.7, label=f'Average: {avg_latency:.0f} ms', zorder=2)
ax1.legend(loc='upper right', frameon=True, fancybox=False, edgecolor='black', fontsize=9)

# Chart 2: Component Breakdown (Multiple Lines)
x2 = np.arange(1, len(test_cases) + 1)  # 1 to 10

# Plot multiple lines for each component
line_ext = ax2.plot(x2, extraction_latencies, marker='s', markersize=7, linewidth=2, 
                    color='#A23B72', markerfacecolor='#A23B72', markeredgecolor='black', 
                    markeredgewidth=1.2, label='IOC Extraction', zorder=3)

line_phase2 = ax2.plot(x2, phase2_latencies, marker='^', markersize=7, linewidth=2, 
                      color='#F18F01', markerfacecolor='#F18F01', markeredgecolor='black', 
                      markeredgewidth=1.2, label='Phase-2 Execution', zorder=3)

line_llm = ax2.plot(x2, llm_latencies, marker='D', markersize=7, linewidth=2, 
                    color='#C73E1D', markerfacecolor='#C73E1D', markeredgecolor='black', 
                    markeredgewidth=1.2, label='LLM Classification', zorder=3)

ax2.set_ylabel('Latency (ms)', fontsize=11, fontweight='bold')
ax2.set_xlabel('Test Case', fontsize=11, fontweight='bold')
ax2.set_title('Component Latency Breakdown (10 Test Cases)', fontsize=12, fontweight='bold', pad=15)
ax2.set_xticks(x2)
ax2.set_xticklabels([f'Case {i}' for i in x2], fontsize=9)
ax2.legend(loc='upper left', frameon=True, fancybox=False, edgecolor='black', fontsize=9)
ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='both')
ax2.set_axisbelow(True)

plt.tight_layout()

# Save
output_dir = reports_dir / "visualizations"
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "latency_graph_ieee.png"
plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
print(f"[OK] Latency graph saved to {output_file}")

# Also save summary data
summary = {
    "test_cases": len(data),
    "average_total_latency_ms": float(np.mean(total_latencies)),
    "average_llm_latency_ms": float(np.mean(llm_latencies)),
    "average_phase2_latency_ms": float(np.mean(phase2_latencies)),
    "average_extraction_latency_ms": float(np.mean(extraction_latencies)),
    "min_total_latency_ms": float(np.min(total_latencies)),
    "max_total_latency_ms": float(np.max(total_latencies)),
    "data_points": [
        {
            "test_case": i+1,
            "total_ms": float(total_latencies[i]),
            "llm_ms": float(llm_latencies[i]),
            "phase2_ms": float(phase2_latencies[i]),
            "extraction_ms": float(extraction_latencies[i])
        }
        for i in range(len(data))
    ]
}

summary_file = output_dir / "latency_summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"[OK] Summary saved to {summary_file}")
plt.close()

