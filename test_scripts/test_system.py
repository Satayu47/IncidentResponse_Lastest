#!/usr/bin/env python3
"""Quick system integration test."""

import sys
sys.path.insert(0, '.')

from phase2_engine.core.playbook_utils import load_playbook_by_id, build_dag, merge_graphs
import networkx as nx

def test_critical_four():
    """Test the critical four playbooks merge (A01, A04, A05, A07)."""
    print("🎯 Critical Four Playbooks Test")
    print("=" * 60)
    
    playbooks = [
        'A01_broken_access_control',
        'A04_insecure_design', 
        'A05_misconfiguration',
        'A07_authentication_failures'
    ]
    
    # Load and build DAGs
    dags = []
    for pid in playbooks:
        playbook = load_playbook_by_id(pid)
        dag = build_dag(playbook)
        dags.append(dag)
        print(f"  ✓ {pid}: {len(dag.nodes())} nodes, {len(dag.edges())} edges")
    
    # Merge
    merged = merge_graphs(dags)
    sizes = [len(d.nodes()) for d in dags]
    
    print(f"\n📊 Merge Results:")
    print(f"  Individual sizes: {sizes}")
    print(f"  Total if concatenated: {sum(sizes)} nodes")
    print(f"  Merged DAG: {len(merged.nodes())} nodes")
    print(f"  Deduplication saved: {sum(sizes) - len(merged.nodes())} nodes")
    print(f"  Edges in merged DAG: {len(merged.edges())}")
    print(f"  Is acyclic: {nx.is_directed_acyclic_graph(merged)}")
    
    # Validation
    assert len(merged.nodes()) > 0, "Merged DAG has no nodes"
    assert nx.is_directed_acyclic_graph(merged), "Merged DAG has cycles!"
    
    print(f"\n✅ All validations passed!")
    return True

def test_all_eight():
    """Test all eight playbooks merge."""
    print("\n🎯 All Eight Playbooks Test")
    print("=" * 60)
    
    playbooks = [
        'A01_broken_access_control',
        'A02_cryptographic_failures',
        'A03_injection',
        'A04_insecure_design',
        'A05_misconfiguration',
        'A06_vulnerable_components',
        'A07_authentication_failures',
        'A10_ssrf'
    ]
    
    # Load and build DAGs
    dags = []
    for pid in playbooks:
        playbook = load_playbook_by_id(pid)
        dag = build_dag(playbook)
        dags.append(dag)
    
    # Merge
    merged = merge_graphs(dags)
    sizes = [len(d.nodes()) for d in dags]
    
    print(f"  Individual sizes: {sizes}")
    print(f"  Total if concatenated: {sum(sizes)} nodes")
    print(f"  Merged DAG: {len(merged.nodes())} nodes")
    print(f"  Deduplication saved: {sum(sizes) - len(merged.nodes())} nodes")
    print(f"  Is acyclic: {nx.is_directed_acyclic_graph(merged)}")
    
    assert len(merged.nodes()) > 0, "Merged DAG has no nodes"
    assert nx.is_directed_acyclic_graph(merged), "Merged DAG has cycles!"
    
    print(f"\n✅ All eight playbooks merged successfully!")
    return True

if __name__ == '__main__':
    try:
        test_critical_four()
        test_all_eight()
        print("\n" + "=" * 60)
        print("🎉 SYSTEM VALIDATED - All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
