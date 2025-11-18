"""
Overall System Latency Measurement
===================================

Measures end-to-end system latency from user input to final response.
This measures the complete flow: input → classification → playbook → response.
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

from src import LLMAdapter, SecurityExtractor, ExplicitDetector, KnowledgeBaseRetriever, DialogueState
from phase2_engine.core.runner_bridge import run_phase2_from_incident

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

def measure_full_system_latency(text: str) -> Dict[str, Any]:
    """
    Measure complete end-to-end system latency.
    
    Flow:
    1. User input received
    2. IOC extraction
    3. Explicit detection
    4. Knowledge base retrieval
    5. LLM classification
    6. Dialogue state update
    7. Phase-2 playbook generation
    8. Final response ready
    """
    start_time = time.time()
    
    # Initialize components (simulate app.py initialization)
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
    elif llm_available:
        try:
            classification = llm.classify_incident(text)
            classification_result = {
                "fine_label": classification.get("fine_label", "other"),
                "confidence": classification.get("confidence", 0.5),
                "incident_type": classification.get("incident_type", "Unknown"),
            }
        except:
            # If API fails, use explicit result
            classification_result = {
                "fine_label": explicit_label if explicit_label else "other",
                "confidence": explicit_conf if explicit_conf else 0.5,
                "incident_type": "Unknown",
            }
        step4_time = (time.time() - step4_start) * 1000
    else:
        # Use explicit detection result
        classification_result = {
            "fine_label": explicit_label if explicit_label else "other",
            "confidence": explicit_conf if explicit_conf else 0.5,
            "incident_type": "Unknown",
        }
        step4_time = (time.time() - step4_start) * 1000
    
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
        "phase2_status": phase2_result.get("status", "unknown"),
        "playbooks_found": len(phase2_result.get("playbooks", [])),
        "steps_generated": len(phase2_result.get("steps", [])),
    }

def main():
    """Run overall system latency measurements."""
    print("=" * 60)
    print("OVERALL SYSTEM LATENCY MEASUREMENT")
    print("=" * 60)
    print("\nMeasuring end-to-end latency from input to response...")
    print("(This includes: extraction -> detection -> classification -> playbook)\n")
    
    results: List[Dict[str, Any]] = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"[{i}/10] Testing: {test_case[:50]}...")
        
        measurement = measure_full_system_latency(test_case)
        measurement["test_case"] = i
        measurement["description"] = test_case
        
        results.append(measurement)
        
        print(f"        Total: {measurement['total_latency_ms']:.2f} ms")
    
    # Save results
    output_dir = project_root / "reports"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"overall_latency_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Results saved to {output_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("OVERALL SYSTEM LATENCY SUMMARY (10 Test Cases)")
    print("=" * 60)
    
    total_latencies = [r["total_latency_ms"] for r in results]
    avg_latency = sum(total_latencies) / len(total_latencies)
    min_latency = min(total_latencies)
    max_latency = max(total_latencies)
    
    print(f"\nOverall System Latency:")
    print(f"  Average: {avg_latency:.2f} ms ({avg_latency/1000:.2f} seconds)")
    print(f"  Minimum: {min_latency:.2f} ms ({min_latency/1000:.2f} seconds)")
    print(f"  Maximum: {max_latency:.2f} ms ({max_latency/1000:.2f} seconds)")
    print(f"  Range:   {max_latency - min_latency:.2f} ms")
    
    # Breakdown
    avg_extraction = sum(r["step1_extraction_ms"] for r in results) / len(results)
    avg_detection = sum(r["step2_explicit_detection_ms"] for r in results) / len(results)
    avg_kb = sum(r["step3_kb_retrieval_ms"] for r in results) / len(results)
    avg_llm = sum(r["step4_llm_classification_ms"] for r in results) / len(results)
    avg_dialogue = sum(r["step5_dialogue_update_ms"] for r in results) / len(results)
    avg_phase2 = sum(r["step6_phase2_generation_ms"] for r in results) / len(results)
    
    print(f"\nComponent Breakdown (Average):")
    print(f"  IOC Extraction:        {avg_extraction:.2f} ms ({avg_extraction/avg_latency*100:.1f}%)")
    print(f"  Explicit Detection:    {avg_detection:.2f} ms ({avg_detection/avg_latency*100:.1f}%)")
    print(f"  Knowledge Base:        {avg_kb:.2f} ms ({avg_kb/avg_latency*100:.1f}%)")
    print(f"  LLM Classification:    {avg_llm:.2f} ms ({avg_llm/avg_latency*100:.1f}%)")
    print(f"  Dialogue Update:       {avg_dialogue:.2f} ms ({avg_dialogue/avg_latency*100:.1f}%)")
    print(f"  Phase-2 Generation:    {avg_phase2:.2f} ms ({avg_phase2/avg_latency*100:.1f}%)")
    
    print(f"\n[OK] Measurement complete! {len(results)} data points collected.")
    print(f"     Use scripts/visualization/create_overall_latency_chart.py to generate graph.")
    
    return output_file

if __name__ == "__main__":
    main()

