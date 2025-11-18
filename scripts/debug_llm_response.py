"""Debug script to see what LLM actually returns"""
import os
from dotenv import load_dotenv
load_dotenv()

from src.llm_adapter import LLMAdapter

adapter = LLMAdapter(model="gemini-2.5-pro")

test_cases = [
    "I changed the number in the URL and saw someone else's profile",
    "Our passwords are stored in plain text in the database",
    "Weird syntax appear on login page",
    "I can log in with password '12345'"
]

for test_input in test_cases:
    print(f"\n{'='*60}")
    print(f"Input: {test_input}")
    print(f"{'='*60}")
    result = adapter.classify_incident(test_input)
    print(f"Raw result: {result}")
    print(f"incident_type: {result.get('incident_type')}")
    print(f"fine_label: {result.get('fine_label')}")
    print(f"category: {result.get('category')}")
    print(f"confidence: {result.get('confidence')}")
    print(f"rationale: {result.get('rationale', '')[:200]}...")

