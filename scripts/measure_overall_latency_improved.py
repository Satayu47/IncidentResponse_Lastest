"""
Improved Overall System Latency Measurement
===========================================

Measures end-to-end system latency with:
- 30-50 test cases (from test suite)
- Multiple runs (3-5 per case) for confidence intervals
- Percentiles (P25, P50, P75, P95, P99)
- Separate fast path vs LLM path analysis
"""

import time
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import json
import numpy as np
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import LLMAdapter, SecurityExtractor, ExplicitDetector, KnowledgeBaseRetriever, DialogueState
from phase2_engine.core.runner_bridge import run_phase2_from_incident

# Import test cases from test suite
try:
    from tests.test_human_multiturn_single import CASES_SINGLE
    # Use first 50 test cases for latency measurement
    TEST_CASES = [(" ".join(turns)) for _, _, turns in CASES_SINGLE[:50]]
    print(f"[INFO] Using {len(TEST_CASES)} test cases from test suite")
except ImportError:
    # Fallback to original test cases
    TEST_CASES = [
        "SQL injection detected from IP 192.168.1.1",
        "XSS vulnerability found in login form",
        "Broken access control allows unauthorized data access",
        "Authentication failure detected - multiple failed login attempts",
        "Security misconfiguration exposes sensitive data",
        "Vulnerable component detected - outdated library version",
        "SSRF attack attempted from external source",
        "Cryptographic failure - weak encryption algorithm used",
        "Insecure design allows privilege escalation",
        "Logging failure - security events not recorded",
    ]
    print(f"[INFO] Using {len(TEST_CASES)} fallback test cases")

# Configuration
NUM_RUNS = 3  # Number of runs per test case for confidence intervals
CONFIDENCE_LEVEL = 0.95  # 95% confidence interval

def calculate_confidence_interval(data: List[float], confidence: float = 0.95) -> tuple:
    """Calculate confidence interval using t-distribution."""
    if len(data) < 2:
        return (data[0], data[0])
    
    mean = np.mean(data)
    std = np.std(data, ddof=1)  # Sample standard deviation
    n = len(data)
    
    # t-value for 95% confidence (approximate for n>=30, use 1.96 for large n)
    if n >= 30:
        t_value = 1.96
    elif n >= 10:
        t_value = 2.262  # t-value for n=10, df=9
    else:
        t_value = 2.776  # t-value for n=5, df=4
    
    margin = t_value * (std / np.sqrt(n))
    return (mean - margin, mean + margin)

def measure_full_system_latency(text: str) -> Dict[str, Any]:
    """
    Measure complete end-to-end system latency.
    Returns detailed timing breakdown.
    """
    start_time = time.time()
    
    # Initialize components
    extractor = SecurityExtractor()
    detector = ExplicitDetector()
    retriever = KnowledgeBaseRetriever()
    dialogue = DialogueState()
    
    # Try to initialize LLM
    try:
        llm = LLMAdapter(model="gemini-2.5-pro")
        llm_available = True
    except:
        llm_available = False
        llm = None
    
    # Step 1: IOC Extraction
    step1_start = time.time()
    entities = extractor.extract(text)
    step1_time = (time.time() - step1_start) * 1000
    
    # Step 2: Explicit Detection
    step2_start = time.time()
    explicit_result = detector.detect(text)
    step2_time = (time.time() - step2_start) * 1000
    
    # Step 3: Knowledge Base Retrieval
    step3_start = time.time()
    kb_context = retriever.retrieve(text[:50])
    step3_time = (time.time() - step3_start) * 1000
    
    # Step 4: LLM Classification (with fast path optimization)
    step4_start = time.time()
    
    # Fast path: Skip LLM if explicit detection confidence >= 0.85
    explicit_label, explicit_conf = explicit_result if explicit_result else (None, 0.0)
    use_fast_path = explicit_label and explicit_conf >= 0.85
    
    if use_fast_path:
        # Fast path - skip LLM call (optimization)
        from src.classification_rules import canonicalize_label
        canonical = canonicalize_label(explicit_label)
        classification_result = {
            "fine_label": canonical,
            "confidence": explicit_conf,
            "incident_type": "Unknown",
        }
        step4_time = (time.time() - step4_start) * 1000
        path_used = "fast_path"
    elif llm_available:
        try:
            classification = llm.classify_incident(text)
            classification_result = {
                "fine_label": classification.get("fine_label", "other"),
                "confidence": classification.get("confidence", 0.5),
                "incident_type": classification.get("incident_type", "Unknown"),
            }
            path_used = "llm_path"
        except:
            # If API fails, use explicit result
            classification_result = {
                "fine_label": explicit_label if explicit_label else "other",
                "confidence": explicit_conf if explicit_conf else 0.5,
                "incident_type": "Unknown",
            }
            path_used = "fallback"
        step4_time = (time.time() - step4_start) * 1000
    else:
        # Use explicit detection result
        classification_result = {
            "fine_label": explicit_label if explicit_label else "other",
            "confidence": explicit_conf if explicit_conf else 0.5,
            "incident_type": "Unknown",
        }
        step4_time = (time.time() - step4_start) * 1000
        path_used = "explicit_only"
    
    # Step 5: Dialogue State Update
    step5_start = time.time()
    dialogue.add_turn(
        user_input=text,
        classification=classification_result
    )
    step5_time = (time.time() - step5_start) * 1000
    
    # Step 6: Phase-2 Playbook Generation
    step6_start = time.time()
    incident = {
        "fine_label": classification_result["fine_label"],
        "confidence": classification_result["confidence"],
        "incident_type": classification_result["incident_type"],
        "text": text,
        "entities": entities.__dict__() if hasattr(entities, '__dict__') else {},
    }
    
    phase2_result = run_phase2_from_incident(
        incident=incident,
        merged_with=None,
        dry_run=True,
        opa_url=None
    )
    step6_time = (time.time() - step6_start) * 1000
    
    # Total time
    total_time = (time.time() - start_time) * 1000
    
    return {
        "total_latency_ms": total_time,
        "step1_extraction_ms": step1_time,
        "step2_explicit_detection_ms": step2_time,
        "step3_kb_retrieval_ms": step3_time,
        "step4_llm_classification_ms": step4_time,
        "step5_dialogue_update_ms": step5_time,
        "step6_phase2_generation_ms": step6_time,
        "classification_result": classification_result,
        "path_used": path_used,
        "phase2_status": phase2_result.get("status", "unknown"),
        "playbooks_found": len(phase2_result.get("playbooks", [])),
        "steps_generated": len(phase2_result.get("steps", [])),
    }

def main():
    """Run improved overall system latency measurements."""
    print("=" * 70)
    print("IMPROVED OVERALL SYSTEM LATENCY MEASUREMENT")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Test cases: {len(TEST_CASES)}")
    print(f"  Runs per case: {NUM_RUNS}")
    print(f"  Total measurements: {len(TEST_CASES) * NUM_RUNS}")
    print(f"  Confidence level: {CONFIDENCE_LEVEL * 100}%")
    print("\nMeasuring end-to-end latency from input to response...")
    print("(This includes: extraction -> detection -> classification -> playbook)\n")
    
    all_results: List[Dict[str, Any]] = []
    per_case_results = defaultdict(list)
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] Testing: {test_case[:60]}...")
        
        case_results = []
        for run in range(NUM_RUNS):
            measurement = measure_full_system_latency(test_case)
            measurement["test_case"] = i
            measurement["description"] = test_case
            measurement["run"] = run + 1
            case_results.append(measurement["total_latency_ms"])
            all_results.append(measurement)
        
        per_case_results[i] = case_results
        avg_latency = np.mean(case_results)
        std_latency = np.std(case_results)
        print(f"        Avg: {avg_latency:.2f} ms (std: {std_latency:.2f} ms)")
    
    # Save detailed results
    output_dir = project_root / "reports"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"overall_latency_improved_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Detailed results saved to {output_file}")
    
    # Calculate statistics
    total_latencies = [r["total_latency_ms"] for r in all_results]
    fast_path_latencies = [r["total_latency_ms"] for r in all_results if r.get("path_used") == "fast_path"]
    llm_path_latencies = [r["total_latency_ms"] for r in all_results if r.get("path_used") == "llm_path"]
    
    # Overall statistics
    mean_latency = np.mean(total_latencies)
    std_latency = np.std(total_latencies)
    median_latency = np.median(total_latencies)
    min_latency = np.min(total_latencies)
    max_latency = np.max(total_latencies)
    ci_lower, ci_upper = calculate_confidence_interval(total_latencies, CONFIDENCE_LEVEL)
    
    # Percentiles
    p25 = np.percentile(total_latencies, 25)
    p75 = np.percentile(total_latencies, 75)
    p95 = np.percentile(total_latencies, 95)
    p99 = np.percentile(total_latencies, 99)
    
    # Per-case statistics
    per_case_stats = {}
    for case_id, latencies in per_case_results.items():
        per_case_stats[case_id] = {
            "mean": float(np.mean(latencies)),
            "std": float(np.std(latencies)),
            "min": float(np.min(latencies)),
            "max": float(np.max(latencies)),
            "ci_lower": float(calculate_confidence_interval(latencies, CONFIDENCE_LEVEL)[0]),
            "ci_upper": float(calculate_confidence_interval(latencies, CONFIDENCE_LEVEL)[1]),
        }
    
    # Path analysis
    path_stats = {}
    if fast_path_latencies:
        path_stats["fast_path"] = {
            "count": len(fast_path_latencies),
            "percentage": len(fast_path_latencies) / len(total_latencies) * 100,
            "mean": float(np.mean(fast_path_latencies)),
            "std": float(np.std(fast_path_latencies)),
            "median": float(np.median(fast_path_latencies)),
        }
    if llm_path_latencies:
        path_stats["llm_path"] = {
            "count": len(llm_path_latencies),
            "percentage": len(llm_path_latencies) / len(total_latencies) * 100,
            "mean": float(np.mean(llm_path_latencies)),
            "std": float(np.std(llm_path_latencies)),
            "median": float(np.median(llm_path_latencies)),
        }
    
    # Component breakdown
    avg_extraction = np.mean([r["step1_extraction_ms"] for r in all_results])
    avg_detection = np.mean([r["step2_explicit_detection_ms"] for r in all_results])
    avg_kb = np.mean([r["step3_kb_retrieval_ms"] for r in all_results])
    avg_llm = np.mean([r["step4_llm_classification_ms"] for r in all_results])
    avg_dialogue = np.mean([r["step5_dialogue_update_ms"] for r in all_results])
    avg_phase2 = np.mean([r["step6_phase2_generation_ms"] for r in all_results])
    
    # Create summary
    summary = {
        "test_cases": len(TEST_CASES),
        "runs_per_case": NUM_RUNS,
        "total_measurements": len(all_results),
        "confidence_level": CONFIDENCE_LEVEL,
        "overall_statistics": {
            "mean_ms": float(mean_latency),
            "std_dev_ms": float(std_latency),
            "median_ms": float(median_latency),
            "min_ms": float(min_latency),
            "max_ms": float(max_latency),
            "range_ms": float(max_latency - min_latency),
            "p25_ms": float(p25),
            "p75_ms": float(p75),
            "p95_ms": float(p95),
            "p99_ms": float(p99),
            "ci_95_lower_ms": float(ci_lower),
            "ci_95_upper_ms": float(ci_upper),
        },
        "path_analysis": path_stats,
        "component_breakdown": {
            "extraction_ms": float(avg_extraction),
            "explicit_detection_ms": float(avg_detection),
            "knowledge_base_ms": float(avg_kb),
            "llm_classification_ms": float(avg_llm),
            "dialogue_update_ms": float(avg_dialogue),
            "phase2_generation_ms": float(avg_phase2),
        },
        "per_case_statistics": per_case_stats,
    }
    
    # Save summary
    summary_file = output_dir / f"overall_latency_improved_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("IMPROVED LATENCY SUMMARY")
    print("=" * 70)
    
    print(f"\nOverall System Latency ({len(all_results)} measurements):")
    print(f"  Mean: {mean_latency:.2f} ms")
    print(f"  Median: {median_latency:.2f} ms")
    print(f"  Std Dev: {std_latency:.2f} ms")
    print(f"  Range: {min_latency:.2f} - {max_latency:.2f} ms")
    print(f"  95% CI: [{ci_lower:.2f}, {ci_upper:.2f}] ms")
    
    print(f"\nPercentiles:")
    print(f"  P25: {p25:.2f} ms")
    print(f"  P50 (Median): {median_latency:.2f} ms")
    print(f"  P75: {p75:.2f} ms")
    print(f"  P95: {p95:.2f} ms")
    print(f"  P99: {p99:.2f} ms")
    
    if path_stats:
        print(f"\nPath Analysis:")
        if "fast_path" in path_stats:
            fp = path_stats["fast_path"]
            print(f"  Fast Path: {fp['count']} cases ({fp['percentage']:.1f}%)")
            print(f"    Mean: {fp['mean']:.2f} ms, Median: {fp['median']:.2f} ms")
        if "llm_path" in path_stats:
            lp = path_stats["llm_path"]
            print(f"  LLM Path: {lp['count']} cases ({lp['percentage']:.1f}%)")
            print(f"    Mean: {lp['mean']:.2f} ms, Median: {lp['median']:.2f} ms")
    
    print(f"\nComponent Breakdown (Average):")
    print(f"  IOC Extraction:        {avg_extraction:.2f} ms ({avg_extraction/mean_latency*100:.1f}%)")
    print(f"  Explicit Detection:    {avg_detection:.2f} ms ({avg_detection/mean_latency*100:.1f}%)")
    print(f"  Knowledge Base:        {avg_kb:.2f} ms ({avg_kb/mean_latency*100:.1f}%)")
    print(f"  LLM Classification:    {avg_llm:.2f} ms ({avg_llm/mean_latency*100:.1f}%)")
    print(f"  Dialogue Update:       {avg_dialogue:.2f} ms ({avg_dialogue/mean_latency*100:.1f}%)")
    print(f"  Phase-2 Generation:    {avg_phase2:.2f} ms ({avg_phase2/mean_latency*100:.1f}%)")
    
    print(f"\n[OK] Summary saved to {summary_file}")
    print(f"[OK] Measurement complete! {len(all_results)} data points collected.")
    print(f"     Use scripts/visualization/create_improved_latency_chart.py to generate graph.")
    
    return output_file, summary_file

if __name__ == "__main__":
    main()

