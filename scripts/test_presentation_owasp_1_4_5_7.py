#!/usr/bin/env python3
"""
Presentation Test Script for OWASP 2025 Categories: A01, A04, A05, A07
Designed for live demonstration to professor (ajarn)

Usage:
    python scripts/test_presentation_owasp_1_4_5_7.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.phase1_core import run_phase1_classification
from phase2_engine.core.runner_bridge import run_phase2_from_incident
import time

# Presentation test cases for A01, A04, A05, A07
PRESENTATION_TEST_CASES = {
    "A01": {
        "name": "A01:2025 - Broken Access Control",
        "test_cases": [
            "I changed the number in the URL and saw someone else's profile",
            "Normal staff can access /admin dashboard without admin role",
            "I can edit other users' posts by changing the post ID in the URL",
            "Unauthenticated user can call /export-all-users endpoint",
        ]
    },
    "A04": {
        "name": "A04:2025 - Cryptographic Failures",
        "test_cases": [
            "Our passwords are stored in plain text in the database",
            "The website uses HTTP instead of HTTPS for login",
            "Credit card numbers are stored without encryption",
            "API keys are hardcoded in the source code",
        ]
    },
    "A05": {
        "name": "A05:2025 - Injection",
        "test_cases": [
            "Login works when I type ' OR 1=1 -- as username",
            "Weird syntax appear on web login page",
            "SQL error appears when user types special characters",
            "Attacker sent DROP TABLE users in the query string",
        ]
    },
    "A07": {
        "name": "A07:2025 - Authentication Failures",
        "test_cases": [
            "Any 6-digit code is accepted as OTP",
            "Session never expires even after days",
            "Users can set password to just one character",
            "Password reset link works forever, never expires",
        ]
    }
}


def test_category(category_id: str, test_cases: list, category_name: str):
    """Test a specific OWASP category with multiple test cases."""
    print(f"\n{'='*70}")
    print(f"Testing {category_name}")
    print(f"{'='*70}\n")
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] Test: {test_case}")
        print("   Analyzing...", end=" ", flush=True)
        
        try:
            # Classify the incident
            result = run_phase1_classification(test_case)
            
            label = result.get("label", "unknown")
            confidence = result.get("score", 0.0)
            rationale = result.get("rationale", "No rationale")
            
            # Check if correct category
            expected_labels = {
                "A01": ["broken_access_control"],
                "A04": ["cryptographic_failures", "sensitive_data_exposure"],
                "A05": ["injection", "sql_injection", "xss"],
                "A07": ["broken_authentication", "authentication_failures"],
            }
            
            is_correct = any(
                expected in label.lower() 
                for expected in expected_labels.get(category_id, [])
            )
            
            status = "✅ PASS" if is_correct else "❌ FAIL"
            conf_pct = int(confidence * 100)
            
            print(f"{status} | Confidence: {conf_pct}% | Label: {label}")
            
            if not is_correct:
                print(f"   ⚠️  Expected: {category_id} category, Got: {label}")
            
            results.append({
                "test": test_case,
                "correct": is_correct,
                "confidence": confidence,
                "label": label
            })
            
            # Small delay to avoid rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)[:50]}")
            results.append({
                "test": test_case,
                "correct": False,
                "error": str(e)
            })
    
    # Summary
    correct = sum(1 for r in results if r.get("correct", False))
    total = len(results)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"\n📊 Summary for {category_name}:")
    print(f"   Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"   Average Confidence: {sum(r.get('confidence', 0) for r in results) / total * 100:.1f}%")
    
    return results


def test_playbook_generation():
    """Test that playbooks are generated correctly for each category."""
    print(f"\n{'='*70}")
    print("Testing Playbook Generation")
    print(f"{'='*70}\n")
    
    test_incidents = {
        "A01": {
            "fine_label": "broken_access_control",
            "incident_type": "Broken Access Control",
            "confidence": 0.9,
            "labels": ["broken_access_control"]
        },
        "A04": {
            "fine_label": "cryptographic_failures",
            "incident_type": "Cryptographic Failures",
            "confidence": 0.9,
            "labels": ["cryptographic_failures"]
        },
        "A05": {
            "fine_label": "injection",
            "incident_type": "Injection",
            "confidence": 0.9,
            "labels": ["injection"]
        },
        "A07": {
            "fine_label": "broken_authentication",
            "incident_type": "Authentication Failures",
            "confidence": 0.9,
            "labels": ["broken_authentication"]
        }
    }
    
    for category_id, incident in test_incidents.items():
        print(f"Testing {category_id} playbook generation...", end=" ", flush=True)
        
        try:
            result = run_phase2_from_incident(
                incident=incident,
                merged_with=None,
                dry_run=True,
                opa_url=None
            )
            
            if result.get("status") == "success":
                playbooks = result.get("playbooks", [])
                steps = result.get("steps", [])
                print(f"✅ PASS | Playbooks: {len(playbooks)} | Steps: {len(steps)}")
            else:
                print(f"❌ FAIL | Status: {result.get('status')}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)[:50]}")
        
        time.sleep(0.5)


def main():
    """Run presentation tests for A01, A04, A05, A07."""
    print("\n" + "="*70)
    print("PRESENTATION TEST: OWASP 2025 Categories A01, A04, A05, A07")
    print("="*70)
    print("\nThis script tests the 4 categories required by your professor.")
    print("Categories:")
    print("  - A01: Broken Access Control")
    print("  - A04: Cryptographic Failures")
    print("  - A05: Injection")
    print("  - A07: Authentication Failures")
    print("\nPress Enter to start...")
    input()
    
    all_results = {}
    
    # Test each category
    for category_id in ["A01", "A04", "A05", "A07"]:
        category_data = PRESENTATION_TEST_CASES[category_id]
        results = test_category(
            category_id,
            category_data["test_cases"],
            category_data["name"]
        )
        all_results[category_id] = results
    
    # Test playbook generation
    test_playbook_generation()
    
    # Final summary
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}\n")
    
    total_correct = 0
    total_tests = 0
    
    for category_id, results in all_results.items():
        correct = sum(1 for r in results if r.get("correct", False))
        total = len(results)
        total_correct += correct
        total_tests += total
        
        category_name = PRESENTATION_TEST_CASES[category_id]["name"]
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"{category_id}: {correct}/{total} ({accuracy:.1f}%) - {category_name}")
    
    overall_accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0
    print(f"\n🎯 Overall Accuracy: {total_correct}/{total_tests} ({overall_accuracy:.1f}%)")
    print(f"\n✅ Ready for presentation!")


if __name__ == "__main__":
    main()

