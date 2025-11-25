"""
WebSocket Manager for the Generic Trading Bot
"""
import logging
import websocket
import json
import time
import threading
from typing import Dict, List, Callable, Optional
from config.config_manager import ConfigManager
from utils.error_handler import WebSocketError, log_exception

class WebSocketManager:
    """Manages WebSocket connections for real-time market data"""
    
    def __init__(self, config: ConfigManager):
        """Initialize WebSocket manager"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connections = {}  # {(exchange, symbol): connection_info}
        self.running = {}  # {(exchange, symbol): bool}
        self.threads = {}  # {(exchange, symbol): thread}
        self.callbacks = {}  # {(exchange, symbol): callback_function}
        self.reconnect_attempts = {}  # {(exchange, symbol): attempt_count}
        self.max_reconnect_attempts = 5
        
    def _get_websocket_url(self, exchange: str, symbol: str, data_type: str) -> str:
        """
        Get WebSocket URL for a specific exchange, symbol, and data type
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            data_type (str): Type of data ('l1' or 'l2')
            
        Returns:
            WebSocket URL
        """
        # This is a placeholder - actual WebSocket URLs would be different
        # For now, we're using a placeholder URL
        return f"wss://market-data.generic-trading-bot.io/ws/{data_type}/{exchange}/{symbol}"
        
    def _on_message(self, ws, message, exchange: str, symbol: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            self.logger.debug(f"Received WebSocket data for {symbol} on {exchange}")
            
            # Call the registered callback if it exists
            key = (exchange, symbol)
            if key in self.callbacks and self.callbacks[key]:
                self.callbacks[key](exchange, symbol, data)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse WebSocket message for {symbol} on {exchange}: {e}")
        except Exception as e:
            log_exception(self.logger, e, f"Error handling WebSocket message for {symbol} on {exchange}")
            
    def _on_error(self, ws, error, exchange: str, symbol: str):
        """Handle WebSocket error"""
        self.logger.error(f"WebSocket error for {symbol} on {exchange}: {error}")
        key = (exchange, symbol)
        self.running[key] = False
        
        # Log additional details if available
        if hasattr(error, 'status_code'):
            self.logger.error(f"WebSocket error status code: {error.status_code}")
        if hasattr(error, 'message'):
            self.logger.error(f"WebSocket error message: {error.message}")
            
    def _on_close(self, ws, close_status_code, close_msg, exchange: str, symbol: str):
        """Handle WebSocket close"""
        key = (exchange, symbol)
        self.logger.info(f"WebSocket connection closed for {symbol} on {exchange} (code: {close_status_code}, message: {close_msg})")
        self.running[key] = False
        
        # Attempt to reconnect if still needed
        if key in self.running and self.running[key]:
            self.reconnect_attempts[key] = self.reconnect_attempts.get(key, 0) + 1
            if self.reconnect_attempts[key] <= self.max_reconnect_attempts:
                self.logger.info(f"Attempting to reconnect WebSocket for {symbol} on {exchange} (attempt {self.reconnect_attempts[key]})")
                time.sleep(5)  # Wait before reconnecting
                try:
                    self.connect(exchange, symbol, self.callbacks.get(key))
                except Exception as e:
                    self.logger.error(f"Failed to reconnect WebSocket for {symbol} on {exchange}: {e}")
            else:
                self.logger.error(f"Max reconnect attempts reached for {symbol} on {exchange}")
                
    def _on_open(self, ws, exchange: str, symbol: str):
        """Handle WebSocket open"""
        key = (exchange, symbol)
        self.logger.info(f"WebSocket connection opened for {symbol} on {exchange}")
        self.reconnect_attempts[key] = 0  # Reset reconnect attempts on successful connection
        
    def connect(self, exchange: str, symbol: str, callback: Callable = None):
        """
        Connect to WebSocket for real-time data
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            callback (Callable): Function to call when data is received
        """
        key = (exchange, symbol)
        
        # Store callback
        self.callbacks[key] = callback
        
        # Set running status
        self.running[key] = True
        
        try:
            # Get WebSocket URL for L1 data (BBO and last trade)
            ws_url = self._get_websocket_url(exchange, symbol, 'l1')
            
            def on_message(ws, message):
                self._on_message(ws, message, exchange, symbol)
                
            def on_error(ws, error):
                self._on_error(ws, error, exchange, symbol)
                
            def on_close(ws, close_status_code, close_msg):
                self._on_close(ws, close_status_code, close_msg, exchange, symbol)
                
            def on_open(ws):
                self._on_open(ws, exchange, symbol)
            
            # Create WebSocket connection
            ws = websocket.WebSocketApp(ws_url,
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            
            # Store connection
            self.connections[key] = ws
            
            # Start WebSocket in a separate thread
            thread = threading.Thread(target=ws.run_forever, 
                                    kwargs={'ping_interval': 30, 'ping_timeout': 10})
            thread.daemon = True
            thread.start()
            
            self.threads[key] = thread
            
            self.logger.info(f"WebSocket connection initiated for {symbol} on {exchange}")
            
        except Exception as e:
            log_exception(self.logger, e, f"Failed to connect WebSocket for {symbol} on {exchange}")
            self.running[key] = False
            raise WebSocketError(f"Failed to connect WebSocket for {symbol} on {exchange}: {e}")
            
    def connect_multiple(self, exchange_symbol_pairs: List[tuple], callback: Callable = None):
        """
        Connect to multiple WebSocket streams
        
        Args:
            exchange_symbol_pairs (List[tuple]): List of (exchange, symbol) tuples
            callback (Callable): Function to call when data is received
        """
        connected_count = 0
        failed_count = 0
        
        for exchange, symbol in exchange_symbol_pairs:
            try:
                self.connect(exchange, symbol, callback)
                connected_count += 1
            except Exception as e:
                self.logger.error(f"Failed to connect WebSocket for {symbol} on {exchange}: {e}")
                failed_count += 1
                
        self.logger.info(f"Connected to {connected_count} WebSocket streams, {failed_count} failed")
            
    def disconnect(self, exchange: str, symbol: str):
        """
        Disconnect WebSocket connection
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
        """
        key = (exchange, symbol)
        
        try:
            # Set running status to False
            self.running[key] = False
            
            # Close WebSocket connection
            if key in self.connections:
                ws = self.connections[key]
                if ws:
                    ws.close()
                del self.connections[key]
                
            # Clean up other data structures
            if key in self.threads:
                del self.threads[key]
            if key in self.callbacks:
                del self.callbacks[key]
            if key in self.reconnect_attempts:
                del self.reconnect_attempts[key]
                
            self.logger.info(f"Disconnected WebSocket for {symbol} on {exchange}")
            
        except Exception as e:
            log_exception(self.logger, e, f"Error disconnecting WebSocket for {symbol} on {exchange}")
            raise WebSocketError(f"Error disconnecting WebSocket for {symbol} on {exchange}: {e}")
            
    def disconnect_all(self):
        """Disconnect all WebSocket connections"""
        try:
            keys = list(self.connections.keys())
            disconnected_count = 0
            
            for exchange, symbol in keys:
                try:
                    self.disconnect(exchange, symbol)
                    disconnected_count += 1
                except Exception as e:
                    self.logger.error(f"Error disconnecting WebSocket for {symbol} on {exchange}: {e}")
                    
            self.logger.info(f"Disconnected {disconnected_count} WebSocket connections")
            
        except Exception as e:
            log_exception(self.logger, e, "Error disconnecting all WebSocket connections")
            raise WebSocketError(f"Error disconnecting all WebSocket connections: {e}")
            
    def is_connected(self, exchange: str, symbol: str) -> bool:
        """
        Check if WebSocket is connected
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            key = (exchange, symbol)
            return key in self.connections and self.running.get(key, False)
        except Exception as e:
            self.logger.error(f"Error checking WebSocket connection status for {symbol} on {exchange}: {e}")
            return False