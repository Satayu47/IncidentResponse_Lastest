# Overall System Latency Summary

## 📊 Graph Created

**File**: `reports/visualizations/overall_latency_graph_ieee.png`

IEEE-format line graph showing **overall system latency** (end-to-end) from user input to final response.

## 🎯 What This Measures

**Overall System Latency** = Complete end-to-end time from:
1. User input received
2. IOC extraction
3. Explicit detection  
4. Knowledge base retrieval
5. LLM classification
6. Dialogue state update
7. Phase-2 playbook generation
8. **Final response ready**

This is the **total time** a user experiences from typing their incident to getting the complete response.

## 📈 Results (10 Data Points)

| Test Case | Description | Overall Latency |
|-----------|-------------|----------------|
| 1 | SQL injection detected | 146.90 ms |
| 2 | XSS vulnerability found | 107.90 ms |
| 3 | Broken access control | 105.49 ms |
| 4 | Authentication failure | 103.49 ms |
| 5 | Security misconfiguration | 104.62 ms |
| 6 | Vulnerable component | 99.48 ms |
| 7 | SSRF attack attempted | 233.33 ms |
| 8 | Cryptographic failure | 112.50 ms |
| 9 | Insecure design | 112.26 ms |
| 10 | Logging failure | 108.80 ms |

## 📊 Statistics

- **Average**: 123.48 ms (0.12 seconds)
- **Minimum**: 99.48 ms (0.10 seconds)
- **Maximum**: 233.33 ms (0.23 seconds)
- **Range**: 133.85 ms

## 🔍 Component Breakdown

| Component | Average Time | Percentage |
|-----------|-------------|------------|
| LLM Classification | 117.58 ms | 95.2% |
| Phase-2 Generation | 3.99 ms | 3.2% |
| Explicit Detection | 1.46 ms | 1.2% |
| IOC Extraction | 0.15 ms | 0.1% |
| Knowledge Base | 0.00 ms | 0.0% |
| Dialogue Update | 0.00 ms | 0.0% |

## 📁 Files Created

1. **`reports/overall_latency_20251118_184915.json`** - Raw measurement data
2. **`reports/visualizations/overall_latency_graph_ieee.png`** - IEEE-format graph
3. **`reports/visualizations/overall_latency_summary.json`** - Summary statistics

## 📝 For Your Report

**Title**: "Overall System Latency - End-to-End Performance"

**Key Points**:
- System responds in **~120 ms average** (0.12 seconds)
- Fast enough for real-time incident response
- LLM API call is the main bottleneck (95% of time)
- Local processing is very fast (< 5 ms)

---

**Status**: ✅ Overall system latency graph created with 10 data points!

