# GoQuant Trading Bot Setup and Deployment Guide

This guide provides step-by-step instructions for setting up, configuring, and deploying the GoQuant Trading Bot. Follow these instructions to get your bot running locally or deploy it to a production server.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration Steps](#configuration-steps)
4. [Running the Application](#running-the-application)
5. [Deployment Considerations](#deployment-considerations)

## Prerequisites

### Python Version Required

The GoQuant Trading Bot requires Python 3.8 or higher. Verify your Python version:

```bash
python --version
```

or

```bash
python3 --version
```

If you don't have Python installed or need to upgrade, download it from [python.org](https://www.python.org/downloads/).

### Operating System Requirements

The bot is compatible with:

- **Windows 10/11** (64-bit)
- **Linux** (Ubuntu 20.04+, CentOS 8+, or equivalent)
- **macOS** (10.15+)

### Required API Keys

Before installing the bot, you'll need to obtain the following API keys:

1. **Telegram Bot Token**
   - Create a Telegram bot using BotFather
   - See [Configuration Steps](#configuration-steps) for detailed instructions

2. **GoMarket API Key**
   - Access code: 2194
   - Contact GoMarket support to obtain your API key

## Installation Steps

### 1. Clone/Download Code

Clone the repository using Git:

```bash
git clone <repository-url>
cd trading_bot
```

Or download and extract the ZIP archive to your desired location.

### 2. Set Up Virtual Environment

Using a virtual environment isolates the bot's dependencies from other Python projects.

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

Alternatively, you can use the provided batch scripts:

- `setup_env.bat` - Automatically sets up the virtual environment and installs dependencies
- `run_bot.bat` - Runs the bot (requires the virtual environment to be set up first)

### 3. Install Dependencies

With the virtual environment activated, install the required dependencies:

```bash
pip install -r requirements.txt
```

The required dependencies are:
- python-telegram-bot==13.15
- requests==2.31.0
- websocket-client==1.6.1
- aiohttp==3.8.5
- asyncio-mqtt==0.11.0
- asyncio==3.4.3
- websockets==10.3

### 4. Configure API Keys and Tokens

Create a `.env` file based on the example:

**On Linux/macOS:**
```bash
cp .env.example .env
```

**On Windows:**
```cmd
copy .env.example .env
```

Edit the `.env` file with your actual API keys (see [Configuration Steps](#configuration-steps)).

## Configuration Steps

### 1. Create Telegram Bot with BotFather

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Start a chat with BotFather and send `/newbot`
3. Follow the prompts to:
   - Choose a name for your bot (e.g., "GoQuant Trading Bot")
   - Choose a username for your bot (must end in "bot", e.g., "goquant_trading_bot")
4. BotFather will provide you with a token that looks like: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
5. Copy this token for use in your `.env` file

### 2. Obtain GoMarket API Access

Contact GoMarket support with access code 2194 to obtain your API key. They will provide you with a key that looks like: `gomarket_api_key_xxxxxxxxxxxxxxxx`

### 3. Configure Bot Settings in Code

Edit the `.env` file in the root directory with your API keys:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# GoMarket API Configuration
GOMARKET_API_KEY=your_gomarket_api_key_here

# Arbitrage Detection Thresholds
MIN_PROFIT_PERCENTAGE=0.5
MIN_PROFIT_ABSOLUTE=1.0

# Supported Exchanges
EXCHANGES=binance,okx,bybit,deribit
```

Replace the placeholder values with your actual API keys and adjust thresholds as needed.

### 4. Set Up Log File Locations

Logs are automatically stored in the `logs/` directory which is created when the bot starts. The logging system creates two types of log files:

1. **General logs**: `logs/trading_bot_YYYYMMDD.log` - Contains all application logs
2. **Error logs**: `logs/errors_YYYYMMDD.log` - Contains only error-level logs

Log files are rotated when they reach 10MB, with up to 5 backup files retained.

## Running the Application

### Command to Start the Bot

With your virtual environment activated:

```bash
python src/main.py
```

Or on Windows, you can use the provided batch script:

```cmd
run_bot.bat
```

### How to Verify It's Running

1. **Console Output**: You should see initialization messages in the console:
   ```
   Initializing GoQuant Trading Bot...
   Configuration loaded
   Logging system initialized
   ...
   Telegram bot started
   Entering main application loop
   ```

2. **Telegram Bot**: Interact with your bot in Telegram:
   - Send `/start` to receive a welcome message
   - Send `/status` to check the bot's status

3. **Log Files**: Check the log files in the `logs/` directory for detailed information.

### How to Monitor Logs

Monitor logs in real-time:

**On Linux/macOS:**
```bash
tail -f logs/trading_bot_*.log
```

**On Windows (PowerShell):**
```powershell
Get-Content logs\trading_bot_*.log -Wait
```

You can also check specific log files:
```bash
cat logs/trading_bot_$(date +%Y%m%d).log
```

### How to Stop the Bot

1. **Graceful Shutdown**: Press `Ctrl+C` in the terminal where the bot is running
2. **Force Kill** (if necessary):
   - On Linux/macOS: `kill -TERM <process_id>`
   - On Windows: `taskkill /PID <process_id> /F`

The bot handles SIGINT and SIGTERM signals gracefully, ensuring all services are properly shut down.

## Deployment Considerations

### Running on a Server (Linux)

For production deployment on a Linux server:

1. Ensure Python 3.8+ is installed:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. Create a dedicated user for the bot:
   ```bash
   sudo useradd -r -s /bin/false tradingbot
   sudo mkdir /opt/trading_bot
   sudo chown tradingbot:tradingbot /opt/trading_bot
   ```

3. Set up the application as described in [Installation Steps](#installation-steps)

### Running as a Background Service

Create a systemd service file at `/etc/systemd/system/tradingbot.service`:

```ini
[Unit]
Description=GoQuant Trading Bot
After=network.target

[Service]
Type=simple
User=tradingbot
WorkingDirectory=/opt/trading_bot
ExecStart=/opt/trading_bot/venv/bin/python src/main.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tradingbot.service
sudo systemctl start tradingbot.service
```

Check the service status:
```bash
sudo systemctl status tradingbot.service
```

View logs:
```bash
sudo journalctl -u tradingbot.service -f
```

### Monitoring and Maintenance

1. **Health Checks**: Regularly check the bot status through Telegram using `/status`
2. **Log Monitoring**: Set up log rotation and monitoring for errors
3. **Resource Monitoring**: Monitor CPU and memory usage
4. **API Quotas**: Monitor GoMarket API usage to ensure you're within limits
5. **Network Connectivity**: Ensure stable internet connection for real-time data

### Backup and Recovery

1. **Configuration Backup**: Regularly backup your `.env` file (store securely)
2. **Code Backup**: Maintain version control of your codebase
3. **Log Archival**: Archive old log files for historical analysis
4. **Recovery Procedure**:
   - Restore `.env` file with API keys
   - Reinstall dependencies using `requirements.txt`
   - Restart the bot service

### Security Considerations

1. **API Key Protection**: Never commit API keys to version control
2. **File Permissions**: Restrict access to `.env` file:
   ```bash
   chmod 600 .env
   ```
3. **Network Security**: Use firewalls to restrict unnecessary access
4. **Regular Updates**: Keep dependencies updated for security patches

---

This concludes the setup and deployment guide for the GoQuant Trading Bot. For usage instructions, refer to the [Telegram Bot User Guide](telegram_bot_user_guide.md).