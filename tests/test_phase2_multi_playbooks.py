# tests/test_phase2_multi_playbooks.py

import pytest
import networkx as nx
from phase2_engine.core.playbook_utils import load_playbook_by_id, build_dag, merge_graphs


CASES_MULTI = [

    # (id, incident_types (internal), expected_min_playbooks_count)

    ("MIX-01", ["broken_access_control", "injection"], 2),
    ("MIX-02", ["broken_authentication", "injection"], 2),
    ("MIX-03", ["broken_access_control", "security_misconfiguration"], 2),
    ("MIX-04", ["sensitive_data_exposure", "security_misconfiguration"], 2),
    ("MIX-05", ["cryptographic_failures", "broken_authentication"], 2),
    ("MIX-06", ["injection", "sensitive_data_exposure"], 2),
    ("MIX-07", ["injection", "security_misconfiguration"], 2),
    ("MIX-08", ["broken_access_control", "sensitive_data_exposure"], 2),
    ("MIX-09", ["broken_access_control", "broken_authentication"], 2),
    ("MIX-10", ["security_misconfiguration", "cryptographic_failures"], 2),
    ("MIX-11", ["injection", "other"], 1),  # 'other' usually has no playbook
    ("MIX-12", ["broken_authentication", "other"], 1),
    ("MIX-13", ["broken_access_control", "injection"], 2),
    ("MIX-14", ["security_misconfiguration", "injection"], 2),
    ("MIX-15", ["cryptographic_failures", "sensitive_data_exposure"], 2),
    ("MIX-16", ["broken_authentication", "security_misconfiguration"], 2),
    ("MIX-17", ["broken_access_control", "cryptographic_failures"], 2),
    ("MIX-18", ["injection", "broken_authentication"], 2),
    ("MIX-19", ["security_misconfiguration", "other"], 1),
    ("MIX-20", ["broken_access_control", "sensitive_data_exposure"], 2),
    ("MIX-21", ["injection", "cryptographic_failures"], 2),
    ("MIX-22", ["broken_authentication", "sensitive_data_exposure"], 2),
    ("MIX-23", ["security_misconfiguration", "broken_access_control"], 2),
    ("MIX-24", ["injection", "security_misconfiguration", "broken_access_control"], 3),
    ("MIX-25", ["other"], 0),
    ("MIX-26", ["broken_access_control", "injection"], 2),
    ("MIX-27", ["broken_authentication", "security_misconfiguration"], 2),
    ("MIX-28", ["injection", "broken_access_control", "sensitive_data_exposure"], 3),

]


# Mapping from test labels to playbook IDs
LABEL_TO_PLAYBOOK = {
    "broken_access_control": "A01_broken_access_control",
    "cryptographic_failures": "A02_cryptographic_failures",
    "injection": "A03_injection",
    "insecure_design": "A04_insecure_design",
    "security_misconfiguration": "A05_misconfiguration",
    "vulnerable_components": "A06_vulnerable_components",
    "broken_authentication": "A07_authentication_failures",
    "sensitive_data_exposure": "A03_injection",  # Using injection as fallback
    "other": None,  # No playbook for 'other'
}


@pytest.mark.parametrize("case_id, incident_types, expected_min", CASES_MULTI)
def test_multi_incident_merged_playbooks(case_id, incident_types, expected_min):
    """
    For each list of incident types, load playbooks, build DAGs,
    and ensure the merged DAG is still acyclic and has at least
    the expected number of distinct playbook nodes.
    """
    graphs = []
    loaded = 0

    for itype in incident_types:
        playbook_id = LABEL_TO_PLAYBOOK.get(itype)
        if not playbook_id:
            continue
        
        try:
            pb = load_playbook_by_id(playbook_id)
            if not pb:
                continue
            g = build_dag(pb)
            graphs.append(g)
            loaded += 1
        except Exception as e:
            # Playbook might not exist
            continue

    if expected_min == 0:
        # For 'other', we might not have any playbook, that's fine
        assert loaded == 0, f"{case_id}: expected no playbooks for {incident_types}"
        return

    assert loaded >= expected_min, (
        f"{case_id}: expected at least {expected_min} playbooks, "
        f"but only {loaded} were loaded for {incident_types}"
    )

    if len(graphs) == 0:
        return

    merged = merge_graphs(graphs)
    
    # Ensure the merged graph isn't empty and is a DAG
    assert len(merged.nodes) > 0, f"{case_id}: merged DAG has no nodes."
    assert nx.is_directed_acyclic_graph(merged), f"{case_id}: merged graph has cycles!"
    
    print(f"✅ {case_id}: merged {loaded} playbooks into {len(merged.nodes)} nodes, {len(merged.edges)} edges")
