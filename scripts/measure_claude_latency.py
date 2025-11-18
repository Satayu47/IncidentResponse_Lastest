"""
Measure Claude (Anthropic) Latency for Comparison
=================================================

Measures end-to-end latency for Claude baseline:
- Same test cases as ChatOps
- Multiple runs for consistency
- Fast mode support (fewer cases)
"""

import time
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import json
import numpy as np
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm_adapter import LLMAdapter
from src.classification_rules import canonicalize_label

# Import test cases
try:
    from tests.test_human_multiturn_single import CASES_SINGLE
    # Use same test cases as ChatOps measurement
    TEST_CASES = [(" ".join(turns)) for _, _, turns in CASES_SINGLE[:50]]
    print(f"[INFO] Using {len(TEST_CASES)} test cases from test suite")
except ImportError:
    TEST_CASES = [
        "SQL injection detected from IP 192.168.1.1",
        "XSS vulnerability found in login form",
        "Broken access control allows unauthorized data access",
        "Authentication failure detected - multiple failed login attempts",
        "Security misconfiguration exposes sensitive data",
    ]
    print(f"[INFO] Using {len(TEST_CASES)} fallback test cases")

# Configuration
NUM_RUNS = 1  # Fast mode: 1 run per case
FAST_MODE = True  # Use fewer test cases
RATE_LIMIT = 0.5  # seconds between requests

def measure_claude_latency(text: str, adapter: LLMAdapter) -> Dict[str, Any]:
    """Measure Claude classification latency."""
    start_time = time.time()
    
    try:
        # Claude classification (end-to-end)
        classification = adapter.classify_incident(
            description=text,
            context="",
            conversation_history=None
        )
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "latency_ms": total_time,
            "success": True,
            "label": classification.get("fine_label", "unknown"),
            "confidence": classification.get("confidence", 0.0)
        }
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        return {
            "latency_ms": total_time,
            "success": False,
            "error": str(e)[:100]
        }

def main():
    """Measure Claude latency."""
    print("=" * 70)
    print("CLAUDE LATENCY MEASUREMENT")
    print("=" * 70)
    
    # Check API key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("[ERROR] ANTHROPIC_API_KEY not set!")
        print("Set it with: $env:ANTHROPIC_API_KEY = 'sk-or-v1-...'")
        return
    
    # Use fast mode if enabled
    test_cases = TEST_CASES[:30] if FAST_MODE else TEST_CASES
    print(f"\nConfiguration:")
    print(f"  Test cases: {len(test_cases)}")
    print(f"  Runs per case: {NUM_RUNS}")
    print(f"  Fast mode: {FAST_MODE}")
    print(f"  Rate limit: {RATE_LIMIT}s")
    
    # Initialize Claude adapter
    try:
        adapter = LLMAdapter(model="claude-3-5-sonnet-20241022", api_key=anthropic_key)
        print(f"\n[OK] Claude (Anthropic) initialized")
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize Claude: {e}")
        return
    
    print(f"\nMeasuring latency for {len(test_cases)} test cases...")
    print("=" * 70)
    
    all_results = []
    per_case_latencies = []
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"[{idx}/{len(test_cases)}] Testing: {test_case[:60]}...")
        
        case_latencies = []
        for run in range(NUM_RUNS):
            result = measure_claude_latency(test_case, adapter)
            all_results.append({
                "test_case": idx,
                "run": run + 1,
                "text": test_case,
                **result
            })
            
            if result["success"]:
                case_latencies.append(result["latency_ms"])
                print(f"        Run {run+1}: {result['latency_ms']:.2f} ms")
            else:
                print(f"        Run {run+1}: ERROR - {result.get('error', 'Unknown')}")
            
            # Rate limiting
            if idx < len(test_cases) or run < NUM_RUNS - 1:
                time.sleep(RATE_LIMIT)
        
        if case_latencies:
            per_case_latencies.append({
                "test_case": idx,
                "mean": np.mean(case_latencies),
                "std": np.std(case_latencies) if len(case_latencies) > 1 else 0.0,
                "min": np.min(case_latencies),
                "max": np.max(case_latencies),
                "runs": case_latencies
            })
    
    # Calculate overall statistics
    all_latencies = [r["latency_ms"] for r in all_results if r.get("success")]
    
    if not all_latencies:
        print("\n[ERROR] No successful measurements!")
        return
    
    overall_stats = {
        "mean_ms": float(np.mean(all_latencies)),
        "std_dev_ms": float(np.std(all_latencies)),
        "median_ms": float(np.median(all_latencies)),
        "min_ms": float(np.min(all_latencies)),
        "max_ms": float(np.max(all_latencies)),
        "p25_ms": float(np.percentile(all_latencies, 25)),
        "p75_ms": float(np.percentile(all_latencies, 75)),
        "p95_ms": float(np.percentile(all_latencies, 95)),
        "p99_ms": float(np.percentile(all_latencies, 99)),
    }
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("reports") / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "timestamp": timestamp,
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "test_cases": len(test_cases),
        "runs_per_case": NUM_RUNS,
        "fast_mode": FAST_MODE,
        "overall_statistics": overall_stats,
        "per_case_statistics": per_case_latencies,
        "all_measurements": all_results
    }
    
    output_file = output_dir / f"claude_latency_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("CLAUDE LATENCY SUMMARY")
    print("=" * 70)
    print(f"Total measurements: {len(all_latencies)}")
    print(f"Mean latency: {overall_stats['mean_ms']:.2f} ms")
    print(f"Median latency: {overall_stats['median_ms']:.2f} ms")
    print(f"Std Dev: {overall_stats['std_dev_ms']:.2f} ms")
    print(f"Min: {overall_stats['min_ms']:.2f} ms")
    print(f"Max: {overall_stats['max_ms']:.2f} ms")
    print(f"P95: {overall_stats['p95_ms']:.2f} ms")
    print(f"\n[OK] Results saved to {output_file}")
    print(f"     Use scripts/visualization/create_latency_comparison.py to generate graph.")
    
    return output_file

if __name__ == "__main__":
    main()

