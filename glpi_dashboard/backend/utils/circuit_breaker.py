"""Circuit Breaker pattern implementation for resilient API calls."""

import time
import asyncio
from enum import Enum
from typing import Callable, Any, Optional, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with circuit breaker."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return self._call(func, *args, **kwargs)
        return wrapper

    def _call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker logic."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful function execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker reset to CLOSED")
        self.failure_count = 0

    def _on_failure(self):
        """Handle failed function execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    @property
    def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit breaker is closed."""
        return self.state == CircuitState.CLOSED

    def reset(self):
        """Manually reset the circuit breaker."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker manually reset")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        return self._call(func, *args, **kwargs)

    async def acall(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e


class GLPICircuitBreaker(CircuitBreaker):
    """GLPI-specific Circuit Breaker with enhanced monitoring."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60,
                 service_name: str = "GLPI", expected_exception: type = Exception):
        super().__init__(failure_threshold, recovery_timeout, expected_exception)
        self.service_name = service_name
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'circuit_opens': 0,
            'last_open_time': None
        }

    def _on_success(self):
        """Handle successful call with metrics."""
        super()._on_success()
        self.metrics['successful_calls'] += 1
        logger.info(f"{self.service_name} circuit breaker: successful call")

    def _on_failure(self):
        """Handle failed call with metrics."""
        was_closed = self.state == CircuitState.CLOSED
        super()._on_failure()
        self.metrics['failed_calls'] += 1

        if was_closed and self.state == CircuitState.OPEN:
            self.metrics['circuit_opens'] += 1
            self.metrics['last_open_time'] = time.time()
            logger.error(f"{self.service_name} circuit breaker opened")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with enhanced GLPI monitoring."""
        self.metrics['total_calls'] += 1
        return super().call(func, *args, **kwargs)

    async def acall(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with enhanced GLPI monitoring."""
        self.metrics['total_calls'] += 1
        return await super().acall(func, *args, **kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        success_rate = 0
        if self.metrics['total_calls'] > 0:
            success_rate = self.metrics['successful_calls'] / self.metrics['total_calls']

        return {
            **self.metrics,
            'success_rate': success_rate,
            'current_state': self.state.value,
            'failure_count': self.failure_count,
            'service_name': self.service_name
        }


# Convenience function for quick usage
def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
):
    """Decorator factory for circuit breaker."""
    cb = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await cb.acall(func, *args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


def glpi_circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60,
                        service_name: str = "GLPI"):
    """Decorator for GLPI-specific circuit breaker functionality."""
    cb = GLPICircuitBreaker(failure_threshold, recovery_timeout, service_name)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await cb.acall(func, *args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator
