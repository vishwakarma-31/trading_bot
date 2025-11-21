"""
Configuration Manager for the GoQuant Trading Bot
"""
import os
from typing import Optional

class ConfigManager:
    """Manages all configuration settings for the trading bot"""
    
    def __init__(self):
        """Initialize configuration manager"""
        self._telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self._gomarket_api_key = os.getenv('GOMARKET_API_KEY')
        self._gomarket_access_code = os.getenv('GOMARKET_ACCESS_CODE', '2194')
        self._min_profit_percentage = float(os.getenv('MIN_PROFIT_PERCENTAGE', '0.5'))
        self._min_profit_absolute = float(os.getenv('MIN_PROFIT_ABSOLUTE', '1.0'))
        
    @property
    def telegram_token(self) -> Optional[str]:
        """Get Telegram bot token"""
        return self._telegram_token
    
    @telegram_token.setter
    def telegram_token(self, token: str):
        """Set Telegram bot token"""
        self._telegram_token = token
        
    @property
    def gomarket_api_key(self) -> Optional[str]:
        """Get GoMarket API key"""
        return self._gomarket_api_key
        
    @gomarket_api_key.setter
    def gomarket_api_key(self, api_key: str):
        """Set GoMarket API key"""
        self._gomarket_api_key = api_key
        
    @property
    def gomarket_access_code(self) -> str:
        """Get GoMarket access code"""
        return self._gomarket_access_code
        
    @property
    def min_profit_percentage(self) -> float:
        """Get minimum profit percentage threshold"""
        return self._min_profit_percentage
        
    @min_profit_percentage.setter
    def min_profit_percentage(self, value: float):
        """Set minimum profit percentage threshold"""
        self._min_profit_percentage = value
        
    @property
    def min_profit_absolute(self) -> float:
        """Get minimum profit absolute value threshold"""
        return self._min_profit_absolute
        
    @min_profit_absolute.setter
    def min_profit_absolute(self, value: float):
        """Set minimum profit absolute value threshold"""
        self._min_profit_absolute = value
        
    def get_gomarket_symbols_endpoint(self, exchange: str) -> str:
        """Get GoMarket symbols endpoint for a specific exchange"""
        return f"https://gomarket-api.goquant.io/api/symbols/{exchange}/spot"
        
    def get_gomarket_l1_endpoint(self, exchange: str, symbol: str) -> str:
        """Get GoMarket L1 market data endpoint"""
        return f"https://gomarket-api.goquant.io/api/market/l1/{exchange}/{symbol}"
        
    def get_gomarket_l2_endpoint(self, exchange: str, symbol: str) -> str:
        """Get GoMarket L2 order book data endpoint"""
        return f"https://gomarket-api.goquant.io/api/market/l2/{exchange}/{symbol}"