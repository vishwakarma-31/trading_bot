# Alerting System

The GoQuant Trading Bot includes a comprehensive alerting system that sends formatted notifications to Telegram for both arbitrage opportunities and market view updates.

## Alert Types

### Arbitrage Alerts
Sent immediately when arbitrage opportunities are detected, with the following format:

```
🔔 ARBITRAGE OPPORTUNITY DETECTED

Asset: BTC-USDT
Exchange A: Binance @ $60,000.00
Exchange B: OKX @ $60,150.00
Spread: $150.00 (0.25%)
Threshold: 0.20%
Time: 2025-10-05 14:30:15 UTC
```

### Market View Alerts
Sent periodically for market view updates, with the following format:

```
📊 MARKET VIEW UPDATE

Symbol: BTC-USDT
Best Bid: Kraken @ $60,000.50
Best Offer: Bybit @ $60,001.00
CBBO Mid: $60,000.75
Time: 2025-10-05 14:30:15 UTC
```

## Alert Manager

The AlertManager class handles all alert functionality:

### Key Features
- **Formatted Alerts**: Professional, structured message formatting
- **Subscriber Management**: Track which chats should receive alerts
- **Message Tracking**: Track sent messages for editing/updating
- **Rate Limiting**: Prevent spam and respect Telegram API limits
- **Error Handling**: Robust error handling with retry logic
- **Alert History**: Maintain history of recent alerts

### Methods
- `add_subscriber(chat_id)`: Add a chat to receive alerts
- `remove_subscriber(chat_id)`: Remove a chat from alerts
- `send_arbitrage_alert(opportunity)`: Send arbitrage alert to all subscribers
- `send_market_view_alert(market_view)`: Send market view alert to all subscribers
- `update_arbitrage_alert(opportunity)`: Update existing arbitrage alert
- `update_market_view_alert(market_view)`: Update existing market view alert
- `format_arbitrage_alert(opportunity)`: Format arbitrage opportunity as alert message
- `format_market_view_alert(market_view)`: Format market view as alert message

## Alert Triggering Logic

### Arbitrage Alerts
- **Immediate Sending**: Alerts are sent immediately when opportunities are detected
- **Deduplication**: Prevent duplicate alerts for the same opportunity
- **Continuous Monitoring**: Ongoing monitoring during active sessions

### Market View Alerts
- **Periodic Sending**: Alerts sent at configurable intervals (default: 30 seconds)
- **Significant Changes**: Alerts can be triggered on significant market movements
- **Configurable Frequency**: Users can adjust update frequency

## Message Management

### Message Tracking
- **Message IDs**: Track sent message IDs for editing
- **Update Capability**: Edit existing messages with updated information
- **History Management**: Maintain alert history with size limits

### Rate Limiting
- **Frequency Control**: Limit message frequency to prevent spam
- **Telegram API Compliance**: Handle rate limits imposed by Telegram
- **Backoff Logic**: Implement retry logic with exponential backoff

## Error Handling

### Message Sending Failures
- **Retry Logic**: Automatic retry attempts for failed sends
- **Error Logging**: Comprehensive error logging for debugging
- **Graceful Degradation**: Continue functioning even when some sends fail

### Message Editing Failures
- **Age Handling**: Handle "message too old" errors gracefully
- **Fallback Strategy**: Send new messages when editing fails
- **Error Recovery**: Automatic recovery from common editing errors

## Configuration

### Alert Settings
Access alert configuration through the `/alerts` command or the interactive menu:

- **Enable/Disable Alerts**: Toggle alert reception for individual chats
- **Alert History**: View recent alerts sent to your chat
- **Customization**: Future support for alert customization

### Update Intervals
Configure market view update intervals:
- **30 seconds**: Frequent updates (default)
- **60 seconds**: Moderate updates
- **120 seconds**: Infrequent updates

## Integration with Services

### Arbitrage Service Integration
- **Opportunity Detection**: Automatic alerts when opportunities exceed thresholds
- **Real-time Updates**: Live updating of opportunity information
- **Threshold-Based**: Alerts only sent when meeting configured thresholds

### Market View Service Integration
- **CBBO Updates**: Regular updates of consolidated best bid/offer
- **Venue Signaling**: Clear indication of best venues for trading
- **Timestamp Tracking**: Accurate timing information for all updates

## Implementation Details

### Alert Formatting
```python
def format_arbitrage_alert(self, opportunity: ArbitrageOpportunity) -> str:
    """Format arbitrage opportunity as an alert message"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(opportunity.timestamp))
    
    alert_message = f"""
🔔 *ARBITRAGE OPPORTUNITY DETECTED*

Asset: {opportunity.symbol}
Exchange A: {opportunity.buy_exchange.upper()} @ ${opportunity.buy_price:,.2f}
Exchange B: {opportunity.sell_exchange.upper()} @ ${opportunity.sell_price:,.2f}
Spread: ${opportunity.profit_absolute:,.2f} ({opportunity.profit_percentage:.2f}%)
Threshold: {opportunity.threshold_percentage:.2f}%
Time: {timestamp}
"""
    return alert_message.strip()
```

### Message Sending with Rate Limiting
```python
def _rate_limit_check(self):
    """Check and enforce rate limiting"""
    current_time = time.time()
    time_since_last = current_time - self.last_message_time
    
    if time_since_last < self.rate_limit_delay:
        sleep_time = self.rate_limit_delay - time_since_last
        time.sleep(sleep_time)
        
    self.last_message_time = time.time()
```

### Error Handling
```python
def _send_message_to_subscribers(self, message: str, parse_mode: str = 'Markdown') -> Dict[int, int]:
    """Send message to all subscribers with error handling"""
    sent_messages = {}
    
    for chat_id in self.subscribers:
        try:
            self._rate_limit_check()
            msg = self.bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
            sent_messages[chat_id] = msg.message_id
        except TelegramError as e:
            self.logger.error(f"Failed to send message to {chat_id}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error sending message to {chat_id}: {e}")
            
    return sent_messages
```

## Best Practices

### Performance Considerations
- **Efficient Formatting**: Pre-format messages to minimize processing time
- **Caching**: Cache formatted messages when possible
- **Asynchronous Operations**: Non-blocking message sending where possible
- **Resource Cleanup**: Remove stale tracking information

### User Experience
- **Clear Formatting**: Easy-to-read message formatting with emojis
- **Consistent Structure**: Standardized message structure across all alerts
- **Relevant Information**: Include all necessary information without clutter
- **Timely Updates**: Provide current information with accurate timestamps

### Reliability
- **Error Recovery**: Automatic recovery from common failure scenarios
- **Logging**: Comprehensive logging for debugging and monitoring
- **Validation**: Validate all inputs before processing
- **Fallbacks**: Provide fallback options when primary methods fail

## Future Enhancements

### Planned Features
- **Custom Alert Conditions**: User-defined alert triggers
- **Advanced Filtering**: More sophisticated alert filtering options
- **Multiple Alert Types**: Additional alert categories and formats
- **Integration with External Services**: Webhook support for other alerting systems

### Technical Improvements
- **Enhanced Deduplication**: More intelligent duplicate detection
- **Improved Rate Limiting**: Dynamic rate limiting based on API responses
- **Extended Error Handling**: More comprehensive error recovery
- **Better State Management**: Enhanced tracking of alert states