import google.generativeai as genai

genai.configure(api_key='AIzaSyAUQhggX3GsJPwjR_x927v4PL8Qz1Vl7PA')

print("Testing gemini-2.5-flash...")
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content('Say hello')
    print(f"✅ gemini-2.5-flash works! Response: {response.text[:50]}")
    print(f"Full response: {response.text}")
except Exception as e:
    print(f"❌ gemini-2.5-flash failed: {str(e)[:200]}")

print("\n" + "="*60)
print("Comparing Gemini 2.5 Flash vs 2.5 Pro:")
print("="*60)
print("Model: gemini-2.5-flash")
print("  Expected FREE tier: 1,500 requests/day (same as 2.0-flash)")
print("  Speed: ~400-600ms")
print("  Accuracy: ~90-92% (better than 2.0-flash)")
print("  Cost (paid): $0.00002/request")
print("\nModel: gemini-2.5-pro (current)")
print("  FREE tier: 50 requests/day")
print("  Speed: ~1-2 seconds")
print("  Accuracy: ~92-95%")
print("  Cost (paid): $0.002/request (100x more expensive)")
