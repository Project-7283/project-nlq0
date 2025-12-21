import time
import functools
import asyncio
from enum import Enum
from typing import Callable, Any, Optional
from src.utils.logging import app_logger as logger

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(
        self, 
        name: str, 
        failure_threshold: int = 5, 
        recovery_timeout: int = 30,
        expected_exception: type = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def __call__(self, func: Callable):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self.call_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self.call_sync(func, *args, **kwargs)
            return sync_wrapper

    def _before_call(self):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit {self.name} is HALF_OPEN")
            else:
                raise Exception(f"Circuit {self.name} is OPEN. Request rejected.")

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info(f"Circuit {self.name} is CLOSED again")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self, e: Exception):
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.error(f"Circuit {self.name} failure {self.failure_count}: {str(e)}")
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit {self.name} is now OPEN")
        
        raise e

    def call_sync(self, func: Callable, *args, **kwargs) -> Any:
        self._before_call()
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            return self._on_failure(e)

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        self._before_call()
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            return self._on_failure(e)
