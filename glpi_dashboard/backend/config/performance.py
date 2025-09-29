#!/usr/bin/env python3
"""
Configurações otimizadas de performance para o GLPI Dashboard
"""

# Configurações de Cache
CACHE_CONFIG = {
    "REDIS_URL": "redis://localhost:6379/0",
    "DEFAULT_TTL": 120,  # 2 minutos
    "METRICS_TTL": 180,  # 3 minutos
    "RANKING_TTL": 300,  # 5 minutos
    "TICKETS_TTL": 60,   # 1 minuto
    "MAX_CACHE_SIZE": 1000,
}

# Configurações de API
API_CONFIG = {
    "TIMEOUT": 8,        # 8 segundos
    "MAX_RETRIES": 2,    # Máximo 2 tentativas
    "BATCH_SIZE": 50,    # Processar em lotes de 50
    "MAX_RANGE": 1000,   # Máximo 1000 registros por consulta
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    "TARGET_P95": 200,   # 200ms target
    "TARGET_P99": 500,   # 500ms target
    "SLOW_QUERY_THRESHOLD": 300,  # 300ms
    "ENABLE_MONITORING": True,
    "ENABLE_PROFILING": False,
}

# Configurações de Conexão Pool
CONNECTION_CONFIG = {
    "POOL_SIZE": 10,
    "MAX_OVERFLOW": 20,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 3600,
}

# Configurações de Concorrência
CONCURRENCY_CONFIG = {
    "MAX_WORKERS": 4,
    "ENABLE_ASYNC": True,
    "BATCH_PROCESSING": True,
}
