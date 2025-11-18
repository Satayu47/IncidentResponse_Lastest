import os
import google.generativeai as genai

# Configure with API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not set. Please set it in your environment or .env file.")
    exit(1)

genai.configure(api_key=api_key)

# Create model - using stable gemini-2.5-flash instead
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Test generation
prompt = """You are a security incident classifier. Classify this incident into OWASP category.
Return JSON with: {"category": "broken_access_control", "confidence": 0.9}

Incident: Normal users can access /admin dashboard

Respond with valid JSON only."""

response = model.generate_content(
    prompt,
    generation_config=genai.GenerationConfig(
        temperature=0.3,
        response_mime_type="application/json"
    )
)

print('✅ Gemini API working!')
print(f'Response: {response.text}')
