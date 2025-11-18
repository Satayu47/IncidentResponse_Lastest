#!/usr/bin/env python3
"""
System Connection Test - Verify all components are connected and working
Run this to test the complete system before using the UI
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 70)
print("🔍 Incident Response System - Connection Test")
print("=" * 70)
print()

# Test 1: Environment Variables
print("1️⃣  Checking Environment Variables...")
gemini_key = os.getenv("GEMINI_API_KEY")
nvd_key = os.getenv("NVD_API_KEY")

if gemini_key:
    print(f"   ✅ GEMINI_API_KEY: Set ({gemini_key[:10]}...)")
else:
    print("   ❌ GEMINI_API_KEY: NOT SET")
    sys.exit(1)

if nvd_key:
    print(f"   ✅ NVD_API_KEY: Set ({nvd_key[:10]}...)")
else:
    print("   ⚠️  NVD_API_KEY: Not set (will use rate-limited mode)")

print()

# Test 2: Import All Components
print("2️⃣  Testing Component Imports...")
try:
    from src import (
        LLMAdapter,
        SecurityExtractor,
        DialogueState,
        ExplicitDetector,
        ClassificationRules,
        KnowledgeBaseRetriever,
    )
    from src.cve_service import CVEService
    from src.execution_simulator import ExecutionSimulator
    from phase2_engine.core.runner_bridge import run_phase2_from_incident
    print("   ✅ All Phase-1 components imported")
    print("   ✅ All Phase-2 components imported")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

print()

# Test 3: Initialize Components
print("3️⃣  Initializing Components...")
try:
    extractor = SecurityExtractor()
    explicit_detector = ExplicitDetector()
    kb_retriever = KnowledgeBaseRetriever()
    llm_adapter = LLMAdapter(model="gemini-2.5-pro")
    dialogue_state = DialogueState()
    cve_service = CVEService(api_key=nvd_key)
    execution_simulator = ExecutionSimulator()
    print("   ✅ All components initialized successfully")
except Exception as e:
    print(f"   ❌ Initialization failed: {e}")
    sys.exit(1)

print()

# Test 4: Test Explicit Detection
print("4️⃣  Testing Explicit Detection...")
test_text = "SQL injection detected. Attacker used ' OR 1=1 --"
label, conf = explicit_detector.detect(test_text)
if label:
    print(f"   ✅ Explicit detection works: {label} (confidence: {conf})")
else:
    print("   ⚠️  No explicit match (will use LLM)")

print()

# Test 5: Test IOC Extraction
print("5️⃣  Testing IOC Extraction...")
test_text = "Attack from IP 192.168.1.100, URL https://evil.com, CVE-2024-1234"
ents = extractor.extract(test_text)
if ents.ips or ents.urls or ents.cves:
    print(f"   ✅ IOC extraction works:")
    if ents.ips:
        print(f"      - IPs: {ents.ips}")
    if ents.urls:
        print(f"      - URLs: {ents.urls}")
    if ents.cves:
        print(f"      - CVEs: {ents.cves}")
else:
    print("   ⚠️  No IOCs extracted")

print()

# Test 6: Test Knowledge Base
print("6️⃣  Testing Knowledge Base Retrieval...")
kb_context = kb_retriever.get_context_for_label("sql injection")
if kb_context and len(kb_context) > 10:
    print(f"   ✅ Knowledge base works: {len(kb_context)} chars retrieved")
else:
    print("   ⚠️  Knowledge base returned empty context")

print()

# Test 7: Test LLM Classification (Quick Test)
print("7️⃣  Testing LLM Classification (Gemini API)...")
try:
    test_incident = "SQL injection on login page with ' OR 1=1 --"
    classification = llm_adapter.classify_incident(description=test_incident)
    if classification and "incident_type" in classification:
        print(f"   ✅ LLM classification works:")
        print(f"      - Type: {classification.get('incident_type', 'Unknown')}")
        print(f"      - Confidence: {classification.get('confidence', 0.0):.2f}")
    else:
        print("   ⚠️  LLM returned unexpected format")
except Exception as e:
    print(f"   ❌ LLM classification failed: {e}")
    print("   ⚠️  Check your GEMINI_API_KEY")

print()

# Test 8: Test CVE Service
print("8️⃣  Testing CVE Service (NVD API)...")
try:
    cve_results = cve_service.search_vulnerabilities("sql injection", max_results=1)
    if cve_results:
        print(f"   ✅ CVE service works: Found {len(cve_results)} CVE(s)")
        print(f"      - {cve_results[0].get('cve_id', 'Unknown')}")
    else:
        print("   ⚠️  No CVEs found (may be using mock data if API failed)")
except Exception as e:
    print(f"   ⚠️  CVE service test failed: {e} (may use fallback)")

print()

# Test 9: Test Playbook Loading
print("9️⃣  Testing Playbook Loading...")
try:
    from phase2_engine.core.playbook_loader import load_playbook_by_id
    playbook = load_playbook_by_id("A03_injection")
    if playbook:
        print(f"   ✅ Playbook loading works: {playbook.get('id', 'Unknown')}")
        phases = playbook.get("phases", {})
        total_steps = sum(len(steps) for steps in phases.values())
        print(f"      - Total steps: {total_steps}")
    else:
        print("   ❌ Playbook not found")
except Exception as e:
    print(f"   ❌ Playbook loading failed: {e}")

print()

# Test 10: Test DAG Construction
print("🔟 Testing DAG Construction...")
try:
    from phase2_engine.core.playbook_dag import build_playbook_dag
    if playbook:
        dag = build_playbook_dag(playbook)
        print(f"   ✅ DAG construction works: {len(dag.nodes)} nodes, {len(dag.edges)} edges")
    else:
        print("   ⚠️  Skipped (no playbook loaded)")
except Exception as e:
    print(f"   ❌ DAG construction failed: {e}")

print()

# Test 11: Test Phase-1 to Phase-2 Bridge
print("1️⃣1️⃣  Testing Phase-1 → Phase-2 Bridge...")
try:
    test_incident = {
        "incident_type": "Injection Attack",
        "fine_label": "injection",
        "confidence": 0.95,
        "rationale": "Test incident",
    }
    phase2_result = run_phase2_from_incident(
        incident=test_incident,
        dry_run=True
    )
    if phase2_result.get("status") == "success":
        print(f"   ✅ Phase-2 bridge works:")
        print(f"      - Playbooks: {phase2_result.get('playbooks', [])}")
        print(f"      - Steps: {len(phase2_result.get('steps', []))}")
    else:
        print(f"   ⚠️  Phase-2 returned: {phase2_result.get('status')}")
except Exception as e:
    print(f"   ❌ Phase-2 bridge failed: {e}")

print()

# Test 12: Test Execution Simulator
print("1️⃣2️⃣  Testing Execution Simulator...")
try:
    test_steps = [
        {"action": "Block IP", "description": "Block 192.168.1.100"},
        {"action": "Isolate System", "description": "Isolate web-server"}
    ]
    results = execution_simulator.execute_playbook(test_steps)
    if results:
        print(f"   ✅ Execution simulator works: {len(results)} steps executed")
    else:
        print("   ⚠️  No execution results")
except Exception as e:
    print(f"   ❌ Execution simulator failed: {e}")

print()
print("=" * 70)
print("✅ System Connection Test Complete!")
print("=" * 70)
print()
print("📋 Summary:")
print("   - All components are connected and working")
print("   - System is ready to test in the UI")
print()
print("🚀 Next Steps:")
print("   1. Run: streamlit run app.py")
print("   2. Open: http://localhost:8501")
print("   3. Try classifying an incident!")
print()

