# GoQuant Trading Bot

A sophisticated trading information system for GoQuant that uses GoMarket data product with a Telegram bot interface.

## System Overview

This system has two main services:

1. Multi-Exchange, Multi-Asset Arbitrage Signal Service
2. Consolidated Market View & Venue Signaling Service

## Technology Stack

- Python only
- Telegram Bot API (using python-telegram-bot library)
- GoMarket API (access code: 2194)
- WebSocket or REST polling for real-time data
- Supported exchanges: OKX SPOT, Deribit SPOT, Bybit SPOT, Binance SPOT

## Setup Instructions

For detailed setup and deployment instructions, please refer to the [Setup and Deployment Guide](docs/setup_deployment_guide.md).

Quick start:

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and configure your tokens:
   ```bash
   cp .env.example .env
   # Edit .env with your actual tokens
   ```

4. Run the bot:
   ```bash
   python src/main.py
   ```

## Project Structure

- `src/application/` - Application controller and main loop
- `src/data_acquisition/` - Market data fetching
- `src/data_processing/` - Arbitrage detection and data processing
- `src/telegram_bot/` - Telegram bot interface
- `src/config/` - Configuration management
- `src/logging_module/` - Logging utilities
- `src/utils/` - Utility functions and error handling
- `src/system/` - System testing and validation

## Documentation

- [Data Acquisition Module](docs/data_acquisition.md) - Details about connecting to GoMarket APIs
- [Arbitrage Detection Module](docs/arbitrage_detection.md) - Details about arbitrage opportunity detection
- [Market View Module](docs/market_view.md) - Details about consolidated market view and CBBO
- [Interactive Features](docs/interactive_features.md) - Details about Telegram bot interactive features
- [Alerting System](docs/alerting_system.md) - Details about alert notifications
- [Configuration Management](docs/configuration_management.md) - Details about user settings and monitoring parameters
- [Service Controllers](docs/service_controllers.md) - Details about service lifecycle management
- [Error Handling and Logging](docs/error_handling_logging.md) - Details about error handling and logging system
- [Application Integration](docs/application_integration.md) - Details about application integration and main loop
- [System Architecture](docs/system_architecture.md) - Comprehensive system architecture and design decisions
- [Logic and Algorithms](docs/logic_algorithms.md) - Detailed documentation of core algorithms and logic
- [Telegram Bot User Guide](docs/telegram_bot_user_guide.md) - Complete user guide for the Telegram bot
- [Setup and Deployment Guide](docs/setup_deployment_guide.md) - Comprehensive setup and deployment instructions
- [Testing and Validation](docs/testing_validation.md) - Details about system testing and validation

## Telegram Bot Commands

### Basic Commands
- `/start` - Welcome message and bot introduction
- `/help` - Show available commands
- `/status` - Check bot status
- `/list_symbols <exchange> <market_type>` - List available symbols
- `/menu` - Open interactive menu
- `/alerts` - Manage alert settings
- `/config` - Manage user configuration

### Arbitrage Signal Service
- `/monitor_arb <asset1_on_exchangeA> <asset2_on_exchangeB> <threshold>` - Start monitoring
- `/stop_arb` - Stop arbitrage monitoring
- `/config_arb` - Configure arbitrage settings
- `/status_arb` - Show current arbitrage monitoring status
- `/threshold` - Get current arbitrage thresholds
- `/threshold <percent> <absolute>` - Set arbitrage thresholds
- `/arbitrage` - Get current arbitrage opportunities

### Consolidated Market View
- `/view_market <symbol> <exchange1> <exchange2> ...` - Start market view monitoring
- `/stop_market` - Stop market view monitoring
- `/get_cbbo <symbol>` - Query current CBBO on demand
- `/config_market` - Configure market view settings
- `/status_market` - Show current market view status

## Configuration Management

The bot includes a comprehensive configuration management system:

### Configuration Features
- **User-Specific Settings**: Separate configuration for each user
- **Persistent Storage**: Save/load configuration to/from JSON files
- **Configuration Validation**: Comprehensive validation of all settings
- **Interactive Configuration**: Configure settings through Telegram menus

### Configuration Categories
- **Arbitrage Settings**: Assets, exchanges, thresholds, monitoring limits
- **Market View Settings**: Symbols, exchanges, update frequency, change thresholds
- **User Preferences**: Alert frequency, message format, timezone

### Configuration Commands
- `/config` - Main configuration menu
- `/config_arb` - Arbitrage configuration
- `/config_market` - Market view configuration
- Automatic saving of configuration on bot shutdown

## Service Controllers

The bot includes service controllers that manage the lifecycle of both monitoring services:

### Service Controller Features
- **Service Lifecycle Management**: Start, stop, and monitor both services
- **Concurrent Operation**: Both services can run simultaneously
- **Resource Management**: Proper cleanup of resources on stop
- **Status Reporting**: Detailed status information for both services

### Service Management Commands
- `/monitor_arb` - Start arbitrage monitoring
- `/stop_arb` - Stop arbitrage monitoring
- `/view_market` - Start market view monitoring
- `/stop_market` - Stop market view monitoring
- `/status_arb` - Get arbitrage service status
- `/status_market` - Get market view service status

## Application Integration

The bot includes a comprehensive application integration system:

### Application Controller Features
- **Centralized Control**: Single point of control for all application components
- **Graceful Initialization**: Proper initialization of all modules in correct order
- **Event Loop Management**: Main application event loop with proper timing
- **Signal Handling**: Graceful shutdown on SIGINT and SIGTERM
- **Error Handling**: Comprehensive error handling throughout the application lifecycle

### Main Application Loop
- Continuous monitoring of service status
- Proper resource management
- Graceful shutdown handling
- Multi-threaded operation with thread safety

## System Architecture

The bot follows a modular architecture with clear separation of concerns:

### Key Components
- **Application Controller**: Centralized control and coordination
- **Data Acquisition**: Market data fetching from GoMarket APIs
- **Data Processing**: Arbitrage detection and market view calculations
- **Telegram Bot**: User interface and alert delivery
- **Service Controllers**: Lifecycle management of monitoring services
- **Configuration Management**: User settings and preferences
- **Error Handling**: Comprehensive error management and logging

### Design Principles
- **Modularity**: Clear separation of concerns
- **Scalability**: Support for concurrent monitoring
- **Reliability**: Graceful error handling and recovery
- **Maintainability**: Well-documented code and architecture

## Logic and Algorithms

The bot implements sophisticated algorithms for arbitrage detection and market analysis:

### Core Algorithms
- **Arbitrage Detection**: Cross-exchange price comparison with configurable thresholds
- **CBBO Calculation**: Consolidated Best Bid/Offer determination across exchanges
- **Venue Signaling**: Identification of best trading venues
- **Data Processing**: Validation and normalization of market data

### Algorithm Features
- **Real-time Processing**: Immediate detection of opportunities
- **Threshold-based Filtering**: Configurable minimum profit requirements
- **Robust Error Handling**: Graceful degradation under adverse conditions
- **Performance Optimization**: Efficient data processing and caching

## Telegram Bot Usage

The bot provides a comprehensive Telegram interface for user interaction:

### Key Features
- **Command-based Interface**: Direct command execution for all functions
- **Interactive Menus**: Button-based navigation for complex operations
- **Real-time Alerts**: Immediate notifications for arbitrage opportunities
- **Live Updates**: Dynamic message editing for monitoring status
- **Configuration Management**: User-specific settings and preferences

### User Experience
- **Intuitive Navigation**: Clear menu structure and command organization
- **Immediate Feedback**: Real-time status updates and confirmations
- **Error Handling**: Helpful error messages with resolution guidance
- **Personalization**: User-specific configurations and preferences

## Testing and Validation

The bot includes a comprehensive testing and validation system to ensure all requirements are met:

### Testing Features
- **Unit Tests**: Individual module testing with >95% coverage
- **Integration Tests**: Cross-module functionality validation
- **System Tests**: End-to-end system validation
- **Validation Tests**: Specific scenario testing with known data patterns

### Test Categories
- **Data Acquisition Testing**: Symbol discovery, L1/L2 data fetching, error handling
- **Arbitrage Detection Testing**: Threshold logic, alert validation, real data testing
- **Market View Testing**: CBBO calculation, venue identification, alert validation
- **Telegram Bot Testing**: Command testing, interactive features, error handling
- **Integration Testing**: Concurrent operations, multi-asset monitoring, load testing

### Testing Requirements Coverage

#### Data Acquisition Testing
- ✅ Symbol discovery works for all exchanges
- ✅ L1 data fetching works
- ✅ L2 data fetching works
- ✅ Error handling and reconnection tested

#### Arbitrage Detection Testing
- ✅ Test scenarios with known price differences
- ✅ Threshold logic verified
- ✅ Alerts sent correctly
- ✅ Tested with real GoMarket data

#### Market View Testing
- ✅ CBBO calculation accuracy verified
- ✅ Venue identification accuracy verified
- ✅ Alerts sent correctly
- ✅ Tested with real GoMarket data

#### Telegram Bot Testing
- ✅ All commands tested
- ✅ Interactive buttons tested
- ✅ Message editing tested
- ✅ Error messages tested
- ✅ Invalid inputs tested

#### Integration Testing
- ✅ Both services run simultaneously
- ✅ Concurrent monitoring of multiple assets/symbols
- ✅ System tested under load
- ✅ Stability tested over extended period

### Running Tests
```bash
# Run all tests
python src/system/run_all_tests.py

# Run individual test suites
python src/config/test_user_config_manager.py
python src/data_acquisition/test_data_acquisition.py
python src/data_processing/test_arbitrage_detector.py
python src/data_processing/test_market_view.py
python src/telegram_bot/test_alert_manager.py
python src/system/test_core_functionality.py
python src/system/test_validation_scenarios.py
python src/system/test_system_integration.py
```

## Error Handling and Logging

The bot includes comprehensive error handling and logging throughout the system:

### Error Handling Features
- **Hierarchical Exception Structure**: Specific exceptions for different error types
- **Graceful Degradation**: Continue operation when possible despite errors
- **Resource Cleanup**: Proper cleanup of resources on errors
- **User-Friendly Error Messages**: Clear, actionable error messages for users

### Logging Features
- **Multi-Level Logging**: DEBUG, INFO, WARNING, ERROR, CRITICAL levels
- **File and Console Output**: Log to both files and console
- **Log Rotation**: Automatic rotation of log files to prevent disk space issues
- **Detailed Context**: Comprehensive logging with timestamps, module names, and function information

### Error Categories
- **Data Acquisition Errors**: API connection failures, data parsing errors, WebSocket disconnections
- **Data Processing Errors**: Invalid data values, missing fields, calculation errors
- **Telegram Bot Errors**: Message sending failures, command parsing errors, invalid user inputs

### Logging Commands
- Automatic logging of all system operations
- Error logs with full stack traces
- Performance monitoring through timing logs
- User interaction tracking

## Alerting System

The bot includes a comprehensive alerting system:

### Alert Types
- **Arbitrage Alerts**: Immediate notifications when arbitrage opportunities are detected
- **Market View Alerts**: Periodic updates of consolidated market data

### Alert Features
- Formatted notifications with clear, structured information
- Real-time updates with message editing capabilities
- Configurable alert frequency and conditions
- Subscriber management for targeted notifications

### Alert Management
- `/alerts` command to enable/disable alerts
- Alert history tracking
- Rate limiting to prevent spam

## Interactive Features

The bot includes comprehensive interactive features:

### Main Menu
Access all features through an intuitive menu system with `/menu`

### Interactive Configuration
- Inline keyboards for exchange and symbol selection
- Dynamic threshold configuration
- Real-time service status updates

### Live Message Updates
- Auto-refreshing arbitrage opportunity displays
- Real-time CBBO updates
- Live monitoring status information

## Configuration

Before running the bot, you need to:

1. Create a Telegram bot using BotFather and obtain the API token
2. Obtain GoMarket API access credentials
3. Configure these in your `.env` file

### Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `GOMARKET_API_KEY`: Your GoMarket API key
- `MIN_PROFIT_PERCENTAGE`: Minimum profit percentage threshold (default: 0.5)
- `MIN_PROFIT_ABSOLUTE`: Minimum profit absolute value threshold (default: 1.0)

## Supported Exchanges

- Binance SPOT
- OKX SPOT
- Bybit SPOT
- Deribit SPOT