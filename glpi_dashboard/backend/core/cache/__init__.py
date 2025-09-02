#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Cache Unificado

Consolida todas as implementações de cache do sistema.
"""

from .unified_cache import (
    ICacheManager,
    UnifiedCache,
    TechnicianCache,
    CacheFactory,
    get_unified_cache,
    get_technician_cache,
    generate_cache_key
)

__all__ = [
    "ICacheManager",
    "UnifiedCache",
    "TechnicianCache",
    "CacheFactory",
    "get_unified_cache",
    "get_technician_cache",
    "generate_cache_key"
]