# Generic Trading Bot

A trading information system using CCXT library to fetch real market data from public exchanges with a Telegram bot interface for arbitrage detection and market view services.

## System Overview

This system provides two main services:
1. **Arbitrage Signal Service** - Detects price differences across exchanges for potential profit opportunities
2. **Consolidated Market View Service** - Provides a unified view of market data across multiple exchanges

## Technology Stack

- Language: Python 3.8+
- Telegram Bot API (using python-telegram-bot library v22.5)
- CCXT Library for exchange data fetching
- REST API polling for market data acquisition
- Supported exchanges: Binance SPOT, OKX SPOT

## Quick Start

### Option 1: Full Functionality

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

### Option 2: With Mock Data (No API Required)

You can run the system with simulated market data:

1. Create a Python virtual environment (if not already done):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install required dependencies (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the mock version:
   ```bash
   python src/main_mock.py
   ```
   
   Or on Windows:
   ```bash
   run_mock.bat
   ```

For detailed instructions, see [Setup Guide](docs/setup_deployment_guide.md)

## Project Structure

```
src/
├── application/      # Application controller and main loop
├── config/           # Configuration management
├── data_acquisition/ # Market data fetching using CCXT
├── data_processing/  # Arbitrage detection and market view calculations
├── telegram_bot/     # Telegram bot interface
├── logging_module/   # Logging utilities
└── utils/            # Utility functions
```

## Telegram Bot Commands

### Basic Commands
- `/start` - Welcome message and bot introduction
- `/help` - Show available commands
- `/status` - Check bot status
- `/list_symbols <exchange> <market_type>` - List available symbols for an exchange
- `/menu` - Open interactive menu
- `/alerts` - Manage alert settings
- `/config` - Manage user configuration

### Arbitrage Signal Service
- `/monitor_arb <asset1_on_exchangeA> <asset2_on_exchangeB> <threshold>` - Start monitoring arbitrage
- `/stop_arb` - Stop arbitrage monitoring
- `/config_arb` - Configure arbitrage settings
- `/status_arb` - Show arbitrage monitoring status
- `/threshold <percent> <absolute>` - Set arbitrage thresholds
- `/arbitrage` - Get current arbitrage opportunities
- `/arb_stats` - Show overall statistics
- `/arb_stats <symbol>` - Show statistics for specific symbol

### Consolidated Market View Service
- `/view_market <symbol> <exchange1> <exchange2> ...` - Start market view monitoring
- `/stop_market` - Stop market view monitoring
- `/get_cbbo <symbol>` - Query current CBBO on demand
- `/config_market` - Configure market view settings
- `/status_market` - Show market view status

For complete command reference, see [User Guide](docs/telegram_bot_user_guide.md)

## Documentation

- [System Architecture](docs/system_architecture.md) - System design and component interactions
- [Logic and Algorithms](docs/logic_algorithms.md) - Core algorithms for arbitrage detection and market analysis
- [Setup and Deployment Guide](docs/setup_deployment_guide.md) - Installation and configuration instructions
- [Telegram Bot User Guide](docs/telegram_bot_user_guide.md) - Complete guide to bot features and usage

## Configuration

Configure your Telegram bot token in the `.env` file.

Example `.env`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
MIN_PROFIT_PERCENTAGE=0.5
MIN_PROFIT_ABSOLUTE=1.0
BINANCE_ENABLED=true
OKX_ENABLED=true
```

For detailed configuration instructions, see [Setup Guide](docs/setup_deployment_guide.md)

## Supported Exchanges

- Binance SPOT
- OKX SPOT

## Features

### Arbitrage Signal Service
- Cross-exchange price comparison
- Configurable profit thresholds
- Real-time opportunity detection
- Telegram alerts for opportunities
- Multi-asset monitoring capability
- Service start/stop controls
- Historical statistics tracking

### Consolidated Market View Service
- Unified market data display
- Best Bid/Offer (CBBO) calculation
- Venue signaling for optimal trading
- Periodic market updates
- On-demand market queries
- Multi-exchange data aggregation

## Exchange Integration

The system connects to public exchanges using the CCXT library to obtain real-time L1 market data (BBO, last trade price) and L2 order book data. Symbol discovery is performed using the exchange's public API.