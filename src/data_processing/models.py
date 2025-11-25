"""
Data Models for the Generic Trading Bot
Contains all dataclass definitions to avoid circular imports
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

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
class MarketViewData:
    """Represents market view data for a symbol on an exchange"""
    symbol: str
    exchange: str
    bid_price: float
    ask_price: float
    bid_size: float
    ask_size: float
    timestamp: float

@dataclass
class ConsolidatedMarketView:
    """Represents consolidated market view across multiple exchanges"""
    symbol: str
    exchanges_data: Dict[str, MarketViewData]
    cbbo_bid_exchange: str  # Exchange with best bid
    cbbo_ask_exchange: str  # Exchange with best ask
    cbbo_bid_price: float   # Best bid price
    cbbo_ask_price: float   # Best ask price
    timestamp: float

@dataclass
class ThresholdConfig:
    """Configuration for arbitrage thresholds"""
    min_profit_percentage: float = 0.5  # Minimum profit percentage
    min_profit_absolute: float = 1.0    # Minimum profit in absolute value (USD)

@dataclass
class ArbitrageStatistics:
    """Represents arbitrage statistics"""
    total_opportunities: int = 0
    average_spread: float = 0.0
    max_spread: float = 0.0
    opportunities_by_symbol: Dict[str, int] = None
    opportunities_by_exchange_pair: Dict[str, int] = None
    start_time: float = 0.0
    end_time: float = 0.0
    
    def __post_init__(self):
        if self.opportunities_by_symbol is None:
            self.opportunities_by_symbol = {}
        if self.opportunities_by_exchange_pair is None:
            self.opportunities_by_exchange_pair = {}