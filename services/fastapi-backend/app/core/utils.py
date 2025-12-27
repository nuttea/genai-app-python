"""Utility functions."""

import asyncio
from typing import TypeVar, Callable, Awaitable
from functools import wraps

T = TypeVar('T')


def with_timeout(seconds: float):
    """
    Decorator to add timeout to async functions.
    
    Args:
        seconds: Timeout in seconds
        
    Returns:
        Decorated function that will raise TimeoutError if exceeded
        
    Example:
        @with_timeout(30)
        async def my_function():
            await long_running_operation()
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError as e:
                raise TimeoutError(f"{func.__name__} timed out after {seconds}s") from e
        return wrapper
    return decorator


async def run_with_timeout(coro: Awaitable[T], timeout: float) -> T:
    """
    Run a coroutine with a timeout.
    
    Args:
        coro: The coroutine to run
        timeout: Timeout in seconds
        
    Returns:
        Result of the coroutine
        
    Raises:
        TimeoutError: If the coroutine exceeds the timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError as e:
        raise TimeoutError(f"Operation timed out after {timeout}s") from e

