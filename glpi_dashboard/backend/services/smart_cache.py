import time
import hashlib
import json
import logging
from typing import Any, Dict, Optional, Callable, Union
from functools import wraps
from datetime import datetime, timedelta
from config.settings import get_cache_config
from utils.performance import performance_monitor

logger = logging.getLogger(__name__)

class SmartCache:
    """Sistema de cache inteligente com TTL adaptativo e invalidação baseada em padrões."""

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.config = get_cache_config()
        self._local_cache = {}  # Fallback para quando Redis não estiver disponível
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "adaptive_ttl_adjustments": 0
        }

        # Configurações de TTL por tipo de endpoint
        self._ttl_configs = {
            "metrics": {
                "base_ttl": 300,  # 5 minutos
                "max_ttl": 1800,  # 30 minutos
                "min_ttl": 60,    # 1 minuto
                "volatility_factor": 0.8
            },
            "technicians": {
                "base_ttl": 600,  # 10 minutos
                "max_ttl": 3600,  # 1 hora
                "min_ttl": 300,   # 5 minutos
                "volatility_factor": 0.6
            },
            "tickets": {
                "base_ttl": 180,  # 3 minutos
                "max_ttl": 900,   # 15 minutos
                "min_ttl": 30,    # 30 segundos
                "volatility_factor": 0.9
            },
            "status": {
                "base_ttl": 30,   # 30 segundos
                "max_ttl": 300,   # 5 minutos
                "min_ttl": 10,    # 10 segundos
                "volatility_factor": 1.0
            },
            "default": {
                "base_ttl": 300,
                "max_ttl": 1800,
                "min_ttl": 60,
                "volatility_factor": 0.7
            }
        }

    def _generate_cache_key(self, endpoint: str, params: Dict = None, user_context: str = None) -> str:
        """Gera chave de cache única baseada no endpoint, parâmetros e contexto do usuário."""
        key_parts = [endpoint]

        if params:
            # Ordena parâmetros para garantir consistência
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(sorted_params)

        if user_context:
            key_parts.append(user_context)

        key_string = "|".join(key_parts)
        return f"glpi_cache:{hashlib.md5(key_string.encode()).hexdigest()}"

    def _get_endpoint_type(self, endpoint: str) -> str:
        """Determina o tipo de endpoint para configuração de TTL."""
        if "/metrics" in endpoint:
            return "metrics"
        elif "/technicians" in endpoint:
            return "technicians"
        elif "/tickets" in endpoint:
            return "tickets"
        elif "/status" in endpoint or "/health" in endpoint:
            return "status"
        else:
            return "default"

    def _calculate_adaptive_ttl(self, endpoint_type: str, hit_rate: float, last_access_time: float) -> int:
        """Calcula TTL adaptativo baseado na taxa de hit e padrão de acesso."""
        config = self._ttl_configs[endpoint_type]
        base_ttl = config["base_ttl"]
        max_ttl = config["max_ttl"]
        min_ttl = config["min_ttl"]
        volatility = config["volatility_factor"]

        # Ajusta TTL baseado na taxa de hit
        if hit_rate > 0.8:  # Alta taxa de hit = pode aumentar TTL
            ttl_multiplier = 1.5
        elif hit_rate > 0.6:  # Taxa média = TTL normal
            ttl_multiplier = 1.0
        else:  # Baixa taxa de hit = diminui TTL
            ttl_multiplier = 0.7

        # Ajusta baseado no tempo desde último acesso
        time_since_access = time.time() - last_access_time
        if time_since_access < 60:  # Acesso recente = aumenta TTL
            time_multiplier = 1.2
        elif time_since_access < 300:  # Acesso moderado = TTL normal
            time_multiplier = 1.0
        else:  # Acesso antigo = diminui TTL
            time_multiplier = 0.8

        # Aplica volatilidade do endpoint
        adaptive_ttl = int(base_ttl * ttl_multiplier * time_multiplier * volatility)

        # Garante que está dentro dos limites
        adaptive_ttl = max(min_ttl, min(max_ttl, adaptive_ttl))

        self._cache_stats["adaptive_ttl_adjustments"] += 1

        return adaptive_ttl

    def get(self, key: str, endpoint_type: str = "default") -> Optional[Any]:
        """Recupera valor do cache com estatísticas."""
        try:
            if self.redis_client:
                # Tenta Redis primeiro
                cached_data = self.redis_client.get(key)
                if cached_data:
                    data = json.loads(cached_data)

                    # Atualiza tempo de último acesso
                    access_key = f"{key}:access"
                    self.redis_client.set(access_key, time.time(), ex=3600)

                    self._cache_stats["hits"] += 1
                    performance_monitor.record_cache_hit(endpoint_type)
                    return data["value"]
            else:
                # Fallback para cache local
                if key in self._local_cache:
                    cache_entry = self._local_cache[key]
                    if cache_entry["expires_at"] > time.time():
                        self._cache_stats["hits"] += 1
                        performance_monitor.record_cache_hit(endpoint_type)
                        return cache_entry["value"]
                    else:
                        # Remove entrada expirada
                        del self._local_cache[key]

            self._cache_stats["misses"] += 1
            performance_monitor.record_cache_miss(endpoint_type)
            return None

        except Exception as e:
            logger.error(f"Erro ao recuperar do cache: {e}")
            self._cache_stats["misses"] += 1
            return None

    def set(self, key: str, value: Any, endpoint_type: str = "default", custom_ttl: int = None) -> bool:
        """Armazena valor no cache com TTL adaptativo."""
        try:
            # Calcula TTL adaptativo se não fornecido
            if custom_ttl is None:
                hit_rate = self.get_hit_rate(endpoint_type)
                last_access = time.time()  # Novo item, acesso atual
                ttl = self._calculate_adaptive_ttl(endpoint_type, hit_rate, last_access)
            else:
                ttl = custom_ttl

            cache_data = {
                "value": value,
                "created_at": time.time(),
                "endpoint_type": endpoint_type,
                "ttl": ttl
            }

            if self.redis_client:
                # Armazena no Redis
                self.redis_client.set(key, json.dumps(cache_data), ex=ttl)

                # Armazena tempo de acesso
                access_key = f"{key}:access"
                self.redis_client.set(access_key, time.time(), ex=3600)
            else:
                # Fallback para cache local
                self._local_cache[key] = {
                    "value": value,
                    "expires_at": time.time() + ttl,
                    "endpoint_type": endpoint_type
                }

            return True

        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalida chaves de cache que correspondem ao padrão."""
        invalidated_count = 0

        try:
            if self.redis_client:
                # Busca chaves que correspondem ao padrão
                keys = self.redis_client.keys(f"glpi_cache:*{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
                    invalidated_count = len(keys)
            else:
                # Invalida no cache local
                keys_to_remove = [k for k in self._local_cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self._local_cache[key]
                invalidated_count = len(keys_to_remove)

            self._cache_stats["invalidations"] += invalidated_count
            logger.info(f"Invalidadas {invalidated_count} entradas de cache para padrão: {pattern}")

        except Exception as e:
            logger.error(f"Erro ao invalidar cache por padrão: {e}")

        return invalidated_count

    def get_hit_rate(self, endpoint_type: str = None) -> float:
        """Calcula taxa de hit do cache."""
        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        if total_requests == 0:
            return 0.0

        return self._cache_stats["hits"] / total_requests

    def get_stats(self) -> Dict:
        """Retorna estatísticas detalhadas do cache."""
        stats = self._cache_stats.copy()
        stats["hit_rate"] = self.get_hit_rate()
        stats["total_requests"] = stats["hits"] + stats["misses"]

        if self.redis_client:
            try:
                info = self.redis_client.info("memory")
                stats["redis_memory_used"] = info.get("used_memory_human", "N/A")
                stats["redis_connected"] = True
            except:
                stats["redis_connected"] = False
        else:
            stats["local_cache_size"] = len(self._local_cache)
            stats["redis_connected"] = False

        return stats

    def clear_expired(self) -> int:
        """Remove entradas expiradas do cache local."""
        if self.redis_client:
            return 0  # Redis gerencia expiração automaticamente

        current_time = time.time()
        expired_keys = [
            key for key, entry in self._local_cache.items()
            if entry["expires_at"] <= current_time
        ]

        for key in expired_keys:
            del self._local_cache[key]

        return len(expired_keys)

# Instância global do cache inteligente
smart_cache = SmartCache()

def cache_with_smart_ttl(endpoint_pattern: str = None, invalidation_patterns: list = None):
    """Decorador para cache inteligente com TTL adaptativo."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave de cache baseada na função e argumentos
            endpoint = endpoint_pattern or func.__name__
            cache_key = smart_cache._generate_cache_key(
                endpoint,
                kwargs,
                kwargs.get('user_id', 'anonymous')
            )

            endpoint_type = smart_cache._get_endpoint_type(endpoint)

            # Tenta recuperar do cache
            cached_result = smart_cache.get(cache_key, endpoint_type)
            if cached_result is not None:
                return cached_result

            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            smart_cache.set(cache_key, result, endpoint_type)

            return result

        # Adiciona método para invalidação manual
        def invalidate_cache(**kwargs):
            if invalidation_patterns:
                for pattern in invalidation_patterns:
                    smart_cache.invalidate_pattern(pattern)
            else:
                # Invalida baseado no endpoint
                pattern = endpoint_pattern or func.__name__
                smart_cache.invalidate_pattern(pattern)

        wrapper.invalidate_cache = invalidate_cache
        return wrapper

    return decorator
