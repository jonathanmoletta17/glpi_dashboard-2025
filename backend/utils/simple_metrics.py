"""Módulo de métricas simples para cache de funções"""

import functools
import time
from functools import wraps
from typing import Any, Callable, Dict

# Import consolidated cache system
from services.simple_dict_cache import simple_cache


class SimpleMetrics:
    """Classe simples para cache de funções com timeout e métricas básicas"""

    def __init__(self):
        # Use consolidated cache instead of local cache
        self._counters: Dict[str, int] = {}

    def cached(self, timeout: int = 300):
        """Decorator para cache com timeout usando sistema consolidado"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Gerar chave única para a função e argumentos
                cache_key = f"simple_metrics_{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"

                # Verificar se existe no cache consolidado
                cached_result = simple_cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Executar função e cachear resultado no sistema consolidado
                result = func(*args, **kwargs)
                simple_cache.set(cache_key, result, ttl=timeout)

                return result

            return wrapper

        return decorator

    def clear_cache(self):
        """Limpa cache relacionado ao simple_metrics no sistema consolidado"""
        # Clear only simple_metrics related cache entries
        simple_cache.invalidate_pattern("simple_metrics_*")

    def clear_expired(self, max_age: int = 3600):
        """Remove entradas expiradas do cache consolidado"""
        # The consolidated cache system handles TTL automatically
        # Just trigger cleanup of expired entries
        return simple_cache.cleanup_expired()

    def increment_counter(self, counter_name: str, **kwargs):
        """Incrementa um contador simples"""
        key = f"{counter_name}_{hash(str(sorted(kwargs.items())))}"
        self._counters[key] = self._counters.get(key, 0) + 1

    def get_counter(self, counter_name: str, **kwargs) -> int:
        """Obtém o valor de um contador"""
        key = f"{counter_name}_{hash(str(sorted(kwargs.items())))}"
        return self._counters.get(key, 0)


# Instância global para uso em toda a aplicação
simple_metrics = SimpleMetrics()
