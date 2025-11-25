# Trading Bot UI

This directory contains the Streamlit-based web interface for the Generic Trading Bot.

## Features

- Real-time market data visualization
- Arbitrage opportunity detection
- Consolidated market view (CBBO)
- Configuration management
- Interactive dashboards with charts and metrics

## Requirements

The UI requires the following additional dependencies:
- streamlit==1.40.0
- plotly==6.0.0
- pandas==2.2.0

These are included in the updated requirements.txt file.

## Running the UI

### Windows
```bash
ui\run_ui.bat
```

### Linux/Mac
```bash
cd ui
python -m streamlit run trading_bot_ui.py
```

## UI Pages

1. **Overview** - System status and recent opportunities
2. **Market Data** - Real-time market data from exchanges
3. **Arbitrage Detection** - Find and visualize arbitrage opportunities
4. **Market View** - Consolidated market view across exchanges
5. **Settings** - Configuration management

## Architecture

The UI integrates directly with the core trading bot modules:
- Uses the same configuration manager
- Accesses market data through the fetcher
- Utilizes arbitrage detection logic
- Leverages market view functionality

All data processing happens in real-time through the existing bot infrastructure.