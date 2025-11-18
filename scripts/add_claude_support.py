"""
Quick script to add Claude (Anthropic) support to LLMAdapter
This allows using Claude as a baseline comparison model.
"""

# This would extend src/llm_adapter.py to support Claude
# Example implementation:

"""
To add Claude support, modify src/llm_adapter.py:

1. Add import:
   from anthropic import Anthropic

2. Update _detect_provider:
   elif model.startswith("claude-"):
       return "anthropic"

3. Add Claude initialization:
   elif self.provider == "anthropic":
       self.client = Anthropic(api_key=api_key)
       self.model = model

4. Add Claude API call in classify_incident:
   elif self.provider == "anthropic":
       response = self.client.messages.create(
           model=self.model,
           max_tokens=1024,
           system=system_prompt,
           messages=[{"role": "user", "content": "\n".join(prompt_parts[1:])}]
       )
       result = json.loads(response.content[0].text)
"""

print("""
To add Claude support:

1. Install: pip install anthropic
2. Get API key: https://console.anthropic.com/
3. Set: $env:ANTHROPIC_API_KEY = "your-key"
4. Use: LLMAdapter(model="claude-3-5-sonnet-20241022")

I can help implement this if you want!
""")

