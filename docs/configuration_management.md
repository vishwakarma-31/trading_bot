# Configuration Management

The GoQuant Trading Bot includes a comprehensive configuration management system that handles user-specific settings and monitoring parameters.

## User Configuration Manager

The UserConfigManager class handles all user-specific configuration:

### Key Features
- **User-Specific Settings**: Separate configuration for each user
- **Configuration Validation**: Comprehensive validation of all settings
- **Persistent Storage**: Save/load configuration to/from JSON files
- **Default Values**: Sensible defaults for all configuration parameters
- **Configuration Updates**: Granular updates for specific settings

### Configuration Categories

#### Arbitrage Configuration
- **Assets**: List of asset pairs to monitor
- **Exchanges**: Exchanges to monitor for arbitrage opportunities
- **Thresholds**: Percentage and absolute profit thresholds
- **Monitoring Limits**: Maximum number of simultaneous monitors
- **Enabled Status**: Whether arbitrage monitoring is active

#### Market View Configuration
- **Symbols**: Trading symbols to monitor
- **Exchanges**: Exchanges to include in market view
- **Update Frequency**: How often to update market data
- **Significant Change Threshold**: Percentage change to trigger alerts
- **Enabled Status**: Whether market view monitoring is active

#### User Preferences
- **Alert Frequency**: How often to send alerts (immediate, hourly, daily)
- **Message Format**: Detail level of alert messages (simple, detailed)
- **Timezone**: User's preferred timezone for timestamps

## Configuration Storage

### In-Memory Storage
- Fast access to user configurations
- Thread-safe operations
- Automatic initialization for new users

### File-Based Persistence
- JSON format for human-readable configuration files
- Automatic backup of existing configuration files
- Graceful handling of file corruption with backup recovery
- Save configuration on bot shutdown

### Configuration Validation
- **Exchange Validation**: Check against supported exchanges list
- **Symbol Validation**: Validate symbol format using regex patterns
- **Threshold Validation**: Ensure numerical thresholds are valid
- **Limit Validation**: Validate monitoring limits are within bounds

## Configuration Parameters

### Arbitrage Parameters
```json
{
  "arbitrage": {
    "assets": ["BTC-USDT", "ETH-USDT"],
    "exchanges": ["binance", "okx", "bybit", "deribit"],
    "threshold_percentage": 0.5,
    "threshold_absolute": 1.0,
    "max_monitors": 10,
    "enabled": false
  }
}
```

### Market View Parameters
```json
{
  "market_view": {
    "symbols": ["BTC-USDT", "ETH-USDT"],
    "exchanges": ["binance", "okx", "bybit", "deribit"],
    "update_frequency": 30,
    "significant_change_threshold": 0.1,
    "enabled": false
  }
}
```

### User Preferences
```json
{
  "preferences": {
    "alert_frequency": "immediate",
    "message_format": "detailed",
    "timezone": "UTC"
  }
}
```

## Telegram Integration

### Configuration Commands
- **/config**: Main configuration menu
- **/config_arb**: Arbitrage configuration
- **/config_market**: Market view configuration

### Interactive Configuration
- **Inline Menus**: Navigate configuration options with buttons
- **Real-time Updates**: See current configuration values
- **Granular Control**: Modify specific settings individually
- **Validation Feedback**: Immediate feedback on invalid inputs

## Implementation Details

### User Configuration Manager
```python
class UserConfigManager:
    def __init__(self, config: ConfigManager, config_file: str = "user_config.json"):
        self.config = config
        self.config_file = config_file
        self.user_configs = {}  # In-memory storage
        self.default_config = {...}  # Default configuration template
        
    def get_user_config(self, user_id: int) -> Dict:
        """Get configuration for a specific user"""
        # Implementation details...
        
    def update_arbitrage_config(self, user_id: int, **kwargs) -> bool:
        """Update arbitrage configuration for a user"""
        # Implementation details...
```

### Configuration Validation
```python
def _validate_user_config(self, config: Dict) -> bool:
    """Validate user configuration"""
    # Validate arbitrage settings
    # Validate market view settings
    # Validate preferences
    # Return True if all valid, False otherwise
```

### Configuration Persistence
```python
def save_config(self) -> bool:
    """Save configuration to file"""
    # Create backup
    # Save current configuration
    # Handle errors gracefully
    
def load_config(self) -> bool:
    """Load configuration from file"""
    # Load from file
    # Validate configurations
    # Handle corrupted files with backup recovery
```

## Best Practices

### Security Considerations
- **File Permissions**: Secure configuration files
- **Data Validation**: Prevent injection attacks through configuration
- **Error Handling**: Graceful degradation on configuration errors

### Performance Considerations
- **Caching**: In-memory caching for fast access
- **Lazy Loading**: Load configurations only when needed
- **Efficient Updates**: Granular updates without full reloads

### User Experience
- **Clear Feedback**: Immediate validation feedback
- **Sensible Defaults**: Reasonable defaults for all settings
- **Progressive Disclosure**: Reveal complexity as needed
- **Error Recovery**: Automatic recovery from common issues

## API Reference

### UserConfigManager Methods
- `get_user_config(user_id)` - Get user configuration
- `set_user_config(user_id, config)` - Set user configuration
- `update_arbitrage_config(user_id, **kwargs)` - Update arbitrage settings
- `update_market_view_config(user_id, **kwargs)` - Update market view settings
- `update_preferences(user_id, **kwargs)` - Update user preferences
- `save_config()` - Save configuration to file
- `load_config()` - Load configuration from file
- `reset_user_config(user_id)` - Reset user configuration to defaults

### Configuration Access Methods
- `get_arbitrage_config(user_id)` - Get arbitrage configuration
- `get_market_view_config(user_id)` - Get market view configuration
- `get_preferences(user_id)` - Get user preferences

## Future Enhancements

### Planned Features
- **Configuration Templates**: Predefined configuration templates
- **Configuration Sharing**: Share configurations between users
- **Advanced Validation**: More sophisticated validation rules
- **Configuration History**: Track configuration changes over time

### Technical Improvements
- **Database Storage**: Support for database-backed configuration storage
- **Configuration Encryption**: Encrypt sensitive configuration data
- **Asynchronous Operations**: Non-blocking configuration operations
- **Extended Validation**: More comprehensive input validation