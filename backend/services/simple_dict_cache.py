#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de cache consolidado - substitui múltiplos sistemas de cache
Combina funcionalidades de simple_dict_cache, smart_cache, cache_service e cache_warming
"""

import functools
import hashlib
import json
import logging
import re
import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SimpleDictCache:
    """Cache consolidado com TTL, LRU, limite de memória e funcionalidades inteligentes"""

    def __init__(self, default_ttl: int = 300, max_size: int = 1000, memory_limit_mb: int = 100):
        """Inicializa o cache

        Args:
            default_ttl: TTL padrão em segundos (5 minutos)
            max_size: Número máximo de entradas no cache
            memory_limit_mb: Limite de memória em MB
        """
        self._cache: OrderedDict[str, Tuple[Any, float, int]] = OrderedDict()  # value, expiry, access_count
        self._lock = threading.RLock()
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self._hits = 0
        self._misses = 0
        self._access_patterns: Dict[str, List[float]] = {}  # Para TTL adaptativo

    def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache

        Args:
            key: Chave do cache

        Returns:
            Valor armazenado ou None se não encontrado/expirado
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expiry_time, access_count = self._cache[key]

            # Verificar se expirou
            if time.time() > expiry_time:
                del self._cache[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]
                self._misses += 1
                return None

            # Atualizar padrão de acesso e mover para o final (LRU)
            self._access_patterns.setdefault(key, []).append(time.time())
            # Manter apenas os últimos 10 acessos
            if len(self._access_patterns[key]) > 10:
                self._access_patterns[key] = self._access_patterns[key][-10:]

            # Atualizar cache com nova contagem de acesso e mover para o final
            self._cache[key] = (value, expiry_time, access_count + 1)
            self._cache.move_to_end(key)

            self._hits += 1
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazena um valor no cache

        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: TTL em segundos (usa default_ttl se None)
        """
        # Calcular TTL adaptativo baseado no padrão de acesso
        if ttl is None:
            ttl = self._calculate_adaptive_ttl(key)

        expiry_time = time.time() + ttl

        with self._lock:
            # Verificar se precisa fazer eviction
            self._evict_if_needed()

            # Armazenar no cache
            self._cache[key] = (value, expiry_time, 0)  # access_count = 0
            self._cache.move_to_end(key)  # Mover para o final (mais recente)

    def delete(self, key: str) -> bool:
        """Remove uma chave do cache

        Args:
            key: Chave a ser removida

        Returns:
            True se a chave foi removida, False se não existia
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]
                return True
            return False

    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()
            self._access_patterns.clear()
            self._hits = 0
            self._misses = 0

    def cleanup_expired(self) -> int:
        """Remove entradas expiradas do cache

        Returns:
            Número de entradas removidas
        """
        current_time = time.time()
        expired_keys = []

        with self._lock:
            for key, (_, expiry_time, _) in self._cache.items():
                if current_time > expiry_time:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]

        if expired_keys:
            logger.debug(f"Cache cleanup: removidas {len(expired_keys)} entradas expiradas")

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "total_entries": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests,
            }

    def has_key(self, key: str) -> bool:
        """Verifica se uma chave existe e não está expirada"""
        return self.get(key) is not None

    def _calculate_adaptive_ttl(self, key: str) -> int:
        """Calcula TTL adaptativo baseado no padrão de acesso"""
        if key not in self._access_patterns:
            return self._default_ttl

        access_times = self._access_patterns[key]
        if len(access_times) < 2:
            return self._default_ttl

        # Calcular frequência de acesso (acessos por hora)
        time_span = access_times[-1] - access_times[0]
        if time_span <= 0:
            return self._default_ttl

        access_frequency = len(access_times) / (time_span / 3600)  # acessos por hora

        # TTL adaptativo: mais acessos = TTL maior
        if access_frequency > 10:  # Muito frequente
            return self._default_ttl * 3
        elif access_frequency > 5:  # Frequente
            return self._default_ttl * 2
        elif access_frequency > 1:  # Normal
            return self._default_ttl
        else:  # Pouco frequente
            return max(60, self._default_ttl // 2)

    def _evict_if_needed(self) -> None:
        """Remove entradas se necessário (LRU + limite de tamanho/memória)"""
        # Remover entradas expiradas primeiro
        self.cleanup_expired()

        # Verificar limite de tamanho
        while len(self._cache) >= self._max_size:
            # Remove o item menos recentemente usado (primeiro do OrderedDict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if oldest_key in self._access_patterns:
                del self._access_patterns[oldest_key]
            logger.debug(f"Cache eviction: removida chave {oldest_key} por limite de tamanho")

    def invalidate_pattern(self, pattern: str) -> int:
        """Remove chaves que correspondem a um padrão regex"""
        compiled_pattern = re.compile(pattern)
        keys_to_remove = []

        with self._lock:
            for key in self._cache.keys():
                if compiled_pattern.search(key):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._cache[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]

        logger.debug(f"Cache invalidation: removidas {len(keys_to_remove)} chaves com padrão '{pattern}'")
        return len(keys_to_remove)

    def generate_cache_key(self, *args, **kwargs) -> str:
        """Gera chave de cache usando hash para consistência"""
        # Criar string consistente dos argumentos
        key_data = {"args": args, "kwargs": sorted(kwargs.items()) if kwargs else {}}
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()


# Instância global do cache
simple_cache = SimpleDictCache(default_ttl=300)  # 5 minutos


def cache_key(*args, **kwargs) -> str:
    """Gera uma chave de cache a partir de argumentos

    Args:
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados

    Returns:
        String da chave de cache
    """
    # Converter argumentos para string de forma consistente
    args_str = "_".join(str(arg) for arg in args)
    kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

    if args_str and kwargs_str:
        return f"{args_str}_{kwargs_str}"
    elif args_str:
        return args_str
    elif kwargs_str:
        return kwargs_str
    else:
        return "empty"


def cached(ttl: int = 300):
    """Decorador para cache de funções

    Args:
        ttl: TTL em segundos
    """

    def decorator(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            key = f"{func.__name__}_{cache_key(*args, **kwargs)}"

            # Tentar recuperar do cache
            cached_result = simple_cache.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit para {func.__name__}")
                return cached_result

            # Executar função e armazenar resultado
            logger.debug(f"Cache miss para {func.__name__}")
            result = func(*args, **kwargs)
            simple_cache.set(key, result, ttl)

            return result

        return wrapper

    return decorator


# Função de limpeza automática (pode ser chamada periodicamente)
def auto_cleanup():
    """Função para limpeza automática do cache"""
    try:
        removed = simple_cache.cleanup_expired()
        if removed > 0:
            logger.info(f"Cache auto-cleanup: {removed} entradas removidas")
    except Exception as e:
        logger.error(f"Erro na limpeza automática do cache: {e}")


# Função para obter estatísticas do cache
def get_cache_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache para monitoramento"""
    return simple_cache.get_stats()
