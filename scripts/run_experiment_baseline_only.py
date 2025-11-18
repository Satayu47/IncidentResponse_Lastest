"""
Run Baseline Experiment Only (No API Key Needed)
================================================

Runs baseline keyword classifier evaluation.
This doesn't need any API keys!
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.evaluate_with_rubric import evaluate_system
from test_cases import TEST_CASES


def main():
    """Run baseline evaluation only."""
    print("\n" + "="*70)
    print("D3 Experiment: Baseline Keyword Classifier")
    print("(No API key needed for baseline!)")
    print("="*70 + "\n")
    
    # Evaluate baseline (no API key needed)
    print("Evaluating Baseline Keyword Classifier...")
    print("(This uses simple keyword matching - no LLM needed)\n")
    
    try:
        baseline_results = evaluate_system(
            TEST_CASES,
            use_baseline=True,
            system_name="Baseline Keyword Classifier"
        )
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        baseline_file = f"reports/baseline_rubric_{timestamp}.json"
        os.makedirs("reports", exist_ok=True)
        
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Baseline results saved to {baseline_file}")
        
        # Print summary
        print("\n" + "="*70)
        print("Baseline Results Summary")
        print("="*70)
        print(f"Single-Incident Accuracy: {baseline_results['single_incident']['accuracy']:.2f}%")
        print(f"Ambiguous Case Accuracy: {baseline_results['ambiguous_incident']['accuracy']:.2f}%")
        print(f"Overall Accuracy: {baseline_results['overall']['accuracy']:.2f}%")
        print(f"Average Rubric Score: {baseline_results['rubric']['average_score']:.2f}/35")
        print(f"Overconfidence Errors: {baseline_results['overconfidence_errors']}")
        print("="*70)
        
        print("\n📝 Next Step:")
        print("   To evaluate your proposed system (Gemini), you need:")
        print("   1. Get Gemini API key: https://aistudio.google.com/apikey")
        print("   2. Set: $env:GEMINI_API_KEY = 'your-key'")
        print("   3. Run: python scripts/run_full_experiment.py")
        print("\n   OR use your existing results:")
        print("   - You already have 98% accuracy results!")
        print("   - Use: reports/accuracy_results_all_50_20251118_152137.json")
        
        return baseline_results
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

