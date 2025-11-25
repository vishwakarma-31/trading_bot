"""
Error Handler Utilities for the Generic Trading Bot
"""
import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

class TradingBotError(Exception):
    """Base exception class for trading bot errors"""
    pass

class DataAcquisitionError(TradingBotError):
    """Exception for data acquisition errors"""
    pass

class DataProcessingError(TradingBotError):
    """Exception for data processing errors"""
    pass

class TelegramBotError(TradingBotError):
    """Exception for Telegram bot errors"""
    pass

class APIConnectionError(DataAcquisitionError):
    """Exception for API connection errors"""
    pass

class DataParsingError(DataAcquisitionError):
    """Exception for data parsing errors"""
    pass

class WebSocketError(DataAcquisitionError):
    """Exception for WebSocket errors"""
    pass

class RateLimitError(DataAcquisitionError):
    """Exception for rate limiting errors"""
    pass

class AuthenticationError(DataAcquisitionError):
    """Exception for authentication errors"""
    pass

class InvalidDataError(DataProcessingError):
    """Exception for invalid data values"""
    pass

class MissingDataError(DataProcessingError):
    """Exception for missing data fields"""
    pass

class CalculationError(DataProcessingError):
    """Exception for calculation errors"""
    pass

class ThresholdValidationError(DataProcessingError):
    """Exception for threshold validation errors"""
    pass

class MessageSendingError(TelegramBotError):
    """Exception for message sending failures"""
    pass

class CommandParsingError(TelegramBotError):
    """Exception for command parsing errors"""
    pass

class InvalidUserInputError(TelegramBotError):
    """Exception for invalid user inputs"""
    pass

class BotAPIError(TelegramBotError):
    """Exception for bot API errors"""
    pass

def handle_exception(logger_name: str = None, reraise: bool = True, default_return=None):
    """Decorator to handle exceptions with logging
    
    Args:
        logger_name (str): Name of logger to use (defaults to module name)
        reraise (bool): Whether to reraise the exception
        default_return: Default value to return if exception occurs and not reraised
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get logger
            if logger_name:
                logger = get_logger(logger_name)
            else:
                logger = get_logger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the exception with full traceback
                logger.error(f"Exception in {func.__name__}: {str(e)}", exc_info=True)
                
                if reraise:
                    raise
                else:
                    return default_return
        return wrapper
    return decorator

def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """Log an exception with full traceback
    
    Args:
        logger (logging.Logger): Logger instance
        exception (Exception): Exception to log
        context (str): Additional context information
    """
    if context:
        logger.error(f"{context}: {str(exception)}", exc_info=True)
    else:
        logger.error(str(exception), exc_info=True)

def safe_execute(func: Callable, logger: logging.Logger, default_return=None, *args, **kwargs):
    """Safely execute a function with exception handling
    
    Args:
        func (Callable): Function to execute
        logger (logging.Logger): Logger instance
        default_return: Default value to return if exception occurs
        *args: Positional arguments for function
        **kwargs: Keyword arguments for function
        
    Returns:
        Function result or default_return if exception occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Exception in {func.__name__}: {str(e)}", exc_info=True)
        return default_return