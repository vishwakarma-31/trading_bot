# Telegram Bot User Guide

## Overview

The GoQuant Trading Bot provides a comprehensive Telegram interface for monitoring arbitrage opportunities and market views across multiple cryptocurrency exchanges. This guide explains how to use all available commands, interact with the bot's features, and configure your monitoring preferences.

## Command Reference

### Basic Commands

#### `/start`
**Purpose**: Initialize the bot and receive a welcome message
**Syntax**: `/start`
**Parameters**: None
**Description**: This command introduces you to the bot and provides basic navigation information.
**Example**: 
```
/start
```

#### `/help`
**Purpose**: Display a list of all available commands
**Syntax**: `/help`
**Parameters**: None
**Description**: Shows all available commands with brief descriptions.
**Example**: 
```
/help
```

#### `/status`
**Purpose**: Check the overall status of the bot
**Syntax**: `/status`
**Parameters**: None
**Description**: Displays the current status of both arbitrage and market view services.
**Example**: 
```
/status
```

#### `/list_symbols`
**Purpose**: List available trading symbols for a specific exchange
**Syntax**: `/list_symbols <exchange> <market_type>`
**Parameters**: 
- `exchange`: Name of the exchange (binance, okx, bybit, deribit)
- `market_type`: Type of market (spot)
**Description**: Shows all available trading symbols for the specified exchange and market type.
**Examples**: 
```
/list_symbols binance spot
/list_symbols okx spot
```

#### `/menu`
**Purpose**: Open the interactive main menu
**Syntax**: `/menu`
**Parameters**: None
**Description**: Provides access to all bot features through an interactive menu system.
**Example**: 
```
/menu
```

#### `/alerts`
**Purpose**: Manage alert settings
**Syntax**: `/alerts`
**Parameters**: None
**Description**: Toggle alert reception and view alert history.
**Example**: 
```
/alerts
```

#### `/config`
**Purpose**: Access the main configuration menu
**Syntax**: `/config`
**Parameters**: None
**Description**: Configure arbitrage settings, market view settings, and user preferences.
**Example**: 
```
/config
```

### Arbitrage Signal Service Commands

#### `/monitor_arb`
**Purpose**: Start arbitrage monitoring for specific assets
**Syntax**: `/monitor_arb <asset1_on_exchangeA> <asset2_on_exchangeB> <threshold>`
**Parameters**: 
- `asset1_on_exchangeA`: First asset with exchange (e.g., BTC-USDT_on_binance)
- `asset2_on_exchangeB`: Second asset with exchange (e.g., BTC-USDT_on_okx)
- `threshold`: Optional threshold values (percentage and absolute)
**Description**: Begin monitoring arbitrage opportunities between specified assets and exchanges.
**Examples**: 
```
/monitor_arb BTC-USDT_on_binance BTC-USDT_on_okx
/monitor_arb BTC-USDT_on_binance BTC-USDT_on_okx 1.0 2.0
```

#### `/stop_arb`
**Purpose**: Stop arbitrage monitoring
**Syntax**: `/stop_arb`
**Parameters**: None
**Description**: Stop all active arbitrage monitoring services.
**Example**: 
```
/stop_arb
```

#### `/config_arb`
**Purpose**: Configure arbitrage monitoring settings
**Syntax**: `/config_arb`
**Parameters**: None
**Description**: Access detailed arbitrage configuration options.
**Example**: 
```
/config_arb
```

#### `/status_arb`
**Purpose**: Check the status of arbitrage monitoring
**Syntax**: `/status_arb`
**Parameters**: None
**Description**: Display current arbitrage monitoring status and active opportunities.
**Example**: 
```
/status_arb
```

#### `/threshold`
**Purpose**: View or set arbitrage profit thresholds
**Syntax**: `/threshold` or `/threshold <percent> <absolute>`
**Parameters**: 
- `percent`: Minimum profit percentage threshold
- `absolute`: Minimum profit absolute value threshold
**Description**: View current thresholds or set new values for arbitrage detection.
**Examples**: 
```
/threshold
/threshold 1.0 2.0
```

#### `/arbitrage`
**Purpose**: View current arbitrage opportunities
**Syntax**: `/arbitrage`
**Parameters**: None
**Description**: Display all currently detected arbitrage opportunities.
**Example**: 
```
/arbitrage
```

### Consolidated Market View Commands

#### `/view_market`
**Purpose**: Start market view monitoring for specific symbols
**Syntax**: `/view_market <symbol> <exchange1> <exchange2> ...`
**Parameters**: 
- `symbol`: Trading symbol to monitor (e.g., BTC-USDT)
- `exchange1, exchange2, ...`: List of exchanges to include
**Description**: Begin monitoring consolidated market view for the specified symbol across exchanges.
**Examples**: 
```
/view_market BTC-USDT binance okx bybit
/view_market ETH-USDT binance okx deribit bybit
```

#### `/stop_market`
**Purpose**: Stop market view monitoring
**Syntax**: `/stop_market`
**Parameters**: None
**Description**: Stop all active market view monitoring services.
**Example**: 
```
/stop_market
```

#### `/get_cbbo`
**Purpose**: Query current Consolidated Best Bid/Offer
**Syntax**: `/get_cbbo <symbol>`
**Parameters**: 
- `symbol`: Trading symbol to query
**Description**: Get the current CBBO for the specified symbol across all monitored exchanges.
**Example**: 
```
/get_cbbo BTC-USDT
```

#### `/config_market`
**Purpose**: Configure market view settings
**Syntax**: `/config_market`
**Parameters**: None
**Description**: Access detailed market view configuration options.
**Example**: 
```
/config_market
```

#### `/status_market`
**Purpose**: Check the status of market view monitoring
**Syntax**: `/status_market`
**Parameters**: None
**Description**: Display current market view monitoring status and configuration.
**Example**: 
```
/status_market
```

## Interaction Flows

### Setting Up Arbitrage Monitoring (Step-by-Step)

1. **Configure Thresholds** (Optional but Recommended):
   ```
   /threshold 0.5 1.0
   ```

2. **Select Assets and Exchanges**:
   - Use `/list_symbols` to find available assets
   - Identify assets you want to monitor across different exchanges

3. **Start Monitoring**:
   ```
   /monitor_arb BTC-USDT_on_binance BTC-USIT_on_okx
   ```

4. **Verify Monitoring Status**:
   ```
   /status_arb
   ```

5. **View Opportunities**:
   ```
   /arbitrage
   ```

6. **Stop Monitoring** (When Done):
   ```
   /stop_arb
   ```

### Setting Up Market View (Step-by-Step)

1. **Select Symbol and Exchanges**:
   - Use `/list_symbols` to find available symbols
   - Identify the symbol and exchanges you want to monitor

2. **Start Monitoring**:
   ```
   /view_market BTC-USDT binance okx bybit deribit
   ```

3. **Verify Monitoring Status**:
   ```
   /status_market
   ```

4. **View CBBO**:
   ```
   /get_cbbo BTC-USDT
   ```

5. **Stop Monitoring** (When Done):
   ```
   /stop_market
   ```

### Using Interactive Buttons

1. **Access Main Menu**:
   ```
   /menu
   ```

2. **Navigate Options**:
   - Use inline buttons to select services (Arbitrage, Market View, Settings)
   - Click "Back" to return to previous menus
   - Click "Done" to confirm selections

3. **Configure Settings**:
   - Use buttons to set thresholds, select exchanges, and choose symbols
   - Real-time feedback shows current selections

4. **Start/Stop Services**:
   - Use action buttons to begin or end monitoring
   - Status updates show current service state

### Interpreting Alerts

#### Arbitrage Alerts
When an arbitrage opportunity is detected, you'll receive a message like:
```
🔔 ARBITRAGE OPPORTUNITY DETECTED

Asset: BTC-USDT
Exchange A: Binance @ $60,000.00
Exchange B: OKX @ $60,150.00
Spread: $150.00 (0.25%)
Threshold: 0.20%
Time: 2025-10-05 14:30:15 UTC
```

**Interpretation**:
- **Asset**: The trading pair with arbitrage opportunity
- **Exchange A**: Where to buy (lower price)
- **Exchange B**: Where to sell (higher price)
- **Spread**: Profit per unit (absolute and percentage)
- **Threshold**: Minimum profit requirements that triggered the alert
- **Time**: When the opportunity was detected

#### Market View Alerts
Periodic market view updates appear as:
```
📊 MARKET VIEW UPDATE

Symbol: BTC-USDT
Best Bid: Kraken @ $60,000.50
Best Offer: Bybit @ $60,001.00
CBBO Mid: $60,000.75
Time: 2025-10-05 14:30:15 UTC
```

**Interpretation**:
- **Symbol**: The trading pair being monitored
- **Best Bid**: Highest bid price across all exchanges
- **Best Offer**: Lowest ask price across all exchanges
- **CBBO Mid**: Mid-price between best bid and offer
- **Time**: When the data was last updated

## Configuration Guide

### Configuring Thresholds

1. **View Current Thresholds**:
   ```
   /threshold
   ```

2. **Set New Thresholds**:
   ```
   /threshold <percentage> <absolute>
   ```
   Example:
   ```
   /threshold 1.0 2.0
   ```

3. **Recommended Values**:
   - **Percentage**: 0.5% to 2.0% (depending on trading fees and risk tolerance)
   - **Absolute**: $1.00 to $10.00 (depending on asset value and trading size)

### Selecting Exchanges

1. **List Available Exchanges**:
   - Supported exchanges: Binance, OKX, Bybit, Deribit

2. **Select Exchanges for Monitoring**:
   - Use interactive menus via `/config`
   - Toggle exchanges on/off using buttons
   - Multiple exchanges can be selected simultaneously

3. **Best Practices**:
   - Select 2-4 exchanges for optimal performance
   - Choose exchanges with good liquidity for your assets
   - Mix of different exchange types (global, Asian, European)

### Selecting Symbols

1. **Discover Available Symbols**:
   ```
   /list_symbols <exchange> spot
   ```

2. **Select Symbols for Monitoring**:
   - Use interactive menus via `/config`
   - Choose from available symbols
   - Multiple symbols can be monitored

3. **Recommended Symbols**:
   - High liquidity pairs (BTC-USDT, ETH-USDT)
   - Stablecoin pairs (USDT-USDC)
   - Popular altcoin pairs (ADA-USDT, SOL-USDT)

### Managing Multiple Monitors

1. **Monitor Limits**:
   - Maximum 10 concurrent arbitrage monitors
   - Maximum 20 concurrent market view monitors

2. **Managing Active Monitors**:
   ```
   /status_arb
   /status_market
   /stop_arb
   /stop_market
   ```

3. **Optimization Tips**:
   - Focus on high-volume symbols
   - Rotate monitored assets based on market conditions
   - Stop unused monitors to free up resources

## Troubleshooting

### Common Error Messages and Solutions

#### "Invalid exchange name"
**Cause**: Exchange name not recognized
**Solution**: Use supported exchanges (binance, okx, bybit, deribit)

#### "Symbol not found on exchange"
**Cause**: Specified symbol not available on the exchange
**Solution**: Use `/list_symbols` to verify available symbols

#### "Invalid threshold values"
**Cause**: Threshold values are negative or non-numeric
**Solution**: Use positive numbers for thresholds

#### "Service already running"
**Cause**: Attempting to start a service that's already active
**Solution**: Stop the service first or check status

#### "No arbitrage opportunities found"
**Cause**: Current market conditions don't meet threshold requirements
**Solution**: Adjust thresholds or wait for better market conditions

### How to Check Service Status

1. **Overall Status**:
   ```
   /status
   ```

2. **Arbitrage Service Status**:
   ```
   /status_arb
   ```

3. **Market View Service Status**:
   ```
   /status_market
   ```

4. **Interactive Status Check**:
   - Use `/menu` and navigate to status options
   - Real-time updates show current service state

### How to Restart Monitoring

1. **Stop Current Monitoring**:
   ```
   /stop_arb
   /stop_market
   ```

2. **Verify Services Stopped**:
   ```
   /status_arb
   /status_market
   ```

3. **Start New Monitoring**:
   ```
   /monitor_arb <parameters>
   /view_market <parameters>
   ```

4. **Confirm Services Running**:
   ```
   /status_arb
   /status_market
   ```

## Best Practices

### Recommended Threshold Values

#### For Beginners:
- **Percentage Threshold**: 0.5% to 1.0%
- **Absolute Threshold**: $1.00 to $5.00

#### For Experienced Traders:
- **Percentage Threshold**: 0.3% to 0.8%
- **Absolute Threshold**: $0.50 to $3.00

#### For High-Frequency Trading:
- **Percentage Threshold**: 0.1% to 0.5%
- **Absolute Threshold**: $0.10 to $1.00

### Recommended Update Frequencies

#### Arbitrage Monitoring:
- **Real-time**: Immediate alerts for opportunities
- **Update Interval**: Continuous monitoring

#### Market View:
- **Frequent Updates**: 30 seconds (default)
- **Moderate Updates**: 60 seconds
- **Infrequent Updates**: 120 seconds

### How to Avoid Rate Limits

1. **Limit Concurrent Monitors**:
   - Don't exceed recommended monitor limits
   - Stop unused monitoring services

2. **Optimize Update Frequencies**:
   - Use longer intervals for less volatile assets
   - Reduce update frequency during quiet market periods

3. **Efficient Exchange Selection**:
   - Monitor fewer exchanges for better performance
   - Focus on exchanges with the best liquidity for your assets

4. **Batch Operations**:
   - Configure multiple settings at once
   - Use interactive menus for efficient configuration

## Advanced Features

### Custom Alert Configuration

1. **Alert Frequency**:
   - Immediate: Alerts sent as soon as detected
   - Hourly: Summary of opportunities each hour
   - Daily: Daily summary of all opportunities

2. **Message Format**:
   - Simple: Basic opportunity information
   - Detailed: Comprehensive data including timestamps and thresholds

3. **Timezone Settings**:
   - Set preferred timezone for timestamp display
   - UTC is default for consistency

### Historical Data Access

1. **Opportunity History**:
   ```
   /arbitrage
   ```
   Shows recent arbitrage opportunities

2. **Market View History**:
   - Use `/get_cbbo` for current data
   - Historical trends available through market view updates

### Performance Monitoring

1. **Service Metrics**:
   - Opportunity detection rates
   - Data processing times
   - API usage statistics

2. **Resource Usage**:
   - Memory consumption
   - CPU utilization
   - Network bandwidth usage

## User Experience Tips

### Navigation Shortcuts

1. **Quick Access Menu**:
   ```
   /menu
   ```

2. **Direct Command Access**:
   - Use specific commands for faster access
   - Bookmark frequently used commands

3. **Status Quick Check**:
   ```
   /status
   ```

### Customization Options

1. **Personalized Settings**:
   - Save preferred exchanges and symbols
   - Set default thresholds
   - Configure alert preferences

2. **User-Specific Configuration**:
   - Each user has independent settings
   - Configurations persist between sessions

### Error Recovery

1. **Automatic Recovery**:
   - Services attempt to restart after failures
   - Graceful degradation during network issues

2. **Manual Recovery**:
   - Use `/stop_arb` and `/stop_market` to reset services
   - Reconfigure and restart monitoring

3. **Support Resources**:
   - Check documentation for detailed help
   - Contact support for persistent issues

## Conclusion

The GoQuant Trading Bot provides a powerful yet user-friendly Telegram interface for cryptocurrency arbitrage monitoring and market analysis. By following this guide, you can effectively utilize all available features to monitor trading opportunities and make informed decisions.

Remember to:
- Start with conservative thresholds
- Monitor service status regularly
- Adjust settings based on market conditions
- Follow best practices for optimal performance

For technical issues or feature requests, refer to the documentation or contact support.