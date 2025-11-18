# IEEE-Format Visualizations Guide

## Overview

Both visualizations have been updated to meet IEEE paper standards with professional styling, proper fonts, and high-quality output.

---

## Generated Files

### 1. Category Accuracy Chart
**File:** `reports/accuracy_by_category_ieee.png`

**IEEE Features:**
- ✅ **Serif fonts** (Times New Roman) for professional academic look
- ✅ **Clean layout** with removed top/right spines
- ✅ **High contrast** colors (blue, green, orange, red) that work in grayscale
- ✅ **Clear labels** with full OWASP category names
- ✅ **Value labels** on each bar showing exact percentages
- ✅ **Reference lines** at 80% and 95% thresholds
- ✅ **300 DPI** resolution for publication quality
- ✅ **Proper sizing** (8×5 inches) for IEEE paper columns

**What it shows:**
- Accuracy by OWASP Top 10:2025 category
- A01: 92.3% (12/13)
- A04: 100.0% (12/12)
- A05: 100.0% (13/13)
- A07: 100.0% (12/12)

---

### 2. Overall Accuracy Gauge
**File:** `reports/overall_accuracy_gauge_ieee.png`

**IEEE Features:**
- ✅ **Serif fonts** (Times New Roman) throughout
- ✅ **Professional color scheme** (light pastels, grayscale-friendly)
- ✅ **Clear tick marks** at 0%, 25%, 50%, 75%, 100%
- ✅ **Bold accuracy display** (98.0%) in large, readable font
- ✅ **Test details** showing 49/50 correct cases
- ✅ **Model information** (Gemini 2.5 Pro) included
- ✅ **300 DPI** resolution
- ✅ **Proper sizing** (8×6 inches)

**What it shows:**
- Overall accuracy: 98.0%
- Test cases: 49/50 correct
- Model: Gemini 2.5 Pro

---

## IEEE Format Compliance

### Typography
- **Font Family:** Times New Roman (serif)
- **Font Sizes:** 
  - Main text: 11pt
  - Labels: 12pt
  - Titles: 13-14pt
  - Large numbers: 42pt (gauge)

### Colors
- **Grayscale-friendly:** Colors chosen to be distinguishable when printed in black & white
- **High contrast:** Black text on light backgrounds
- **Professional palette:** Blue, green, orange, red (standard academic colors)

### Layout
- **Clean borders:** Removed unnecessary spines
- **Grid lines:** Subtle, non-intrusive
- **Spacing:** Proper margins and padding
- **Aspect ratio:** Optimized for IEEE paper columns

### Quality
- **Resolution:** 300 DPI (publication quality)
- **Format:** PNG (lossless)
- **Size:** Optimized for IEEE paper dimensions

---

## Usage in IEEE Paper

### Figure Captions (Suggested)

**Figure 1:**
```
Classification accuracy by OWASP Top 10:2025 category. The system achieves 
100% accuracy on A04 (Cryptographic Failures), A05 (Injection), and A07 
(Authentication Failures), with 92.3% accuracy on A01 (Broken Access Control).
```

**Figure 2:**
```
Overall classification accuracy of 98.0% (49/50 test cases) using Gemini 2.5 Pro. 
The gauge shows performance across 50 hard test cases covering four primary 
OWASP categories.
```

### In LaTeX

```latex
\begin{figure}[!t]
\centering
\includegraphics[width=0.48\textwidth]{accuracy_by_category_ieee.png}
\caption{Classification accuracy by OWASP Top 10:2025 category.}
\label{fig:category_accuracy}
\end{figure}

\begin{figure}[!t]
\centering
\includegraphics[width=0.48\textwidth]{overall_accuracy_gauge_ieee.png}
\caption{Overall classification accuracy: 98.0\% (49/50 test cases).}
\label{fig:overall_accuracy}
\end{figure}
```

---

## Comparison: Before vs After

### Before (Original)
- Sans-serif fonts
- Bright, saturated colors
- No reference lines
- Less professional appearance

### After (IEEE Format)
- ✅ Serif fonts (Times New Roman)
- ✅ Professional color palette
- ✅ Reference lines and tick marks
- ✅ Clean, academic appearance
- ✅ Publication-ready quality

---

## Technical Details

### Chart Specifications
- **DPI:** 300 (high resolution)
- **Format:** PNG (lossless)
- **Color Space:** RGB
- **Dimensions:** 
  - Bar chart: 8×5 inches
  - Gauge: 8×6 inches

### Font Settings
```python
'font.family': 'serif'
'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif']
'font.size': 11
'axes.labelsize': 12
'axes.titlesize': 13
```

---

## Files Location

All IEEE-format visualizations are saved in:
- `reports/accuracy_by_category_ieee.png`
- `reports/overall_accuracy_gauge_ieee.png`

Original versions (if needed):
- `reports/accuracy_by_category.png`
- `reports/overall_accuracy_gauge.png`

---

## Regenerating Visualizations

To regenerate IEEE-format visualizations:

```bash
python scripts/visualize_accuracy_results.py reports/accuracy_results_all_50_20251118_152137.json
```

This will create both IEEE-format charts automatically.

---

**Status:** ✅ Ready for IEEE paper submission

