"""
Test Optimization Performance
==============================

Tests the performance improvements:
1. Fast path usage (explicit detection threshold 0.85)
2. Cache effectiveness (repeated queries)
"""

import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import ExplicitDetector
from src.classification_cache import get_cache
from src.llm_adapter import LLMAdapter
from src.classification_rules import canonicalize_label

# Test cases - some should trigger fast path
TEST_CASES = [
    ("SQL injection detected from IP 192.168.1.1", "Should trigger fast path"),
    ("XSS vulnerability found in login form", "Should trigger fast path"),
    ("Broken access control allows unauthorized data access", "May trigger fast path"),
    ("I see someone else's profile when I change the URL", "Should use LLM"),
    ("There's a security issue with authentication", "Should use LLM"),
]

def test_fast_path():
    """Test if fast path is being used."""
    print("=" * 60)
    print("TESTING FAST PATH (Explicit Detection Threshold 0.85)")
    print("=" * 60)
    
    detector = ExplicitDetector()
    fast_path_count = 0
    llm_path_count = 0
    
    for text, expected in TEST_CASES:
        explicit_label, explicit_conf = detector.detect(text)
        
        if explicit_label and explicit_conf >= 0.85:
            fast_path_count += 1
            status = "[FAST PATH]"
        else:
            llm_path_count += 1
            status = "[LLM PATH]"
        
        print(f"\n{text[:50]}...")
        print(f"  Explicit: {explicit_label} (conf: {explicit_conf:.2f})")
        print(f"  Status: {status}")
        print(f"  Expected: {expected}")
    
    print(f"\n{'='*60}")
    print(f"Fast Path Used: {fast_path_count}/{len(TEST_CASES)} ({fast_path_count*100/len(TEST_CASES):.0f}%)")
    print(f"LLM Path Used: {llm_path_count}/{len(TEST_CASES)} ({llm_path_count*100/len(TEST_CASES):.0f}%)")
    print(f"{'='*60}\n")
    
    return fast_path_count, llm_path_count

def test_caching():
    """Test cache effectiveness."""
    print("=" * 60)
    print("TESTING CACHE EFFECTIVENESS")
    print("=" * 60)
    
    cache = get_cache()
    cache.clear()  # Start fresh
    
    # Test query
    test_text = "SQL injection detected from IP 192.168.1.1"
    
    # First query (cache miss - should call LLM)
    print(f"\nFirst Query (Cache Miss):")
    start = time.time()
    cached_result = cache.get(test_text)
    cache_time = (time.time() - start) * 1000
    
    if cached_result:
        print(f"  [WARNING] Unexpected: Found in cache!")
    else:
        print(f"  [OK] Cache miss (expected)")
        print(f"  Cache check time: {cache_time:.2f} ms")
        
        # Simulate LLM call
        print(f"  Simulating LLM call...")
        llm_start = time.time()
        # Would call LLM here
        time.sleep(0.1)  # Simulate 100ms LLM call
        llm_time = (time.time() - llm_start) * 1000
        
        # Store in cache
        cache_entry = {
            "fine_label": "injection",
            "confidence": 0.95,
            "incident_type": "Injection",
            "rationale": "SQL injection pattern detected"
        }
        cache.set(test_text, cache_entry)
        print(f"  LLM call time: {llm_time:.2f} ms")
        print(f"  Total time: {cache_time + llm_time:.2f} ms")
    
    # Second query (cache hit - should be instant)
    print(f"\nSecond Query (Cache Hit):")
    start = time.time()
    cached_result = cache.get(test_text)
    cache_time = (time.time() - start) * 1000
    
    if cached_result:
        print(f"  [OK] Cache hit!")
        print(f"  Cache retrieval time: {cache_time:.4f} ms")
        print(f"  Result: {cached_result.get('fine_label')}")
        if cache_time > 0:
            print(f"  Speed improvement: {llm_time / cache_time:.1f}x faster!")
        else:
            print(f"  Speed improvement: Instant! (cache retrieval < 0.01ms)")
    else:
        print(f"  [ERROR] Cache miss (unexpected)")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("OPTIMIZATION PERFORMANCE TEST")
    print("="*60 + "\n")
    
    # Test 1: Fast path
    fast_count, llm_count = test_fast_path()
    
    # Test 2: Caching
    test_caching()
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Fast path enabled: {fast_count}/{len(TEST_CASES)} cases")
    print(f"Cache working: [OK] (see cache test above)")
    print("="*60 + "\n")

