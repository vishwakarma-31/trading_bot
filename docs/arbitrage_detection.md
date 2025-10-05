# Arbitrage Detection Module

The Arbitrage Detection Module identifies profitable trading opportunities across multiple exchanges by comparing prices for the same assets.

## Components

### ArbitrageDetector
The main class for detecting arbitrage opportunities.

#### Key Features:
- Cross-exchange price comparison
- Synthetic pair arbitrage detection
- Configurable profit thresholds
- Real-time monitoring with WebSocket support
- Opportunity tracking and history

#### Methods:
- `set_thresholds()`: Configure minimum profit thresholds
- `find_arbitrage_opportunities()`: Find opportunities for specific symbols
- `find_synthetic_arbitrage_opportunities()`: Find opportunities between related assets
- `start_monitoring()`: Begin continuous monitoring
- `stop_monitoring()`: Stop continuous monitoring
- `get_active_opportunities()`: Get currently active opportunities
- `get_opportunity_history()`: Get historical opportunities
- `get_opportunity_count()`: Get opportunity statistics

### ArbitrageOpportunity
Data class representing a detected arbitrage opportunity.

#### Attributes:
- `symbol`: Trading symbol
- `buy_exchange`: Exchange to buy on
- `sell_exchange`: Exchange to sell on
- `buy_price`: Purchase price
- `sell_price`: Selling price
- `profit_percentage`: Profit as percentage
- `profit_absolute`: Profit in absolute value
- `timestamp`: Detection timestamp
- `threshold_percentage`: Percentage threshold used
- `threshold_absolute`: Absolute threshold used

### ThresholdConfig
Configuration class for arbitrage thresholds.

#### Attributes:
- `min_profit_percentage`: Minimum profit percentage (default: 0.5%)
- `min_profit_absolute`: Minimum profit in absolute value (default: $1.0)

## Threshold Mechanism

The module supports two types of configurable thresholds:

1. **Percentage-based**: Minimum profit percentage threshold
2. **Absolute value**: Minimum profit in absolute currency value

Thresholds can be configured via:
- Environment variables in `.env` file
- Programmatic API calls
- Telegram bot commands: `/threshold <percent> <absolute>`

## Continuous Monitoring

The module supports continuous monitoring of arbitrage opportunities:

- Real-time updates via WebSocket connections
- Periodic REST API polling as fallback
- Concurrent monitoring of multiple assets
- All four supported exchanges (Binance, OKX, Bybit, Deribit)

## Opportunity Detection

When an arbitrage opportunity is detected:

1. Price differences are calculated between exchanges
2. Profitability is checked against configured thresholds
3. Opportunity details are recorded with full metadata
4. Duration tracking begins for active opportunities

## Data Structure

Each arbitrage opportunity includes:

- **Asset names**: Symbols involved in the opportunity
- **Involved exchanges**: Buy and sell exchange names
- **Prices**: Buy and sell prices on each exchange
- **Calculated spread**: Profit percentage and absolute value
- **Timestamp**: When the opportunity was detected
- **Thresholds used**: Configuration values that triggered the opportunity

## Usage Example

```python
from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.arbitrage_detector import ArbitrageDetector

# Initialize components
config = ConfigManager()
fetcher = MarketDataFetcher(config)
detector = ArbitrageDetector(fetcher, config)

# Configure thresholds
detector.set_thresholds(min_profit_percentage=1.0, min_profit_absolute=2.0)

# Find opportunities
opportunities = detector.find_arbitrage_opportunities(
    ['binance', 'okx', 'bybit', 'deribit'], 
    'BTC-USDT'
)

# Start continuous monitoring
detector.start_monitoring(['BTC-USDT', 'ETH-USDT'])

# Get active opportunities
active_opps = detector.get_active_opportunities()
```

## Telegram Integration

The module integrates with the Telegram bot for real-time configuration and monitoring:

- `/threshold` - View current thresholds
- `/threshold <percent> <absolute>` - Set new thresholds
- `/arbitrage` - View current arbitrage opportunities

## Synthetic Pair Comparisons

The module can detect arbitrage opportunities between related assets:

- Compare BTC/USDT vs BTC/USDC on the same exchange
- Identify pricing inefficiencies between quote currencies
- Calculate synthetic price ratios for cross-validation

## Error Handling

The module includes comprehensive error handling for:

- Network connectivity issues
- API rate limiting
- Data parsing errors
- Invalid threshold configurations

All errors are logged and appropriate fallback mechanisms are in place.