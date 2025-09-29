"""Intelligent Cache Service for GLPI Dashboard."""

import time
import asyncio
import hashlib
import pickle
from typing import Any, Dict, Optional, Callable, Union, List
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta


class CacheStrategy(Enum):
    """Cache eviction strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    ttl: Optional[float] = None
    size: int = 0

    def __post_init__(self):
        """Calculate entry size."""
        try:
            self.size = len(pickle.dumps(self.value))
        except (pickle.PicklingError, TypeError):
            self.size = len(str(self.value))

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def touch(self):
        """Update access metadata."""
        self.last_accessed = time.time()
        self.access_count += 1


class IntelligentCache:
    """Intelligent cache with multiple eviction strategies and analytics."""

    def __init__(self,
                 max_size: int = 1000,
                 max_memory_mb: int = 100,
                 default_ttl: Optional[float] = None,
                 strategy: CacheStrategy = CacheStrategy.LRU,
                 enable_analytics: bool = True):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.strategy = strategy
        self.enable_analytics = enable_analytics

        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)

        # Analytics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_removals': 0,
            'total_requests': 0,
            'memory_usage': 0,
            'avg_access_time': 0.0
        }

    def _generate_key(self, key: Union[str, tuple, dict]) -> str:
        """Generate consistent cache key."""
        if isinstance(key, str):
            return key
        elif isinstance(key, (tuple, list)):
            return hashlib.md5(str(sorted(key)).encode()).hexdigest()
        elif isinstance(key, dict):
            return hashlib.md5(str(sorted(key.items())).encode()).hexdigest()
        else:
            return hashlib.md5(str(key).encode()).hexdigest()

    def _calculate_memory_usage(self) -> int:
        """Calculate current memory usage."""
        return sum(entry.size for entry in self._cache.values())

    def _should_evict(self) -> bool:
        """Check if eviction is needed."""
        return (
            len(self._cache) >= self.max_size or
            self._calculate_memory_usage() >= self.max_memory_bytes
        )

    def _evict_entries(self):
        """Evict entries based on strategy."""
        if not self._cache:
            return

        entries_to_remove = max(1, len(self._cache) // 10)  # Remove 10% or at least 1

        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].last_accessed
            )
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].access_count
            )
        elif self.strategy == CacheStrategy.FIFO:
            # Remove oldest entries
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].created_at
            )
        else:  # TTL or default
            # Remove expired first, then oldest
            expired = [(k, v) for k, v in self._cache.items() if v.is_expired()]
            if expired:
                sorted_entries = expired
            else:
                sorted_entries = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].created_at
                )

        for i in range(min(entries_to_remove, len(sorted_entries))):
            key, _ = sorted_entries[i]
            del self._cache[key]
            self.stats['evictions'] += 1
            self.logger.debug(f"Evicted cache entry: {key}")

    def _cleanup_expired(self):
        """Remove expired entries."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            del self._cache[key]
            self.stats['expired_removals'] += 1
            self.logger.debug(f"Removed expired cache entry: {key}")

    async def get(self, key: Union[str, tuple, dict], default: Any = None) -> Any:
        """Get value from cache."""
        async with self._lock:
            start_time = time.time()
            cache_key = self._generate_key(key)
            self.stats['total_requests'] += 1

            # Cleanup expired entries periodically
            if self.stats['total_requests'] % 100 == 0:
                self._cleanup_expired()

            if cache_key in self._cache:
                entry = self._cache[cache_key]

                if entry.is_expired():
                    del self._cache[cache_key]
                    self.stats['expired_removals'] += 1
                    self.stats['misses'] += 1
                    return default

                entry.touch()
                self.stats['hits'] += 1

                # Update average access time
                access_time = time.time() - start_time
                self.stats['avg_access_time'] = (
                    (self.stats['avg_access_time'] * (self.stats['hits'] - 1) + access_time) /
                    self.stats['hits']
                )

                return entry.value

            self.stats['misses'] += 1
            return default

    async def set(self, key: Union[str, tuple, dict], value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache."""
        async with self._lock:
            cache_key = self._generate_key(key)

            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl

            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                value=value,
                ttl=ttl
            )

            # Check if eviction is needed
            if self._should_evict():
                self._evict_entries()

            self._cache[cache_key] = entry
            self.stats['memory_usage'] = self._calculate_memory_usage()

            self.logger.debug(f"Cached entry: {cache_key} (size: {entry.size} bytes)")
            return True

    async def delete(self, key: Union[str, tuple, dict]) -> bool:
        """Delete value from cache."""
        async with self._lock:
            cache_key = self._generate_key(key)

            if cache_key in self._cache:
                del self._cache[cache_key]
                self.stats['memory_usage'] = self._calculate_memory_usage()
                self.logger.debug(f"Deleted cache entry: {cache_key}")
                return True

            return False

    async def clear(self):
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self.stats['memory_usage'] = 0
            self.logger.info("Cache cleared")

    async def exists(self, key: Union[str, tuple, dict]) -> bool:
        """Check if key exists in cache."""
        async with self._lock:
            cache_key = self._generate_key(key)

            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if entry.is_expired():
                    del self._cache[cache_key]
                    self.stats['expired_removals'] += 1
                    return False
                return True

            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats['total_requests']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
        miss_rate = self.stats['misses'] / total_requests if total_requests > 0 else 0

        return {
            **self.stats,
            'hit_rate': hit_rate,
            'miss_rate': miss_rate,
            'cache_size': len(self._cache),
            'memory_usage_mb': self.stats['memory_usage'] / (1024 * 1024),
            'memory_utilization': self.stats['memory_usage'] / self.max_memory_bytes,
            'size_utilization': len(self._cache) / self.max_size
        }

    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        return list(self._cache.keys())

    async def get_or_set(self, key: Union[str, tuple, dict],
                        factory: Callable, *args, ttl: Optional[float] = None, **kwargs) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key)

        if value is None:
            if asyncio.iscoroutinefunction(factory):
                value = await factory(*args, **kwargs)
            else:
                value = factory(*args, **kwargs)

            await self.set(key, value, ttl)

        return value

    def __len__(self) -> int:
        """Get cache size."""
        return len(self._cache)

    def __contains__(self, key: Union[str, tuple, dict]) -> bool:
        """Check if key is in cache (sync version)."""
        cache_key = self._generate_key(key)
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            return not entry.is_expired()
        return False


# Global cache instance
_cache_instance: Optional[IntelligentCache] = None


def get_cache() -> IntelligentCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = IntelligentCache()
    return _cache_instance


def set_cache(cache: IntelligentCache):
    """Set global cache instance."""
    global _cache_instance
    _cache_instance = cache


# Decorator for caching function results
def cached(ttl: Optional[float] = None, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        cache = get_cache()

        async def async_wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

            cache_key = ":".join(filter(None, key_parts))

            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await cache.set(cache_key, result, ttl)
            return result

        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to handle async cache operations
            import asyncio

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(async_wrapper(*args, **kwargs))

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
