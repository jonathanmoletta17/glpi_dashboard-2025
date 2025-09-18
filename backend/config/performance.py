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
    "TIMEOUT": 12,       # 12 segundos (aumentado para operações complexas)
    "FAST_TIMEOUT": 5,   # 5 segundos para operações rápidas
    "SLOW_TIMEOUT": 20,  # 20 segundos para operações pesadas
    "MAX_RETRIES": 3,    # Máximo 3 tentativas (aumentado)
    "BATCH_SIZE": 30,    # Processar em lotes menores de 30
    "MAX_RANGE": 500,    # Máximo 500 registros por consulta (reduzido)
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
