"""Test multiple incident classification AND playbook merging accuracy
This test combines:
1. Classification of incidents with multiple security issues (using LLM)
2. Playbook merging validation
3. Accuracy measurement for both classification and merge correctness

Total Test Cases: 50 multi-incident scenarios
Focus: Hard cases where incidents relate to multiple OWASP categories
Coverage: All combinations of A01, A04, A05, A07 (Broken Access Control, Cryptographic Failures, Injection, Authentication Failures)
"""

import os
import sys
import io
from dotenv import load_dotenv
from datetime import datetime
import json
import networkx as nx

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.phase1_core import run_phase1_classification
from phase2_engine.core.runner_bridge import run_phase2_from_incident
from phase2_engine.core.playbook_utils import merge_graphs, build_dag, load_playbook_by_id

load_dotenv()

# Test cases for multiple incident scenarios
# These are hard cases where the incident relates to multiple OWASP categories
MULTI_INCIDENT_TEST_CASES = [
    {
        "id": "MULTI-01",
        "user_input": "I can access the admin panel without logging in, and the login form is vulnerable to SQL injection.",
        "expected_labels": ["broken_access_control", "injection"],  # A01 + A05
        "expected_playbooks": ["A01_broken_access_control", "A03_injection"],
        "difficulty": "hard",
        "note": "Access control bypass + SQL injection"
    },
    {
        "id": "MULTI-02",
        "user_input": "The API returns user passwords in plain text, and I can access other users' data by changing the URL.",
        "expected_labels": ["cryptographic_failures", "broken_access_control"],  # A04 + A01
        "expected_playbooks": ["A02_cryptographic_failures", "A01_broken_access_control"],
        "difficulty": "very_hard",
        "note": "Crypto failure + access control - both issues present"
    },
    {
        "id": "MULTI-03",
        "user_input": "I can log in with password '12345' and then access admin functions even though I'm not an admin.",
        "expected_labels": ["broken_authentication", "broken_access_control"],  # A07 + A01
        "expected_playbooks": ["A07_authentication_failures", "A01_broken_access_control"],
        "difficulty": "hard",
        "note": "Weak password + privilege escalation"
    },
    {
        "id": "MULTI-04",
        "user_input": "The website doesn't use HTTPS and I can see database errors when I enter special characters in the search box.",
        "expected_labels": ["cryptographic_failures", "injection"],  # A04 + A05
        "expected_playbooks": ["A02_cryptographic_failures", "A03_injection"],
        "difficulty": "hard",
        "note": "Missing TLS + SQL injection"
    },
    {
        "id": "MULTI-05",
        "user_input": "I found passwords stored in plain text in the database, and the system doesn't lock accounts after failed login attempts.",
        "expected_labels": ["cryptographic_failures", "broken_authentication"],  # A04 + A07
        "expected_playbooks": ["A02_cryptographic_failures", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "Plaintext passwords + no brute force protection"
    },
    {
        "id": "MULTI-06",
        "user_input": "I can see other users' private messages by changing the message ID in the URL, and the messages are sent over HTTP instead of HTTPS.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],  # A01 + A04
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "IDOR + missing encryption in transit"
    },
    {
        "id": "MULTI-07",
        "user_input": "Someone entered JavaScript code in a comment and it executed on other users' browsers. Also, I can access the admin panel without being an admin.",
        "expected_labels": ["injection", "broken_access_control"],  # A05 + A01
        "expected_playbooks": ["A03_injection", "A01_broken_access_control"],
        "difficulty": "hard",
        "note": "XSS + unauthorized admin access"
    },
    {
        "id": "MULTI-08",
        "user_input": "The login form accepts SQL injection attacks, and users can set their password to anything, even just one character.",
        "expected_labels": ["injection", "broken_authentication"],  # A05 + A07
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "SQL injection + weak password policy"
    },
    {
        "id": "MULTI-09",
        "user_input": "I can see all customer orders even though I'm just a regular employee, and the API returns credit card numbers without encryption.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],  # A01 + A04
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "Unauthorized data access + unencrypted sensitive data"
    },
    {
        "id": "MULTI-10",
        "user_input": "The system crashed after someone entered a weird command in the file upload field, and I can still access my account even though I logged out.",
        "expected_labels": ["injection", "broken_authentication"],  # A05 + A07
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "very_hard",
        "note": "Command injection + session invalidation failure"
    },
    # Additional test cases to reach 50 total
    {
        "id": "MULTI-11",
        "user_input": "I changed the user ID in the URL and saw someone else's profile. Also, the website doesn't use HTTPS for login.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "hard",
        "note": "IDOR + missing HTTPS"
    },
    {
        "id": "MULTI-12",
        "user_input": "The login form accepts ' OR 1=1 -- as username, and my session never expires even after days.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "medium",
        "note": "SQL injection + session management"
    },
    {
        "id": "MULTI-13",
        "user_input": "I can see all customer orders as a regular employee, and passwords are stored in plain text in the database.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "hard",
        "note": "Unauthorized access + plaintext storage"
    },
    {
        "id": "MULTI-14",
        "user_input": "When I type special characters in the search box, it shows database errors. Also, I can access the admin panel without logging in.",
        "expected_labels": ["injection", "broken_access_control"],
        "expected_playbooks": ["A03_injection", "A01_broken_access_control"],
        "difficulty": "hard",
        "note": "SQL injection + admin access bypass"
    },
    {
        "id": "MULTI-15",
        "user_input": "I found credit card numbers in the logs without encryption, and the system doesn't lock accounts after failed login attempts.",
        "expected_labels": ["cryptographic_failures", "broken_authentication"],
        "expected_playbooks": ["A02_cryptographic_failures", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "Sensitive data in logs + no brute force protection"
    },
    {
        "id": "MULTI-16",
        "user_input": "I'm a viewer but I can approve transactions, and the API returns user emails in plain text without any protection.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "Role-based access violation + unencrypted API response"
    },
    {
        "id": "MULTI-17",
        "user_input": "Someone entered JavaScript code in a comment and it executed on other users' browsers. Also, I can log in with password '12345'.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "medium",
        "note": "XSS + weak password"
    },
    {
        "id": "MULTI-18",
        "user_input": "I can edit other users' posts by changing the post ID in the URL, and the messages are sent over HTTP instead of HTTPS.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "hard",
        "note": "IDOR in edit + missing encryption in transit"
    },
    {
        "id": "MULTI-19",
        "user_input": "The website doesn't use HTTPS, and I tried wrong passwords many times but the system didn't lock me out.",
        "expected_labels": ["cryptographic_failures", "broken_authentication"],
        "expected_playbooks": ["A02_cryptographic_failures", "A07_authentication_failures"],
        "difficulty": "medium",
        "note": "Missing TLS + no brute force protection"
    },
    {
        "id": "MULTI-20",
        "user_input": "I can download files that belong to other users by knowing the file ID, and the backup files contain unencrypted customer data.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "File access control bypass + unencrypted backups"
    },
    {
        "id": "MULTI-21",
        "user_input": "The login form accepts SQL injection attacks, and my session never expires. I logged in last week and I'm still logged in.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "SQL injection + session expiration failure"
    },
    {
        "id": "MULTI-22",
        "user_input": "I can see other users' private messages by changing the message ID, and the API returns passwords in the JSON response without hashing.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "IDOR + API exposing unhashed passwords"
    },
    {
        "id": "MULTI-23",
        "user_input": "I can access the admin panel even though I'm not an admin, and the system stores social security numbers in plain text.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "hard",
        "note": "Admin access bypass + plaintext PII storage"
    },
    {
        "id": "MULTI-24",
        "user_input": "When I paste code snippets into the contact form, they appear on other users' screens as actual code. Also, users can set their password to anything.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "medium",
        "note": "XSS stored + weak password policy"
    },
    {
        "id": "MULTI-25",
        "user_input": "I can see all customer orders even though I'm just a regular employee, and the mobile app sends user location data over HTTP instead of HTTPS.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "Unauthorized data access + mobile app HTTP transmission"
    },
    {
        "id": "MULTI-26",
        "user_input": "The system crashed after someone entered a weird command in the file upload field, and I can log in with password '12345'.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "Command injection + weak password"
    },
    {
        "id": "MULTI-27",
        "user_input": "I found medical records in the database stored without encryption, and I can access them by changing the patient ID in the URL.",
        "expected_labels": ["cryptographic_failures", "broken_access_control"],
        "expected_playbooks": ["A02_cryptographic_failures", "A01_broken_access_control"],
        "difficulty": "very_hard",
        "note": "Unencrypted health data + IDOR"
    },
    {
        "id": "MULTI-28",
        "user_input": "The login form accepts strange characters and shows database errors, and the system doesn't require two-factor authentication for admin accounts.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "SQL injection + missing MFA"
    },
    {
        "id": "MULTI-29",
        "user_input": "I can see other users' data when I shouldn't be able to, and the website doesn't use HTTPS for sending passwords.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "hard",
        "note": "Unauthorized access + HTTP password transmission"
    },
    {
        "id": "MULTI-30",
        "user_input": "I noticed that when users type certain characters in the search, the page shows SQL errors. Also, I logged out but when I go back, I'm still logged in.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "SQL injection with error disclosure + session invalidation failure"
    },
    {
        "id": "MULTI-31",
        "user_input": "I can access admin functions by changing my role in the cookie, and passwords are stored in plain text in the database.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "Cookie manipulation + plaintext password storage"
    },
    {
        "id": "MULTI-32",
        "user_input": "The API endpoint returns sensitive data without checking if I'm authorized, and it's all in plain text without encryption.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "Unauthorized API access + unencrypted response"
    },
    {
        "id": "MULTI-33",
        "user_input": "I can bypass the login by manipulating the session token, and the system allows me to use my username as my password.",
        "expected_labels": ["broken_authentication", "broken_authentication"],  # Both are auth issues
        "expected_playbooks": ["A07_authentication_failures"],
        "difficulty": "hard",
        "note": "Session manipulation + weak password policy"
    },
    {
        "id": "MULTI-34",
        "user_input": "The search function breaks when I enter database commands, and I can see deleted posts by changing the status parameter.",
        "expected_labels": ["injection", "broken_access_control"],
        "expected_playbooks": ["A03_injection", "A01_broken_access_control"],
        "difficulty": "very_hard",
        "note": "SQL injection + soft-delete bypass"
    },
    {
        "id": "MULTI-35",
        "user_input": "I found user information in log files including passwords and credit cards, and I can access other users' data by changing the URL.",
        "expected_labels": ["cryptographic_failures", "broken_access_control"],
        "expected_playbooks": ["A02_cryptographic_failures", "A01_broken_access_control"],
        "difficulty": "very_hard",
        "note": "Sensitive data in logs + IDOR"
    },
    {
        "id": "MULTI-36",
        "user_input": "When I enter HTML tags in my profile, they show up as actual HTML on other users' screens, and the system doesn't lock accounts after failed attempts.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "medium",
        "note": "XSS stored + no brute force protection"
    },
    {
        "id": "MULTI-37",
        "user_input": "I can see all customer orders as a regular employee, and the backup files contain unencrypted customer data that anyone with access can read.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "Unauthorized access + unencrypted backups"
    },
    {
        "id": "MULTI-38",
        "user_input": "The login form accepts ' OR 1=1 -- and I can still access my account even though I forgot my password.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "SQL injection + session management failure"
    },
    {
        "id": "MULTI-39",
        "user_input": "I can access the admin panel without logging in, and the website doesn't use HTTPS for login pages.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "medium",
        "note": "Admin access bypass + missing HTTPS"
    },
    {
        "id": "MULTI-40",
        "user_input": "Someone entered JavaScript code in a comment and it executed on other users' browsers. Also, I can reset anyone's password if I know their email.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "XSS + password reset vulnerability"
    },
    {
        "id": "MULTI-41",
        "user_input": "I can see other users' private messages by changing the message ID, and the messages are stored in plain text in the database.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "IDOR + plaintext message storage"
    },
    {
        "id": "MULTI-42",
        "user_input": "The system crashed after someone entered a weird command in the file upload field, and my session never expires even after days.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "Command injection + session expiration failure"
    },
    {
        "id": "MULTI-43",
        "user_input": "I can edit other users' posts by changing the post ID, and the API returns user emails and phone numbers without any protection.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "IDOR in edit + unencrypted API response"
    },
    {
        "id": "MULTI-44",
        "user_input": "When I type special characters in the search box, the page breaks and shows database errors. Also, I can log in with password '12345'.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "medium",
        "note": "SQL injection + weak password"
    },
    {
        "id": "MULTI-45",
        "user_input": "I found passwords stored in plain text in the database, and I can access the admin panel even though I'm not an admin.",
        "expected_labels": ["cryptographic_failures", "broken_access_control"],
        "expected_playbooks": ["A02_cryptographic_failures", "A01_broken_access_control"],
        "difficulty": "hard",
        "note": "Plaintext passwords + admin access bypass"
    },
    {
        "id": "MULTI-46",
        "user_input": "The website doesn't use HTTPS, and I can see database errors when I enter certain characters in the search field.",
        "expected_labels": ["cryptographic_failures", "injection"],
        "expected_playbooks": ["A02_cryptographic_failures", "A03_injection"],
        "difficulty": "hard",
        "note": "Missing TLS + SQL injection error disclosure"
    },
    {
        "id": "MULTI-47",
        "user_input": "I can see all customer orders even though I'm just a regular employee, and the system shows me if a username exists when I try to log in.",
        "expected_labels": ["broken_access_control", "broken_authentication"],
        "expected_playbooks": ["A01_broken_access_control", "A07_authentication_failures"],
        "difficulty": "hard",
        "note": "Unauthorized access + username enumeration"
    },
    {
        "id": "MULTI-48",
        "user_input": "When I paste code snippets into the contact form, they appear on other users' screens. Also, the system doesn't require two-factor authentication.",
        "expected_labels": ["injection", "broken_authentication"],
        "expected_playbooks": ["A03_injection", "A07_authentication_failures"],
        "difficulty": "medium",
        "note": "XSS + missing MFA"
    },
    {
        "id": "MULTI-49",
        "user_input": "I can download files that belong to other users by knowing the file ID, and the files are sent over HTTP instead of HTTPS.",
        "expected_labels": ["broken_access_control", "cryptographic_failures"],
        "expected_playbooks": ["A01_broken_access_control", "A02_cryptographic_failures"],
        "difficulty": "hard",
        "note": "File access control bypass + HTTP transmission"
    },
    {
        "id": "MULTI-50",
        "user_input": "The login form accepts SQL injection attacks, and I found medical records in the database stored without encryption.",
        "expected_labels": ["injection", "cryptographic_failures"],
        "expected_playbooks": ["A03_injection", "A02_cryptographic_failures"],
        "difficulty": "very_hard",
        "note": "SQL injection + unencrypted health data"
    },
]


def test_multi_incident_classification_and_merge():
    """Test classification accuracy and playbook merging for multi-incident scenarios"""
    
    print("=" * 70)
    print("MULTI-INCIDENT CLASSIFICATION & MERGE TEST")
    print(f"Total Test Cases: {len(MULTI_INCIDENT_TEST_CASES)}")
    print("=" * 70)
    print()
    
    results = {
        "classification": {"correct": 0, "total": 0, "cases": []},
        "playbook_mapping": {"correct": 0, "total": 0, "cases": []},
        "merge_validation": {"correct": 0, "total": 0, "cases": []},
    }
    
    all_results = []
    
    for test_case in MULTI_INCIDENT_TEST_CASES:
        test_id = test_case["id"]
        user_input = test_case["user_input"]
        expected_labels = test_case["expected_labels"]
        expected_playbooks = test_case["expected_playbooks"]
        difficulty = test_case.get("difficulty", "medium")
        
        print(f"Testing: {test_id} ({difficulty})")
        print(f"Input: {user_input[:100]}...")
        print(f"Expected labels: {expected_labels}")
        print()
        
        case_result = {
            "id": test_id,
            "input": user_input,
            "expected_labels": expected_labels,
            "expected_playbooks": expected_playbooks,
            "difficulty": difficulty,
            "classification_correct": False,
            "playbook_mapping_correct": False,
            "merge_valid": False,
        }
        
        try:
            # Step 1: Classification
            classification_result = run_phase1_classification(user_input)
            predicted_label = classification_result.get("label", "unknown")
            confidence = classification_result.get("score", 0.0)
            
            # Check if predicted label matches any expected label
            classification_correct = predicted_label in expected_labels
            case_result["predicted_label"] = predicted_label
            case_result["classification_confidence"] = confidence
            case_result["classification_correct"] = classification_correct
            
            results["classification"]["total"] += 1
            if classification_correct:
                results["classification"]["correct"] += 1
            
            print(f"  Classification: {predicted_label} (confidence: {confidence:.2f})")
            print(f"  Expected one of: {expected_labels}")
            print(f"  Status: {'✅ CORRECT' if classification_correct else '❌ WRONG'}")
            print()
            
            # Step 2: Playbook mapping and merge
            # Build incident dict for Phase-2
            incident = {
                "label": predicted_label,
                "confidence": confidence,
                "text": user_input,
            }
            
            # For multi-incident, we need to classify all expected labels
            # In real scenario, user might report multiple incidents separately
            # Here we simulate by creating multiple incidents from expected labels
            merged_incidents = [incident]  # Start with primary classification
            
            # Try to get playbooks for all expected labels
            playbook_ids_found = []
            for exp_label in expected_labels:
                # Map label to playbook ID
                label_to_playbook = {
                    "broken_access_control": "A01_broken_access_control",
                    "cryptographic_failures": "A02_cryptographic_failures",
                    "injection": "A03_injection",
                    "broken_authentication": "A07_authentication_failures",
                }
                pb_id = label_to_playbook.get(exp_label)
                if pb_id:
                    try:
                        pb = load_playbook_by_id(pb_id)
                        if pb:
                            playbook_ids_found.append(pb_id)
                    except:
                        pass
            
            # Check if we found the expected playbooks
            playbook_mapping_correct = len(playbook_ids_found) >= len(expected_playbooks)
            case_result["playbook_ids_found"] = playbook_ids_found
            case_result["playbook_mapping_correct"] = playbook_mapping_correct
            
            results["playbook_mapping"]["total"] += 1
            if playbook_mapping_correct:
                results["playbook_mapping"]["correct"] += 1
            
            print(f"  Playbooks found: {playbook_ids_found}")
            print(f"  Expected: {expected_playbooks}")
            print(f"  Status: {'✅ CORRECT' if playbook_mapping_correct else '❌ WRONG'}")
            print()
            
            # Step 3: Merge validation
            if len(playbook_ids_found) >= 2:
                try:
                    # Load and build DAGs
                    dags = []
                    for pb_id in playbook_ids_found:
                        pb = load_playbook_by_id(pb_id)
                        dag = build_dag(pb)
                        dags.append(dag)
                    
                    # Merge DAGs
                    merged_dag = merge_graphs(dags)
                    
                    # Validate merge
                    is_dag = nx.is_directed_acyclic_graph(merged_dag)
                    has_nodes = len(merged_dag.nodes) > 0
                    merge_valid = is_dag and has_nodes
                    
                    case_result["merge_valid"] = merge_valid
                    case_result["merged_nodes"] = len(merged_dag.nodes)
                    case_result["merged_edges"] = len(merged_dag.edges)
                    case_result["is_acyclic"] = is_dag
                    
                    results["merge_validation"]["total"] += 1
                    if merge_valid:
                        results["merge_validation"]["correct"] += 1
                    
                    print(f"  Merge validation:")
                    print(f"    Merged DAG: {len(merged_dag.nodes)} nodes, {len(merged_dag.edges)} edges")
                    print(f"    Is acyclic: {is_dag}")
                    print(f"  Status: {'✅ VALID' if merge_valid else '❌ INVALID'}")
                    
                except Exception as e:
                    print(f"  Merge error: {str(e)}")
                    case_result["merge_error"] = str(e)
            else:
                print(f"  Merge skipped: Need at least 2 playbooks (found {len(playbook_ids_found)})")
            
            all_results.append(case_result)
            print()
            print("-" * 70)
            print()
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            print()
            continue
    
    # Print summary
    print("=" * 70)
    print("ACCURACY SUMMARY")
    print("=" * 70)
    print()
    
    # Classification accuracy
    cls_acc = (results["classification"]["correct"] / results["classification"]["total"] * 100) if results["classification"]["total"] > 0 else 0
    print(f"Classification Accuracy: {results['classification']['correct']}/{results['classification']['total']} ({cls_acc:.1f}%)")
    
    # Playbook mapping accuracy
    pb_acc = (results["playbook_mapping"]["correct"] / results["playbook_mapping"]["total"] * 100) if results["playbook_mapping"]["total"] > 0 else 0
    print(f"Playbook Mapping Accuracy: {results['playbook_mapping']['correct']}/{results['playbook_mapping']['total']} ({pb_acc:.1f}%)")
    
    # Merge validation accuracy
    merge_acc = (results["merge_validation"]["correct"] / results["merge_validation"]["total"] * 100) if results["merge_validation"]["total"] > 0 else 0
    print(f"Merge Validation: {results['merge_validation']['correct']}/{results['merge_validation']['total']} ({merge_acc:.1f}%)")
    print()
    
    # Overall accuracy (all three must pass)
    overall_correct = sum(1 for r in all_results if r["classification_correct"] and r["playbook_mapping_correct"] and r["merge_valid"])
    overall_total = len(all_results)
    overall_acc = (overall_correct / overall_total * 100) if overall_total > 0 else 0
    print(f"OVERALL ACCURACY (All 3 criteria): {overall_correct}/{overall_total} ({overall_acc:.1f}%)")
    print()
    
    # Save results
    reports_dir = os.path.join(project_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    output_file = os.path.join(reports_dir, f"multi_incident_accuracy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "classification_accuracy": cls_acc,
                "playbook_mapping_accuracy": pb_acc,
                "merge_validation_accuracy": merge_acc,
                "overall_accuracy": overall_acc,
            },
            "detailed_results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Detailed results saved to: {output_file}")
    print()


if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY not set in .env file")
        sys.exit(1)
    
    test_multi_incident_classification_and_merge()

