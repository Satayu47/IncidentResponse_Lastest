"""
Quick test to verify Gemini API key works
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Set API key if provided
if len(sys.argv) > 1:
    os.environ["GEMINI_API_KEY"] = sys.argv[1]
elif not os.getenv("GEMINI_API_KEY"):
    print("[ERROR] GEMINI_API_KEY not set")
    print("Usage: python scripts/test_gemini_key.py <your_api_key>")
    print("Or set: $env:GEMINI_API_KEY = 'your_key'")
    sys.exit(1)

from src.llm_adapter import LLMAdapter

print("Testing Gemini API key...")
print(f"Key: {os.getenv('GEMINI_API_KEY', 'Not set')[:20]}...")

try:
    adapter = LLMAdapter(model="gemini-2.5-pro")
    result = adapter.classify_incident("SQL injection detected from IP 192.168.1.1")
    
    print("[OK] API key is valid!")
    print(f"Test classification: {result.get('fine_label', 'unknown')}")
    print(f"Confidence: {result.get('confidence', 0.0):.2f}")
    print("\nYou can now run the improved accuracy comparison!")
    
except Exception as e:
    print(f"[ERROR] API key test failed: {e}")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. API quota exceeded")
    print("  3. Network connection issue")
    sys.exit(1)

