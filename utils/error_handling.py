#!/usr/bin/env python3
"""
Error Handling Utilities for AI Microscope Application
Provides decorators and utilities for error handling and retry logic
"""

import functools
import time
import logging
from typing import Callable, Optional, Type, Tuple, Any

logger = logging.getLogger("AI_Microscope")


class GracefulDegradationError(Exception):
    """Exception raised when a component fails but application can continue."""
    pass


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    fallback_value: Optional[Any] = None
):
    """Decorator to retry a function on exception with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry on
        fallback_value: Value to return if all retries fail
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            if fallback_value is not None:
                logger.warning(f"Using fallback value for {func.__name__}")
                return fallback_value
            raise last_exception
        
        return wrapper
    return decorator


def handle_error_gracefully(
    fallback_value: Optional[Any] = None,
    log_level: str = "error",
    reraise: bool = False
):
    """Decorator to handle errors gracefully without crashing.
    
    Args:
        fallback_value: Value to return if function fails
        log_level: Logging level ('error', 'warning', 'info')
        reraise: Whether to re-raise the exception after handling
        
    Returns:
        Decorated function with graceful error handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_func = getattr(logger, log_level.lower(), logger.error)
                log_func(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                
                if reraise:
                    raise
                return fallback_value
        
        return wrapper
    return decorator


def validate_input(*validators: Callable):
    """Decorator to validate function inputs.
    
    Args:
        validators: Functions that validate input and raise ValueError if invalid
        
    Returns:
        Decorated function with input validation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for validator in validators:
                validator(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator
