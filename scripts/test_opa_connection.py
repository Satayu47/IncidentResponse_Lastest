"""
Test OPA Server Connection
===========================

Quick script to verify OPA server is running and policies are loaded.
"""

import requests
import json
from pathlib import Path

OPA_BASE_URL = "http://localhost:8181"

def test_health():
    """Test if OPA server is healthy."""
    try:
        response = requests.get(f"{OPA_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✓ OPA server is healthy")
            return True
        else:
            print(f"✗ OPA server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to OPA server. Is it running?")
        print("  Start with: docker run -d -p 8181:8181 --name opa-server openpolicyagent/opa run --server")
        return False
    except Exception as e:
        print(f"✗ Error checking health: {e}")
        return False

def test_playbook_policy():
    """Test playbook policy evaluation."""
    print("\n[Testing Playbook Policy]")
    
    # Test case 1: Low-risk action should be allowed
    test_input = {
        "input": {
            "action": {
                "risk_level": "low",
                "type": "send_alert"
            },
            "incident": {
                "severity": "medium"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{OPA_BASE_URL}/v1/data/playbook/result",
            json=test_input,
            timeout=2
        )
        
        if response.status_code == 200:
            result = response.json()
            decision = result.get("result", "UNKNOWN")
            print(f"  Test 1 (low-risk action): {decision}")
            
            if decision == "ALLOW":
                print("  ✓ Policy working correctly")
                return True
            else:
                print("  ⚠ Unexpected result")
                return False
        else:
            print(f"  ✗ Policy evaluation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error testing policy: {e}")
        return False

def test_incident_policy():
    """Test incident policy evaluation."""
    print("\n[Testing Incident Policy]")
    
    # Test case: High confidence, high severity
    test_input = {
        "input": {
            "confidence": 0.90,
            "severity": "high",
            "owasp_category": "A03:2021-Injection"
        }
    }
    
    try:
        response = requests.post(
            f"{OPA_BASE_URL}/v1/data/incident/result",
            json=test_input,
            timeout=2
        )
        
        if response.status_code == 200:
            result = response.json()
            decision = result.get("result", {})
            can_automate = decision.get("can_automate", False)
            print(f"  Test (high confidence): can_automate = {can_automate}")
            
            if can_automate:
                print("  ✓ Policy working correctly")
                return True
            else:
                print("  ⚠ Unexpected result")
                return False
        else:
            print(f"  ✗ Policy evaluation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error testing policy: {e}")
        return False

def main():
    print("=== OPA Connection Test ===\n")
    
    # Test 1: Health check
    print("[1/3] Health Check")
    if not test_health():
        print("\n⚠ OPA server is not running. Run setup script first:")
        print("  Windows: .\\scripts\\setup_opa.ps1")
        print("  Linux/Mac: ./scripts/setup_opa.sh")
        return
    
    # Test 2: Playbook policy
    print("\n[2/3] Playbook Policy Test")
    playbook_ok = test_playbook_policy()
    
    # Test 3: Incident policy
    print("\n[3/3] Incident Policy Test")
    incident_ok = test_incident_policy()
    
    # Summary
    print("\n=== Summary ===")
    if playbook_ok and incident_ok:
        print("✓ All tests passed! OPA is configured correctly.")
        print("\nYou can now use OPA in your application:")
        print("  OPA_URL=http://localhost:8181/v1/data/playbook/allow")
    else:
        print("⚠ Some tests failed. Check OPA server logs:")
        print("  docker logs opa-server")

if __name__ == "__main__":
    main()

