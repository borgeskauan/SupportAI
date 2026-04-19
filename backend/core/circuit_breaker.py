"""Circuit breaker pattern implementation for handling API failures gracefully."""

import logging
import time
from typing import Callable, TypeVar, Any
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Too many failures, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


T = TypeVar("T")


class CircuitBreaker:
    """
    Circuit breaker for handling API failures with exponential backoff retry.
    
    Prevents cascading failures and allows services time to recover.
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures detected, requests fail fast
    - HALF_OPEN: Testing recovery, one request allowed to pass
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout_seconds: int = 60,
        max_retries: int = 5,
        base_delay_seconds: float = 10.0,
        max_delay_seconds: float = 60.0,
        name: str = "CircuitBreaker",
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit (default: 3)
            timeout_seconds: Seconds to wait before retrying (default: 60)
            max_retries: Maximum retry attempts with linear backoff (default: 5)
            base_delay_seconds: Initial delay for retries in seconds (default: 10.0)
            max_delay_seconds: Maximum delay cap in seconds (default: 60.0)
            name: Circuit breaker name for logging (default: "CircuitBreaker")
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.name = name

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Result from function

        Raises:
            Exception: If circuit is open or all retries exhausted
        """
        # Check if circuit should transition to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"{self.name}: Circuit HALF_OPEN - testing recovery")
            else:
                raise RuntimeError(
                    f"{self.name}: Circuit OPEN - service unavailable (will retry in "
                    f"{self.timeout_seconds - (time.time() - self.last_failure_time):.0f}s)"
                )

        # Execute with retries and exponential backoff
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result

            except Exception as e:
                last_exception = e
                is_retryable = self._is_retryable_error(e)

                if not is_retryable:
                    # Non-retryable errors fail immediately
                    self._on_failure()
                    raise

                if attempt < self.max_retries:
                    # Calculate linear backoff delay, capped at max_delay
                    delay = min(self.base_delay_seconds * attempt, self.max_delay_seconds)
                    logger.warning(
                        f"{self.name}: Attempt {attempt}/{self.max_retries} failed "
                        f"({type(e).__name__}). Retrying in {delay:.0f}s..."
                    )
                    time.sleep(delay)
                else:
                    # All retries exhausted
                    logger.error(
                        f"{self.name}: All {self.max_retries} retries exhausted. "
                        f"Opening circuit."
                    )
                    self._on_failure()

        # If we get here, all retries failed
        raise last_exception or RuntimeError(f"{self.name}: Unknown error")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.timeout_seconds

    def _on_success(self) -> None:
        """Handle successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info(f"{self.name}: Circuit CLOSED - service recovered")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"{self.name}: Circuit OPEN - {self.failure_count} failures detected. "
                f"Blocking requests for {self.timeout_seconds}s"
            )

    @staticmethod
    def _is_retryable_error(error: Exception) -> bool:
        """
        Determine if error is retryable.

        Retryable errors: 429 (rate limit), 503 (service unavailable), timeouts
        Non-retryable: 401 (auth), 400 (bad request), etc.
        """
        error_str = str(error)

        # Check for HTTP status codes in error message
        if "429" in error_str or "Too Many Requests" in error_str:
            return True
        if "503" in error_str or "Service Unavailable" in error_str:
            return True
        if "500" in error_str or "Internal Server Error" in error_str:
            return True

        # Check for timeout-like errors
        if any(timeout_term in error_str for timeout_term in ["timeout", "connection", "UNAVAILABLE"]):
            return True

        # Default to retryable for API errors
        if "API" in error_str or "api" in error_str:
            return True

        return False

    def reset(self) -> None:
        """Force reset the circuit breaker."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        logger.info(f"{self.name}: Circuit manually reset")

    @property
    def status(self) -> dict:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self.failure_count,
            "threshold": self.failure_threshold,
            "last_failure": self.last_failure_time,
        }


def circuit_breaker(
    failure_threshold: int = 3,
    timeout_seconds: int = 60,
    max_retries: int = 5,
    base_delay_seconds: float = 10.0,
    max_delay_seconds: float = 60.0,
):
    """
    Decorator to apply circuit breaker protection to a function.

    Args:
        failure_threshold: Number of failures before opening (default: 3)
        timeout_seconds: Seconds before retry (default: 60)
        max_retries: Max retry attempts (default: 5)
        base_delay_seconds: Initial delay for retries (default: 10.0)
        max_delay_seconds: Maximum delay cap (default: 60.0)

    Example:
        @circuit_breaker(failure_threshold=3, timeout_seconds=60)
        def call_api():
            return requests.get(...)
    """
    cb = CircuitBreaker(
        failure_threshold=failure_threshold,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        base_delay_seconds=base_delay_seconds,
        max_delay_seconds=max_delay_seconds,
        name=f"CircuitBreaker",
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return cb.call(func, *args, **kwargs)

        wrapper.circuit_breaker = cb  # type: ignore
        return wrapper

    return decorator
