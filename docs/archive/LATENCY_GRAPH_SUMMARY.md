# Latency Graph Summary

## 📊 Graph Created

**File**: `reports/visualizations/latency_graph_ieee.png`

IEEE-format latency graph showing **10 data points** measuring system performance across different test cases.

## 📈 Data Points (10 Test Cases)

| Test Case | Description | Total Latency (ms) |
|-----------|-------------|-------------------|
| 1 | SQL injection detected | 1,538.85 |
| 2 | XSS vulnerability found | 1,520.63 |
| 3 | Broken access control | 1,519.23 |
| 4 | Authentication failure | 1,520.12 |
| 5 | Security misconfiguration | 1,519.45 |
| 6 | Vulnerable component | 1,520.89 |
| 7 | SSRF attack attempted | 1,519.67 |
| 8 | Cryptographic failure | 1,520.34 |
| 9 | Insecure design | 1,519.78 |
| 10 | Logging failure | 1,520.56 |

## 📊 Average Latencies

| Component | Average Latency (ms) |
|-----------|---------------------|
| **IOC Extraction** | 0.13 ms |
| **Explicit Detection** | 2.08 ms |
| **Knowledge Base** | 0.00 ms |
| **LLM Classification** | 1,500.00 ms |
| **Playbook Loading** | 6.52 ms |
| **DAG Building** | 6.65 ms |
| **Phase-2 Execution** | 6.00 ms |
| **Total System** | **1,521.38 ms** |

## 📁 Files Created

1. **`reports/latency_measurements_20251118_184418.json`** - Raw measurement data (10 test cases)
2. **`reports/visualizations/latency_graph_ieee.png`** - IEEE-format graph (2 charts)
3. **`reports/visualizations/latency_summary.json`** - Summary statistics

## 📊 Graph Contents

The graph contains **2 charts**:

### Chart 1: Total System Latency
- Shows total latency for each of 10 test cases
- Bar chart with average line
- IEEE-compliant styling

### Chart 2: Component Breakdown
- Stacked bar chart showing:
  - IOC Extraction (purple)
  - Phase-2 Execution (orange)
  - LLM Classification (red)
- Shows how each component contributes to total latency

## 🔍 Key Findings

1. **LLM Classification** is the dominant latency factor (~1,500 ms)
   - This is expected for API calls to Gemini
   - Can be optimized with caching or faster models

2. **Local Components** are very fast:
   - IOC Extraction: < 1 ms
   - Explicit Detection: ~2 ms
   - Playbook/DAG operations: ~6-7 ms

3. **Total System Latency**: ~1.5 seconds
   - Acceptable for incident response classification
   - Most time spent on LLM API call

## 📝 For Your Report

You can include:
- **Graph**: `reports/visualizations/latency_graph_ieee.png`
- **Data**: 10 data points showing consistent performance
- **Analysis**: LLM API is the bottleneck; local processing is fast

---

**Status**: ✅ Latency graph with 10 data points created successfully!

