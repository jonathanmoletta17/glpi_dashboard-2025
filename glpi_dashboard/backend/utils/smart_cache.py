#!/usr/bin/env python3
"""
Sistema de cache inteligente para o GLPI Dashboard
Implementa cache com TTL adaptativo e invalidação inteligente
"""

import time
import threading
from typing import Any, Optional, Dict, Callable
from functools import wraps
import hashlib
import json


class SmartCache:
    """Cache inteligente com TTL adaptativo baseado em padrões de uso"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_patterns: Dict[str, list] = {}
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "adaptive_ttl_adjustments": 0
        }

    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Gera chave única para cache baseada em função e parâmetros"""
        key_data = {
            "func": func_name,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _calculate_adaptive_ttl(self, key: str, base_ttl: int) -> int:
        """Calcula TTL adaptativo baseado no padrão de acesso"""
        with self._lock:
            if key not in self._access_patterns:
                return base_ttl

            accesses = self._access_patterns[key]
            now = time.time()

            # Remover acessos antigos (últimas 24 horas)
            recent_accesses = [t for t in accesses if now - t < 86400]
            self._access_patterns[key] = recent_accesses

            if len(recent_accesses) < 2:
                return base_ttl

            # Calcular frequência de acesso
            time_span = recent_accesses[-1] - recent_accesses[0]
            if time_span == 0:
                return base_ttl

            access_frequency = len(recent_accesses) / time_span  # acessos por segundo

            # TTL adaptativo: mais acessos = TTL maior
            if access_frequency > 0.1:  # > 1 acesso a cada 10 segundos
                adaptive_ttl = int(base_ttl * 2)  # Dobrar TTL
                self._stats["adaptive_ttl_adjustments"] += 1
                return min(adaptive_ttl, base_ttl * 3)  # Máximo 3x o TTL base
            elif access_frequency < 0.01:  # < 1 acesso por 100 segundos
                return max(int(base_ttl * 0.5), 30)  # Mínimo 30 segundos

            return base_ttl

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return None

            cache_entry = self._cache[key]
            now = time.time()

            # Verificar se expirou
            if now > cache_entry["expires_at"]:
                del self._cache[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]
                self._stats["misses"] += 1
                self._stats["invalidations"] += 1
                return None

            # Registrar acesso
            if key not in self._access_patterns:
                self._access_patterns[key] = []
            self._access_patterns[key].append(now)

            self._stats["hits"] += 1
            return cache_entry["value"]

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Define valor no cache com TTL adaptativo"""
        with self._lock:
            adaptive_ttl = self._calculate_adaptive_ttl(key, ttl)
            expires_at = time.time() + adaptive_ttl

            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time(),
                "ttl": adaptive_ttl
            }

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalida todas as chaves que correspondem ao padrão"""
        with self._lock:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]

            self._stats["invalidations"] += len(keys_to_remove)
            return len(keys_to_remove)

    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            invalidated = len(self._cache)
            self._cache.clear()
            self._access_patterns.clear()
            self._stats["invalidations"] += invalidated

    def get_stats(self) -> dict:
        """Retorna estatísticas do cache"""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

            return {
                **self._stats,
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_requests,
                "cache_size": len(self._cache),
                "patterns_tracked": len(self._access_patterns)
            }


# Instância global do cache inteligente
smart_cache = SmartCache()


def smart_cache_decorator(ttl: int = 300, key_prefix: str = ""):
    """Decorator para cache inteligente com TTL adaptativo"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            func_name = f"{key_prefix}{func.__name__}" if key_prefix else func.__name__
            cache_key = smart_cache._generate_key(func_name, args, kwargs)

            # Tentar obter do cache
            cached_result = smart_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            smart_cache.set(cache_key, result, ttl)

            return result

        wrapper.cache_invalidate = lambda pattern="": smart_cache.invalidate_pattern(pattern or func.__name__)
        wrapper.cache_stats = smart_cache.get_stats

        return wrapper
    return decorator


def cache_performance_monitor():
    """Monitor de performance do cache"""
    stats = smart_cache.get_stats()

    # Log estatísticas se hit rate for baixo
    if stats["total_requests"] > 100 and stats["hit_rate_percent"] < 70:
        print(f"⚠️  Cache hit rate baixo: {stats['hit_rate_percent']:.1f}%")
        print(f"   Hits: {stats['hits']}, Misses: {stats['misses']}")
        print(f"   Cache size: {stats['cache_size']}")

    return stats


if __name__ == "__main__":
    # Teste do cache inteligente
    @smart_cache_decorator(ttl=60, key_prefix="test_")
    def expensive_operation(x, y):
        time.sleep(0.1)  # Simular operação custosa
        return x + y

    # Testar cache
    start = time.time()
    result1 = expensive_operation(1, 2)  # Miss - deve demorar
    time1 = time.time() - start

    start = time.time()
    result2 = expensive_operation(1, 2)  # Hit - deve ser rápido
    time2 = time.time() - start

    print(f"Primeira execução: {time1:.3f}s")
    print(f"Segunda execução: {time2:.3f}s")
    print(f"Speedup: {time1/time2:.1f}x")
    print(f"Cache stats: {smart_cache.get_stats()}")
