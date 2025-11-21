"""
Market View Module for the Generic Trading Bot
"""
import logging
import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.models import MarketViewData, ConsolidatedMarketView
from utils.error_handler import (
    DataProcessingError, InvalidDataError, MissingDataError,
    log_exception, handle_exception
)

class MarketViewManager:
    """Manages consolidated market view across multiple exchanges"""
    
    def __init__(self, market_fetcher: MarketDataFetcher):
        """Initialize market view manager"""
        self.market_fetcher = market_fetcher
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitoring_thread = None
        self.monitored_symbols = {}  # symbol -> exchanges list
        self.latest_market_data = {}  # (exchange, symbol) -> MarketViewData
        self.consolidated_views = {}  # symbol -> ConsolidatedMarketView
        self.supported_exchanges = ['binance', 'okx', 'bybit', 'deribit']
        
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_market_data(self, exchange: str, symbol: str) -> Optional[MarketViewData]:
        """
        Get market data for a specific exchange and symbol
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            MarketViewData or None if failed
        """
        try:
            # Validate inputs
            if not exchange:
                raise InvalidDataError("No exchange provided")
            if not symbol:
                raise InvalidDataError("No symbol provided")
                
            # Get L1 market data
            data = self.market_fetcher.get_l1_market_data(exchange, symbol)
            
            if not data:
                return None
                
            # Validate required data fields
            required_fields = ['bid_price', 'ask_price', 'bid_size', 'ask_size', 'timestamp']
            for field in required_fields:
                if field not in data:
                    raise MissingDataError(f"Missing {field} in market data for {symbol} on {exchange}")
                    
            # Validate data types
            for field in ['bid_price', 'ask_price', 'bid_size', 'ask_size']:
                value = data.get(field)
                if value is not None and not isinstance(value, (int, float)):
                    raise InvalidDataError(f"Invalid {field} data for {symbol} on {exchange}: {value}")
                    
            market_view = MarketViewData(
                symbol=symbol,
                exchange=exchange,
                bid_price=data.get('bid_price', 0),
                ask_price=data.get('ask_price', 0),
                bid_size=data.get('bid_size', 0),
                ask_size=data.get('ask_size', 0),
                timestamp=data.get('timestamp', time.time())
            )
            
            # Validate market view data
            if market_view.bid_price < 0 or market_view.ask_price < 0:
                raise InvalidDataError(f"Negative price values for {symbol} on {exchange}")
                
            # Cache the data
            self.latest_market_data[(exchange, symbol)] = market_view
            return market_view
            
        except Exception as e:
            log_exception(self.logger, e, f"Error getting market data for {symbol} on {exchange}")
            raise DataProcessingError(f"Error getting market data for {symbol} on {exchange}: {e}")
            
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_consolidated_market_view(self, symbol: str, exchanges: List[str]) -> Optional[ConsolidatedMarketView]:
        """
        Get consolidated market view for a symbol across multiple exchanges
        
        Args:
            symbol (str): Trading symbol
            exchanges (List[str]): List of exchanges to include
            
        Returns:
            ConsolidatedMarketView or None if failed
        """
        try:
            # Validate inputs
            if not symbol:
                raise InvalidDataError("No symbol provided")
            if not exchanges:
                raise InvalidDataError("No exchanges provided")
                
            # Get market data from all exchanges
            exchanges_data = {}
            valid_exchanges = []
            
            for exchange in exchanges:
                try:
                    if exchange in self.supported_exchanges:
                        market_data = self.get_market_data(exchange, symbol)
                        if market_data:
                            exchanges_data[exchange] = market_data
                            valid_exchanges.append(exchange)
                except Exception as e:
                    self.logger.warning(f"Failed to get market data for {symbol} on {exchange}: {e}")
                    # Continue with other exchanges
            
            if not exchanges_data:
                self.logger.warning(f"No valid market data found for {symbol} on any exchange")
                return None
                
            # Find CBBO (Consolidated Best Bid/Offer)
            best_bid_price = 0
            best_bid_exchange = ""
            best_ask_price = float('inf')
            best_ask_exchange = ""
            
            for exchange, data in exchanges_data.items():
                try:
                    # Check for best bid (highest bid)
                    if data.bid_price > best_bid_price:
                        best_bid_price = data.bid_price
                        best_bid_exchange = exchange
                        
                    # Check for best ask (lowest ask)
                    if 0 < data.ask_price < best_ask_price:
                        best_ask_price = data.ask_price
                        best_ask_exchange = exchange
                except Exception as e:
                    self.logger.warning(f"Error processing market data for {symbol} on {exchange}: {e}")
                    # Continue with other exchanges
                    
            # Validate CBBO data
            if best_bid_price <= 0:
                self.logger.warning(f"No valid bid price found for {symbol}")
                best_bid_price = 0
                best_bid_exchange = ""
                
            if best_ask_price == float('inf') or best_ask_price <= 0:
                self.logger.warning(f"No valid ask price found for {symbol}")
                best_ask_price = 0
                best_ask_exchange = ""
                
            # Create consolidated view
            consolidated_view = ConsolidatedMarketView(
                symbol=symbol,
                exchanges_data=exchanges_data,
                cbbo_bid_exchange=best_bid_exchange,
                cbbo_ask_exchange=best_ask_exchange,
                cbbo_bid_price=best_bid_price,
                cbbo_ask_price=best_ask_price,
                timestamp=time.time()
            )
            
            # Cache the consolidated view
            self.consolidated_views[symbol] = consolidated_view
            return consolidated_view
            
        except Exception as e:
            log_exception(self.logger, e, f"Error creating consolidated market view for {symbol}")
            raise DataProcessingError(f"Error creating consolidated market view for {symbol}: {e}")
            
    def get_cbbo(self, symbol: str) -> Optional[ConsolidatedMarketView]:
        """
        Get current CBBO (Consolidated Best Bid/Offer) for a symbol
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            ConsolidatedMarketView with CBBO data or None if failed
        """
        try:
            # If we're monitoring this symbol, use the cached consolidated view
            if symbol in self.consolidated_views:
                return self.consolidated_views[symbol]
                
            # Otherwise, get fresh data from all supported exchanges
            return self.get_consolidated_market_view(symbol, self.supported_exchanges)
        except Exception as e:
            self.logger.error(f"Error getting CBBO for {symbol}: {e}")
            return None
        
    def start_monitoring(self, symbol_exchanges: Dict[str, List[str]]):
        """
        Start monitoring market data for specified symbols and exchanges
        
        Args:
            symbol_exchanges (Dict[str, List[str]]): Mapping of symbols to exchange lists
        """
        try:
            if self.monitoring:
                self.logger.warning("Market view monitoring is already running")
                return
                
            self.monitoring = True
            self.monitored_symbols = symbol_exchanges
            self.logger.info(f"Starting market view monitoring for {len(symbol_exchanges)} symbols")
            
            # Subscribe to WebSocket data for real-time updates
            exchange_symbol_pairs = []
            for symbol, exchanges in symbol_exchanges.items():
                for exchange in exchanges:
                    if exchange in self.supported_exchanges:
                        exchange_symbol_pairs.append((exchange, symbol))
                        
            if exchange_symbol_pairs:
                self.market_fetcher.subscribe_multiple_l1_data(exchange_symbol_pairs, self._websocket_data_callback)
                self.logger.info(f"Subscribed to {len(exchange_symbol_pairs)} market data streams")
                
            # Start monitoring thread for periodic checks
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
        except Exception as e:
            log_exception(self.logger, e, "Error starting market view monitoring")
            raise DataProcessingError(f"Error starting market view monitoring: {e}")
        
    def stop_monitoring(self):
        """Stop market view monitoring"""
        try:
            self.monitoring = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
                
            # Unsubscribe from all WebSocket data
            self.market_fetcher.unsubscribe_all_data()
            self.logger.info("Stopped market view monitoring")
        except Exception as e:
            log_exception(self.logger, e, "Error stopping market view monitoring")
            raise DataProcessingError(f"Error stopping market view monitoring: {e}")
            
    def _websocket_data_callback(self, exchange: str, symbol: str, data: Dict):
        """
        Callback function for WebSocket data
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            data (Dict): Market data
        """
        try:
            # Update latest market data cache
            market_view = MarketViewData(
                symbol=symbol,
                exchange=exchange,
                bid_price=data.get('bid_price', 0),
                ask_price=data.get('ask_price', 0),
                bid_size=data.get('bid_size', 0),
                ask_size=data.get('ask_size', 0),
                timestamp=data.get('timestamp', time.time())
            )
            self.latest_market_data[(exchange, symbol)] = market_view
            
            # Update consolidated view for this symbol
            if symbol in self.monitored_symbols:
                exchanges = self.monitored_symbols[symbol]
                self.get_consolidated_market_view(symbol, exchanges)
                
        except Exception as e:
            log_exception(self.logger, e, f"Error processing WebSocket data for {symbol} on {exchange}")
            
    def _monitoring_loop(self):
        """Background loop for periodic market data checking"""
        while self.monitoring:
            try:
                # Update market data for all monitored symbols
                for symbol, exchanges in self.monitored_symbols.items():
                    try:
                        self.get_consolidated_market_view(symbol, exchanges)
                    except Exception as e:
                        self.logger.error(f"Error updating market view for {symbol}: {e}")
                        
                # Sleep to avoid excessive CPU usage
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in market view monitoring loop: {e}")
                time.sleep(5)  # Sleep longer on error
                
    def get_monitoring_status(self) -> Dict:
        """
        Get current monitoring status
        
        Returns:
            Dict with monitoring status information
        """
        return {
            'monitoring': self.monitoring,
            'monitored_symbols': self.monitored_symbols,
            'latest_data_count': len(self.latest_market_data),
            'consolidated_views_count': len(self.consolidated_views)
        }