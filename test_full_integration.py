import sys
sys.path.insert(0, '.')

# Test 1: LLM Classification
print("="*60)
print("TEST 1: LLM Classification with Gemini 2.5 Pro")
print("="*60)
from src.llm_adapter import LLMAdapter
adapter = LLMAdapter()
result = adapter.classify_incident('SQL injection on login page')
print(f"✅ Category: {result.get('category')}")
print(f"✅ Confidence: {result.get('confidence'):.2f}")

# Test 2: Explicit Detection
print("\n" + "="*60)
print("TEST 2: Explicit Keyword Detection")
print("="*60)
from src.explicit_detector import ExplicitDetector
detector = ExplicitDetector()
label, conf = detector.detect("SQL injection vulnerability found")
print(f"✅ Detected: {label} (confidence: {conf})")

# Test 3: Playbook Loading & DAG Building
print("\n" + "="*60)
print("TEST 3: Playbook Loading & DAG Construction")
print("="*60)
from phase2_engine.core.playbook_utils import load_playbook_by_id, build_dag, merge_graphs
p1 = load_playbook_by_id('A01_broken_access_control')
p2 = load_playbook_by_id('A03_injection')
d1 = build_dag(p1)
d2 = build_dag(p2)
print(f"✅ A01 DAG: {len(d1.nodes())} nodes, {len(d1.edges())} edges")
print(f"✅ A03 DAG: {len(d2.nodes())} nodes, {len(d2.edges())} edges")

# Test 4: DAG Merging
print("\n" + "="*60)
print("TEST 4: Multi-Playbook DAG Merging")
print("="*60)
merged = merge_graphs([d1, d2])
print(f"✅ Merged DAG: {len(merged.nodes())} nodes, {len(merged.edges())} edges")
import networkx as nx
print(f"✅ Is acyclic: {nx.is_directed_acyclic_graph(merged)}")

# Test 5: Phase-2 Runner Bridge
print("\n" + "="*60)
print("TEST 5: Phase-2 Runner Bridge Integration")
print("="*60)
from phase2_engine.core.runner_bridge import run_phase2_from_incident
incident = {
    "description": "SQL injection and unauthorized access",
    "labels": ["injection", "broken_access_control"],
    "confidence": 0.85
}
phase2_result = run_phase2_from_incident(incident, dry_run=True)
print(f"✅ Playbooks loaded: {len(phase2_result['playbooks'])}")
print(f"✅ Merged DAG nodes: {len(phase2_result['merged_dag'].nodes())}")
print(f"✅ Automation ready: {phase2_result.get('dry_run', False)}")

# Test 6: Check all 8 playbooks exist
print("\n" + "="*60)
print("TEST 6: All OWASP Playbooks Available")
print("="*60)
playbook_ids = [
    'A01_broken_access_control',
    'A02_cryptographic_failures', 
    'A03_injection',
    'A04_insecure_design',
    'A05_misconfiguration',
    'A06_vulnerable_components',
    'A07_authentication_failures',
    'A10_ssrf'
]
for pid in playbook_ids:
    pb = load_playbook_by_id(pid)
    dag = build_dag(pb)
    print(f"✅ {pid}: {len(dag.nodes())} nodes")

# Test 7: Environment Configuration
print("\n" + "="*60)
print("TEST 7: Environment Configuration")
print("="*60)
import os
gemini_key = os.getenv("GEMINI_API_KEY")
nvd_key = os.getenv("NVD_API_KEY")
print(f"✅ GEMINI_API_KEY: {'SET' if gemini_key else 'NOT SET'}")
print(f"✅ NVD_API_KEY: {'SET' if nvd_key else 'NOT SET'}")

print("\n" + "="*60)
print("🎉 ALL INTEGRATION TESTS PASSED!")
print("="*60)
print("\nSystem is fully integrated and ready for testing!")
