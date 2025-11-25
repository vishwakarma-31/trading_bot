"""
Mock Market Data Fetcher for the Generic Trading Bot
This allows running the system with simulated market data.
"""
import logging
import random
import time
from typing import Dict, List, Optional
from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher

class MockMarketDataFetcher(MarketDataFetcher):
    """Mock fetcher that simulates market data for testing purposes"""
    
    def __init__(self, config: ConfigManager):
        """Initialize mock market data fetcher"""
        # Initialize the parent class
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.mock_symbols = {
            'binance': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT'],
            'okx': ['BTC-USDT', 'ETH-USDT', 'OKB-USDT', 'DOT-USDT', 'UNI-USDT'],
            'bybit': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'MATICUSDT', 'DOGEUSDT'],
            'deribit': ['BTC_USDC', 'ETH_USDC', 'SOL_USDC', 'ADA_USDC', 'XRP_USDC']
        }
        
    def get_available_symbols(self, exchange: str) -> Optional[List[str]]:
        """
        Get available symbols for a specific exchange (mock implementation)
        
        Args:
            exchange (str): Exchange name (e.g., 'binance', 'okx')
            
        Returns:
            List of available symbols or None if failed
        """
        try:
            if exchange not in self.supported_exchanges:
                self.logger.warning(f"Unsupported exchange: {exchange}")
                return None
                
            symbols = self.mock_symbols.get(exchange, [])
            self.logger.info(f"Retrieved {len(symbols)} mock symbols from {exchange}")
            return symbols
            
        except Exception as e:
            self.logger.error(f"Failed to get mock symbols from {exchange}: {e}")
            return None
            
    def get_all_symbols(self) -> Dict[str, List[str]]:
        """
        Get available symbols for all supported exchanges (mock implementation)
        
        Returns:
            Dictionary mapping exchange names to symbol lists
        """
        all_symbols = {}
        for exchange in self.supported_exchanges:
            try:
                symbols = self.get_available_symbols(exchange)
                if symbols:
                    all_symbols[exchange] = symbols
            except Exception as e:
                self.logger.warning(f"Failed to get mock symbols from {exchange}: {e}")
                # Continue with other exchanges
        return all_symbols
        
    def get_l1_market_data(self, exchange: str, symbol: str) -> Optional[Dict]:
        """
        Get L1 market data (BBO, last trade price) for a symbol (mock implementation)
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            Market data dictionary or None if failed
        """
        try:
            # Check if exchange and symbol are valid
            if exchange not in self.supported_exchanges:
                self.logger.warning(f"Unsupported exchange: {exchange}")
                return None
                
            # Check if symbol exists for this exchange
            exchange_symbols = self.mock_symbols.get(exchange, [])
            if symbol not in exchange_symbols:
                # Try to find a similar symbol by normalizing both
                normalized_input = self._normalize_symbol_name(symbol)
                found_symbol = None
                for exch_sym in exchange_symbols:
                    normalized_exchange = self._normalize_symbol_name(exch_sym)
                    if normalized_input == normalized_exchange:
                        found_symbol = exch_sym
                        break
                if not found_symbol:
                    self.logger.warning(f"Symbol {symbol} not found on {exchange}")
                    return None
                symbol = found_symbol
                
            # Generate realistic mock market data
            base_price = self._get_base_price(symbol)
            # Ensure bid < ask by generating them in the right order
            bid_price = base_price * (1 - random.uniform(0.001, 0.005))  # 0.1%-0.5% below base
            ask_price = base_price * (1 + random.uniform(0.001, 0.005))  # 0.1%-0.5% above base
            
            # Ensure bid < ask
            if bid_price >= ask_price:
                bid_price = ask_price * 0.999
                
            market_data = {
                'symbol': symbol,
                'exchange': exchange,
                'bid_price': round(bid_price, self._get_precision(symbol)),
                'ask_price': round(ask_price, self._get_precision(symbol)),
                'last_price': round(base_price, self._get_precision(symbol)),
                'bid_size': round(random.uniform(0.1, 10), 4),
                'ask_size': round(random.uniform(0.1, 10), 4),
                'timestamp': time.time()
            }
            
            self.logger.debug(f"Generated mock L1 data for {symbol} on {exchange}")
            return market_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate mock L1 data for {symbol} on {exchange}: {e}")
            return None
            
    def get_l2_order_book(self, exchange: str, symbol: str) -> Optional[Dict]:
        """
        Get L2 order book data for a symbol (mock implementation)
        
        Args:
            exchange (str): Exchange name
            symbol (str): Trading symbol
            
        Returns:
            Order book data dictionary or None if failed
        """
        try:
            # Check if exchange and symbol are valid
            if exchange not in self.supported_exchanges:
                self.logger.warning(f"Unsupported exchange: {exchange}")
                return None
                
            # Check if symbol exists for this exchange
            exchange_symbols = self.mock_symbols.get(exchange, [])
            if symbol not in exchange_symbols:
                # Try to find a similar symbol by normalizing both
                normalized_input = self._normalize_symbol_name(symbol)
                found_symbol = None
                for exch_sym in exchange_symbols:
                    normalized_exchange = self._normalize_symbol_name(exch_sym)
                    if normalized_input == normalized_exchange:
                        found_symbol = exch_sym
                        break
                if not found_symbol:
                    self.logger.warning(f"Symbol {symbol} not found on {exchange}")
                    return None
                symbol = found_symbol
                
            # Generate realistic mock order book data
            base_price = self._get_base_price(symbol)
            bid_levels = []
            ask_levels = []
            
            # Generate 10 levels of bids and asks
            for i in range(10):
                # Bids (lower prices)
                bid_price = base_price * (1 - random.uniform(0.0001 * (i+1), 0.0005 * (i+1)))
                bid_size = random.uniform(0.1, 5)
                bid_levels.append({
                    'price': round(bid_price, self._get_precision(symbol)),
                    'size': round(bid_size, 4)
                })
                
                # Asks (higher prices)
                ask_price = base_price * (1 + random.uniform(0.0001 * (i+1), 0.0005 * (i+1)))
                ask_size = random.uniform(0.1, 5)
                ask_levels.append({
                    'price': round(ask_price, self._get_precision(symbol)),
                    'size': round(ask_size, 4)
                })
            
            # Sort bids (highest first) and asks (lowest first)
            bid_levels.sort(key=lambda x: x['price'], reverse=True)
            ask_levels.sort(key=lambda x: x['price'])
            
            order_book_data = {
                'symbol': symbol,
                'exchange': exchange,
                'bids': bid_levels,
                'asks': ask_levels,
                'timestamp': time.time()
            }
            
            self.logger.debug(f"Generated mock L2 data for {symbol} on {exchange}")
            return order_book_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate mock L2 data for {symbol} on {exchange}: {e}")
            return None
            
    def _normalize_symbol_name(self, symbol: str) -> str:
        """Normalize symbol name by removing separators"""
        return symbol.replace('-', '').replace('_', '').replace('/', '').upper()
            
    def _get_base_price(self, symbol: str) -> float:
        """Get a base price for a symbol based on its name"""
        symbol_lower = symbol.lower()
        if 'btc' in symbol_lower:
            return random.uniform(30000, 60000)  # BTC price range
        elif 'eth' in symbol_lower:
            return random.uniform(2000, 4000)    # ETH price range
        elif 'bnb' in symbol_lower:
            return random.uniform(300, 600)      # BNB price range
        elif 'ada' in symbol_lower:
            return random.uniform(0.5, 1.5)      # ADA price range
        elif 'xrp' in symbol_lower:
            return random.uniform(0.5, 1.0)      # XRP price range
        elif 'sol' in symbol_lower:
            return random.uniform(100, 200)      # SOL price range
        elif 'dot' in symbol_lower:
            return random.uniform(7, 15)         # DOT price range
        elif 'uni' in symbol_lower:
            return random.uniform(5, 15)         # UNI price range
        elif 'matic' in symbol_lower:
            return random.uniform(0.8, 1.5)      # MATIC price range
        elif 'doge' in symbol_lower:
            return random.uniform(0.1, 0.2)      # DOGE price range
        elif 'okb' in symbol_lower:
            return random.uniform(50, 100)       # OKB price range
        else:
            return random.uniform(1, 100)        # Default price range
            
    def _get_precision(self, symbol: str) -> int:
        """Get the price precision for a symbol"""
        symbol_lower = symbol.lower()
        if 'btc' in symbol_lower:
            return 2  # BTC typically priced to 2 decimal places
        elif 'eth' in symbol_lower:
            return 2  # ETH typically priced to 2 decimal places
        else:
            return 4  # Most other symbols to 4 decimal places