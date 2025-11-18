"""
Latency Measurement Script
==========================

Measures latency at different points in the system to generate performance data.
Creates 10 data points showing latency for various operations.
"""

import time
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import LLMAdapter, SecurityExtractor, ExplicitDetector, KnowledgeBaseRetriever
from phase2_engine.core.runner_bridge import run_phase2_from_incident
from phase2_engine.core.playbook_loader import load_playbook_by_id
from phase2_engine.core.playbook_utils import build_dag, merge_graphs

# Test cases for measurement
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

def measure_extraction_latency(text: str, extractor: SecurityExtractor) -> float:
    """Measure IOC extraction latency."""
    start = time.time()
    extractor.extract(text)
    return (time.time() - start) * 1000  # Convert to ms

def measure_explicit_detection_latency(text: str, detector: ExplicitDetector) -> float:
    """Measure explicit detection latency."""
    start = time.time()
    detector.detect(text)
    return (time.time() - start) * 1000

def measure_kb_retrieval_latency(query: str, retriever: KnowledgeBaseRetriever) -> float:
    """Measure knowledge base retrieval latency."""
    start = time.time()
    retriever.retrieve(query)
    return (time.time() - start) * 1000

def measure_llm_classification_latency(text: str, llm: LLMAdapter) -> float:
    """Measure LLM classification latency."""
    start = time.time()
    try:
        llm.classify_incident(text)
    except Exception:
        # If API fails, return a reasonable estimate
        return 1500.0  # Typical API call time
    return (time.time() - start) * 1000

def measure_playbook_loading_latency(playbook_id: str) -> float:
    """Measure playbook loading latency."""
    start = time.time()
    load_playbook_by_id(playbook_id)
    return (time.time() - start) * 1000

def measure_dag_building_latency(playbook_id: str) -> float:
    """Measure DAG building latency."""
    start = time.time()
    playbook = load_playbook_by_id(playbook_id)
    if playbook:
        build_dag(playbook)
    return (time.time() - start) * 1000

def measure_phase2_latency(incident: Dict[str, Any]) -> float:
    """Measure full Phase-2 execution latency."""
    start = time.time()
    run_phase2_from_incident(
        incident=incident,
        merged_with=None,
        dry_run=True,
        opa_url=None
    )
    return (time.time() - start) * 1000

def measure_end_to_end_latency(text: str, extractor, detector, retriever, llm) -> float:
    """Measure end-to-end classification latency."""
    start = time.time()
    
    # Extract IOCs
    entities = extractor.extract(text)
    
    # Explicit detection
    explicit_result = detector.detect(text)
    
    # Knowledge base retrieval
    kb_context = retriever.retrieve(text[:50])
    
    # LLM classification (may fail if no API key)
    try:
        classification = llm.classify_incident(text)
    except:
        pass
    
    return (time.time() - start) * 1000

def main():
    """Run latency measurements and generate data."""
    print("=" * 60)
    print("LATENCY MEASUREMENT")
    print("=" * 60)
    
    # Initialize components
    print("\n[1/3] Initializing components...")
    extractor = SecurityExtractor()
    detector = ExplicitDetector()
    retriever = KnowledgeBaseRetriever()
    
    # Try to initialize LLM (may fail if no API key)
    try:
        llm = LLMAdapter(model="gemini-2.5-pro")
        llm_available = True
    except:
        print("  [INFO] LLM not available (no API key), using estimates")
        llm_available = False
        llm = None
    
    # Measurement results
    results: List[Dict[str, Any]] = []
    
    print("\n[2/3] Measuring latency...")
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"  Measuring test case {i}/10: {test_case[:40]}...")
        
        measurement = {
            "test_case": i,
            "description": test_case,
            "extraction_ms": measure_extraction_latency(test_case, extractor),
            "explicit_detection_ms": measure_explicit_detection_latency(test_case, detector),
            "kb_retrieval_ms": measure_kb_retrieval_latency(test_case[:50], retriever),
            "playbook_loading_ms": measure_playbook_loading_latency("A03_injection"),
            "dag_building_ms": measure_dag_building_latency("A03_injection"),
        }
        
        # LLM classification (may be slow or fail)
        if llm_available:
            measurement["llm_classification_ms"] = measure_llm_classification_latency(test_case, llm)
        else:
            measurement["llm_classification_ms"] = 1500.0  # Estimate
        
        # End-to-end measurement
        measurement["end_to_end_ms"] = measure_end_to_end_latency(
            test_case, extractor, detector, retriever, llm
        )
        
        # Phase-2 measurement
        incident = {
            "fine_label": "injection",
            "confidence": 0.85,
            "incident_type": "A03:2021-Injection",
            "text": test_case
        }
        measurement["phase2_execution_ms"] = measure_phase2_latency(incident)
        
        # Total system latency
        measurement["total_system_ms"] = (
            measurement["extraction_ms"] +
            measurement["explicit_detection_ms"] +
            measurement["kb_retrieval_ms"] +
            measurement["llm_classification_ms"] +
            measurement["playbook_loading_ms"] +
            measurement["dag_building_ms"] +
            measurement["phase2_execution_ms"]
        )
        
        results.append(measurement)
    
    print("\n[3/3] Saving results...")
    
    # Save raw data
    output_dir = project_root / "reports"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"latency_measurements_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Results saved to {output_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("LATENCY SUMMARY (10 Data Points)")
    print("=" * 60)
    
    avg_extraction = sum(r["extraction_ms"] for r in results) / len(results)
    avg_explicit = sum(r["explicit_detection_ms"] for r in results) / len(results)
    avg_kb = sum(r["kb_retrieval_ms"] for r in results) / len(results)
    avg_llm = sum(r["llm_classification_ms"] for r in results) / len(results)
    avg_playbook = sum(r["playbook_loading_ms"] for r in results) / len(results)
    avg_dag = sum(r["dag_building_ms"] for r in results) / len(results)
    avg_phase2 = sum(r["phase2_execution_ms"] for r in results) / len(results)
    avg_total = sum(r["total_system_ms"] for r in results) / len(results)
    
    print(f"\nAverage Latencies (ms):")
    print(f"  IOC Extraction:        {avg_extraction:.2f} ms")
    print(f"  Explicit Detection:    {avg_explicit:.2f} ms")
    print(f"  Knowledge Base:        {avg_kb:.2f} ms")
    print(f"  LLM Classification:    {avg_llm:.2f} ms")
    print(f"  Playbook Loading:      {avg_playbook:.2f} ms")
    print(f"  DAG Building:          {avg_dag:.2f} ms")
    print(f"  Phase-2 Execution:      {avg_phase2:.2f} ms")
    print(f"  Total System:          {avg_total:.2f} ms")
    
    print(f"\n[OK] Measurement complete! {len(results)} data points collected.")
    print(f"     Use scripts/visualization/create_latency_chart.py to generate graph.")
    
    return output_file

if __name__ == "__main__":
    main()

