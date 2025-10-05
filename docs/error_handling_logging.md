# Error Handling and Logging

The GoQuant Trading Bot includes comprehensive error handling and logging throughout the system to ensure robust operation and effective debugging.

## Error Handling Architecture

### Custom Exception Hierarchy

The system uses a hierarchical exception structure for precise error categorization:

```
TradingBotError (Base)
├── DataAcquisitionError
│   ├── APIConnectionError
│   ├── DataParsingError
│   ├── WebSocketError
│   ├── RateLimitError
│   └── AuthenticationError
├── DataProcessingError
│   ├── InvalidDataError
│   ├── MissingDataError
│   ├── CalculationError
│   └── ThresholdValidationError
└── TelegramBotError
    ├── MessageSendingError
    ├── CommandParsingError
    ├── InvalidUserInputError
    └── BotAPIError
```

### Exception Handling Utilities

#### Custom Exceptions
- **TradingBotError**: Base exception for all trading bot errors
- **DataAcquisitionError**: Errors related to data fetching
- **DataProcessingError**: Errors related to data processing and calculations
- **TelegramBotError**: Errors related to Telegram bot operations

#### Decorators
```python
@handle_exception(logger_name=__name__, reraise=False, default_return=None)
def risky_function():
    # Function implementation
    pass
```

#### Utility Functions
- `log_exception()`: Log exceptions with full traceback
- `safe_execute()`: Safely execute functions with exception handling

## Logging System

### Logging Configuration

The system uses Python's logging module with the following configuration:

- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output Destinations**: Console and rotating files
- **File Rotation**: Automatic rotation at 10MB with 5 backup files
- **Log Format**: Detailed format including timestamp, module, function, line number

### Log Categories

1. **General Application Logs**: `logs/trading_bot_YYYYMMDD.log`
2. **Error-Specific Logs**: `logs/errors_YYYYMMDD.log`
3. **Module-Specific Logs**: Individual module logs

### Logging Implementation

#### Data Acquisition Logging
- API requests and responses
- Connection status changes
- Data parsing operations
- WebSocket connection events

#### Data Processing Logging
- Arbitrage opportunity detection
- Market view calculations
- Threshold validations
- Data quality checks

#### Telegram Bot Logging
- User command execution
- Message sending operations
- User interaction tracking
- Bot state changes

## Error Handling by Module

### Data Acquisition Module

#### API Connection Errors
```python
try:
    response = self.session.get(endpoint, headers=headers, timeout=10)
    response.raise_for_status()
except requests.exceptions.Timeout:
    raise APIConnectionError(f"Timeout while fetching data")
except requests.exceptions.ConnectionError:
    raise APIConnectionError(f"Connection error")
```

#### Data Parsing Errors
```python
try:
    data = response.json()
except json.JSONDecodeError as e:
    raise DataParsingError(f"Data parsing error: {e}")
```

#### WebSocket Errors
```python
try:
    self.ws_manager.connect(exchange, symbol, callback)
except Exception as e:
    raise WebSocketError(f"WebSocket connection failed: {e}")
```

### Data Processing Module

#### Invalid Data Handling
```python
if not isinstance(price, (int, float)) or price <= 0:
    raise InvalidDataError(f"Invalid price data: {price}")
```

#### Calculation Errors
```python
try:
    profit_percentage = ((sell_price - buy_price) / buy_price) * 100
except ZeroDivisionError:
    raise CalculationError("Division by zero in profit calculation")
```

#### Threshold Validation
```python
if min_profit_percentage < 0:
    raise ThresholdValidationError("Threshold must be non-negative")
```

### Telegram Bot Module

#### Message Sending Errors
```python
try:
    context.bot.send_message(chat_id=chat_id, text=message)
except Exception as e:
    raise MessageSendingError(f"Failed to send message: {e}")
```

#### Command Parsing Errors
```python
try:
    threshold = float(context.args[0])
except ValueError:
    raise CommandParsingError("Invalid threshold value")
```

#### User Input Validation
```python
if not self._validate_exchange(exchange):
    raise InvalidUserInputError(f"Invalid exchange: {exchange}")
```

## Best Practices

### Error Handling Guidelines

1. **Specific Exceptions**: Use specific exception types rather than generic exceptions
2. **Graceful Degradation**: Continue operation when possible despite errors
3. **Informative Messages**: Provide clear, actionable error messages
4. **Resource Cleanup**: Ensure proper cleanup of resources on errors
5. **Logging**: Log all errors with appropriate context and stack traces

### Logging Guidelines

1. **Appropriate Levels**: Use correct log levels (DEBUG for detailed info, ERROR for problems)
2. **Context Information**: Include relevant context in log messages
3. **Performance Considerations**: Avoid expensive string formatting in logging
4. **Security**: Never log sensitive information like API keys
5. **Rotation**: Use log rotation to prevent disk space issues

### Example Implementation

```python
import logging
from utils.error_handler import handle_exception, log_exception

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @handle_exception(logger_name=__name__, reraise=False, default_return=None)
    def process_data(self, data):
        try:
            # Processing logic
            result = self._perform_calculation(data)
            self.logger.info(f"Processed data successfully: {len(data)} items")
            return result
        except Exception as e:
            log_exception(self.logger, e, "Error processing data")
            raise DataProcessingError(f"Failed to process data: {e}")
    
    def _perform_calculation(self, data):
        # Calculation implementation
        pass
```

## Configuration

### Log Level Configuration
Set log levels through environment variables or configuration files:
```python
import os
log_level = os.getenv('LOG_LEVEL', 'INFO')
```

### File Rotation Configuration
```python
file_handler = RotatingFileHandler(
    filename, 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## Monitoring and Debugging

### Log Analysis
- Monitor error logs for recurring issues
- Track performance through timing logs
- Analyze user behavior through command logs

### Debugging Features
- Detailed DEBUG level logging for troubleshooting
- Context-rich error messages
- Stack trace preservation

## Future Enhancements

### Planned Improvements
- **Centralized Error Reporting**: Aggregate error statistics and reports
- **External Monitoring Integration**: Integrate with external monitoring services
- **Advanced Log Filtering**: Dynamic log filtering based on conditions
- **Performance Profiling**: Add performance profiling capabilities

### Technical Improvements
- **Asynchronous Logging**: Non-blocking logging operations
- **Structured Logging**: JSON-formatted logs for easier parsing
- **Log Aggregation**: Centralized log collection for distributed systems
- **Alerting System**: Automated alerts for critical errors