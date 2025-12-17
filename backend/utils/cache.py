"""
Redis Cache Utility with In-Memory Fallback
===========================================

Phase 4: Performance & Caching
Provides caching layer with Redis support and automatic fallback to in-memory cache.

Features:
- Redis caching for distributed systems
- In-memory fallback if Redis unavailable
- Automatic cache invalidation
- TTL (Time To Live) support
- Thread-safe operations
"""

import json
import time
import threading
from typing import Any, Optional, Dict
from functools import wraps

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from backend.config.settings import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD,
    REDIS_ENABLED, CACHE_TTL_SECONDS
)


class InMemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expiry_time)
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry = self._cache[key]
            if expiry and time.time() > expiry:
                # Expired, remove it
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL."""
        with self._lock:
            expiry = None
            if ttl:
                expiry = time.time() + ttl
            
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear all cache."""
        with self._lock:
            self._cache.clear()
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern (simple string matching)."""
        with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]


class CacheManager:
    """Unified cache manager with Redis and in-memory fallback."""
    
    def __init__(self):
        self.redis_client = None
        self.in_memory_cache = InMemoryCache()
        self.use_redis = False
        self._lock = threading.Lock()
        
        # Initialize Redis if enabled and available
        if REDIS_ENABLED and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                    decode_responses=True,  # Automatically decode bytes to strings
                    socket_connect_timeout=2,  # Fast timeout for connection
                    socket_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                print("[CACHE] Redis connected successfully")
            except Exception as e:
                print(f"[CACHE] Redis connection failed, using in-memory cache: {e}")
                self.redis_client = None
                self.use_redis = False
        else:
            if not REDIS_AVAILABLE:
                print("[CACHE] Redis not installed, using in-memory cache")
            else:
                print("[CACHE] Redis disabled in config, using in-memory cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (Redis or in-memory)."""
        if self.use_redis and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                print(f"[CACHE] Redis get error, falling back to in-memory: {e}")
                # Fallback to in-memory
                return self.in_memory_cache.get(key)
        else:
            return self.in_memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache (Redis or in-memory)."""
        ttl = ttl or CACHE_TTL_SECONDS
        
        if self.use_redis and self.redis_client:
            try:
                json_value = json.dumps(value)
                if ttl:
                    self.redis_client.setex(key, ttl, json_value)
                else:
                    self.redis_client.set(key, json_value)
            except Exception as e:
                print(f"[CACHE] Redis set error, falling back to in-memory: {e}")
                # Fallback to in-memory
                self.in_memory_cache.set(key, value, ttl)
        else:
            self.in_memory_cache.set(key, value, ttl)
    
    def delete(self, key: str):
        """Delete key from cache."""
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"[CACHE] Redis delete error, falling back to in-memory: {e}")
                # Fallback to in-memory
                self.in_memory_cache.delete(key)
        else:
            self.in_memory_cache.delete(key)
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern."""
        if self.use_redis and self.redis_client:
            try:
                # Redis pattern matching
                keys = self.redis_client.keys(f"*{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                print(f"[CACHE] Redis delete_pattern error, falling back to in-memory: {e}")
                # Fallback to in-memory
                self.in_memory_cache.delete_pattern(pattern)
        else:
            self.in_memory_cache.delete_pattern(pattern)
    
    def clear(self):
        """Clear all cache."""
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                print(f"[CACHE] Redis clear error, falling back to in-memory: {e}")
                # Fallback to in-memory
                self.in_memory_cache.clear()
        else:
            self.in_memory_cache.clear()


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None
_cache_lock = threading.Lock()


def get_cache() -> CacheManager:
    """Get or create global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        with _cache_lock:
            if _cache_manager is None:
                _cache_manager = CacheManager()
    return _cache_manager


def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from prefix and arguments."""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds (None = use default)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            cache_key_str = cache_key(
                key_prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = cache.get(cache_key_str)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key_str, result, ttl)
            
            return result
        
        return wrapper
    return decorator

