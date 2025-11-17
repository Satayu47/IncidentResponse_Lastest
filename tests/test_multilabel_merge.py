"""
tests/test_multilabel_merge.py

Multi-incident / merged playbook tests for Phase-2.

Goal:
- Verify that given multiple OWASP incident labels (e.g. injection + broken_access_control),
  Phase-2 can load multiple playbooks and merge them into a single, valid DAG.
- Ensure:
    * All requested playbooks exist
    * Merged graph is still a DAG (no cycles)
    * Duplicate logical steps are de-duplicated
    * Node count of merged DAG is at least as large as any single DAG
"""

import pytest
import networkx as nx
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase2_engine.core.playbook_utils import (
    load_playbook_by_id,
    build_dag,
    merge_graphs,
    normalize_node,
)


# ---------------------------------------------------------------------------
# 1. Basic single-playbook sanity checks
# ---------------------------------------------------------------------------

# Playbook IDs matching your YAML files in phase2_engine/playbooks/
# A01_broken_access_control.yaml -> "A01_broken_access_control"
# A03_injection.yaml -> "A03_injection"
# etc.
BASE_LABELS = [
    "A01_broken_access_control",
    "A02_cryptographic_failures",
    "A03_injection",
    "A04_insecure_design",
    "A05_misconfiguration",
    "A06_vulnerable_components",
    "A07_authentication_failures",
    "A10_ssrf",
]


@pytest.mark.parametrize("playbook_id", BASE_LABELS)
def test_single_playbook_loads_and_is_dag(playbook_id):
    """Each base OWASP playbook should load and produce a valid DAG."""
    playbook = load_playbook_by_id(playbook_id)
    assert playbook is not None, f"Playbook YAML missing for playbook_id={playbook_id}"

    dag = build_dag(playbook)
    assert isinstance(dag, nx.DiGraph), f"build_dag({playbook_id}) did not return DiGraph"
    assert dag.number_of_nodes() > 0, f"No nodes in DAG for {playbook_id}"
    assert nx.is_directed_acyclic_graph(dag), f"DAG for {playbook_id} has cycles"


# ---------------------------------------------------------------------------
# 2. Multi-label merge scenarios (2 labels)
# ---------------------------------------------------------------------------

MULTI_LABEL_SCENARIOS_2 = [
    (
        "case_injection_plus_bac",
        ["A03_injection", "A01_broken_access_control"],
        "SQL injection on login + normal users can access /admin page",
    ),
    (
        "case_injection_plus_auth",
        ["A03_injection", "A07_authentication_failures"],
        "SQL injection on login combined with weak or broken login checks",
    ),
    (
        "case_bac_plus_auth",
        ["A01_broken_access_control", "A07_authentication_failures"],
        "Normal users can access admin endpoints and login throttling is missing",
    ),
    (
        "case_design_plus_crypto",
        ["A04_insecure_design", "A02_cryptographic_failures"],
        "Insecure design patterns with weak crypto/TLS",
    ),
    (
        "case_bac_plus_misconfig",
        ["A01_broken_access_control", "A05_misconfiguration"],
        "Admin panel exposed due to misconfigured reverse proxy",
    ),
    (
        "case_injection_plus_misconfig",
        ["A03_injection", "A05_misconfiguration"],
        "SQL injection on a debug endpoint accidentally exposed",
    ),
    (
        "case_auth_plus_misconfig",
        ["A07_authentication_failures", "A05_misconfiguration"],
        "Login endpoint left without HTTPS and no lockout policy",
    ),
    (
        "case_auth_plus_vuln_components",
        ["A07_authentication_failures", "A06_vulnerable_components"],
        "Weak authentication with outdated libraries containing CVEs",
    ),
]


@pytest.mark.parametrize("case_id, playbook_ids, description", MULTI_LABEL_SCENARIOS_2)
def test_merge_two_labels_is_valid_dag(case_id, playbook_ids, description):
    """
    For each 2-label scenario:
      - all playbooks must exist
      - single DAGs build successfully
      - merged DAG is acyclic
      - merged DAG has >= max(single DAG sizes)
      - merged DAG has no duplicate logical nodes
    """
    graphs = []
    node_counts = []

    for pb_id in playbook_ids:
        pb = load_playbook_by_id(pb_id)
        assert pb is not None, f"[{case_id}] Missing playbook for playbook_id={pb_id}"

        g = build_dag(pb)
        assert nx.is_directed_acyclic_graph(g), f"[{case_id}] DAG for {pb_id} has cycles"

        graphs.append(g)
        node_counts.append(g.number_of_nodes())

    merged = merge_graphs(graphs)

    assert nx.is_directed_acyclic_graph(merged), f"[{case_id}] merged DAG has cycles"

    # merged DAG should not be smaller than the largest individual DAG
    max_single = max(node_counts)
    assert (
        merged.number_of_nodes() >= max_single
    ), f"[{case_id}] merged DAG smaller than largest single DAG"

    # no duplicate logical steps (based on normalize_node)
    all_hashes = []
    for _, data in merged.nodes(data=True):
        meta = data.get("meta", {})
        h = normalize_node(meta)
        all_hashes.append(h)

    assert len(all_hashes) == len(
        set(all_hashes)
    ), f"[{case_id}] duplicate logical steps found after merge"

    # Optional: basic sanity check that merging actually combined content
    # (merged DAG node count greater than each individual DAG, if they share little)
    if len(set(node_counts)) == 1 and node_counts[0] > 1:
        # If both DAGs were non-trivial and same size, we expect merged to be >= that
        assert merged.number_of_nodes() >= node_counts[0]


# ---------------------------------------------------------------------------
# 3. Multi-label merge scenarios (3 labels)
# ---------------------------------------------------------------------------

MULTI_LABEL_SCENARIOS_3 = [
    (
        "case_injection_bac_auth",
        ["A03_injection", "A01_broken_access_control", "A07_authentication_failures"],
        "SQL injection, normal users can access admin, and login brute force signs",
    ),
    (
        "case_injection_design_crypto",
        ["A03_injection", "A04_insecure_design", "A02_cryptographic_failures"],
        "SQL injection with insecure design patterns and weak crypto/TLS",
    ),
    (
        "case_full_web_stack",
        ["A03_injection", "A01_broken_access_control", "A05_misconfiguration"],
        "Misconfigured web server, broken ACL, and injection on exposed endpoints",
    ),
    (
        "case_auth_vuln_misconfig",
        ["A07_authentication_failures", "A06_vulnerable_components", "A05_misconfiguration"],
        "Authentication bypass via vulnerable library on misconfigured endpoint",
    ),
]


@pytest.mark.parametrize("case_id, playbook_ids, description", MULTI_LABEL_SCENARIOS_3)
def test_merge_three_labels_is_valid_dag(case_id, playbook_ids, description):
    """
    For 3-label scenarios:
      - Same checks as for 2-label merges
      - This simulates more complex, real-world multi-vector incidents.
    """
    graphs = []
    node_counts = []

    for pb_id in playbook_ids:
        pb = load_playbook_by_id(pb_id)
        assert pb is not None, f"[{case_id}] Missing playbook for playbook_id={pb_id}"

        g = build_dag(pb)
        assert nx.is_directed_acyclic_graph(g), f"[{case_id}] DAG for {pb_id} has cycles"

        graphs.append(g)
        node_counts.append(g.number_of_nodes())

    merged = merge_graphs(graphs)
    assert nx.is_directed_acyclic_graph(merged), f"[{case_id}] merged DAG has cycles"

    max_single = max(node_counts)
    assert (
        merged.number_of_nodes() >= max_single
    ), f"[{case_id}] merged DAG smaller than largest single DAG"

    # no duplicate logical steps
    all_hashes = []
    for _, data in merged.nodes(data=True):
        meta = data.get("meta", {})
        h = normalize_node(meta)
        all_hashes.append(h)

    assert len(all_hashes) == len(
        set(all_hashes)
    ), f"[{case_id}] duplicate logical steps found after merge"


# ---------------------------------------------------------------------------
# 4. Helper: ensure we can at least load & merge A01 + A04 + A05 + A07
#    (the 4 OWASP groups your instructor cares about)
# ---------------------------------------------------------------------------

CRITICAL_FOUR = [
    "A01_broken_access_control",
    "A04_insecure_design",
    "A05_misconfiguration",
    "A07_authentication_failures",
]


def test_merge_critical_four_labels():
    """
    Special test: merge the 4 main OWASP categories (A01, A04, A05, A07)
    into one DAG and ensure it's valid.
    """
    graphs = []
    for pb_id in CRITICAL_FOUR:
        pb = load_playbook_by_id(pb_id)
        assert pb is not None, f"[critical_four] Missing playbook for playbook_id={pb_id}"
        g = build_dag(pb)
        assert nx.is_directed_acyclic_graph(g), f"[critical_four] DAG for {pb_id} has cycles"
        graphs.append(g)

    merged = merge_graphs(graphs)
    assert nx.is_directed_acyclic_graph(
        merged
    ), "[critical_four] merged DAG for A01+A04+A05+A07 has cycles"

    # De-duplication check
    all_hashes = [normalize_node(data.get("meta", {})) for _, data in merged.nodes(data=True)]
    assert len(all_hashes) == len(
        set(all_hashes)
    ), "[critical_four] duplicate logical steps found after merging the 4 labels"

    print(f"\n✅ Critical four playbooks merged successfully!")
    print(f"   Individual DAG sizes: {[g.number_of_nodes() for g in graphs]}")
    print(f"   Merged DAG size: {merged.number_of_nodes()} nodes")
    print(f"   Unique logical steps: {len(set(all_hashes))}")


# ---------------------------------------------------------------------------
# 5. Additional test: Verify all 8 playbooks can be merged together
# ---------------------------------------------------------------------------

def test_merge_all_eight_playbooks():
    """
    Stress test: merge all 8 OWASP playbooks into one mega-DAG.
    This simulates a worst-case multi-vector attack.
    """
    graphs = []
    for pb_id in BASE_LABELS:
        pb = load_playbook_by_id(pb_id)
        assert pb is not None, f"[all_eight] Missing playbook for playbook_id={pb_id}"
        g = build_dag(pb)
        assert nx.is_directed_acyclic_graph(g), f"[all_eight] DAG for {pb_id} has cycles"
        graphs.append(g)

    merged = merge_graphs(graphs)
    assert nx.is_directed_acyclic_graph(
        merged
    ), "[all_eight] merged DAG for all 8 playbooks has cycles"

    # De-duplication check
    all_hashes = [normalize_node(data.get("meta", {})) for _, data in merged.nodes(data=True)]
    unique_count = len(set(all_hashes))
    total_count = len(all_hashes)
    
    assert unique_count == total_count, (
        f"[all_eight] duplicate logical steps found: {total_count - unique_count} duplicates"
    )

    print(f"\n✅ All 8 playbooks merged successfully!")
    print(f"   Individual DAG sizes: {[g.number_of_nodes() for g in graphs]}")
    print(f"   Merged DAG size: {merged.number_of_nodes()} nodes")
    print(f"   Total unique logical steps: {unique_count}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s",  # Show print statements
    ])
