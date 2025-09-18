# -*- coding: utf-8 -*-
"""Decoradores simples para substituir funcionalidades removidas"""

from functools import wraps


def monitor_api_endpoint(endpoint_name):
    """Decorador simples para monitoramento de endpoints"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Simplesmente executa a função sem monitoramento adicional
            return func(*args, **kwargs)
        return wrapper
    return decorator