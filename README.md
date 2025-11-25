# Generic Trading Bot

A comprehensive trading bot that monitors arbitrage opportunities and market views across multiple cryptocurrency exchanges.

## Features

- Real-time arbitrage detection across Binance, OKX, Bybit, and Deribit
- Consolidated market view (CBBO) monitoring
- Telegram bot integration for alerts and interactive commands
- Configurable thresholds and monitoring settings
- Historical statistics tracking

## Prerequisites

1. Python 3.8 or higher
2. A Telegram account
3. API keys for the exchanges you want to monitor

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd trading_bot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your configuration:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your actual values.

## Telegram Bot Setup

1. Open Telegram and talk to [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions to create a new bot
3. Copy the provided token
4. Update the `TELEGRAM_BOT_TOKEN` in your `.env` file with this token

## Configuration

Edit the `.env` file to configure:

- Telegram bot token
- Arbitrage detection thresholds
- Exchange configurations
- API keys for exchanges

## Running the Bot

```bash
python src/main.py
```

## Telegram Commands

Once the bot is running and you've started a conversation with it in Telegram:

- `/start` - Welcome message and introduction
- `/help` - List all available commands
- `/status` - Check bot status
- `/list_symbols <exchange> <market_type>` - List available symbols
- `/menu` - Open interactive menu
- `/alerts` - Manage alert settings
- `/config` - Manage user configuration

### Arbitrage Service Commands

- `/monitor_arb <asset1_on_exchangeA> <asset2_on_exchangeB> <threshold>` - Start monitoring arbitrage
- `/stop_arb` - Stop arbitrage monitoring
- `/config_arb` - Configure arbitrage settings
- `/status_arb` - Show current arbitrage monitoring status
- `/threshold` - Get current arbitrage thresholds
- `/threshold <percent> <absolute>` - Set arbitrage thresholds
- `/arbitrage` - Get current arbitrage opportunities
- `/arb_stats` - Show overall statistics
- `/arb_stats <symbol>` - Show statistics for specific symbol

### Market View Commands

- `/view_market <symbol> <exchange1> <exchange2> ...` - Start market view monitoring
- `/stop_market` - Stop market view monitoring
- `/get_cbbo <symbol>` - Query current CBBO on demand
- `/config_market` - Configure market view settings
- `/status_market` - Show current market view status

## Supported Exchanges

- Binance
- OKX
- Bybit
- Deribit

## Data Storage

The bot stores data in:
- `data/arbitrage_opportunities.db` - SQLite database with arbitrage opportunities
- `persistence_data.json` - Service monitoring states
- `user_config.json` - User configurations

## License

This project is licensed under the MIT License.