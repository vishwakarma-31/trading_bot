# Service Controllers

The GoQuant Trading Bot includes service controllers that manage the lifecycle of both the Arbitrage Signal Service and Market View Service.

## Service Controller

The ServiceController class manages both monitoring services, providing a unified interface for starting, stopping, and monitoring the services.

### Key Features
- **Service Lifecycle Management**: Start, stop, and monitor both services
- **Concurrent Operation**: Both services can run simultaneously
- **Resource Management**: Proper cleanup of resources on stop
- **Status Reporting**: Detailed status information for both services
- **Thread Safety**: Safe concurrent operation of services

## Service Controller API

### Initialization
```python
from data_processing.service_controller import ServiceController

# Create service controller
service_controller = ServiceController(market_fetcher, config)
```

### Arbitrage Signal Service Control

#### Starting Arbitrage Monitoring
```python
# Define assets and exchanges to monitor
asset_exchanges = {
    'BTC-USDT': ['binance', 'okx'],
    'ETH-USDT': ['binance', 'bybit']
}

# Start monitoring with optional thresholds
success = service_controller.start_arbitrage_monitoring(
    asset_exchanges, 
    threshold_percentage=0.5,  # 0.5% minimum profit
    threshold_absolute=1.0     # $1.00 minimum profit
)
```

#### Stopping Arbitrage Monitoring
```python
# Stop arbitrage monitoring
success = service_controller.stop_arbitrage_monitoring()
```

#### Getting Arbitrage Status
```python
# Get current arbitrage service status
status = service_controller.get_arbitrage_status()
# Returns:
# {
#     'monitoring': bool,
#     'monitored_assets': dict,
#     'active_opportunities_count': int,
#     'last_update': float,
#     'thresholds': {
#         'percentage': float,
#         'absolute': float
#     }
# }
```

### Market View Service Control

#### Starting Market View Monitoring
```python
# Define symbols and exchanges to monitor
symbol_exchanges = {
    'BTC-USDT': ['binance', 'okx', 'bybit'],
    'ETH-USDT': ['binance', 'okx', 'deribit']
}

# Start market view monitoring
success = service_controller.start_market_view_monitoring(symbol_exchanges)
```

#### Stopping Market View Monitoring
```python
# Stop market view monitoring
success = service_controller.stop_market_view_monitoring()
```

#### Getting Market View Status
```python
# Get current market view service status
status = service_controller.get_market_view_status()
# Returns:
# {
#     'monitoring': bool,
#     'monitored_symbols': dict,
#     'manager_status': dict,
#     'last_update': float,
#     'consolidated_views_count': int
# }
```

### Overall Service Management

#### Getting Overall Service Status
```python
# Get status of both services
status = service_controller.get_service_status()
# Returns:
# {
#     'arbitrage_service': dict,
#     'market_view_service': dict,
#     'timestamp': float
# }
```

#### Stopping All Services
```python
# Stop all monitoring services
success = service_controller.stop_all_services()
```

#### Checking Service Status
```python
# Check if a specific service is running
is_running = service_controller.is_service_running('arbitrage')  # or 'market_view'
```

## Implementation Details

### Service Controller Class
```python
class ServiceController:
    def __init__(self, market_fetcher: MarketDataFetcher, config: ConfigManager):
        self.arbitrage_detector = ArbitrageDetector(market_fetcher, config)
        self.market_view_manager = MarketViewManager(market_fetcher)
        # ... other initialization
        
    def start_arbitrage_monitoring(self, asset_exchanges: Dict[str, List[str]], 
                                 threshold_percentage: float = None, 
                                 threshold_absolute: float = None) -> bool:
        # Implementation details...
        
    def stop_arbitrage_monitoring(self) -> bool:
        # Implementation details...
        
    def get_arbitrage_status(self) -> Dict:
        # Implementation details...
```

### Resource Management
- **WebSocket Connections**: Properly closed on service stop
- **Threads**: Cleanly terminated with timeout handling
- **Data Structures**: Cleared to prevent memory leaks
- **Subscriptions**: Unsubscribed from market data feeds

### Concurrent Operation
- **Thread Safety**: Services operate independently without interference
- **Resource Isolation**: Each service manages its own resources
- **State Tracking**: Separate state tracking for each service
- **Error Isolation**: Errors in one service don't affect the other

## Integration with Telegram Bot

### Service Commands
- **/monitor_arb**: Start arbitrage monitoring
- **/stop_arb**: Stop arbitrage monitoring
- **/view_market**: Start market view monitoring
- **/stop_market**: Stop market view monitoring
- **/status_arb**: Get arbitrage service status
- **/status_market**: Get market view service status

### Interactive Service Management
- **Inline Menus**: Navigate service options with buttons
- **Real-time Status**: See current service status
- **Configuration Integration**: Use user-specific settings
- **Error Handling**: Graceful error reporting

## Best Practices

### Service Management
- **Always Stop Services**: Ensure proper cleanup when shutting down
- **Check Status Before Operations**: Verify service state before actions
- **Handle Errors Gracefully**: Continue operation even if one service fails
- **Monitor Resource Usage**: Watch for memory leaks or excessive CPU usage

### Performance Considerations
- **Efficient Threading**: Minimal overhead for service monitoring
- **Caching**: Cache market data to reduce API calls
- **Batch Operations**: Process multiple assets/symbols efficiently
- **Rate Limiting**: Respect exchange API rate limits

### Error Handling
- **Graceful Degradation**: Continue operation if one service fails
- **Automatic Recovery**: Attempt to restart failed services
- **Detailed Logging**: Comprehensive error logging for debugging
- **User Feedback**: Clear error messages for end users

## API Reference

### ServiceController Methods

#### Arbitrage Service Methods
- `start_arbitrage_monitoring(asset_exchanges, threshold_percentage, threshold_absolute)` - Start arbitrage monitoring
- `stop_arbitrage_monitoring()` - Stop arbitrage monitoring
- `get_arbitrage_status()` - Get arbitrage service status

#### Market View Service Methods
- `start_market_view_monitoring(symbol_exchanges)` - Start market view monitoring
- `stop_market_view_monitoring()` - Stop market view monitoring
- `get_market_view_status()` - Get market view service status

#### Service Management Methods
- `get_service_status()` - Get status of both services
- `stop_all_services()` - Stop all monitoring services
- `is_service_running(service_name)` - Check if a service is running

## Future Enhancements

### Planned Features
- **Dynamic Configuration**: Update service parameters while running
- **Advanced Monitoring**: More sophisticated monitoring algorithms
- **Service Scheduling**: Schedule service start/stop times
- **Performance Metrics**: Detailed performance statistics

### Technical Improvements
- **Asynchronous Operations**: Non-blocking service operations
- **Database Integration**: Persistent storage of service data
- **Enhanced Error Recovery**: More robust error handling
- **Extended Status Reporting**: More detailed status information