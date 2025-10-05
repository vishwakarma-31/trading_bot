# Market View Module

The Market View Module provides consolidated market data across multiple exchanges, including CBBO (Consolidated Best Bid/Offer) calculations and real-time monitoring capabilities.

## Components

### MarketViewManager
The main class for managing consolidated market views across exchanges.

#### Key Features:
- Real-time market data aggregation
- CBBO (Consolidated Best Bid/Offer) calculation
- Multi-exchange market monitoring
- WebSocket and REST API data fetching

#### Methods:
- `get_market_data()`: Get market data for a specific exchange and symbol
- `get_consolidated_market_view()`: Get consolidated view across multiple exchanges
- `get_cbbo()`: Get current CBBO for a symbol
- `start_monitoring()`: Begin continuous market monitoring
- `stop_monitoring()`: Stop continuous market monitoring
- `get_monitoring_status()`: Get current monitoring status

### MarketViewData
Data class representing market data for a symbol on a specific exchange.

#### Attributes:
- `symbol`: Trading symbol
- `exchange`: Exchange name
- `bid_price`: Best bid price
- `ask_price`: Best ask price
- `bid_size`: Best bid size
- `ask_size`: Best ask size
- `timestamp`: Data timestamp

### ConsolidatedMarketView
Data class representing consolidated market view across multiple exchanges.

#### Attributes:
- `symbol`: Trading symbol
- `exchanges_data`: Dictionary of MarketViewData by exchange
- `cbbo_bid_exchange`: Exchange with best bid
- `cbbo_ask_exchange`: Exchange with best ask
- `cbbo_bid_price`: Best bid price across all exchanges
- `cbbo_ask_price`: Best ask price across all exchanges
- `timestamp`: Data timestamp

## Supported Exchanges
- Binance SPOT
- OKX SPOT
- Bybit SPOT
- Deribit SPOT

## Telegram Integration

The module integrates with the Telegram bot for real-time monitoring and querying:

- `/view_market <symbol> <exchange1> <exchange2> ...` - Start market view monitoring
- `/stop_market` - Stop market view monitoring
- `/get_cbbo <symbol>` - Query current CBBO on demand
- `/config_market` - Configure market view settings
- `/status_market` - Show current market view status

## Usage Example

```python
from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.market_view import MarketViewManager

# Initialize components
config = ConfigManager()
fetcher = MarketDataFetcher(config)
manager = MarketViewManager(fetcher)

# Get consolidated market view
consolidated_view = manager.get_consolidated_market_view('BTC-USDT', ['binance', 'okx', 'bybit'])

# Get CBBO
cbbo = manager.get_cbbo('BTC-USDT')

# Start monitoring
manager.start_monitoring({'BTC-USDT': ['binance', 'okx', 'bybit', 'deribit']})
```

## Data Structure

Each consolidated market view includes:

- **Symbol**: Trading pair being monitored
- **Exchange data**: Market data from each exchange
- **CBBO information**: Best bid/ask prices and exchanges
- **Timestamp**: When the data was collected

## Error Handling

The module includes comprehensive error handling for:

- Network connectivity issues
- API rate limiting
- Data parsing errors
- Invalid symbol/exchange combinations

All errors are logged and appropriate fallback mechanisms are in place.