"""
Check API Keys and Run Baseline Experiment
===========================================

This script checks available API keys and guides you through running
the baseline comparison experiment.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent))

def check_api_keys():
    """Check which API keys are available."""
    keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }
    
    status = {}
    for name, key in keys.items():
        if key and len(key) > 10:
            # Mask key for display
            masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            status[name] = {"available": True, "masked": masked}
        else:
            status[name] = {"available": False, "masked": None}
    
    return status


def test_api_key(provider: str, api_key: str) -> bool:
    """Test if an API key works."""
    try:
        from src.llm_adapter import LLMAdapter
        
        if provider == "gemini":
            adapter = LLMAdapter(model="gemini-2.5-pro", api_key=api_key)
        elif provider == "anthropic":
            adapter = LLMAdapter(model="claude-3-5-sonnet-20241022", api_key=api_key)
        elif provider == "openai":
            adapter = LLMAdapter(model="gpt-4o", api_key=api_key)
        else:
            return False
        
        # Quick test
        result = adapter.classify_incident("SQL injection test", context="", conversation_history=None)
        return result is not None and result.get("incident_type") is not None
        
    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
        return False


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("Baseline Comparison Experiment Setup")
    print("="*70 + "\n")
    
    # Check keys
    print("Checking API keys...")
    status = check_api_keys()
    
    print("\nCurrent Status:")
    for name, info in status.items():
        provider = name.replace("_API_KEY", "").lower()
        if info["available"]:
            print(f"  ✓ {provider.upper()}: {info['masked']} (Set)")
        else:
            print(f"  ✗ {provider.upper()}: Not set")
    
    # Guide for missing keys
    print("\n" + "="*70)
    print("Getting API Keys")
    print("="*70)
    
    if not status["GEMINI_API_KEY"]["available"]:
        print("\n📝 Gemini API Key (Required):")
        print("   1. Go to: https://aistudio.google.com/apikey")
        print("   2. Sign in with Google account")
        print("   3. Create new API key")
        print("   4. Set: $env:GEMINI_API_KEY = 'your-key-here'")
    
    if not status["ANTHROPIC_API_KEY"]["available"]:
        print("\n📝 Claude API Key (Recommended - Free $5 credit):")
        print("   1. Go to: https://console.anthropic.com/")
        print("   2. Sign up (free account)")
        print("   3. Go to API Keys section")
        print("   4. Create new key (starts with 'sk-ant-')")
        print("   5. Set: $env:ANTHROPIC_API_KEY = 'sk-ant-your-key-here'")
    
    if not status["OPENAI_API_KEY"]["available"]:
        print("\n📝 OpenAI API Key (Optional):")
        print("   1. Go to: https://platform.openai.com/api-keys")
        print("   2. Sign up and add billing")
        print("   3. Create new key (starts with 'sk-' or 'sk-proj-')")
        print("   4. Set: $env:OPENAI_API_KEY = 'sk-your-key-here'")
    
    # Test available keys
    print("\n" + "="*70)
    print("Testing API Keys")
    print("="*70)
    
    gemini_ready = False
    baseline_models = []
    
    if status["GEMINI_API_KEY"]["available"]:
        print("\nTesting Gemini API key...")
        key = os.getenv("GEMINI_API_KEY")
        if test_api_key("gemini", key):
            print("  ✓ Gemini API key works!")
            gemini_ready = True
        else:
            print("  ✗ Gemini API key test failed")
    
    if status["ANTHROPIC_API_KEY"]["available"]:
        print("\nTesting Claude API key...")
        key = os.getenv("ANTHROPIC_API_KEY")
        if test_api_key("anthropic", key):
            print("  ✓ Claude API key works!")
            baseline_models.append("claude")
        else:
            print("  ✗ Claude API key test failed")
    
    if status["OPENAI_API_KEY"]["available"]:
        print("\nTesting OpenAI API key...")
        key = os.getenv("OPENAI_API_KEY")
        if test_api_key("openai", key):
            print("  ✓ OpenAI API key works!")
            baseline_models.append("openai")
        else:
            print("  ✗ OpenAI API key test failed")
    
    # Ready to run?
    print("\n" + "="*70)
    print("Ready to Run Experiment")
    print("="*70)
    
    if gemini_ready:
        if baseline_models:
            print(f"\n🚀 Ready! You can run the experiment with:")
            print(f"   Baseline models: {', '.join(baseline_models)}")
            print(f"\n   Command:")
            baseline_str = " ".join(baseline_models)
            print(f"   python scripts/run_baseline_experiment.py --limit 50 --baseline {baseline_str}")
            
            # Ask if user wants to run now
            print("\n" + "="*70)
            response = input("Run experiment now? (y/n): ").strip().lower()
            if response == 'y':
                print("\nRunning experiment...")
                import subprocess
                cmd = [sys.executable, "scripts/run_baseline_experiment.py", "--limit", "50", "--baseline"] + baseline_models
                subprocess.run(cmd)
        else:
            print("\n⚠️  Gemini key ready, but no baseline keys available.")
            print("   You can still generate IEEE report with Gemini results only.")
            print("\n   Command:")
            print("   python scripts/generate_ieee_experiment_report.py reports/baseline_experiment_from_gemini_*.json")
    else:
        print("\n⚠️  Need at least Gemini API key to run experiment.")
        print("   Get your key from: https://aistudio.google.com/apikey")
    
    print("\n")


if __name__ == "__main__":
    main()

