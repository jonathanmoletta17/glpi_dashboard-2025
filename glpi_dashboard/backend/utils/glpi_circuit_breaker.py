"""Circuit Breaker para proteção contra falhas da API GLPI.

Este módulo implementa o padrão Circuit Breaker para proteger a aplicação
contra falhas em cascata quando a API GLPI está indisponível ou instável.
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass
from threading import Lock


class CircuitState(Enum):
    """Estados do Circuit Breaker."""
    CLOSED = "closed"      # Funcionamento normal
    OPEN = "open"          # Circuito aberto, rejeitando chamadas
    HALF_OPEN = "half_open" # Testando se o serviço voltou


@dataclass
class CircuitBreakerConfig:
    """Configuração do Circuit Breaker."""
    failure_threshold: int = 5          # Número de falhas para abrir o circuito
    recovery_timeout: float = 60.0      # Tempo em segundos para tentar recuperação
    expected_exception: tuple = (Exception,)  # Exceções que contam como falha
    success_threshold: int = 3          # Sucessos necessários para fechar o circuito
    timeout: float = 60.0               # Timeout para chamadas individuais


class GLPICircuitBreakerError(Exception):
    """Exceção lançada quando o circuit breaker está aberto."""
    pass


class GLPICircuitBreaker:
    """Circuit Breaker para proteção da API GLPI.
    
    Implementa o padrão Circuit Breaker para evitar chamadas desnecessárias
    para uma API que está falhando, permitindo recuperação gradual.
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """Inicializa o Circuit Breaker.
        
        Args:
            name: Nome identificador do circuit breaker
            config: Configuração personalizada
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.logger = logging.getLogger(f"circuit_breaker.{name}")
        
        # Estado do circuit breaker
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._lock = Lock()
        
        # Métricas
        self._total_calls = 0
        self._total_failures = 0
        self._total_successes = 0
        self._total_timeouts = 0
        self._total_circuit_open_calls = 0
        
    @property
    def state(self) -> CircuitState:
        """Estado atual do circuit breaker."""
        return self._state
        
    @property
    def failure_count(self) -> int:
        """Número atual de falhas consecutivas."""
        return self._failure_count
        
    @property
    def metrics(self) -> Dict[str, Any]:
        """Métricas do circuit breaker."""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "total_successes": self._total_successes,
            "total_timeouts": self._total_timeouts,
            "total_circuit_open_calls": self._total_circuit_open_calls,
            "failure_rate": self._total_failures / max(self._total_calls, 1),
            "last_failure_time": self._last_failure_time
        }
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executa uma função protegida pelo circuit breaker.
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
            
        Raises:
            GLPICircuitBreakerError: Quando o circuito está aberto
            Exception: Outras exceções da função executada
        """
        with self._lock:
            self._total_calls += 1
            
            # Verificar se deve tentar recuperação
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    self.logger.info(f"Circuit breaker {self.name} mudou para HALF_OPEN")
                else:
                    self._total_circuit_open_calls += 1
                    raise GLPICircuitBreakerError(
                        f"Circuit breaker {self.name} está OPEN. "
                        f"Próxima tentativa em {self._time_to_next_attempt():.1f}s"
                    )
            
        # Executar a função
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Verificar timeout
            if execution_time > self.config.timeout:
                self._record_timeout()
                raise TimeoutError(
                    f"Operação excedeu timeout de {self.config.timeout}s "
                    f"(executou em {execution_time:.2f}s)"
                )
                
            self._record_success()
            return result
            
        except self.config.expected_exception as e:
            self._record_failure(e)
            raise
            
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuit breaker."""
        return (time.time() - self._last_failure_time) >= self.config.recovery_timeout
        
    def _time_to_next_attempt(self) -> float:
        """Tempo restante até a próxima tentativa de recuperação."""
        elapsed = time.time() - self._last_failure_time
        return max(0, self.config.recovery_timeout - elapsed)
        
    def _record_success(self):
        """Registra um sucesso."""
        with self._lock:
            self._total_successes += 1
            
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._reset()
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0
                
    def _record_failure(self, exception: Exception):
        """Registra uma falha."""
        with self._lock:
            self._total_failures += 1
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._failure_count >= self.config.failure_threshold:
                self._trip()
                
            self.logger.warning(
                f"Circuit breaker {self.name} registrou falha ({self._failure_count}/{self.config.failure_threshold}): {exception}"
            )
            
    def _record_timeout(self):
        """Registra um timeout."""
        with self._lock:
            self._total_timeouts += 1
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._failure_count >= self.config.failure_threshold:
                self._trip()
                
            self.logger.warning(
                f"Circuit breaker {self.name} registrou timeout ({self._failure_count}/{self.config.failure_threshold})"
            )
            
    def _trip(self):
        """Abre o circuit breaker."""
        if self._state != CircuitState.OPEN:
            self._state = CircuitState.OPEN
            self.logger.error(
                f"Circuit breaker {self.name} ABERTO após {self._failure_count} falhas. "
                f"Recuperação em {self.config.recovery_timeout}s"
            )
            
    def _reset(self):
        """Fecha o circuit breaker."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self.logger.info(f"Circuit breaker {self.name} FECHADO - serviço recuperado")
        
    def reset(self):
        """Reset manual do circuit breaker."""
        with self._lock:
            self._reset()
            self.logger.info(f"Circuit breaker {self.name} resetado manualmente")
            
    def force_open(self):
        """Força abertura do circuit breaker."""
        with self._lock:
            self._state = CircuitState.OPEN
            self._last_failure_time = time.time()
            self.logger.warning(f"Circuit breaker {self.name} forçado para OPEN")
            
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type and issubclass(exc_type, self.config.expected_exception):
            self._record_failure(exc_val)
        elif exc_type is None:
            self._record_success()
        return False


class GLPICircuitBreakerManager:
    """Gerenciador de múltiplos circuit breakers."""
    
    def __init__(self):
        self._breakers: Dict[str, GLPICircuitBreaker] = {}
        self._lock = Lock()
        self.logger = logging.getLogger("circuit_breaker_manager")
        
    def get_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> GLPICircuitBreaker:
        """Obtém ou cria um circuit breaker.
        
        Args:
            name: Nome do circuit breaker
            config: Configuração (apenas para novos breakers)
            
        Returns:
            Instância do circuit breaker
        """
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = GLPICircuitBreaker(name, config)
                self.logger.info(f"Circuit breaker '{name}' criado")
            return self._breakers[name]
            
    def register(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> GLPICircuitBreaker:
        """Registra um novo circuit breaker.
        
        Args:
            name: Nome do circuit breaker
            config: Configuração do circuit breaker
            
        Returns:
            Instância do circuit breaker criado
        """
        return self.get_breaker(name, config)
        
    def call(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Executa uma função através do circuit breaker.
        
        Args:
            name: Nome do circuit breaker
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
        """
        breaker = self.get_breaker(name)
        return breaker.call(func, *args, **kwargs)
            
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Obtém métricas de todos os circuit breakers."""
        return {name: breaker.metrics for name, breaker in self._breakers.items()}
        
    def reset_all(self):
        """Reseta todos os circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()
            self.logger.info("Todos os circuit breakers foram resetados")
            
    def get_unhealthy_breakers(self) -> Dict[str, GLPICircuitBreaker]:
        """Retorna circuit breakers que não estão saudáveis."""
        return {
            name: breaker for name, breaker in self._breakers.items()
            if breaker.state != CircuitState.CLOSED
        }


# Instância global do gerenciador
circuit_breaker_manager = GLPICircuitBreakerManager()


def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator para aplicar circuit breaker a uma função.
    
    Args:
        name: Nome do circuit breaker
        config: Configuração personalizada
        
    Example:
        @circuit_breaker("glpi_api", CircuitBreakerConfig(failure_threshold=3))
        def call_glpi_api():
            # código da API
            pass
    """
    def decorator(func: Callable) -> Callable:
        breaker = circuit_breaker_manager.get_breaker(name, config)
        
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
            
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.circuit_breaker = breaker
        return wrapper
        
    return decorator