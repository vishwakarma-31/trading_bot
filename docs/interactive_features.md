# Interactive Features

The GoQuant Trading Bot includes comprehensive interactive features using Telegram's inline keyboards and message editing capabilities.

## Interactive Menus

### Main Menu
Access the main menu with the `/menu` command. This provides intuitive navigation to all bot features:

- **Arbitrage Service**: Access arbitrage monitoring and configuration
- **Market View Service**: Access market view monitoring and configuration
- **General Settings**: Configure general bot preferences
- **Status**: View overall bot status

### Arbitrage Configuration Menu
Configure arbitrage detection settings:

- **Set Percentage Threshold**: Set minimum profit percentage threshold
- **Set Absolute Threshold**: Set minimum profit in absolute USD value
- **Exchange Selection**: Select exchanges to monitor
- **Symbol Selection**: Select symbols to monitor

### Market View Configuration Menu
Configure market view settings:

- **Refresh Interval**: Set how frequently to update market data
- **Exchange Selection**: Select exchanges for market view
- **Symbol Selection**: Select symbols for market view

## Interactive Buttons

### Configuration Buttons
- **Threshold Selection**: Quick-set common threshold values (0.5%, 1.0%, 1.5%, 2.0%)
- **Refresh Interval**: Quick-set market view refresh intervals (1s, 5s, 10s)
- **Exchange Selection**: Toggle exchanges for monitoring
- **Symbol Selection**: Choose symbols from available options

### Navigation Buttons
- **Refresh**: Update displayed information with latest data
- **Back**: Navigate to previous menu
- **Done**: Confirm selections and return to main menu
- **Stop Monitoring**: Immediately stop active monitoring services

### Action Buttons
- **Start Monitoring**: Begin monitoring with current configuration
- **View Opportunities**: Display current arbitrage opportunities
- **View CBBO**: Display current Consolidated Best Bid/Offer
- **Status Check**: View service status information

## Message Editing for Live Updates

### Arbitrage Alerts
Arbitrage opportunity messages are automatically updated with the latest information:

- **Real-time profit calculations**: Updated profit percentages and absolute values
- **Duration tracking**: Live updating of opportunity duration
- **Price updates**: Current buy/sell prices on respective exchanges
- **Timestamp updates**: Last update time for each opportunity

### Market View Updates
Market view messages provide live CBBO updates:

- **Best bid/ask prices**: Real-time updates from all monitored exchanges
- **Spread calculations**: Live updating of price spreads
- **Exchange information**: Which exchange has the best bid/ask
- **Timestamp updates**: Last update time for market data

### Status Updates
Status messages can be refreshed to show current bot state:

- **Service status**: Active/inactive indicators for all services
- **Monitoring information**: Currently monitored symbols and exchanges
- **Performance metrics**: Opportunity counts and data point statistics
- **Timestamp updates**: Last refresh time

## User Flow Design

### Intuitive Navigation
1. **Main Menu**: Central hub for all bot features
2. **Service Menus**: Dedicated menus for arbitrage and market view services
3. **Configuration Menus**: Detailed settings for each service
4. **Action Confirmation**: Clear feedback for all user actions

### Clear Action Confirmations
- **Visual feedback**: Button presses provide immediate acknowledgment
- **Status messages**: Clear indication of successful/failed actions
- **Error handling**: User-friendly error messages with resolution guidance
- **Progress indicators**: Loading states for long-running operations

### Easy Monitoring Controls
- **One-touch start/stop**: Simple buttons to begin/end monitoring
- **Live status updates**: Real-time monitoring status information
- **Quick configuration**: Fast access to common settings
- **Detailed views**: Comprehensive information displays when needed

## Callback Query Handlers

### Button Press Handling
- **Data routing**: Callback data directs to appropriate handlers
- **State management**: Track user interaction states for multi-step processes
- **Error recovery**: Graceful handling of unexpected button presses
- **Performance optimization**: Efficient processing of callback queries

### Configuration Updates
- **Real-time updates**: Configuration changes take effect immediately
- **Validation**: Input validation with clear error messages
- **Persistence**: Settings maintained across sessions
- **Feedback**: Confirmation of successful configuration updates

### Message Management
- **Dynamic editing**: Messages updated in-place without spamming chat
- **Selective updates**: Only relevant information is refreshed
- **Cleanup**: Automatic removal of stale interactive messages
- **Organization**: Related messages grouped logically

## Implementation Details

### Inline Keyboard Implementation
```python
# Example of creating interactive buttons
keyboard = [
    [InlineKeyboardButton("Set Threshold: 1.0%", callback_data='arb_threshold_1.0')],
    [InlineKeyboardButton("Refresh Interval: 5s", callback_data='market_refresh_5')],
    [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
]
reply_markup = InlineKeyboardMarkup(keyboard)
```

### Message Editing
```python
# Example of editing messages for live updates
query.edit_message_text(
    text=f"✅ Arbitrage threshold set to {threshold}%",
    reply_markup=reply_markup
)
```

### User State Management
```python
# Example of tracking user interaction states
self.user_states[chat_id] = {
    'state': 'waiting_threshold_percent',
    'timestamp': time.time()
}
```

## Best Practices

### Performance Considerations
- **Efficient callbacks**: Minimize processing time for button presses
- **Message caching**: Cache frequently accessed data
- **Rate limiting**: Prevent excessive API calls
- **Resource cleanup**: Remove stale data and messages

### User Experience
- **Consistent navigation**: Similar patterns across all menus
- **Clear labeling**: Descriptive button text and menu titles
- **Progressive disclosure**: Reveal complexity as needed
- **Error prevention**: Validate inputs before processing

### Error Handling
- **Graceful degradation**: Continue functioning even when services are unavailable
- **User guidance**: Provide clear next steps when errors occur
- **Logging**: Track errors for debugging and improvement
- **Recovery options**: Offer paths to resolve common issues

## Future Enhancements

### Planned Features
- **Advanced filtering**: More sophisticated arbitrage opportunity filtering
- **Historical data**: Access to historical arbitrage and market data
- **Custom alerts**: User-defined alert conditions and notifications
- **Portfolio tracking**: Integration with user trading portfolio data

### Technical Improvements
- **Asynchronous updates**: Non-blocking message updates
- **Enhanced caching**: More intelligent data caching strategies
- **Extended validation**: More comprehensive input validation
- **Improved state management**: More robust user state tracking