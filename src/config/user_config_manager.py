"""
User Configuration Manager for the Generic Trading Bot
Handles user-specific settings and monitoring parameters.
"""
import json
import os
import logging
import re
from typing import Dict, List, Optional, Any
from config.config_manager import ConfigManager

class UserConfigManager:
    """Manages user-specific configuration settings"""
    
    def __init__(self, config: ConfigManager, config_file: str = "user_config.json"):
        """Initialize user configuration manager"""
        self.config = config
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self.user_configs = {}  # In-memory storage of user configurations
        self.supported_exchanges = ['okx', 'deribit', 'bybit', 'binance']
        self.default_config = {
            # Arbitrage settings
            'arbitrage': {
                'assets': [],  # List of asset pairs to monitor
                'exchanges': self.supported_exchanges.copy(),  # Exchanges to monitor
                'threshold_percentage': config.min_profit_percentage,  # Default from global config
                'threshold_absolute': config.min_profit_absolute,  # Default from global config
                'max_monitors': 10,  # Maximum number of simultaneous monitors
                'enabled': False  # Whether arbitrage monitoring is enabled
            },
            # Market view settings
            'market_view': {
                'symbols': [],  # Symbols to monitor
                'exchanges': self.supported_exchanges.copy(),  # Exchanges to include
                'update_frequency': 30,  # Seconds between updates
                'significant_change_threshold': 0.1,  # Percentage change to trigger alert
                'enabled': False  # Whether market view monitoring is enabled
            },
            # User preferences
            'preferences': {
                'alert_frequency': 'immediate',  # immediate, hourly, daily
                'message_format': 'detailed',  # simple, detailed
                'timezone': 'UTC'  # User's timezone
            }
        }
        
        # Load existing configuration
        self.load_config()
        
    def _validate_exchange(self, exchange: str) -> bool:
        """Validate exchange name"""
        return exchange.lower() in self.supported_exchanges
        
    def _validate_symbol(self, symbol: str) -> bool:
        """Validate symbol format"""
        # Basic validation: should contain letters, numbers, and hyphens/underscores
        pattern = re.compile(r'^[A-Za-z0-9\-_]+$')
        return bool(pattern.match(symbol))
        
    def _validate_threshold(self, value: Any) -> bool:
        """Validate threshold value"""
        try:
            float_value = float(value)
            return float_value >= 0
        except (ValueError, TypeError):
            return False
            
    def _validate_monitoring_limit(self, count: int, max_limit: int) -> bool:
        """Validate monitoring limits"""
        return isinstance(count, int) and 0 <= count <= max_limit
        
    def get_user_config(self, user_id: int) -> Dict:
        """
        Get configuration for a specific user
        
        Args:
            user_id (int): User ID
            
        Returns:
            Dict: User configuration
        """
        if user_id not in self.user_configs:
            # Create default configuration for new user
            self.user_configs[user_id] = self._create_default_user_config()
            
        return self.user_configs[user_id]
        
    def _create_default_user_config(self) -> Dict:
        """Create default user configuration"""
        # Deep copy of default config
        return json.loads(json.dumps(self.default_config))
        
    def set_user_config(self, user_id: int, config: Dict) -> bool:
        """
        Set configuration for a specific user
        
        Args:
            user_id (int): User ID
            config (Dict): Configuration to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate configuration
            if not self._validate_user_config(config):
                self.logger.error(f"Invalid configuration for user {user_id}")
                return False
                
            self.user_configs[user_id] = config
            self.logger.info(f"Updated configuration for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting configuration for user {user_id}: {e}")
            return False
            
    def _validate_user_config(self, config: Dict) -> bool:
        """
        Validate user configuration
        
        Args:
            config (Dict): Configuration to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Validate arbitrage settings
            if 'arbitrage' in config:
                arb_config = config['arbitrage']
                
                # Validate exchanges
                if 'exchanges' in arb_config:
                    for exchange in arb_config['exchanges']:
                        if not self._validate_exchange(exchange):
                            self.logger.error(f"Invalid exchange in arbitrage config: {exchange}")
                            return False
                            
                # Validate assets
                if 'assets' in arb_config:
                    for asset in arb_config['assets']:
                        if not isinstance(asset, str):
                            self.logger.error(f"Invalid asset format in arbitrage config: {asset}")
                            return False
                            
                # Validate thresholds
                if 'threshold_percentage' in arb_config:
                    if not self._validate_threshold(arb_config['threshold_percentage']):
                        self.logger.error(f"Invalid threshold_percentage in arbitrage config: {arb_config['threshold_percentage']}")
                        return False
                        
                if 'threshold_absolute' in arb_config:
                    if not self._validate_threshold(arb_config['threshold_absolute']):
                        self.logger.error(f"Invalid threshold_absolute in arbitrage config: {arb_config['threshold_absolute']}")
                        return False
                        
                # Validate monitoring limit
                if 'max_monitors' in arb_config:
                    if not self._validate_monitoring_limit(arb_config['max_monitors'], 50):
                        self.logger.error(f"Invalid max_monitors in arbitrage config: {arb_config['max_monitors']}")
                        return False
                        
            # Validate market view settings
            if 'market_view' in config:
                mv_config = config['market_view']
                
                # Validate exchanges
                if 'exchanges' in mv_config:
                    for exchange in mv_config['exchanges']:
                        if not self._validate_exchange(exchange):
                            self.logger.error(f"Invalid exchange in market view config: {exchange}")
                            return False
                            
                # Validate symbols
                if 'symbols' in mv_config:
                    for symbol in mv_config['symbols']:
                        if not self._validate_symbol(symbol):
                            self.logger.error(f"Invalid symbol in market view config: {symbol}")
                            return False
                            
                # Validate update frequency
                if 'update_frequency' in mv_config:
                    freq = mv_config['update_frequency']
                    if not isinstance(freq, int) or freq < 1:
                        self.logger.error(f"Invalid update_frequency in market view config: {freq}")
                        return False
                        
                # Validate significant change threshold
                if 'significant_change_threshold' in mv_config:
                    if not self._validate_threshold(mv_config['significant_change_threshold']):
                        self.logger.error(f"Invalid significant_change_threshold in market view config: {mv_config['significant_change_threshold']}")
                        return False
                        
            # Validate preferences
            if 'preferences' in config:
                pref_config = config['preferences']
                
                # Validate alert frequency
                if 'alert_frequency' in pref_config:
                    valid_frequencies = ['immediate', 'hourly', 'daily']
                    if pref_config['alert_frequency'] not in valid_frequencies:
                        self.logger.error(f"Invalid alert_frequency in preferences: {pref_config['alert_frequency']}")
                        return False
                        
                # Validate message format
                if 'message_format' in pref_config:
                    valid_formats = ['simple', 'detailed']
                    if pref_config['message_format'] not in valid_formats:
                        self.logger.error(f"Invalid message_format in preferences: {pref_config['message_format']}")
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating user configuration: {e}")
            return False
            
    def update_arbitrage_config(self, user_id: int, **kwargs) -> bool:
        """
        Update arbitrage configuration for a user
        
        Args:
            user_id (int): User ID
            **kwargs: Configuration parameters to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_config = self.get_user_config(user_id)
            
            # Update arbitrage settings
            for key, value in kwargs.items():
                if key in user_config['arbitrage']:
                    user_config['arbitrage'][key] = value
                    
            # Validate and save
            if self._validate_user_config(user_config):
                self.user_configs[user_id] = user_config
                self.logger.info(f"Updated arbitrage configuration for user {user_id}")
                return True
            else:
                self.logger.error(f"Invalid arbitrage configuration for user {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating arbitrage configuration for user {user_id}: {e}")
            return False
            
    def update_market_view_config(self, user_id: int, **kwargs) -> bool:
        """
        Update market view configuration for a user
        
        Args:
            user_id (int): User ID
            **kwargs: Configuration parameters to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_config = self.get_user_config(user_id)
            
            # Update market view settings
            for key, value in kwargs.items():
                if key in user_config['market_view']:
                    user_config['market_view'][key] = value
                    
            # Validate and save
            if self._validate_user_config(user_config):
                self.user_configs[user_id] = user_config
                self.logger.info(f"Updated market view configuration for user {user_id}")
                return True
            else:
                self.logger.error(f"Invalid market view configuration for user {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating market view configuration for user {user_id}: {e}")
            return False
            
    def update_preferences(self, user_id: int, **kwargs) -> bool:
        """
        Update user preferences
        
        Args:
            user_id (int): User ID
            **kwargs: Preference parameters to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_config = self.get_user_config(user_id)
            
            # Update preferences
            for key, value in kwargs.items():
                if key in user_config['preferences']:
                    user_config['preferences'][key] = value
                    
            # Validate and save
            if self._validate_user_config(user_config):
                self.user_configs[user_id] = user_config
                self.logger.info(f"Updated preferences for user {user_id}")
                return True
            else:
                self.logger.error(f"Invalid preferences for user {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating preferences for user {user_id}: {e}")
            return False
            
    def get_arbitrage_config(self, user_id: int) -> Dict:
        """
        Get arbitrage configuration for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            Dict: Arbitrage configuration
        """
        user_config = self.get_user_config(user_id)
        return user_config.get('arbitrage', {})
        
    def get_market_view_config(self, user_id: int) -> Dict:
        """
        Get market view configuration for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            Dict: Market view configuration
        """
        user_config = self.get_user_config(user_id)
        return user_config.get('market_view', {})
        
    def get_preferences(self, user_id: int) -> Dict:
        """
        Get user preferences
        
        Args:
            user_id (int): User ID
            
        Returns:
            Dict: User preferences
        """
        user_config = self.get_user_config(user_id)
        return user_config.get('preferences', {})
        
    def save_config(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create backup of existing config file
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup"
                os.replace(self.config_file, backup_file)
                
            # Save current configuration
            with open(self.config_file, 'w') as f:
                json.dump(self.user_configs, f, indent=2)
                
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration to {self.config_file}: {e}")
            return False
            
    def load_config(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.user_configs = json.load(f)
                    
                # Validate loaded configurations
                valid_configs = {}
                for user_id, config in self.user_configs.items():
                    if self._validate_user_config(config):
                        valid_configs[int(user_id)] = config
                    else:
                        self.logger.warning(f"Invalid configuration for user {user_id}, using default")
                        valid_configs[int(user_id)] = self._create_default_user_config()
                        
                self.user_configs = valid_configs
                self.logger.info(f"Configuration loaded from {self.config_file}")
                return True
            else:
                self.logger.info(f"Configuration file {self.config_file} not found, using defaults")
                return True
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing configuration file {self.config_file}: {e}")
            # Try to load from backup
            backup_file = f"{self.config_file}.backup"
            if os.path.exists(backup_file):
                self.logger.info(f"Attempting to load from backup file {backup_file}")
                try:
                    with open(backup_file, 'r') as f:
                        self.user_configs = json.load(f)
                    self.logger.info(f"Configuration loaded from backup {backup_file}")
                    return True
                except Exception as backup_error:
                    self.logger.error(f"Error loading backup configuration: {backup_error}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error loading configuration from {self.config_file}: {e}")
            return False
            
    def reset_user_config(self, user_id: int) -> bool:
        """
        Reset user configuration to defaults
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.user_configs[user_id] = self._create_default_user_config()
            self.logger.info(f"Reset configuration for user {user_id} to defaults")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting configuration for user {user_id}: {e}")
            return False
            
    def get_all_users(self) -> List[int]:
        """
        Get all user IDs with configurations
        
        Returns:
            List[int]: List of user IDs
        """
        return list(self.user_configs.keys())
        
    def remove_user_config(self, user_id: int) -> bool:
        """
        Remove user configuration
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if user_id in self.user_configs:
                del self.user_configs[user_id]
                self.logger.info(f"Removed configuration for user {user_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing configuration for user {user_id}: {e}")
            return False