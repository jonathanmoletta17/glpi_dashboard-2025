#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Unificado para Sistema GLPI Dashboard

Consolida todas as implementações de cache em uma única interface.
"""

import time
import threading
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import json
import logging
from abc import ABC, abstractmethod


class ICacheManager(ABC):
    """Interface para gerenciadores de cache"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor do cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Limpa todo o cache"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        pass


class UnifiedCache(ICacheManager):
    """Cache unificado com TTL e métricas integradas"""
    
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._logger = logging.getLogger(__name__)
        
        # Métricas
        self._hit_count = 0
        self._miss_count = 0
        self._set_count = 0
        self._delete_count = 0
        
        self._logger.info(f"Cache unificado inicializado (TTL: {default_ttl}s, Max: {max_size})")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor do cache"""
        with self._lock:
            if key in self._cache:
                # Verificar TTL
                if self._is_valid(key):
                    self._hit_count += 1
                    self._logger.debug(f"Cache HIT: {key}")
                    return self._cache[key]
                else:
                    # Expirado
                    self._remove_expired(key)
            
            self._miss_count += 1
            self._logger.debug(f"Cache MISS: {key}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        with self._lock:
            try:
                ttl = ttl or self._default_ttl
                
                # Verificar limite de tamanho
                if len(self._cache) >= self._max_size and key not in self._cache:
                    self._cleanup_old_entries()
                
                self._cache[key] = value
                self._timestamps[key] = time.time() + ttl
                self._set_count += 1
                
                self._logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
                return True
                
            except Exception as e:
                self._logger.error(f"Erro ao definir cache {key}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._timestamps[key]
                self._delete_count += 1
                self._logger.debug(f"Cache DELETE: {key}")
                return True
            return False
    
    def clear(self) -> bool:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._logger.info("Cache limpo")
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        with self._lock:
            total_requests = self._hit_count + self._miss_count
            hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "cache_size": len(self._cache),
                "max_size": self._max_size,
                "hit_count": self._hit_count,
                "miss_count": self._miss_count,
                "set_count": self._set_count,
                "delete_count": self._delete_count,
                "hit_rate_percent": round(hit_rate, 2),
                "memory_usage_percent": round(len(self._cache) / self._max_size * 100, 2)
            }
    
    def _is_valid(self, key: str) -> bool:
        """Verifica se a entrada do cache ainda é válida"""
        return key in self._timestamps and time.time() < self._timestamps[key]
    
    def _remove_expired(self, key: str) -> None:
        """Remove entrada expirada"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def _cleanup_old_entries(self, cleanup_ratio: float = 0.2) -> None:
        """Remove entradas antigas quando o cache está cheio"""
        cleanup_count = int(self._max_size * cleanup_ratio)
        
        # Ordenar por timestamp (mais antigos primeiro)
        sorted_keys = sorted(self._timestamps.keys(), key=lambda k: self._timestamps[k])
        
        for key in sorted_keys[:cleanup_count]:
            self.delete(key)
        
        self._logger.debug(f"Limpeza de cache: {cleanup_count} entradas removidas")


class TechnicianCache(UnifiedCache):
    """Cache especializado para dados de técnicos"""
    
    def __init__(self):
        super().__init__(default_ttl=3600, max_size=500)  # 1 hora TTL
    
    def get_cached_technicians(self, cache_key: str, technician_id: Optional[int] = None) -> Optional[List[Dict]]:
        """Obtém técnicos do cache"""
        return self.get(cache_key)
    
    def set_cached_technicians(self, cache_key: str, technicians: List[Dict], ttl: int = 3600) -> bool:
        """Armazena técnicos no cache"""
        return self.set(cache_key, technicians, ttl)
    
    def get_hierarchy(self) -> Optional[Dict[int, str]]:
        """Obtém hierarquia de técnicos do cache"""
        return self.get("technician_hierarchy")
    
    def set_hierarchy(self, hierarchy: Dict[int, str], ttl: int = 3600) -> bool:
        """Armazena hierarquia de técnicos no cache"""
        return self.set("technician_hierarchy", hierarchy, ttl)
    
    def clear_hierarchy(self) -> None:
        """Limpa cache de hierarquia"""
        self.delete("technician_hierarchy")


class CacheFactory:
    """Factory para criar instâncias de cache"""
    
    _instances: Dict[str, ICacheManager] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_cache(cls, cache_type: str = "unified", **kwargs) -> ICacheManager:
        """Obtém instância de cache (singleton por tipo)"""
        with cls._lock:
            if cache_type not in cls._instances:
                if cache_type == "unified":
                    cls._instances[cache_type] = UnifiedCache(**kwargs)
                elif cache_type == "technician":
                    cls._instances[cache_type] = TechnicianCache()
                else:
                    raise ValueError(f"Tipo de cache não suportado: {cache_type}")
            
            return cls._instances[cache_type]
    
    @classmethod
    def clear_all_caches(cls) -> None:
        """Limpa todas as instâncias de cache"""
        with cls._lock:
            for cache in cls._instances.values():
                cache.clear()
            cls._instances.clear()


# Instâncias globais para compatibilidade
_unified_cache = CacheFactory.get_cache("unified")
_technician_cache = CacheFactory.get_cache("technician")


def get_unified_cache() -> ICacheManager:
    """Obtém instância do cache unificado"""
    return _unified_cache


def get_technician_cache() -> TechnicianCache:
    """Obtém instância do cache de técnicos"""
    return _technician_cache


def generate_cache_key(prefix: str, **params) -> str:
    """Gera chave de cache padronizada"""
    if not params:
        return prefix
    
    # Ordenar parâmetros para consistência
    sorted_params = sorted(params.items())
    params_str = json.dumps(sorted_params, sort_keys=True, default=str)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
    
    return f"{prefix}:{params_hash}"