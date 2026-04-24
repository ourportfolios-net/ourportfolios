"""Retry utilities for serverless database connections.

Implements retry logic with fixed wait intervals for handling transient
connection errors in serverless environments where connection pools
can be exhausted under burst traffic.

Reference: https://activeno.de/blog/2025-06/properly-connecting-with-a-database-on-serverless/
"""

import asyncio
import time
from typing import Any, Callable


async def retry_async(
    function: Callable[..., Any],
    max_attempts: int = 5,
    wait_ms: int = 1000,
) -> Any:
    """Retry an async function with a fixed wait interval.

    Useful for database operations that may fail due to connection exhaustion
    in serverless environments where traffic bursts can exceed pooler limits.

    Args:
        function: Async callable to retry (e.g., a database operation)
        max_attempts: Total attempts before failing
        wait_ms: Wait time in milliseconds between retries

    Returns:
        The result of function

    Raises:
        The last exception if all retry attempts fail
    """
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return await function()
        except Exception as error:
            last_error = error
            if attempt < max_attempts - 1:
                await asyncio.sleep(wait_ms / 1000)

    raise last_error if last_error else RuntimeError("Retry failed with unknown error")


def retry_sync(
    function: Callable[..., Any],
    max_attempts: int = 5,
    wait_ms: int = 1000,
) -> Any:
    """Retry a sync function with a fixed wait interval.

    Useful for synchronous database operations (e.g., pandas to_sql).

    Args:
        function: Callable to retry
        max_attempts: Total attempts before failing
        wait_ms: Wait time in milliseconds between retries

    Returns:
        The result of function

    Raises:
        The last exception if all retry attempts fail
    """
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return function()
        except Exception as error:
            last_error = error
            if attempt < max_attempts - 1:
                time.sleep(wait_ms / 1000)

    raise last_error if last_error else RuntimeError("Retry failed with unknown error")
