import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not set. Please set it in your environment or .env file.")
    exit(1)

genai.configure(api_key=api_key)

print("Testing gemini-2.0-flash-exp...")
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content('Say hello')
    print(f"✅ Flash works! Response: {response.text[:50]}")
except Exception as e:
    print(f"❌ Flash failed: {e}")

print("\nChecking available models:")
for m in genai.list_models():
    if 'gemini' in m.name.lower() and 'generateContent' in m.supported_generation_methods:
        print(f"  • {m.name}")
