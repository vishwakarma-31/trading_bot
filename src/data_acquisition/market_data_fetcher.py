"""
Market Data Fetcher for the GoQuant Trading Bot
"""
import logging
import requests
import json
import time
from typing import Dict, List, Optional, Callable
from config.config_manager import ConfigManager
from data_acquisition.websocket_manager import WebSocketManager
from utils.error_handler import (
    APIConnectionError, DataParsingError, RateLimitError, AuthenticationError,
    log_exception, handle_exception
)

class MarketDataFetcher:
    """Fetches market data from GoMarket API"""
    
    def __init__(self, config: ConfigManager):
        """Initialize market data fetcher"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.ws_manager = WebSocketManager(config)
        self.supported_exchanges = ['binance', 'okx', 'bybit', 'deribit']
        self.rate_limit_delay = 0.1  # seconds between requests to avoid rate limiting
        
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_available_symbols(self, exchange: str) -> Optional[List[str]]:
        """
        Get available symbols for a specific exchange
        
        Args:
            exchange (str): Exchange name (e.g., 'binance', 'okx')
            
        Returns:
            List of available symbols or None if failed
        """
        try:
            endpoint = self.config.get_gomarket_symbols_endpoint(exchange)
            headers = {
                "Authorization": f"Bearer {self.config.gomarket_api_key}",
                "Access-Code": self.config.gomarket_access_code
            }
            
            self.logger.info(f"Fetching symbols from {exchange} at {endpoint}")
            response = self.session.get(endpoint, headers=headers, timeout=10)
            
            # Handle different HTTP status codes
            if response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded for {exchange}")
            elif response.status_code == 401:
                raise AuthenticationError(f"Authentication failed for {exchange}")
            elif response.status_code == 403:
                raise AuthenticationError(f"Access forbidden for {exchange}")
            elif response.status_code >= 400:
                raise APIConnectionError(f"API error {response.status_code} for {exchange}: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            symbols = data.get('symbols', [])
            self.logger.info(f"Retrieved {len(symbols)} symbols from {exchange}")
            return symbols
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout while fetching symbols from {exchange}")
            raise APIConnectionError(f"Timeout while fetching symbols from {exchange}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error while fetching symbols from {exchange}")
            raise APIConnectionError(f"Connection error while fetching symbols from {exchange}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API connection failed for {exchange}: {e}")
            raise APIConnectionError(f"API connection failed for {exchange}: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Data parsing error for {exchange}: {e}")
            raise DataParsingError(f"Data parsing error for {exchange}: {e}")
        except Exception as e:
            log_exception(self.logger, e, f"Failed to fetch symbols from {exchange}")
            raise APIConnectionError(f"Failed to fetch symbols from {exchange}: {e}")
            
    def get_all_symbols(self) -> Dict[str, List[str]]:
        """
        Get available symbols for all supported exchanges
        
        Returns:
            Dictionary mapping exchange names to symbol lists
        """
        all_symbols = {}
        for exchange in self.supported_exchanges:
            try:
                # Add delay to avoid rate limiting
                time.sleep(self.rate_limit_delay)
                symbols = self.get_available_symbols(exchange)
                if symbols:
                    all_symbols[exchange] = symbols
            except Exception as e:
                self.logger.warning(f"Failed to get symbols from {exchange}: {e}")
                # Continue with other exchanges
        return all_symbols
        
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_l1_market_data(self, exchange: str, symbol: str) -> Optional[Dict]:
        """
        Get L1 market data (BBO, last trade price) for a symbol
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            Market data dictionary or None if failed
        """
        try:
            endpoint = self.config.get_gomarket_l1_endpoint(exchange, symbol)
            headers = {
                "Authorization": f"Bearer {self.config.gomarket_api_key}",
                "Access-Code": self.config.gomarket_access_code
            }
            
            self.logger.debug(f"Fetching L1 data for {symbol} on {exchange}")
            response = self.session.get(endpoint, headers=headers, timeout=10)
            
            # Handle different HTTP status codes
            if response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded for L1 data {symbol} on {exchange}")
            elif response.status_code == 401:
                raise AuthenticationError(f"Authentication failed for L1 data {symbol} on {exchange}")
            elif response.status_code == 403:
                raise AuthenticationError(f"Access forbidden for L1 data {symbol} on {exchange}")
            elif response.status_code == 404:
                self.logger.warning(f"Symbol {symbol} not found on {exchange}")
                return None
            elif response.status_code >= 400:
                raise APIConnectionError(f"API error {response.status_code} for L1 data {symbol} on {exchange}: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"Retrieved L1 data for {symbol} on {exchange} at {data.get('timestamp')}")
            return data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout while fetching L1 data for {symbol} on {exchange}")
            raise APIConnectionError(f"Timeout while fetching L1 data for {symbol} on {exchange}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error while fetching L1 data for {symbol} on {exchange}")
            raise APIConnectionError(f"Connection error while fetching L1 data for {symbol} on {exchange}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API connection failed for L1 data {symbol} on {exchange}: {e}")
            raise APIConnectionError(f"API connection failed for L1 data {symbol} on {exchange}: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Data parsing error for L1 data {symbol} on {exchange}: {e}")
            raise DataParsingError(f"Data parsing error for L1 data {symbol} on {exchange}: {e}")
        except Exception as e:
            log_exception(self.logger, e, f"Failed to fetch L1 data for {symbol} on {exchange}")
            raise APIConnectionError(f"Failed to fetch L1 data for {symbol} on {exchange}: {e}")
            
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_l2_order_book(self, exchange: str, symbol: str) -> Optional[Dict]:
        """
        Get L2 order book data for a symbol
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            Order book data dictionary or None if failed
        """
        try:
            endpoint = self.config.get_gomarket_l2_endpoint(exchange, symbol)
            headers = {
                "Authorization": f"Bearer {self.config.gomarket_api_key}",
                "Access-Code": self.config.gomarket_access_code
            }
            
            self.logger.debug(f"Fetching L2 data for {symbol} on {exchange}")
            response = self.session.get(endpoint, headers=headers, timeout=10)
            
            # Handle different HTTP status codes
            if response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded for L2 data {symbol} on {exchange}")
            elif response.status_code == 401:
                raise AuthenticationError(f"Authentication failed for L2 data {symbol} on {exchange}")
            elif response.status_code == 403:
                raise AuthenticationError(f"Access forbidden for L2 data {symbol} on {exchange}")
            elif response.status_code == 404:
                self.logger.warning(f"Symbol {symbol} not found on {exchange} for L2 data")
                return None
            elif response.status_code >= 400:
                raise APIConnectionError(f"API error {response.status_code} for L2 data {symbol} on {exchange}: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"Retrieved L2 data for {symbol} on {exchange} at {data.get('timestamp')}")
            return data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout while fetching L2 data for {symbol} on {exchange}")
            raise APIConnectionError(f"Timeout while fetching L2 data for {symbol} on {exchange}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error while fetching L2 data for {symbol} on {exchange}")
            raise APIConnectionError(f"Connection error while fetching L2 data for {symbol} on {exchange}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API connection failed for L2 data {symbol} on {exchange}: {e}")
            raise APIConnectionError(f"API connection failed for L2 data {symbol} on {exchange}: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Data parsing error for L2 data {symbol} on {exchange}: {e}")
            raise DataParsingError(f"Data parsing error for L2 data {symbol} on {exchange}: {e}")
        except Exception as e:
            log_exception(self.logger, e, f"Failed to fetch L2 data for {symbol} on {exchange}")
            raise APIConnectionError(f"Failed to fetch L2 data for {symbol} on {exchange}: {e}")
            
    def subscribe_l1_data(self, exchange: str, symbol: str, callback: Callable):
        """
        Subscribe to L1 market data via WebSocket
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            callback (Callable): Function to call when data is received
        """
        try:
            self.ws_manager.connect(exchange, symbol, callback)
        except Exception as e:
            log_exception(self.logger, e, f"Failed to subscribe to L1 data for {symbol} on {exchange}")
            raise WebSocketError(f"Failed to subscribe to L1 data for {symbol} on {exchange}: {e}")
        
    def subscribe_l2_data(self, exchange: str, symbol: str, callback: Callable):
        """
        Subscribe to L2 order book data via WebSocket
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            callback (Callable): Function to call when data is received
        """
        try:
            # For L2 data, we might need a different endpoint
            # This would depend on GoMarket's actual API structure
            self.ws_manager.connect(exchange, symbol, callback)
        except Exception as e:
            log_exception(self.logger, e, f"Failed to subscribe to L2 data for {symbol} on {exchange}")
            raise WebSocketError(f"Failed to subscribe to L2 data for {symbol} on {exchange}: {e}")
        
    def subscribe_multiple_l1_data(self, exchange_symbol_pairs: List[tuple], callback: Callable):
        """
        Subscribe to L1 market data for multiple exchange-symbol pairs
        
        Args:
            exchange_symbol_pairs (List[tuple]): List of (exchange, symbol) tuples
            callback (Callable): Function to call when data is received
        """
        try:
            self.ws_manager.connect_multiple(exchange_symbol_pairs, callback)
        except Exception as e:
            log_exception(self.logger, e, "Failed to subscribe to multiple L1 data streams")
            raise WebSocketError(f"Failed to subscribe to multiple L1 data streams: {e}")
        
    def unsubscribe_data(self, exchange: str, symbol: str):
        """
        Unsubscribe from market data
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
        """
        try:
            self.ws_manager.disconnect(exchange, symbol)
        except Exception as e:
            log_exception(self.logger, e, f"Failed to unsubscribe from data for {symbol} on {exchange}")
            raise WebSocketError(f"Failed to unsubscribe from data for {symbol} on {exchange}: {e}")
        
    def unsubscribe_all_data(self):
        """Unsubscribe from all market data"""
        try:
            self.ws_manager.disconnect_all()
        except Exception as e:
            log_exception(self.logger, e, "Failed to unsubscribe from all data streams")
            raise WebSocketError(f"Failed to unsubscribe from all data streams: {e}")
        
    def get_multiple_l1_data(self, exchange_symbol_pairs: List[tuple]) -> Dict[tuple, Dict]:
        """
        Get L1 market data for multiple exchange-symbol pairs
        
        Args:
            exchange_symbol_pairs (List[tuple]): List of (exchange, symbol) tuples
            
        Returns:
            Dictionary mapping (exchange, symbol) tuples to market data
        """
        results = {}
        for exchange, symbol in exchange_symbol_pairs:
            try:
                # Add delay to avoid rate limiting
                time.sleep(self.rate_limit_delay)
                data = self.get_l1_market_data(exchange, symbol)
                if data:
                    results[(exchange, symbol)] = data
            except Exception as e:
                self.logger.warning(f"Failed to get L1 data for {symbol} on {exchange}: {e}")
                # Continue with other pairs
        return results
        
    def get_multiple_l2_data(self, exchange_symbol_pairs: List[tuple]) -> Dict[tuple, Dict]:
        """
        Get L2 order book data for multiple exchange-symbol pairs
        
        Args:
            exchange_symbol_pairs (List[tuple]): List of (exchange, symbol) tuples
            
        Returns:
            Dictionary mapping (exchange, symbol) tuples to order book data
        """
        results = {}
        for exchange, symbol in exchange_symbol_pairs:
            try:
                # Add delay to avoid rate limiting
                time.sleep(self.rate_limit_delay)
                data = self.get_l2_order_book(exchange, symbol)
                if data:
                    results[(exchange, symbol)] = data
            except Exception as e:
                self.logger.warning(f"Failed to get L2 data for {symbol} on {exchange}: {e}")
                # Continue with other pairs
        return results
        
    def is_websocket_connected(self, exchange: str, symbol: str) -> bool:
        """
        Check if WebSocket is connected for a specific exchange-symbol pair
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            return self.ws_manager.is_connected(exchange, symbol)
        except Exception as e:
            self.logger.error(f"Error checking WebSocket connection status for {symbol} on {exchange}: {e}")
            return False