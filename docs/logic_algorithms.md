# Logic and Algorithms Documentation

## Overview

This document provides detailed documentation of the core algorithms and logic used in the GoQuant Trading Bot, including arbitrage detection, CBBO calculation, venue signaling, and data processing mechanisms.

## 1. Arbitrage Detection Algorithm

### 1.1 Step-by-Step Explanation

The arbitrage detection algorithm follows these steps:

1. **Data Collection**: Fetch L1 market data (best bid/ask prices) for a specific symbol from all specified exchanges
2. **Data Validation**: Validate that all required data fields are present and valid
3. **Cross-Exchange Comparison**: Compare ask prices (buy prices) and bid prices (sell prices) across all exchange pairs
4. **Profit Calculation**: Calculate potential profit percentage and absolute value for each exchange pair
5. **Threshold Comparison**: Check if calculated profits meet user-configured minimum thresholds
6. **Opportunity Recording**: Record valid arbitrage opportunities that meet all criteria

### 1.2 Formula for Spread Calculation

The algorithm uses the following formulas to calculate arbitrage profits:

**Absolute Profit Formula**:
```
Absolute Profit = Sell Price - Buy Price
```

Where:
- Sell Price = Best bid price on selling exchange
- Buy Price = Best ask price on buying exchange

**Percentage Profit Formula**:
```
Percentage Profit = ((Sell Price - Buy Price) / Buy Price) × 100
```

### 1.3 Threshold Comparison Logic

The algorithm compares calculated profits against two configurable thresholds:

1. **Percentage Threshold**: Minimum required profit percentage
2. **Absolute Threshold**: Minimum required profit in absolute currency value

Both conditions must be met for an opportunity to be considered valid:
```
IF (Percentage Profit ≥ Min Percentage Threshold) AND 
   (Absolute Profit ≥ Min Absolute Threshold)
THEN Valid Arbitrage Opportunity
```

### 1.4 Example Calculations

Let's consider an example with BTC-USDT on two exchanges:

**Exchange A (Binance)**:
- Best Ask Price: $60,000.00
- Best Bid Price: $59,999.50

**Exchange B (OKX)**:
- Best Ask Price: $59,950.00
- Best Bid Price: $59,949.00

**Arbitrage Opportunity Calculation**:
1. Buy on Exchange B at $59,950.00 (ask price)
2. Sell on Exchange A at $59,999.50 (bid price)
3. Absolute Profit = $59,999.50 - $59,950.00 = $49.50
4. Percentage Profit = (($59,999.50 - $59,950.00) / $59,950.00) × 100 = 0.0826%

If the user's thresholds are:
- Minimum Percentage: 0.05%
- Minimum Absolute: $10.00

Then this would be a valid arbitrage opportunity since:
- 0.0826% ≥ 0.05% (✓)
- $49.50 ≥ $10.00 (✓)

## 2. CBBO Calculation Algorithm

### 2.1 How Best Bid is Determined Across Exchanges

The Consolidated Best Bid (CBBO) calculation algorithm determines the best bid price across all monitored exchanges by:

1. **Data Collection**: Fetch L1 market data from all specified exchanges
2. **Bid Price Extraction**: Extract the bid price from each exchange's market data
3. **Maximum Selection**: Select the highest bid price among all exchanges
4. **Exchange Identification**: Record which exchange has the best bid price

**Algorithm**:
```
FOR each exchange in monitored_exchanges:
    bid_price = get_bid_price(exchange, symbol)
    IF bid_price > best_bid_price:
        best_bid_price = bid_price
        best_bid_exchange = exchange
```

### 2.2 How Best Offer is Determined Across Exchanges

The Consolidated Best Ask (CBBO) calculation algorithm determines the best ask price across all monitored exchanges by:

1. **Data Collection**: Fetch L1 market data from all specified exchanges
2. **Ask Price Extraction**: Extract the ask price from each exchange's market data
3. **Minimum Selection**: Select the lowest ask price among all exchanges (greater than zero)
4. **Exchange Identification**: Record which exchange has the best ask price

**Algorithm**:
```
FOR each exchange in monitored_exchanges:
    ask_price = get_ask_price(exchange, symbol)
    IF (ask_price > 0) AND (ask_price < best_ask_price):
        best_ask_price = ask_price
        best_ask_exchange = exchange
```

### 2.3 Mid-Price Calculation Formula

The mid-price is calculated as the arithmetic mean of the best bid and best ask prices:

```
Mid-Price = (Best Bid Price + Best Ask Price) / 2
```

### 2.4 Example Calculations

Let's consider BTC-USDT prices across four exchanges:

**Binance**:
- Bid: $60,000.50
- Ask: $60,001.00

**OKX**:
- Bid: $60,000.00
- Ask: $60,000.50

**Bybit**:
- Bid: $60,001.00
- Ask: $60,001.50

**Deribit**:
- Bid: $59,999.50
- Ask: $60,000.00

**CBBO Calculation**:
1. Best Bid = $60,001.00 (Bybit)
2. Best Ask = $60,000.00 (Deribit)
3. Mid-Price = ($60,001.00 + $60,000.00) / 2 = $60,000.50

## 3. Venue Signaling Logic

### 3.1 How Best Venues are Identified

Venue signaling identifies the best venues for trading by:

1. **CBBO Calculation**: Determine the best bid and ask prices across all exchanges
2. **Exchange Mapping**: Record which exchanges have the best prices
3. **Venue Ranking**: Create a ranking of exchanges based on price competitiveness
4. **Signal Generation**: Generate signals indicating the best venues for buying and selling

### 3.2 When Updates are Triggered

Venue signaling updates are triggered by:

1. **Periodic Updates**: Regular intervals based on user configuration (default: 30 seconds)
2. **Significant Changes**: When price movements exceed user-defined thresholds
3. **New Data Arrival**: When fresh market data is received via WebSocket
4. **Manual Requests**: When users explicitly request CBBO information

### 3.3 Significant Change Detection Logic

Significant changes are detected using percentage-based thresholds:

```
Price Change Percentage = |(New Price - Old Price) / Old Price| × 100

IF Price Change Percentage ≥ Significant Change Threshold
THEN Trigger Update
```

For example, if the significant change threshold is 0.1% and the best bid price changes from $60,000.00 to $60,010.00:

```
Change Percentage = |($60,010.00 - $60,000.00) / $60,000.00| × 100 = 0.0167%
```

Since 0.0167% < 0.1%, this would not trigger an update based on significant change alone.

## 4. GoMarket Data Processing

### 4.1 How Raw Data is Received

Raw data is received from GoMarket through two mechanisms:

1. **REST API Polling**: Periodic HTTP requests to fetch market data
2. **WebSocket Streaming**: Real-time data streams for immediate updates

**REST API Format**:
```json
{
  "symbol": "BTC-USDT",
  "bid_price": 60000.50,
  "ask_price": 60001.00,
  "bid_size": 1.5,
  "ask_size": 2.0,
  "timestamp": 1700000000.123
}
```

### 4.2 How Data is Normalized

Data normalization ensures consistency across exchanges:

1. **Price Formatting**: Convert all prices to standard decimal format
2. **Size Formatting**: Convert all sizes to standard decimal format
3. **Timestamp Standardization**: Ensure all timestamps are in Unix format
4. **Symbol Standardization**: Validate and standardize symbol formats

### 4.3 How Data is Validated

Data validation includes several checks:

1. **Required Fields**: Verify presence of bid_price, ask_price, bid_size, ask_size, timestamp
2. **Data Types**: Ensure numeric values are valid floats
3. **Price Validation**: Check that prices are positive and reasonable
4. **Size Validation**: Check that sizes are non-negative
5. **Timestamp Validation**: Verify timestamp is recent (not stale)

**Validation Algorithm**:
```
IF bid_price ≤ 0 OR ask_price ≤ 0:
    REJECT data (invalid prices)
    
IF bid_size < 0 OR ask_size < 0:
    REJECT data (invalid sizes)
    
IF timestamp < (current_time - MAX_AGE):
    REJECT data (stale data)
    
IF NOT isinstance(bid_price, (int, float)):
    REJECT data (invalid type)
```

### 4.4 How Stale Data is Handled

Stale data handling mechanisms:

1. **Age Checking**: Compare data timestamp with current time
2. **Maximum Age Threshold**: Default 30 seconds for stale data detection
3. **Exclusion from Calculations**: Stale data is excluded from arbitrage and CBBO calculations
4. **Warning Logging**: Log warnings when stale data is detected
5. **Fallback Mechanisms**: Attempt to fetch fresh data when stale data is encountered

## 5. Edge Cases

### 5.1 How to Handle Missing Data from an Exchange

When data is missing from an exchange:

1. **Graceful Degradation**: Continue processing with available data from other exchanges
2. **Warning Logging**: Log warning about missing data
3. **Exclusion**: Exclude the exchange from calculations for that symbol
4. **Retry Logic**: Attempt to re-fetch data after a short delay
5. **User Notification**: Inform user about data availability issues

**Algorithm**:
```
FOR each exchange in target_exchanges:
    TRY:
        data = fetch_market_data(exchange, symbol)
        IF data is valid:
            add_to_valid_data(exchange, data)
        ELSE:
            log_warning("Invalid data from " + exchange)
    EXCEPT ConnectionError:
        log_warning("Connection failed to " + exchange)
        continue  // Skip this exchange
```

### 5.2 How to Handle Stale Prices

Stale price handling:

1. **Timestamp Validation**: Check data freshness using timestamp
2. **Maximum Age Limit**: Default 30-second threshold for stale data
3. **Exclusion**: Exclude stale data from arbitrage calculations
4. **Warning Messages**: Log warnings about stale data
5. **Fallback**: Use cached recent data if available

**Staleness Check**:
```
CURRENT_TIME = get_current_timestamp()
DATA_AGE = CURRENT_TIME - data_timestamp

IF DATA_AGE > MAX_STALENESS_THRESHOLD:
    MARK data as stale
    EXCLUDE from calculations
    LOG warning about stale data
```

### 5.3 How to Handle Exchange Outages

Exchange outage handling:

1. **Connection Error Detection**: Identify connection failures and timeouts
2. **Retry Mechanism**: Implement exponential backoff retry logic
3. **Temporary Exclusion**: Temporarily exclude failed exchanges from monitoring
4. **Status Monitoring**: Continuously monitor exchange status
5. **Recovery**: Automatically resume monitoring when exchange becomes available

**Outage Handling Algorithm**:
```
TRY:
    connect_to_exchange(exchange)
EXCEPT ConnectionError:
    increment_failure_count(exchange)
    IF failure_count[exchange] > MAX_FAILURES:
        temporarily_exclude_exchange(exchange)
        schedule_retry(exchange, exponential_backoff_time)
    ELSE:
        schedule_immediate_retry(exchange)
```

### 5.4 How to Handle Invalid Symbols

Invalid symbol handling:

1. **Symbol Validation**: Validate symbol format using regex patterns
2. **Exchange Verification**: Verify symbol exists on specified exchange
3. **Error Messages**: Provide clear error messages for invalid symbols
4. **Graceful Rejection**: Skip invalid symbols without affecting other operations

**Symbol Validation**:
```
VALID_SYMBOL_PATTERN = r'^[A-Za-z0-9\-_]+$'

FUNCTION validate_symbol(symbol):
    IF NOT regex_match(symbol, VALID_SYMBOL_PATTERN):
        RAISE InvalidSymbolError("Invalid symbol format: " + symbol)
    
    IF symbol NOT IN exchange_available_symbols:
        RAISE InvalidSymbolError("Symbol not available on exchange: " + symbol)
```

## 6. Performance Considerations

### 6.1 Caching Strategy

1. **Market Data Caching**: Cache recent market data to reduce API calls
2. **CBBO Caching**: Cache consolidated views for quick access
3. **Configuration Caching**: Cache user configurations in memory
4. **TTL Management**: Implement time-to-live for cached data

### 6.2 Computational Efficiency

1. **Optimized Comparisons**: Minimize redundant calculations
2. **Early Exit Conditions**: Exit loops early when conditions are met
3. **Batch Processing**: Process multiple symbols efficiently
4. **Memory Management**: Efficiently manage data structures

### 6.3 Network Optimization

1. **Connection Reuse**: Reuse HTTP connections for REST API calls
2. **WebSocket Multiplexing**: Use single WebSocket connections for multiple symbols
3. **Rate Limiting**: Respect API rate limits to avoid throttling
4. **Error Recovery**: Quickly recover from network errors

## 7. Historical Statistics

### 7.1 Arbitrage Opportunity Tracking

The system tracks historical arbitrage opportunities to provide insights:

1. **Opportunity Count**: Total number of detected opportunities
2. **Average Spread**: Average profit percentage across opportunities
3. **Maximum Spread**: Highest profit percentage observed
4. **Symbol Distribution**: Opportunities by trading symbol
5. **Exchange Pair Distribution**: Opportunities by exchange pair

### 7.2 Statistical Analysis

Statistical analysis features include:

1. **Time-based Analysis**: Opportunities over different time periods
2. **Symbol-based Analysis**: Performance metrics for specific symbols
3. **Exchange-based Analysis**: Performance metrics for exchange pairs
4. **Threshold-based Analysis**: Effectiveness of different threshold settings

## Conclusion

This documentation provides a comprehensive overview of the core algorithms and logic used in the GoQuant Trading Bot. The system is designed to be robust, efficient, and capable of handling various edge cases while providing accurate arbitrage detection and market view calculations.