"""
Application Controller for the GoQuant Trading Bot
Manages the main application loop and integration of all modules
"""
import logging
import signal
import sys
import time
import threading
import os

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config_manager import ConfigManager
from telegram_bot.bot_handler import TelegramBotHandler
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.arbitrage_detector import ArbitrageDetector
from data_processing.service_controller import ServiceController
from logging_module.logging_config import setup_logging, get_logger

class ApplicationError(Exception):
    """Base exception for application errors"""
    pass

class ApplicationInitializationError(ApplicationError):
    """Exception for application initialization errors"""
    pass

class ApplicationRuntimeError(ApplicationError):
    """Exception for application runtime errors"""
    pass

class ApplicationController:
    """Manages the main application loop and integration of all modules"""
    
    def __init__(self):
        """Initialize application controller"""
        self.logger = None
        self.config = None
        self.market_fetcher = None
        self.arbitrage_detector = None
        self.service_controller = None
        self.bot_handler = None
        self.running = False
        self.shutdown_event = threading.Event()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def initialize(self) -> bool:
        """
        Initialize all application components
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger = get_logger(__name__)
            self.logger.info("Initializing GoQuant Trading Bot...")
            
            # Initialize configuration
            self.config = ConfigManager()
            self.logger.info("Configuration loaded")
            
            # Initialize logging
            setup_logging(log_level="INFO")
            self.logger.info("Logging system initialized")
            
            # Initialize market data fetcher
            self.market_fetcher = MarketDataFetcher(self.config)
            self.logger.info("Market data fetcher initialized")
            
            # Initialize arbitrage detector
            self.arbitrage_detector = ArbitrageDetector(self.market_fetcher, self.config)
            self.logger.info("Arbitrage detector initialized")
            
            # Initialize service controller
            self.service_controller = ServiceController(self.market_fetcher, self.config)
            self.logger.info("Service controller initialized")
            
            # Initialize Telegram bot handler
            self.bot_handler = TelegramBotHandler(
                self.config, 
                self.arbitrage_detector, 
                self.market_fetcher
            )
            self.logger.info("Telegram bot handler initialized")
            
            self.logger.info("Application initialization completed successfully")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize application: {e}", exc_info=True)
            else:
                print(f"Failed to initialize application: {e}")
            return False
            
    def start(self) -> bool:
        """
        Start the main application loop
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.initialize():
                raise ApplicationInitializationError("Failed to initialize application")
                
            self.logger.info("Starting GoQuant Trading Bot...")
            self.running = True
            
            # Start Telegram bot
            self.bot_handler.start()
            self.logger.info("Telegram bot started")
            
            # Main event loop
            self._main_loop()
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error starting application: {e}", exc_info=True)
            else:
                print(f"Error starting application: {e}")
            return False
            
    def _main_loop(self):
        """Main application event loop"""
        self.logger.info("Entering main application loop")
        
        try:
            while self.running and not self.shutdown_event.is_set():
                # Check service status
                if self.service_controller:
                    status = self.service_controller.get_service_status()
                    # Log status periodically (every 60 seconds)
                    if int(time.time()) % 60 == 0:
                        self.logger.debug(f"Service status: Arbitrage monitoring: {status['arbitrage_service']['monitoring']}, "
                                        f"Market view monitoring: {status['market_view_service']['monitoring']}")
                
                # Sleep to avoid excessive CPU usage
                if self.shutdown_event.wait(timeout=1):
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
            raise ApplicationRuntimeError(f"Error in main loop: {e}")
            
    def stop(self):
        """Stop the application gracefully"""
        try:
            self.logger.info("Stopping GoQuant Trading Bot...")
            self.running = False
            self.shutdown_event.set()
            
            # Stop Telegram bot
            if self.bot_handler:
                self.bot_handler.stop()
                self.logger.info("Telegram bot stopped")
                
            # Stop all services
            if self.service_controller:
                self.service_controller.stop_all_services()
                self.logger.info("All services stopped")
                
            self.logger.info("Application stopped successfully")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error stopping application: {e}", exc_info=True)
            else:
                print(f"Error stopping application: {e}")
                
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        if self.logger:
            self.logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")
        else:
            print(f"Received {signal_name} signal, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)
        
    def is_running(self) -> bool:
        """
        Check if application is running
        
        Returns:
            bool: True if running, False otherwise
        """
        return self.running and not self.shutdown_event.is_set()