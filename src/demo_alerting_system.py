"""
Demo script for the Alerting System
This script demonstrates the alerting capabilities of the Telegram bot.
"""
import sys
import os
import time
import logging

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from telegram_bot.alert_manager import AlertManager
from data_processing.arbitrage_detector import ArbitrageOpportunity
from data_processing.market_view import ConsolidatedMarketView

def demo_alert_formatting():
    """Demonstrate alert formatting"""
    print("GoQuant Trading Bot - Alerting System Demo")
    print("=" * 45)
    
    print("\n1. Alert Formatting Examples")
    print("-" * 30)
    
    # Create sample arbitrage opportunity
    opportunity = ArbitrageOpportunity(
        symbol="BTC-USDT",
        buy_exchange="binance",
        sell_exchange="okx",
        buy_price=60000.00,
        sell_price=60150.00,
        profit_percentage=0.25,
        profit_absolute=150.00,
        timestamp=time.time(),
        threshold_percentage=0.20,
        threshold_absolute=100.00
    )
    
    # Create sample market view
    market_view = ConsolidatedMarketView(
        symbol="BTC-USDT",
        exchanges_data={},
        cbbo_bid_exchange="kraken",
        cbbo_ask_exchange="bybit",
        cbbo_bid_price=60000.50,
        cbbo_ask_price=60001.00,
        timestamp=time.time()
    )
    
    # Initialize alert manager (with dummy token for demo)
    alert_manager = AlertManager("dummy_token")
    
    # Format and display arbitrage alert
    print("🔔 Arbitrage Alert Format:")
    arbitrage_alert = alert_manager.format_arbitrage_alert(opportunity)
    print(arbitrage_alert)
    print()
    
    # Format and display market view alert
    print("📊 Market View Alert Format:")
    market_alert = alert_manager.format_market_view_alert(market_view)
    print(market_alert)
    print()

def demo_alert_features():
    """Demonstrate alert features"""
    print("2. Alert System Features")
    print("-" * 25)
    
    features = [
        "✅ Formatted notifications with clear, structured information",
        "✅ Real-time updates with message editing capabilities",
        "✅ Configurable alert frequency and conditions",
        "✅ Subscriber management for targeted notifications",
        "✅ Rate limiting to prevent spam",
        "✅ Error handling with retry logic",
        "✅ Alert history tracking",
        "✅ Duplicate alert prevention"
    ]
    
    for feature in features:
        print(feature)
    print()

def demo_alert_commands():
    """Demonstrate alert commands"""
    print("3. Telegram Alert Commands")
    print("-" * 27)
    
    commands = [
        "/alerts - Manage alert settings",
        "  └── Enable/Disable alerts for your chat",
        "  └── View alert history",
        "",
        "/monitor_arb - Start arbitrage monitoring",
        "  └── Automatically sends alerts when opportunities are detected",
        "",
        "/view_market - Start market view monitoring", 
        "  └── Sends periodic market updates",
        "",
        "Interactive Menu:",
        "  └── Access via /menu",
        "  └── Navigate to 'Alert Settings'",
        "  └── Toggle alerts on/off",
        "  └── View recent alert history"
    ]
    
    for command in commands:
        print(command)
    print()

def demo_alert_workflow():
    """Demonstrate alert workflow"""
    print("4. Alert Workflow")
    print("-" * 18)
    
    workflow = [
        "1. User starts monitoring with /monitor_arb or /view_market",
        "2. Bot adds user to alert subscribers list",
        "3. When opportunities are detected, alerts are formatted",
        "4. Alerts are sent to all subscribers",
        "5. Messages are tracked for potential updates",
        "6. Users can toggle alerts on/off with /alerts",
        "7. Rate limiting prevents spam and API abuse",
        "8. Error handling ensures reliability"
    ]
    
    for step in workflow:
        print(step)
    print()

def main():
    """Main demo function"""
    demo_alert_formatting()
    demo_alert_features()
    demo_alert_commands()
    demo_alert_workflow()
    
    print("=" * 45)
    print("The alerting system is now ready to use!")
    print("\nTo experience the alerting system:")
    print("1. Configure your Telegram bot token in .env")
    print("2. Run 'python src/main.py' to start the bot")
    print("3. Open Telegram and interact with your bot:")
    print("   📋 Essential Commands:")
    print("   /start     - Initialize bot and enable alerts")
    print("   /alerts    - Manage alert settings")
    print("   /monitor_arb - Start arbitrage monitoring")
    print("   /view_market - Start market view monitoring")
    print("\n🔔 You will receive formatted alerts when:")
    print("   • Arbitrage opportunities exceed your thresholds")
    print("   • Market view data is updated periodically")
    print("   • Significant market changes occur")

if __name__ == "__main__":
    main()