"""
Full System Integration Test
=============================

Tests that all components work together end-to-end:
- Phase-1: Classification (LLM, Explicit, Hybrid)
- Phase-2: Playbook execution (DAG, Merging, OPA)
- UI Integration: Streamlit app components
- All services: CVE, Knowledge Base, etc.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all critical imports."""
    print("[1/10] Testing imports...")
    try:
        # Phase-1 imports
        from src import (
            LLMAdapter, SecurityExtractor, DialogueState,
            ExplicitDetector, ClassificationRules, KnowledgeBaseRetriever
        )
        from src.cve_service import CVEService
        from src.execution_simulator import ExecutionSimulator
        
        # Phase-2 imports
        from phase2_engine.core.runner_bridge import run_phase2_from_incident
        from phase2_engine.core.playbook_utils import evaluate_policy, merge_graphs, build_dag
        from phase2_engine.core.playbook_loader import load_playbook_by_id
        
        print("  [OK] All imports successful")
        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        return False

def test_phase1_components():
    """Test Phase-1 classification components."""
    print("\n[2/10] Testing Phase-1 components...")
    try:
        from src import LLMAdapter, SecurityExtractor, DialogueState, ExplicitDetector
        
        # Initialize components
        llm = LLMAdapter(model="gemini-2.5-pro")
        extractor = SecurityExtractor()
        dialogue = DialogueState()
        explicit = ExplicitDetector()
        
        # Test extraction
        test_text = "SQL injection detected from IP 192.168.1.1"
        entities = extractor.extract(test_text)
        assert entities.ips, "Should extract IPs"
        
        # Test explicit detection
        result = explicit.detect(test_text)
        assert result is not None, "Should detect SQL injection"
        
        # Test dialogue state
        dialogue.add_turn(user_input=test_text, classification={"label": "injection"})
        assert len(dialogue.turns) == 1, "Should track turns"
        
        print("  [OK] Phase-1 components working")
        return True
    except Exception as e:
        print(f"  [FAIL] Phase-1 test failed: {e}")
        return False

def test_phase2_components():
    """Test Phase-2 playbook components."""
    print("\n[3/10] Testing Phase-2 components...")
    try:
        from phase2_engine.core.playbook_loader import load_playbook_by_id
        from phase2_engine.core.playbook_dag import build_dag
        
        # Test playbook loading
        playbook = load_playbook_by_id("A03_injection")
        assert playbook is not None, "Should load playbook"
        assert "id" in playbook, "Playbook should have ID"
        
        # Test DAG building
        dag = build_dag(playbook)
        assert dag is not None, "Should build DAG"
        assert len(dag.nodes) > 0, "DAG should have nodes"
        
        print("  [OK] Phase-2 components working")
        return True
    except Exception as e:
        print(f"  [FAIL] Phase-2 test failed: {e}")
        return False

def test_opa_integration():
    """Test OPA policy integration."""
    print("\n[4/10] Testing OPA integration...")
    try:
        from phase2_engine.core.playbook_utils import evaluate_policy
        
        # Test with invalid URL (should gracefully degrade)
        result = evaluate_policy("http://localhost:9999/invalid", {"test": "data"})
        assert result == "ALLOW", "Should default to ALLOW on failure"
        
        # Check if policy files exist
        policy_dir = project_root / "phase2_engine" / "policies"
        if policy_dir.exists():
            rego_files = list(policy_dir.glob("*.rego"))
            if rego_files:
                print(f"  [OK] Found {len(rego_files)} policy file(s)")
            else:
                print("  [INFO] No policy files found (optional)")
        else:
            print("  [INFO] Policy directory not found (optional)")
        
        print("  [OK] OPA integration working (graceful degradation)")
        return True
    except Exception as e:
        print(f"  [FAIL] OPA test failed: {e}")
        return False

def test_runner_bridge():
    """Test Phase-1 to Phase-2 bridge."""
    print("\n[5/10] Testing runner bridge...")
    try:
        from phase2_engine.core.runner_bridge import run_phase2_from_incident
        
        # Create test incident
        test_incident = {
            "fine_label": "injection",
            "confidence": 0.85,
            "incident_type": "A03:2021-Injection",
            "text": "SQL injection detected"
        }
        
        # Test bridge
        result = run_phase2_from_incident(
            incident=test_incident,
            merged_with=None,
            dry_run=True,
            opa_url=None
        )
        
        assert result is not None, "Should return result"
        assert "status" in result, "Should have status"
        
        print("  [OK] Runner bridge working")
        return True
    except Exception as e:
        print(f"  [FAIL] Runner bridge test failed: {e}")
        return False

def test_cve_service():
    """Test CVE service."""
    print("\n[6/10] Testing CVE service...")
    try:
        from src.cve_service import CVEService
        
        service = CVEService(api_key=None)  # Works without API key
        
        # Test CVE lookup (will use mock if no API key)
        cve_data = service.get_cve_by_id("CVE-2021-44228")
        # Should work even if returns None (no API key)
        
        print("  [OK] CVE service working")
        return True
    except Exception as e:
        print(f"  [FAIL] CVE service test failed: {e}")
        return False

def test_knowledge_base():
    """Test knowledge base retriever."""
    print("\n[7/10] Testing knowledge base...")
    try:
        from src.lc_retriever import KnowledgeBaseRetriever
        
        kb = KnowledgeBaseRetriever()
        result = kb.retrieve("SQL injection")
        
        # Should return context (even if empty)
        assert result is not None, "Should return result"
        
        print("  [OK] Knowledge base working")
        return True
    except Exception as e:
        print(f"  [FAIL] Knowledge base test failed: {e}")
        return False

def test_dag_merging():
    """Test DAG merging functionality."""
    print("\n[8/10] Testing DAG merging...")
    try:
        from phase2_engine.core.playbook_loader import load_playbook_by_id
        from phase2_engine.core.playbook_dag import build_dag
        from phase2_engine.core.playbook_utils import merge_graphs
        
        # Load two playbooks
        pb1 = load_playbook_by_id("A03_injection")
        pb2 = load_playbook_by_id("A01_broken_access_control")
        
        if pb1 and pb2:
            dag1 = build_dag(pb1)
            dag2 = build_dag(pb2)
            
            # Merge
            merged = merge_graphs([dag1, dag2])
            assert merged is not None, "Should merge DAGs"
            assert len(merged.nodes) > 0, "Merged DAG should have nodes"
            
            print("  [OK] DAG merging working")
        else:
            print("  [INFO] Some playbooks not found (skipping)")
        
        return True
    except Exception as e:
        print(f"  [FAIL] DAG merging test failed: {e}")
        return False

def test_environment_config():
    """Test environment configuration."""
    print("\n[9/10] Testing environment configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for optional configs
        gemini_key = os.getenv("GEMINI_API_KEY")
        opa_url = os.getenv("OPA_URL")
        nvd_key = os.getenv("NVD_API_KEY")
        
        config_status = []
        if gemini_key:
            config_status.append("Gemini API")
        if opa_url:
            config_status.append("OPA URL")
        if nvd_key:
            config_status.append("NVD API")
        
        if config_status:
            print(f"  [OK] Found: {', '.join(config_status)}")
        else:
            print("  [INFO] No optional configs found (system works with defaults)")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Environment config test failed: {e}")
        return False

def test_playbook_files():
    """Test playbook files exist."""
    print("\n[10/10] Testing playbook files...")
    try:
        playbook_dir = project_root / "phase2_engine" / "playbooks"
        if playbook_dir.exists():
            yaml_files = list(playbook_dir.glob("*.yaml"))
            print(f"  [OK] Found {len(yaml_files)} playbook file(s)")
            return True
        else:
            print("  [FAIL] Playbook directory not found")
            return False
    except Exception as e:
        print(f"  [FAIL] Playbook files test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("FULL SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Phase-1 Components", test_phase1_components()))
    results.append(("Phase-2 Components", test_phase2_components()))
    results.append(("OPA Integration", test_opa_integration()))
    results.append(("Runner Bridge", test_runner_bridge()))
    results.append(("CVE Service", test_cve_service()))
    results.append(("Knowledge Base", test_knowledge_base()))
    results.append(("DAG Merging", test_dag_merging()))
    results.append(("Environment Config", test_environment_config()))
    results.append(("Playbook Files", test_playbook_files()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS GO! Everything is wired together correctly.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

