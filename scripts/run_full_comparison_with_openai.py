"""
Run Full Baseline Comparison with OpenAI
========================================

Uses OpenAI API key to run complete baseline comparison:
- Gemini 2.5 Pro (your system)
- OpenAI GPT-4o (baseline)
- Generates IEEE-formatted reports and visualizations
"""

import os
import sys
from pathlib import Path

# Set OpenAI API key
OPENAI_KEY = "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"
os.environ["OPENAI_API_KEY"] = OPENAI_KEY

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("FULL BASELINE COMPARISON WITH OPENAI")
print("=" * 70)
print(f"\nOpenAI API Key: Set [OK]")
print(f"Model: GPT-4o")
print(f"Comparison: Gemini 2.5 Pro vs OpenAI GPT-4o")
print("\nThis will:")
print("  1. Test Gemini 2.5 Pro on all test cases")
print("  2. Test OpenAI GPT-4o on same test cases")
print("  3. Generate comparison report")
print("  4. Create visualizations")
print("\nStarting experiment...\n")

# Run baseline comparison
from scripts.test_baseline_comparison import compare_models
from test_cases import TEST_CASES

# Run comparison
results = compare_models(
    gemini_model="gemini-2.5-pro",
    baseline_model="gpt-4o",
    baseline_provider="openai",
    test_cases=TEST_CASES,
    gemini_key=os.getenv("GEMINI_API_KEY"),
    baseline_key=OPENAI_KEY
)

# Save results
from datetime import datetime
import json

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"reports/baseline_comparison_openai_{timestamp}.json"

os.makedirs("reports", exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Results saved to {output_file}")

# Generate IEEE report
print("\n[2/3] Generating IEEE-formatted report...")
try:
    from scripts.generate_ieee_baseline_report import generate_report
    
    report_file = f"reports/IEEE_BASELINE_COMPARISON_OPENAI_{timestamp}.md"
    report = generate_report(output_file)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[OK] IEEE report saved to {report_file}")
except Exception as e:
    print(f"[WARNING] Could not generate report: {e}")

# Generate visualizations
print("\n[3/3] Generating visualizations...")
try:
    from scripts.visualize_llm_comparison import main as visualize_main
    import sys as sys_module
    
    # Save original argv
    original_argv = sys_module.argv
    sys_module.argv = ['visualize_llm_comparison.py', output_file]
    
    visualize_main()
    
    # Restore argv
    sys_module.argv = original_argv
    
    print("[OK] Visualizations generated")
except Exception as e:
    print(f"[WARNING] Could not generate visualizations: {e}")

print("\n" + "=" * 70)
print("COMPARISON COMPLETE!")
print("=" * 70)
print(f"\nResults: {output_file}")
print(f"Report: {report_file if 'report_file' in locals() else 'N/A'}")
print("\nYou can now use these results in your D3 report!")

