"""
Arbitrage Detector for the GoQuant Trading Bot
"""
import logging
import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from data_acquisition.market_data_fetcher import MarketDataFetcher
from config.config_manager import ConfigManager
from data_processing.arbitrage_statistics import ArbitrageLogger
from utils.error_handler import (
    DataProcessingError, InvalidDataError, MissingDataError, CalculationError,
    ThresholdValidationError, log_exception, handle_exception
)

@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity"""
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    profit_percentage: float
    profit_absolute: float
    timestamp: float
    threshold_percentage: float
    threshold_absolute: float

@dataclass
class ThresholdConfig:
    """Configuration for arbitrage thresholds"""
    min_profit_percentage: float = 0.5  # Minimum profit percentage
    min_profit_absolute: float = 1.0    # Minimum profit in absolute value (USD)
    
class ArbitrageDetector:
    """Detects arbitrage opportunities across exchanges"""
    
    def __init__(self, market_fetcher: MarketDataFetcher, config: ConfigManager):
        """Initialize arbitrage detector"""
        self.market_fetcher = market_fetcher
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.thresholds = ThresholdConfig()
        self.active_opportunities = {}  # Track ongoing opportunities
        self.opportunity_history = deque(maxlen=1000)  # Keep last 1000 opportunities
        self.monitoring = False
        self.monitoring_thread = None
        self.data_subscriptions = {}  # Track WebSocket subscriptions
        self.latest_market_data = {}  # Cache of latest market data
        self.supported_exchanges = ['binance', 'okx', 'bybit', 'deribit']
        
        # Initialize arbitrage logger for historical data
        self.arbitrage_logger = ArbitrageLogger(storage_type="sqlite", storage_path="data")
        
    def set_thresholds(self, min_profit_percentage: float = None, min_profit_absolute: float = None):
        """
        Set arbitrage detection thresholds
        
        Args:
            min_profit_percentage (float): Minimum profit percentage threshold
            min_profit_absolute (float): Minimum profit absolute value threshold
        """
        try:
            if min_profit_percentage is not None:
                if not isinstance(min_profit_percentage, (int, float)) or min_profit_percentage < 0:
                    raise ThresholdValidationError(f"Invalid percentage threshold: {min_profit_percentage}")
                self.thresholds.min_profit_percentage = float(min_profit_percentage)
                
            if min_profit_absolute is not None:
                if not isinstance(min_profit_absolute, (int, float)) or min_profit_absolute < 0:
                    raise ThresholdValidationError(f"Invalid absolute threshold: {min_profit_absolute}")
                self.thresholds.min_profit_absolute = float(min_profit_absolute)
                
            self.logger.info(f"Updated thresholds: {self.thresholds}")
            
        except Exception as e:
            log_exception(self.logger, e, "Error setting thresholds")
            raise ThresholdValidationError(f"Error setting thresholds: {e}")
        
    def get_thresholds(self) -> ThresholdConfig:
        """
        Get current threshold configuration
        
        Returns:
            ThresholdConfig: Current threshold configuration
        """
        return self.thresholds
        
    @handle_exception(logger_name=__name__, reraise=False, default_return=[])
    def find_arbitrage_opportunities(self, exchanges: List[str], symbol: str) -> List[ArbitrageOpportunity]:
        """
        Find arbitrage opportunities for a symbol across exchanges
        
        Args:
            exchanges (List[str]): List of exchange names
            symbol (str): Trading symbol to check
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        
        try:
            # Validate inputs
            if not exchanges:
                raise InvalidDataError("No exchanges provided")
            if not symbol:
                raise InvalidDataError("No symbol provided")
                
            # Fetch market data from all exchanges
            market_data = {}
            for exchange in exchanges:
                try:
                    data = self.market_fetcher.get_l1_market_data(exchange, symbol)
                    if data:
                        market_data[exchange] = data
                        # Cache the data
                        self.latest_market_data[(exchange, symbol)] = data
                except Exception as e:
                    self.logger.warning(f"Failed to fetch data for {symbol} on {exchange}: {e}")
                    # Continue with other exchanges
                    
            # Compare prices across exchanges
            for buy_exchange in market_data:
                for sell_exchange in market_data:
                    if buy_exchange != sell_exchange:
                        try:
                            buy_data = market_data[buy_exchange]
                            sell_data = market_data[sell_exchange]
                            
                            # Validate required data fields
                            required_fields = ['ask_price', 'bid_price', 'timestamp']
                            for field in required_fields:
                                if field not in buy_data or field not in sell_data:
                                    raise MissingDataError(f"Missing {field} in market data")
                                    
                            # Get best bid and ask prices
                            buy_price = buy_data.get('ask_price')  # Price to buy from this exchange
                            sell_price = sell_data.get('bid_price')  # Price to sell to this exchange
                            
                            # Validate price data
                            if buy_price is None or sell_price is None:
                                self.logger.warning(f"Missing price data for {symbol} on {buy_exchange} or {sell_exchange}")
                                continue
                                
                            if not isinstance(buy_price, (int, float)) or not isinstance(sell_price, (int, float)):
                                raise InvalidDataError(f"Invalid price data for {symbol}")
                                
                            if buy_price <= 0 or sell_price <= 0:
                                self.logger.debug(f"Invalid price values for {symbol}: buy={buy_price}, sell={sell_price}")
                                continue
                                
                            if sell_price > buy_price:
                                profit_percentage = ((sell_price - buy_price) / buy_price) * 100
                                profit_absolute = sell_price - buy_price
                                
                                # Check for division by zero or invalid calculations
                                if not isinstance(profit_percentage, (int, float)) or not isinstance(profit_absolute, (int, float)):
                                    raise CalculationError(f"Invalid profit calculation for {symbol}")
                                    
                                # Check if opportunity meets thresholds
                                if (profit_percentage >= self.thresholds.min_profit_percentage and 
                                    profit_absolute >= self.thresholds.min_profit_absolute):
                                    opportunity = ArbitrageOpportunity(
                                        symbol=symbol,
                                        buy_exchange=buy_exchange,
                                        sell_exchange=sell_exchange,
                                        buy_price=buy_price,
                                        sell_price=sell_price,
                                        profit_percentage=profit_percentage,
                                        profit_absolute=profit_absolute,
                                        timestamp=market_data[buy_exchange].get('timestamp', time.time()),
                                        threshold_percentage=self.thresholds.min_profit_percentage,
                                        threshold_absolute=self.thresholds.min_profit_absolute
                                    )
                                    opportunities.append(opportunity)
                        except Exception as e:
                            self.logger.warning(f"Error comparing prices for {symbol} between {buy_exchange} and {sell_exchange}: {e}")
                            # Continue with other exchange pairs
                                
            self.logger.info(f"Found {len(opportunities)} arbitrage opportunities for {symbol}")
            
        except Exception as e:
            log_exception(self.logger, e, f"Error finding arbitrage opportunities for {symbol}")
            raise DataProcessingError(f"Error finding arbitrage opportunities for {symbol}: {e}")
            
        return opportunities
        
    @handle_exception(logger_name=__name__, reraise=False, default_return=[])
    def find_synthetic_arbitrage_opportunities(self, base_asset: str, quote_assets: List[str]) -> List[ArbitrageOpportunity]:
        """
        Find arbitrage opportunities between synthetic pairs (e.g., BTC/USDT vs BTC/USDC)
        
        Args:
            base_asset (str): Base asset (e.g., 'BTC')
            quote_assets (List[str]): List of quote assets (e.g., ['USDT', 'USDC'])
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        
        try:
            # Validate inputs
            if not base_asset:
                raise InvalidDataError("No base asset provided")
            if not quote_assets:
                raise InvalidDataError("No quote assets provided")
                
            # Create synthetic pairs
            synthetic_pairs = []
            for i, quote1 in enumerate(quote_assets):
                for quote2 in quote_assets[i+1:]:
                    # Example: BTC/USDT vs BTC/USDC
                    pair1 = f"{base_asset}-{quote1}"
                    pair2 = f"{base_asset}-{quote2}"
                    synthetic_pairs.append((pair1, pair2))
                    
            # Check each synthetic pair
            for pair1, pair2 in synthetic_pairs:
                try:
                    # Get market data for both pairs across all exchanges
                    pair1_data = {}
                    pair2_data = {}
                    
                    for exchange in self.supported_exchanges:
                        try:
                            data1 = self.market_fetcher.get_l1_market_data(exchange, pair1)
                            data2 = self.market_fetcher.get_l1_market_data(exchange, pair2)
                            
                            if data1:
                                pair1_data[exchange] = data1
                                self.latest_market_data[(exchange, pair1)] = data1
                            if data2:
                                pair2_data[exchange] = data2
                                self.latest_market_data[(exchange, pair2)] = data2
                        except Exception as e:
                            self.logger.warning(f"Failed to fetch data for synthetic pair {pair1} or {pair2} on {exchange}: {e}")
                            # Continue with other exchanges
                            
                    # Compare prices between the synthetic pairs
                    for exchange in pair1_data:
                        if exchange in pair2_data:
                            try:
                                data1 = pair1_data[exchange]
                                data2 = pair2_data[exchange]
                                
                                # Get mid prices
                                price1 = data1.get('mid_price')
                                if price1 is None:
                                    # Calculate mid price from bid/ask if not provided
                                    ask1 = data1.get('ask_price', 0)
                                    bid1 = data1.get('bid_price', 0)
                                    if ask1 > 0 and bid1 > 0:
                                        price1 = (ask1 + bid1) / 2
                                    else:
                                        price1 = 0
                                        
                                price2 = data2.get('mid_price')
                                if price2 is None:
                                    # Calculate mid price from bid/ask if not provided
                                    ask2 = data2.get('ask_price', 0)
                                    bid2 = data2.get('bid_price', 0)
                                    if ask2 > 0 and bid2 > 0:
                                        price2 = (ask2 + bid2) / 2
                                    else:
                                        price2 = 0
                                        
                                # Validate price data
                                if price1 is None or price2 is None:
                                    self.logger.warning(f"Missing price data for synthetic pair {pair1} or {pair2} on {exchange}")
                                    continue
                                    
                                if not isinstance(price1, (int, float)) or not isinstance(price2, (int, float)):
                                    raise InvalidDataError(f"Invalid price data for synthetic pair on {exchange}")
                                    
                                if price1 <= 0 or price2 <= 0:
                                    self.logger.debug(f"Invalid price values for synthetic pair on {exchange}: {pair1}={price1}, {pair2}={price2}")
                                    continue
                                    
                                # Calculate synthetic price ratio
                                ratio = price1 / price2
                                profit_percentage = abs(ratio - 1) * 100
                                profit_absolute = abs(price1 - price2)
                                
                                # Check for division by zero or invalid calculations
                                if not isinstance(profit_percentage, (int, float)) or not isinstance(profit_absolute, (int, float)):
                                    raise CalculationError(f"Invalid profit calculation for synthetic pair on {exchange}")
                                    
                                # Check if opportunity meets thresholds
                                if (profit_percentage >= self.thresholds.min_profit_percentage and 
                                    profit_absolute >= self.thresholds.min_profit_absolute):
                                    opportunity = ArbitrageOpportunity(
                                        symbol=f"{pair1} vs {pair2}",
                                        buy_exchange=exchange,
                                        sell_exchange=exchange,
                                        buy_price=price1,
                                        sell_price=price2,
                                        profit_percentage=profit_percentage,
                                        profit_absolute=profit_absolute,
                                        timestamp=data1.get('timestamp', time.time()),
                                        threshold_percentage=self.thresholds.min_profit_percentage,
                                        threshold_absolute=self.thresholds.min_profit_absolute
                                    )
                                    opportunities.append(opportunity)
                            except Exception as e:
                                self.logger.warning(f"Error comparing synthetic pair {pair1} vs {pair2} on {exchange}: {e}")
                                # Continue with other exchanges
                except Exception as e:
                    self.logger.warning(f"Error processing synthetic pair {pair1} vs {pair2}: {e}")
                    # Continue with other pairs
                    
            self.logger.info(f"Found {len(opportunities)} synthetic arbitrage opportunities for {base_asset}")
            
        except Exception as e:
            log_exception(self.logger, e, f"Error finding synthetic arbitrage opportunities for {base_asset}")
            raise DataProcessingError(f"Error finding synthetic arbitrage opportunities for {base_asset}: {e}")
            
        return opportunities
        
    def start_monitoring(self, symbols: List[str]):
        """
        Start monitoring for arbitrage opportunities
        
        Args:
            symbols (List[str]): List of symbols to monitor
        """
        if self.monitoring:
            self.logger.warning("Arbitrage monitoring is already running")
            return
            
        self.monitoring = True
        self.logger.info(f"Starting arbitrage monitoring for {len(symbols)} symbols")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(symbols,))
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop arbitrage monitoring"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Stopped arbitrage monitoring")
        
    def _monitoring_loop(self, symbols: List[str]):
        """Background loop for arbitrage monitoring"""
        while self.monitoring:
            try:
                # Check for arbitrage opportunities for each symbol
                for symbol in symbols:
                    try:
                        opportunities = self.find_arbitrage_opportunities(self.supported_exchanges, symbol)
                        if opportunities:
                            self.logger.info(f"Found {len(opportunities)} opportunities for {symbol}")
                            # Store active opportunities and log them
                            for opp in opportunities:
                                key = f"{opp.symbol}_{opp.buy_exchange}_{opp.sell_exchange}"
                                self.active_opportunities[key] = opp
                                self.opportunity_history.append(opp)
                                # Log the opportunity
                                try:
                                    self.arbitrage_logger.log_opportunity(opp)
                                except Exception as log_error:
                                    self.logger.error(f"Failed to log arbitrage opportunity: {log_error}")
                    except Exception as e:
                        self.logger.error(f"Error monitoring {symbol}: {e}")
                        
                # Sleep to avoid excessive CPU usage
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in arbitrage monitoring loop: {e}")
                time.sleep(5)  # Sleep longer on error
                
    def get_active_opportunities(self) -> Dict:
        """Get currently active arbitrage opportunities"""
        return self.active_opportunities
        
    def get_opportunity_count(self) -> Dict:
        """Get count of opportunities by symbol"""
        count = {}
        for opp in self.active_opportunities.values():
            symbol = opp.symbol
            count[symbol] = count.get(symbol, 0) + 1
        return count
        
    def get_historical_statistics(self, symbol: str = None, hours: int = 24):
        """Get historical arbitrage statistics
        
        Args:
            symbol (str, optional): Filter by specific symbol
            hours (int): Time period in hours to calculate statistics for
            
        Returns:
            ArbitrageStatistics: Calculated statistics
        """
        try:
            return self.arbitrage_logger.get_statistics(symbol, hours)
        except Exception as e:
            self.logger.error(f"Error getting historical statistics: {e}")
            raise