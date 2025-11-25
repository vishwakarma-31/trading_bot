"""
Configuration Manager for the Generic Trading Bot
"""
import os
from typing import Optional, Dict, Any

class ConfigManager:
    """Manages all configuration settings for the trading bot"""
    
    def __init__(self):
        """Initialize configuration manager"""
        self._telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self._min_profit_percentage = float(os.getenv('MIN_PROFIT_PERCENTAGE', '0.5'))
        self._min_profit_absolute = float(os.getenv('MIN_PROFIT_ABSOLUTE', '1.0'))
        # Exchange configurations
        self._exchange_configs = {
            'binance': {
                'enabled': os.getenv('BINANCE_ENABLED', 'true').lower() == 'true',
                'rate_limit': float(os.getenv('BINANCE_RATE_LIMIT', '0.1'))
            },
            'okx': {
                'enabled': os.getenv('OKX_ENABLED', 'true').lower() == 'true',
                'rate_limit': float(os.getenv('OKX_RATE_LIMIT', '0.1'))
            }
        }
        
    @property
    def telegram_token(self) -> Optional[str]:
        """Get Telegram bot token"""
        return self._telegram_token
    
    @telegram_token.setter
    def telegram_token(self, token: str):
        """Set Telegram bot token"""
        self._telegram_token = token
        
    def get_exchange_config(self, exchange: str) -> Dict[str, Any]:
        """Get configuration for a specific exchange"""
        return self._exchange_configs.get(exchange, {
            'enabled': True,
            'rate_limit': 0.1
        })
        
    def get_enabled_exchanges(self) -> list:
        """Get list of enabled exchanges"""
        return [exchange for exchange, config in self._exchange_configs.items() 
                if config.get('enabled', True)]
        
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
        
    # Exchange API endpoints are now handled through ccxt