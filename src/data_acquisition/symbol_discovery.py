import requests
import logging
import time
from typing import List, Dict, Optional, Union
from config.config_manager import ConfigManager


class SymbolDiscoveryError(Exception):
    """Base exception for symbol discovery errors"""
    pass


class InvalidExchangeError(SymbolDiscoveryError):
    """Raised when exchange name is invalid"""
    pass


class APIConnectionError(SymbolDiscoveryError):
    """Raised when API connection fails"""
    pass


class SymbolNotFoundError(SymbolDiscoveryError):
    """Raised when symbol doesn't exist"""
    pass


class SymbolFormatError(SymbolDiscoveryError):
    """Raised when symbol format is invalid"""
    pass


class SymbolDiscovery:
    """
    Handles symbol discovery from GoMarket API with format normalization.
    
    Supports different symbol formats across exchanges:
    - Binance: ETHBTC (no separator)
    - Bybit: BTCUSDT (no separator)
    - OKX: USDT-SGD (dash separator)
    - Deribit: BTC_USDC (underscore separator)
    
    Normalizes all symbols to BASE-QUOTE format internally.
    """
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_base_url = "https://gomarket-api.goquant.io"
        self.supported_exchanges = ['binance', 'okx', 'bybit', 'deribit']
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
        self.timeout = 10
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GoQuant-Trading-Bot/1.0'
        })
    
    def normalize_symbol(self, exchange: str, symbol_name: str, base: str, quote: str) -> str:
        """
        Normalize exchange-specific symbol format to standard BASE-QUOTE format.
        
        Args:
            exchange: Exchange name (binance, okx, bybit, deribit)
            symbol_name: Original symbol name from API
            base: Base currency
            quote: Quote currency
            
        Returns:
            Normalized symbol in BASE-QUOTE format
            
        Examples:
            >>> normalize_symbol('binance', 'ETHBTC', 'ETH', 'BTC')
            'ETH-BTC'
            >>> normalize_symbol('deribit', 'BTC_USDC', 'BTC', 'USDC')
            'BTC-USDC'
            >>> normalize_symbol('okx', 'USDT-SGD', 'USDT', 'SGD')
            'USDT-SGD'
        """
        # For Binance/Bybit (no separator): Use base and quote to create BASE-QUOTE
        if exchange in ['binance', 'bybit']:
            return f"{base}-{quote}"
        
        # For OKX (dash separator): Already correct format
        elif exchange == 'okx':
            return symbol_name
        
        # For Deribit (underscore separator): Replace underscore with dash
        elif exchange == 'deribit':
            return symbol_name.replace('_', '-')
        
        # For unsupported exchanges
        else:
            raise InvalidExchangeError(f"Unsupported exchange: {exchange}")
    
    def denormalize_symbol(self, exchange: str, normalized_symbol: str) -> str:
        """
        Convert normalized symbol back to exchange-specific format.
        
        Args:
            exchange: Exchange name (binance, okx, bybit, deribit)
            normalized_symbol: Normalized symbol (e.g., BTC-USDT)
            
        Returns:
            Exchange-specific format
            
        Examples:
            >>> denormalize_symbol('binance', 'ETH-BTC')
            'ETHBTC'
            >>> denormalize_symbol('deribit', 'BTC-USDC')
            'BTC_USDC'
            >>> denormalize_symbol('okx', 'USDT-SGD')
            'USDT-SGD'
        """
        # Split the normalized symbol
        try:
            base, quote = normalized_symbol.split('-')
        except ValueError:
            raise SymbolFormatError(f"Invalid normalized symbol format: {normalized_symbol}")
        
        # For Binance/Bybit: Remove separator
        if exchange in ['binance', 'bybit']:
            return f"{base}{quote}"
        
        # For OKX: Keep dash
        elif exchange == 'okx':
            return normalized_symbol
        
        # For Deribit: Replace dash with underscore
        elif exchange == 'deribit':
            return normalized_symbol.replace('-', '_')
        
        # For unsupported exchanges
        else:
            raise InvalidExchangeError(f"Unsupported exchange: {exchange}")
    
    def _get_cached_symbols(self, exchange: str) -> Optional[List[Dict]]:
        """
        Get cached symbols if valid.
        
        Args:
            exchange: Exchange name
            
        Returns:
            Cached symbols if valid, None otherwise
        """
        if exchange in self.cache:
            cached_data = self.cache[exchange]
            timestamp = cached_data.get('timestamp', 0)
            if time.time() - timestamp < self.cache_duration:
                self.logger.debug(f"Using cached symbols for {exchange}")
                return cached_data.get('symbols', [])
            else:
                self.logger.debug(f"Cache expired for {exchange}")
                del self.cache[exchange]
        return None
    
    def _cache_symbols(self, exchange: str, symbols: List[Dict]):
        """
        Cache symbols with timestamp.
        
        Args:
            exchange: Exchange name
            symbols: List of symbol dictionaries
        """
        self.cache[exchange] = {
            'symbols': symbols,
            'timestamp': time.time()
        }
        self.logger.debug(f"Cached {len(symbols)} symbols for {exchange}")
    
    def clear_cache(self, exchange: Optional[str] = None):
        """
        Clear cache for specific exchange or all.
        
        Args:
            exchange: Exchange name (optional, if None clears all)
        """
        if exchange:
            if exchange in self.cache:
                del self.cache[exchange]
                self.logger.debug(f"Cleared cache for {exchange}")
        else:
            self.cache.clear()
            self.logger.debug("Cleared all cache")
    
    def get_available_symbols(self, exchange: str, market_type: str = 'spot') -> List[Dict]:
        """
        Fetch and normalize symbols from API.
        
        Args:
            exchange: Exchange name
            market_type: Market type (default: spot)
            
        Returns:
            List of enhanced symbol dictionaries with both original and normalized names
            
        Raises:
            InvalidExchangeError: If exchange is not supported
            APIConnectionError: If API connection fails
        """
        # Validate exchange
        if exchange not in self.supported_exchanges:
            raise InvalidExchangeError(f"Unsupported exchange: {exchange}")
        
        # Check cache first
        cached_symbols = self._get_cached_symbols(exchange)
        if cached_symbols is not None:
            return cached_symbols
        
        # Make API request
        url = f"{self.api_base_url}/api/symbols/{exchange}/{market_type}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            raw_symbols = response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch symbols from {exchange}: {e}")
            raise APIConnectionError(f"Failed to connect to GoMarket API for {exchange}: {e}")
        except ValueError as e:
            self.logger.error(f"Failed to parse JSON response from {exchange}: {e}")
            raise SymbolDiscoveryError(f"Invalid JSON response from {exchange}: {e}")
        
        # Process and normalize symbols
        normalized_symbols = []
        for symbol_data in raw_symbols:
            try:
                # Extract required fields
                original_name = symbol_data.get('name', '')
                base = symbol_data.get('base', '')
                quote = symbol_data.get('quote', '')
                
                # Skip if required fields are missing
                if not original_name or not base or not quote:
                    self.logger.warning(f"Skipping invalid symbol data: {symbol_data}")
                    continue
                
                # Normalize symbol name
                normalized_name = self.normalize_symbol(exchange, original_name, base, quote)
                
                # Create enhanced symbol object
                enhanced_symbol = {
                    'exchange': exchange,
                    'original_name': original_name,
                    'normalized_name': normalized_name,
                    'base': base,
                    'quote': quote,
                    'instrument_type': symbol_data.get('instrument_type', market_type),
                    'min_size': symbol_data.get('min_size', ''),
                    'tick_size': symbol_data.get('tick_size', ''),
                    'lot_size': symbol_data.get('lot_size', '')
                }
                
                normalized_symbols.append(enhanced_symbol)
            except Exception as e:
                self.logger.warning(f"Failed to process symbol {symbol_data}: {e}")
                continue
        
        # Cache the results
        self._cache_symbols(exchange, normalized_symbols)
        
        return normalized_symbols
    
    def get_all_symbols(self) -> Dict[str, List[Dict]]:
        """
        Fetch symbols from all exchanges.
        
        Returns:
            Dictionary with exchange names as keys and lists of symbol dictionaries as values
        """
        all_symbols = {}
        for exchange in self.supported_exchanges:
            try:
                symbols = self.get_available_symbols(exchange)
                all_symbols[exchange] = symbols
            except Exception as e:
                self.logger.error(f"Failed to fetch symbols for {exchange}: {e}")
                all_symbols[exchange] = []
        return all_symbols
    
    def get_symbol_names(self, exchange: str, normalized: bool = True) -> List[str]:
        """
        Get symbol names (original or normalized).
        
        Args:
            exchange: Exchange name
            normalized: If True, return normalized names; if False, return original names
            
        Returns:
            List of symbol names
        """
        try:
            symbols = self.get_available_symbols(exchange)
            if normalized:
                return [symbol['normalized_name'] for symbol in symbols]
            else:
                return [symbol['original_name'] for symbol in symbols]
        except Exception as e:
            self.logger.error(f"Failed to get symbol names for {exchange}: {e}")
            return []
    
    def get_all_symbol_names(self, normalized: bool = True) -> Dict[str, List[str]]:
        """
        Get all symbol names.
        
        Args:
            normalized: Format preference
            
        Returns:
            Dictionary with exchange names as keys and lists of symbol names as values
        """
        all_names = {}
        symbols_dict = self.get_all_symbols()
        
        for exchange, symbols in symbols_dict.items():
            if normalized:
                all_names[exchange] = [symbol['normalized_name'] for symbol in symbols]
            else:
                all_names[exchange] = [symbol['original_name'] for symbol in symbols]
        
        return all_names
    
    def validate_symbol(self, exchange: str, symbol_name: str, is_normalized: bool = True) -> bool:
        """
        Validate if symbol exists.
        
        Args:
            exchange: Exchange name
            symbol_name: Symbol to validate
            is_normalized: Whether input is in normalized format
            
        Returns:
            True if exists, False otherwise
        """
        try:
            symbols = self.get_available_symbols(exchange)
            if is_normalized:
                return any(symbol['normalized_name'] == symbol_name for symbol in symbols)
            else:
                return any(symbol['original_name'] == symbol_name for symbol in symbols)
        except Exception as e:
            self.logger.error(f"Failed to validate symbol {symbol_name} on {exchange}: {e}")
            return False
    
    def get_symbol_info(self, exchange: str, symbol_name: str, is_normalized: bool = True) -> Optional[Dict]:
        """
        Get detailed symbol information.
        
        Args:
            exchange: Exchange name
            symbol_name: Symbol name
            is_normalized: Whether input is normalized
            
        Returns:
            Symbol info dict or None
        """
        try:
            symbols = self.get_available_symbols(exchange)
            if is_normalized:
                for symbol in symbols:
                    if symbol['normalized_name'] == symbol_name:
                        return symbol
            else:
                for symbol in symbols:
                    if symbol['original_name'] == symbol_name:
                        return symbol
            return None
        except Exception as e:
            self.logger.error(f"Failed to get symbol info for {symbol_name} on {exchange}: {e}")
            return None
    
    def find_common_symbols(self, exchanges: Optional[List[str]] = None) -> List[str]:
        """
        Find symbols available on multiple exchanges (for arbitrage).
        
        Args:
            exchanges: List of exchanges to check (default: all 4)
            
        Returns:
            List of normalized symbols available on ALL specified exchanges
        """
        if exchanges is None:
            exchanges = self.supported_exchanges
        
        # Validate exchanges
        for exchange in exchanges:
            if exchange not in self.supported_exchanges:
                raise InvalidExchangeError(f"Unsupported exchange: {exchange}")
        
        if not exchanges:
            return []
        
        # Get symbol sets for each exchange
        symbol_sets = []
        for exchange in exchanges:
            try:
                symbols = set(self.get_symbol_names(exchange, normalized=True))
                symbol_sets.append(symbols)
            except Exception as e:
                self.logger.error(f"Failed to get symbols for {exchange}: {e}")
                symbol_sets.append(set())
        
        # Find intersection of all symbol sets
        if symbol_sets:
            common_symbols = set.intersection(*symbol_sets)
            return sorted(list(common_symbols))
        else:
            return []