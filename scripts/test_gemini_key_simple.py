#!/usr/bin/env python3
"""
Simple test to verify Gemini API key is working.
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

import google.generativeai as genai

def test_api_key():
    """Test if Gemini API key is valid."""
    print("="*60)
    print("Testing Gemini API Key")
    print("="*60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not set in environment!")
        print("   Set it in .env file or environment variable")
        return False
    
    print(f"✅ API Key found: {len(api_key)} characters")
    print(f"   First 10 chars: {api_key[:10]}...")
    print()
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("✅ Gemini configured")
        
        # Create model
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        print("✅ Model created: gemini-2.5-pro")
        print()
        
        # Test simple call
        print("Testing API call...")
        response = model.generate_content(
            "Say 'Hello' in one word.",
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=10
            )
        )
        
        print(f"✅ API call successful!")
        print(f"   Response: {response.text}")
        print()
        
        # Test JSON response
        print("Testing JSON response...")
        response = model.generate_content(
            'Return JSON: {"test": "success", "number": 42}',
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        
        import json
        result = json.loads(response.text)
        print(f"✅ JSON response successful!")
        print(f"   Parsed JSON: {result}")
        print()
        
        print("="*60)
        print("✅ ALL TESTS PASSED - API KEY IS VALID!")
        print("="*60)
        return True
        
    except Exception as e:
        print()
        print("="*60)
        print("❌ ERROR - API KEY TEST FAILED")
        print("="*60)
        print(f"Error: {str(e)}")
        print()
        
        error_str = str(e).lower()
        if "api key" in error_str or "invalid" in error_str or "unauthorized" in error_str:
            print("⚠️  This looks like an API key problem!")
            print("   - Check if the key is correct")
            print("   - Check if the key has expired")
            print("   - Get a new key from: https://aistudio.google.com/app/apikey")
        elif "quota" in error_str or "rate limit" in error_str:
            print("⚠️  This looks like a quota/rate limit problem!")
            print("   - You may have exceeded your API quota")
            print("   - Wait a bit and try again")
        elif "permission" in error_str:
            print("⚠️  This looks like a permission problem!")
            print("   - The API key may not have the right permissions")
        else:
            print("⚠️  Unknown error - check the error message above")
        
        import traceback
        print()
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_key()
    sys.exit(0 if success else 1)

