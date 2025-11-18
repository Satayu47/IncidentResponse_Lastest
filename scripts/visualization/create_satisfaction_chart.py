"""
Create User Satisfaction Survey Visualization
=============================================

Generates IEEE-format chart for user satisfaction survey results.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# IEEE style settings
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Survey data
questions = [
    'Q1: Ease\nof Use',
    'Q2: Clarity\nof Responses',
    'Q3: Perceived\nAccuracy',
    'Q4: Usefulness of\nClarification',
    'Q5: Overall\nSatisfaction'
]

means = [4.4, 4.2, 4.3, 4.1, 4.3]
std_devs = [0.89, 0.82, 0.87, 0.91, 0.92]

# Create figure
fig, ax = plt.subplots(figsize=(9, 5))

x = np.arange(len(questions))
width = 0.6

# Create bars
bars = ax.bar(x, means, width, color='#2E86AB', edgecolor='black', linewidth=0.5, alpha=0.8)

# Add error bars
ax.errorbar(x, means, yerr=std_devs, fmt='none', color='black', capsize=5, capthick=1, linewidth=1)

# Add value labels on bars
for i, (bar, mean) in enumerate(zip(bars, means)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
           f'{mean:.1f}',
           ha='center', va='bottom', fontsize=10, fontweight='bold')

# Customize
ax.set_ylabel('Mean Score (1-5)', fontsize=11, fontweight='bold')
ax.set_title('User Satisfaction Survey Results (N=50)', fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(questions, fontsize=10)
ax.set_ylim(0, 5.5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.set_yticklabels(['1 (Very Poor)', '2', '3', '4', '5 (Excellent)'], fontsize=9)
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
ax.set_axisbelow(True)

# Add reference line at 4.0 (good threshold)
ax.axhline(y=4.0, color='gray', linestyle=':', linewidth=0.8, alpha=0.5, label='Good (4.0)')
ax.legend(loc='lower right', frameon=True, fancybox=False, edgecolor='black', fontsize=9)

plt.tight_layout()

# Save
output_dir = Path("reports/visualizations")
if output_dir.exists() and not output_dir.is_dir():
    output_dir.unlink()
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "user_satisfaction_survey_ieee.png"
plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
print(f"[OK] Satisfaction chart saved to {output_file}")
plt.close()

