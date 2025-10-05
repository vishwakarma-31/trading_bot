# Data Acquisition Module

The Data Acquisition Module is responsible for connecting to the GoMarket APIs and fetching market data from multiple exchanges.

## Components

### MarketDataFetcher
The main class for fetching market data from GoMarket APIs.

#### Key Features:
- Symbol discovery across all supported exchanges
- L1 market data fetching (BBO and last trade prices)
- L2 order book data fetching
- REST API polling with rate limiting protection
- Error handling and logging

#### Methods:
- `get_available_symbols(exchange)`: Get symbols for a specific exchange
- `get_all_symbols()`: Get symbols for all exchanges
- `get_l1_market_data(exchange, symbol)`: Get L1 data for a specific symbol
- `get_l2_order_book(exchange, symbol)`: Get L2 data for a specific symbol
- `get_multiple_l1_data(pairs)`: Get L1 data for multiple exchange-symbol pairs
- `get_multiple_l2_data(pairs)`: Get L2 data for multiple exchange-symbol pairs

### WebSocketManager
Manages WebSocket connections for real-time market data streaming.

#### Key Features:
- Real-time data streaming via WebSocket
- Automatic reconnection logic
- Connection status monitoring
- Support for multiple simultaneous connections

#### Methods:
- `connect(exchange, symbol, callback)`: Connect to WebSocket for real-time data
- `connect_multiple(pairs, callback)`: Connect to multiple WebSockets
- `disconnect(exchange, symbol)`: Disconnect a specific WebSocket
- `disconnect_all()`: Disconnect all WebSockets
- `is_connected(exchange, symbol)`: Check connection status

## Supported Exchanges
- Binance SPOT
- OKX SPOT
- Bybit SPOT
- Deribit SPOT

## Usage Example

```python
from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher

# Initialize
config = ConfigManager()
fetcher = MarketDataFetcher(config)

# Get symbols
symbols = fetcher.get_available_symbols('binance')

# Get L1 data
l1_data = fetcher.get_l1_market_data('binance', 'BTC-USDT')

# Get L2 data
l2_data = fetcher.get_l2_order_book('binance', 'BTC-USDT')

# WebSocket subscription
def data_callback(exchange, symbol, data):
    print(f"Received data for {exchange}:{symbol}")

fetcher.subscribe_l1_data('binance', 'BTC-USDT', data_callback)
```

## Error Handling
The module includes comprehensive error handling for:
- API connection failures
- Data parsing errors
- Rate limiting
- Network issues

All errors are logged and appropriate fallback mechanisms are in place.