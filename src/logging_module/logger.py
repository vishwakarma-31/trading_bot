"""
Custom Logger for the GoQuant Trading Bot
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class CustomLogger:
    """Custom logger implementation for the trading bot"""
    
    def __init__(self, name: str, log_level: int = logging.INFO, max_file_size: int = 10*1024*1024, backup_count: int = 5):
        """Initialize custom logger with rotation
        
        Args:
            name (str): Logger name
            log_level (int): Logging level
            max_file_size (int): Maximum log file size in bytes (default 10MB)
            backup_count (int): Number of backup files to keep
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Prevent adding handlers multiple times
        if self.logger.handlers:
            return
        
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Create rotating file handler
        log_filename = f"{log_dir}/{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_filename, 
            maxBytes=max_file_size, 
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger