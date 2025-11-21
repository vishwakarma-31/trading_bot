"""
Market View Module for the Generic Trading Bot
"""
import logging
import time
import threading
from typing import Dict, List, Optional
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
        self.supported_exchanges = ['binance', 'okx']
        
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_market_data(self, exchange: str, symbol: str) -> Optional[MarketViewData]:
        """Get market data for a specific exchange and symbol"""
        try:
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
                    
            market_view = MarketViewData(
                symbol=symbol,
                exchange=exchange,
                bid_price=data.get('bid_price', 0),
                ask_price=data.get('ask_price', 0),
                bid_size=data.get('bid_size', 0),
                ask_size=data.get('ask_size', 0),
                timestamp=data.get('timestamp', time.time())
            )
            
            # Cache the data
            self.latest_market_data[(exchange, symbol)] = market_view
            return market_view
            
        except Exception as e:
            log_exception(self.logger, e, f"Error getting market data for {symbol} on {exchange}")
            raise DataProcessingError(f"Error getting market data for {symbol} on {exchange}: {e}")
            
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def get_consolidated_market_view(self, symbol: str, exchanges: List[str]) -> Optional[ConsolidatedMarketView]:
        """Get consolidated market view for a symbol across multiple exchanges"""
        try:
            if not symbol:
                raise InvalidDataError("No symbol provided")
            if not exchanges:
                raise InvalidDataError("No exchanges provided")
                
            exchanges_data = {}
            
            for exchange in exchanges:
                try:
                    if exchange in self.supported_exchanges:
                        market_data = self.get_market_data(exchange, symbol)
                        if market_data:
                            exchanges_data[exchange] = market_data
                except Exception as e:
                    self.logger.warning(f"Failed to get market data for {symbol} on {exchange}: {e}")
            
            if not exchanges_data:
                self.logger.warning(f"No valid market data found for {symbol} on any exchange")
                return None
                
            # Find CBBO (Consolidated Best Bid/Offer)
            best_bid_price = 0.0
            best_bid_exchange = ""
            best_ask_price = float('inf')
            best_ask_exchange = ""
            
            for exchange, data in exchanges_data.items():
                # Check best bid (highest)
                if data.bid_price > best_bid_price:
                    best_bid_price = data.bid_price
                    best_bid_exchange = exchange
                
                # Check best ask (lowest, non-zero)
                if 0 < data.ask_price < best_ask_price:
                    best_ask_price = data.ask_price
                    best_ask_exchange = exchange
            
            # Reset infinity if no valid ask found
            if best_ask_price == float('inf'):
                best_ask_price = 0.0
                
            consolidated_view = ConsolidatedMarketView(
                symbol=symbol,
                exchanges_data=exchanges_data,
                cbbo_bid_exchange=best_bid_exchange,
                cbbo_ask_exchange=best_ask_exchange,
                cbbo_bid_price=best_bid_price,
                cbbo_ask_price=best_ask_price,
                timestamp=time.time()
            )
            
            self.consolidated_views[symbol] = consolidated_view
            return consolidated_view
            
        except Exception as e:
            log_exception(self.logger, e, f"Error creating consolidated market view for {symbol}")
            return None
            
    def get_cbbo(self, symbol: str) -> Optional[ConsolidatedMarketView]:
        """Get current CBBO for a symbol"""
        try:
            if symbol in self.consolidated_views:
                return self.consolidated_views[symbol]
            return self.get_consolidated_market_view(symbol, self.supported_exchanges)
        except Exception as e:
            self.logger.error(f"Error getting CBBO for {symbol}: {e}")
            return None
            
    def start_monitoring(self, symbol_exchanges: Dict[str, List[str]]):
        """Start monitoring market data"""
        if self.monitoring:
            return
        self.monitoring = True
        self.monitored_symbols = symbol_exchanges
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info(f"Started market view monitoring for {len(symbol_exchanges)} symbols")
        
    def stop_monitoring(self):
        """Stop market view monitoring"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Stopped market view monitoring")
        
    def _monitoring_loop(self):
        """Background loop for periodic market data checking"""
        while self.monitoring:
            try:
                for symbol, exchanges in self.monitored_symbols.items():
                    self.get_consolidated_market_view(symbol, exchanges)
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in market view monitoring loop: {e}")
                time.sleep(5)

    def get_monitoring_status(self) -> Dict:
        return {
            'monitoring': self.monitoring,
            'monitored_symbols': self.monitored_symbols,
            'latest_data_count': len(self.latest_market_data),
            'consolidated_views_count': len(self.consolidated_views)
        }