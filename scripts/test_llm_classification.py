#!/usr/bin/env python3
"""
Test script to diagnose LLM classification issues.
Run this to see what the LLM is actually returning.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.llm_adapter import LLMAdapter

def test_classification(text: str):
    """Test LLM classification on a given text."""
    print("="*60)
    print(f"Testing: '{text}'")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not set!")
        return
    
    print(f"✅ API Key: {'SET' if api_key else 'NOT SET'} ({len(api_key) if api_key else 0} chars)")
    print()
    
    try:
        adapter = LLMAdapter(model="gemini-2.5-pro")
        print("✅ LLM Adapter initialized")
        print()
        
        print("Calling LLM...")
        result = adapter.classify_incident(description=text)
        
        print()
        print("="*60)
        print("LLM RESPONSE:")
        print("="*60)
        import json
        print(json.dumps(result, indent=2))
        print()
        
        # Extract key fields
        fine_label = result.get("fine_label", "NOT FOUND")
        confidence = result.get("confidence", 0.0)
        incident_type = result.get("incident_type", "NOT FOUND")
        rationale = result.get("rationale", "NOT FOUND")
        
        print("="*60)
        print("EXTRACTED FIELDS:")
        print("="*60)
        print(f"fine_label: {fine_label}")
        print(f"confidence: {confidence} ({confidence*100:.1f}%)")
        print(f"incident_type: {incident_type}")
        print(f"rationale: {rationale[:100]}...")
        print()
        
        if confidence < 0.5:
            print("⚠️  WARNING: Low confidence (< 50%)")
        elif confidence < 0.7:
            print("⚠️  WARNING: Medium confidence (< 70%)")
        else:
            print("✅ Good confidence (>= 70%)")
            
    except Exception as e:
        print()
        print("="*60)
        print("ERROR OCCURRED:")
        print("="*60)
        import traceback
        print(f"Error: {str(e)}")
        print()
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    # Test cases from user's examples
    test_cases = [
        "my table is missing from the database",
        "weird syyntax appear on web login",
    ]
    
    if len(sys.argv) > 1:
        # Use command line argument if provided
        test_classification(sys.argv[1])
    else:
        # Test all cases
        for test_case in test_cases:
            test_classification(test_case)
            print("\n" + "="*60 + "\n")

