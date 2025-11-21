"""
Market Data Fetcher using CCXT for the Generic Trading Bot
"""
import logging
import time
import ccxt
import asyncio
from typing import Dict, List, Optional
from config.config_manager import ConfigManager
from utils.error_handler import (
    APIConnectionError, DataParsingError, RateLimitError, AuthenticationError,
    log_exception, handle_exception
)

class MarketDataFetcher:
    """Fetches market data using CCXT library"""
    
    def __init__(self, config: ConfigManager):
        """Initialize market data fetcher with CCXT clients"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.supported_exchanges = ['binance', 'okx']
        
        # Initialize CCXT clients for supported exchanges
        self.exchanges = {}
        enabled_exchanges = config.get_enabled_exchanges()
        
        if 'binance' in enabled_exchanges:
            try:
                binance_config = config.get_exchange_config('binance')
                self.exchanges['binance'] = ccxt.binance({
                    'enableRateLimit': True,
                    'rateLimit': int(binance_config.get('rate_limit', 0.1) * 1000)  # CCXT uses milliseconds
                })
                self.logger.info("Initialized Binance CCXT client")
            except Exception as e:
                self.logger.error(f"Failed to initialize Binance client: {e}")
                
        if 'okx' in enabled_exchanges:
            try:
                okx_config = config.get_exchange_config('okx')
                self.exchanges['okx'] = ccxt.okx({
                    'enableRateLimit': True,
                    'rateLimit': int(okx_config.get('rate_limit', 0.1) * 1000)  # CCXT uses milliseconds
                })
                self.logger.info("Initialized OKX CCXT client")
            except Exception as e:
                self.logger.error(f"Failed to initialize OKX client: {e}")
        
        # Set rate limit delays from config
        self.rate_limit_delays = {
            'binance': config.get_exchange_config('binance').get('rate_limit', 0.1),
            'okx': config.get_exchange_config('okx').get('rate_limit', 0.1)
        }
        
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_available_symbols(self, exchange: str) -> Optional[List[str]]:
        """
        Get available symbols for a specific exchange using CCXT
        
        Args:
            exchange (str): Exchange name (e.g., 'binance', 'okx')
            
        Returns:
            List of available symbols or None if failed
        """
        try:
            if exchange not in self.exchanges:
                raise APIConnectionError(f"Exchange {exchange} not initialized or not supported")
            
            # Load markets for the exchange
            exchange_client = self.exchanges[exchange]
            markets = exchange_client.load_markets()
            
            # Extract symbol names
            symbols = list(markets.keys())
            self.logger.info(f"Retrieved {len(symbols)} symbols from {exchange}")
            return symbols
            
        except ccxt.RateLimitExceeded as e:
            self.logger.error(f"Rate limit exceeded for {exchange}: {e}")
            raise RateLimitError(f"Rate limit exceeded for {exchange}")
        except ccxt.AuthenticationError as e:
            self.logger.error(f"Authentication failed for {exchange}: {e}")
            raise AuthenticationError(f"Authentication failed for {exchange}")
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error for {exchange}: {e}")
            raise APIConnectionError(f"Exchange error for {exchange}: {e}")
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
            if exchange in self.exchanges:  # Only fetch for initialized exchanges
                try:
                    # Add delay to avoid rate limiting
                    time.sleep(self.rate_limit_delays.get(exchange, 0.1))
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
        Get L1 market data (BBO, last trade price) for a symbol using CCXT
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            Market data dictionary or None if failed
        """
        try:
            if exchange not in self.exchanges:
                raise APIConnectionError(f"Exchange {exchange} not initialized or not supported")
            
            # Validate symbol exists
            exchange_client = self.exchanges[exchange]
            if symbol not in exchange_client.markets:
                # Try to load markets if not already loaded
                exchange_client.load_markets()
                if symbol not in exchange_client.markets:
                    self.logger.warning(f"Symbol {symbol} not found on {exchange}")
                    return None
            
            self.logger.debug(f"Fetching L1 data for {symbol} on {exchange}")
            ticker = exchange_client.fetch_ticker(symbol)
            
            # Convert CCXT ticker format to our internal format
            data = {
                'symbol': symbol,
                'bid_price': ticker.get('bid', 0),
                'ask_price': ticker.get('ask', 0),
                'bid_size': ticker.get('bidVolume', 0),
                'ask_size': ticker.get('askVolume', 0),
                'last_price': ticker.get('last', 0),
                'timestamp': ticker.get('timestamp', time.time() * 1000) / 1000,  # Convert ms to seconds
                'datetime': ticker.get('datetime', ''),
                'high': ticker.get('high', 0),
                'low': ticker.get('low', 0),
                'volume': ticker.get('baseVolume', 0)
            }
            
            self.logger.debug(f"Retrieved L1 data for {symbol} on {exchange} at {data.get('timestamp')}")
            return data
            
        except ccxt.RateLimitExceeded as e:
            self.logger.error(f"Rate limit exceeded for L1 data {symbol} on {exchange}: {e}")
            raise RateLimitError(f"Rate limit exceeded for L1 data {symbol} on {exchange}")
        except ccxt.BadSymbol as e:
            self.logger.warning(f"Symbol {symbol} not found on {exchange}: {e}")
            return None
        except ccxt.AuthenticationError as e:
            self.logger.error(f"Authentication failed for L1 data {symbol} on {exchange}: {e}")
            raise AuthenticationError(f"Authentication failed for L1 data {symbol} on {exchange}")
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error for L1 data {symbol} on {exchange}: {e}")
            raise APIConnectionError(f"Exchange error for L1 data {symbol} on {exchange}: {e}")
        except Exception as e:
            log_exception(self.logger, e, f"Failed to fetch L1 data for {symbol} on {exchange}")
            raise APIConnectionError(f"Failed to fetch L1 data for {symbol} on {exchange}: {e}")
            
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_l2_order_book(self, exchange: str, symbol: str) -> Optional[Dict]:
        """
        Get L2 order book data for a symbol using CCXT
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            Order book data dictionary or None if failed
        """
        try:
            if exchange not in self.exchanges:
                raise APIConnectionError(f"Exchange {exchange} not initialized or not supported")
            
            # Validate symbol exists
            exchange_client = self.exchanges[exchange]
            if symbol not in exchange_client.markets:
                # Try to load markets if not already loaded
                exchange_client.load_markets()
                if symbol not in exchange_client.markets:
                    self.logger.warning(f"Symbol {symbol} not found on {exchange}")
                    return None
            
            self.logger.debug(f"Fetching L2 data for {symbol} on {exchange}")
            orderbook = exchange_client.fetch_order_book(symbol)
            
            # Convert CCXT order book format to our internal format
            data = {
                'symbol': symbol,
                'bids': orderbook.get('bids', []),
                'asks': orderbook.get('asks', []),
                'timestamp': orderbook.get('timestamp', time.time() * 1000) / 1000,  # Convert ms to seconds
                'datetime': orderbook.get('datetime', ''),
                'nonce': orderbook.get('nonce', 0)
            }
            
            self.logger.debug(f"Retrieved L2 data for {symbol} on {exchange} at {data.get('timestamp')}")
            return data
            
        except ccxt.RateLimitExceeded as e:
            self.logger.error(f"Rate limit exceeded for L2 data {symbol} on {exchange}: {e}")
            raise RateLimitError(f"Rate limit exceeded for L2 data {symbol} on {exchange}")
        except ccxt.BadSymbol as e:
            self.logger.warning(f"Symbol {symbol} not found on {exchange}: {e}")
            return None
        except ccxt.AuthenticationError as e:
            self.logger.error(f"Authentication failed for L2 data {symbol} on {exchange}: {e}")
            raise AuthenticationError(f"Authentication failed for L2 data {symbol} on {exchange}")
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error for L2 data {symbol} on {exchange}: {e}")
            raise APIConnectionError(f"Exchange error for L2 data {symbol} on {exchange}: {e}")
        except Exception as e:
            log_exception(self.logger, e, f"Failed to fetch L2 data for {symbol} on {exchange}")
            raise APIConnectionError(f"Failed to fetch L2 data for {symbol} on {exchange}: {e}")
            
    # Simplified implementation using REST polling instead of WebSocket for stability
    # In a production environment, you might want to implement proper WebSocket handling
    def poll_l1_data(self, exchange: str, symbol: str, callback, interval: float = 1.0):
        """
        Poll L1 market data at regular intervals (simplified alternative to WebSocket)
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            callback (Callable): Function to call when data is received
            interval (float): Polling interval in seconds
        """
        def poll_loop():
            while True:
                try:
                    data = self.get_l1_market_data(exchange, symbol)
                    if data:
                        callback(data)
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in polling loop for {symbol} on {exchange}: {e}")
                    time.sleep(interval)  # Continue polling even on error
        
        # Start polling in a separate thread
        import threading
        poll_thread = threading.Thread(target=poll_loop, daemon=True)
        poll_thread.start()
        return poll_thread
    
    def poll_l2_data(self, exchange: str, symbol: str, callback, interval: float = 1.0):
        """
        Poll L2 order book data at regular intervals (simplified alternative to WebSocket)
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            callback (Callable): Function to call when data is received
            interval (float): Polling interval in seconds
        """
        def poll_loop():
            while True:
                try:
                    data = self.get_l2_order_book(exchange, symbol)
                    if data:
                        callback(data)
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in polling loop for L2 data {symbol} on {exchange}: {e}")
                    time.sleep(interval)  # Continue polling even on error
        
        # Start polling in a separate thread
        import threading
        poll_thread = threading.Thread(target=poll_loop, daemon=True)
        poll_thread.start()
        return poll_thread
        
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
            if exchange in self.exchanges:  # Only fetch for initialized exchanges
                try:
                    # Add delay to avoid rate limiting
                    time.sleep(self.rate_limit_delays.get(exchange, 0.1))
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
            if exchange in self.exchanges:  # Only fetch for initialized exchanges
                try:
                    # Add delay to avoid rate limiting
                    time.sleep(self.rate_limit_delays.get(exchange, 0.1))
                    data = self.get_l2_order_book(exchange, symbol)
                    if data:
                        results[(exchange, symbol)] = data
                except Exception as e:
                    self.logger.warning(f"Failed to get L2 data for {symbol} on {exchange}: {e}")
                    # Continue with other pairs
        return results