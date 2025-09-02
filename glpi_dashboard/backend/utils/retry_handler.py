#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Retry Robusto

Implementa retry logic com backoff exponencial e integração com circuit breaker.
"""

import time
import random
import logging
from typing import Callable, Any, List, Type, Optional
from functools import wraps
from .circuit_breaker import CircuitBreakerOpenError


class RetryConfig:
    """Configuração para retry logic"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[List[Type[Exception]]] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [
            ConnectionError,
            TimeoutError,
            OSError,
        ]
        
    def is_retryable(self, exception: Exception) -> bool:
        """Verifica se a exceção é passível de retry"""
        # Nunca retry se circuit breaker está aberto
        if isinstance(exception, CircuitBreakerOpenError):
            return False
            
        return any(
            isinstance(exception, exc_type) 
            for exc_type in self.retryable_exceptions
        )
    
    def calculate_delay(self, attempt: int) -> float:
        """Calcula delay com backoff exponencial"""
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Adiciona jitter para evitar thundering herd
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
            
        return max(0, delay)


class RetryHandler:
    """Handler para retry logic"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com retry logic"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                self.logger.debug(f"Tentativa {attempt}/{self.config.max_attempts}")
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if not self.config.is_retryable(e):
                    self.logger.warning(f"Exceção não passível de retry: {type(e).__name__}: {e}")
                    raise
                
                if attempt == self.config.max_attempts:
                    self.logger.error(f"Todas as {self.config.max_attempts} tentativas falharam")
                    raise
                
                delay = self.config.calculate_delay(attempt)
                self.logger.warning(
                    f"Tentativa {attempt} falhou: {type(e).__name__}: {e}. "
                    f"Tentando novamente em {delay:.2f}s"
                )
                
                time.sleep(delay)
        
        # Nunca deveria chegar aqui, mas por segurança
        if last_exception:
            raise last_exception


# Configurações pré-definidas
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=10.0
)

AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    exponential_base=1.5
)

CONSERVATIVE_RETRY_CONFIG = RetryConfig(
    max_attempts=2,
    base_delay=2.0,
    max_delay=5.0
)


def retry_with_config(config: RetryConfig):
    """Decorator para retry com configuração customizada"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = RetryHandler(config)
            return handler.execute(func, *args, **kwargs)
        return wrapper
    return decorator


def retry(max_attempts: int = 3, base_delay: float = 1.0):
    """Decorator simples para retry"""
    config = RetryConfig(max_attempts=max_attempts, base_delay=base_delay)
    return retry_with_config(config)


def robust_retry(func: Callable):
    """Decorator para retry robusto com configuração padrão"""
    return retry_with_config(DEFAULT_RETRY_CONFIG)(func)


def get_retry_handler(config_name: str = "default") -> RetryHandler:
    """Factory para criar retry handlers"""
    configs = {
        "default": DEFAULT_RETRY_CONFIG,
        "aggressive": AGGRESSIVE_RETRY_CONFIG,
        "conservative": CONSERVATIVE_RETRY_CONFIG
    }
    
    config = configs.get(config_name, DEFAULT_RETRY_CONFIG)
    return RetryHandler(config)