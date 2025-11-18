#!/usr/bin/env python3
"""Quick test to verify new Gemini API key works"""

import os
import sys
import io
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

load_dotenv()

from src.llm_adapter import LLMAdapter

print("=" * 70)
print("Testing New Gemini API Key")
print("=" * 70)
print()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

print(f"✅ API Key loaded: {api_key[:20]}...")
print()

try:
    adapter = LLMAdapter()
    print("✅ LLM Adapter initialized")
    
    # Test with a simple classification
    print("\nTesting classification...")
    result = adapter.classify_incident("I can see other users data by changing the URL")
    
    category = result.get("category", "N/A")
    confidence = result.get("confidence", 0.0)
    fine_label = result.get("fine_label", "N/A")
    
    print(f"✅ Classification successful!")
    print(f"   Category: {category}")
    print(f"   Fine Label: {fine_label}")
    print(f"   Confidence: {confidence:.2f}")
    print()
    print("=" * 70)
    print("✅ API Key is working correctly!")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

