"""
Logging Configuration for the GoQuant Trading Bot
"""
import logging
import logging.config
import os
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_to_file: bool = True, log_to_console: bool = True):
    """Set up logging configuration for the entire application
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file (bool): Whether to log to file
        log_to_console (bool): Whether to log to console
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Define logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'detailed',
                'filename': f'{log_dir}/trading_bot_{datetime.now().strftime("%Y%m%d")}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': f'{log_dir}/errors_{datetime.now().strftime("%Y%m%d")}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {  # root logger
                'level': log_level,
                'handlers': [],
                'propagate': False
            }
        }
    }
    
    # Add handlers based on configuration
    handlers = []
    if log_to_console:
        handlers.append('console')
    if log_to_file:
        handlers.append('file')
        handlers.append('error_file')
    
    config['loggers']['']['handlers'] = handlers
    
    # Apply configuration
    logging.config.dictConfig(config)
    
def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)