#!/usr/bin/env python3
"""Quick test to verify new Gemini API key works"""
import os
from dotenv import load_dotenv

load_dotenv()

from src.llm_adapter import LLMAdapter

print("Testing new Gemini API key...")
adapter = LLMAdapter(model="gemini-2.5-pro")
result = adapter.classify_incident("SQL injection on login page")

print(f"✅ LLM Test Successful!")
print(f"   - Type: {result.get('incident_type', 'Unknown')}")
print(f"   - Confidence: {result.get('confidence', 0.0):.2f}")
print(f"   - Label: {result.get('fine_label', 'unknown')}")

