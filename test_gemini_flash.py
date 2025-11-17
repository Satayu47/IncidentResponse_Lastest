import google.generativeai as genai

genai.configure(api_key='AIzaSyAUQhggX3GsJPwjR_x927v4PL8Qz1Vl7PA')

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
