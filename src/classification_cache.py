"""
Classification Cache Module
============================

Simple in-memory cache for LLM classification results to improve performance.
Preserves all algorithm logic - just adds caching layer.
"""

import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache


class ClassificationCache:
    """
    Cache for classification results to avoid redundant LLM API calls.
    
    Uses text hash as cache key to handle similar inputs efficiently.
    """
    
    def __init__(self, ttl_hours: int = 24, max_size: int = 100):
        """
        Initialize cache.
        
        Args:
            ttl_hours: Time-to-live for cache entries (default: 24 hours)
            max_size: Maximum number of cached entries (default: 100)
        """
        self.cache: Dict[str, tuple] = {}  # {hash: (result, timestamp)}
        self.ttl = timedelta(hours=ttl_hours)
        self.max_size = max_size
    
    def _get_hash(self, text: str) -> str:
        """Generate hash for text input."""
        # Normalize text (lowercase, strip whitespace)
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Get cached classification result if available and not expired.
        
        Args:
            text: Input text to classify
            
        Returns:
            Cached result dict or None if not found/expired
        """
        cache_key = self._get_hash(text)
        
        if cache_key in self.cache:
            result, cached_time = self.cache[cache_key]
            
            # Check if cache entry is still valid
            if datetime.now() - cached_time < self.ttl:
                return result
            else:
                # Expired - remove from cache
                del self.cache[cache_key]
        
        return None
    
    def set(self, text: str, result: Dict[str, Any]) -> None:
        """
        Store classification result in cache.
        
        Args:
            text: Input text
            result: Classification result to cache
        """
        cache_key = self._get_hash(text)
        
        # Evict oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        # Store new entry
        self.cache[cache_key] = (result, datetime.now())
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


# Global cache instance (singleton pattern)
_global_cache: Optional[ClassificationCache] = None


def get_cache() -> ClassificationCache:
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = ClassificationCache()
    return _global_cache

