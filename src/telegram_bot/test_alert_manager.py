"""
Test script for the Alert Manager
"""
import sys
import os
import time
from datetime import datetime

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from telegram_bot.alert_manager import AlertManager
from data_processing.arbitrage_detector import ArbitrageOpportunity
from data_processing.market_view import ConsolidatedMarketView

def test_alert_formatting(alert_manager: AlertManager):
    """Test alert formatting functionality"""
    print("Testing alert formatting...")
    
    # Test arbitrage alert formatting
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
    
    formatted_alert = alert_manager.format_arbitrage_alert(opportunity)
    print("Arbitrage alert format:")
    print(formatted_alert)
    print()
    
    # Test market view alert formatting
    market_view = ConsolidatedMarketView(
        symbol="BTC-USDT",
        exchanges_data={},
        cbbo_bid_exchange="kraken",
        cbbo_ask_exchange="bybit",
        cbbo_bid_price=60000.50,
        cbbo_ask_price=60001.00,
        timestamp=time.time()
    )
    
    formatted_market_alert = alert_manager.format_market_view_alert(market_view)
    print("Market view alert format:")
    print(formatted_market_alert)
    print()
    
    return True

def test_subscriber_management(alert_manager: AlertManager):
    """Test subscriber management functionality"""
    print("Testing subscriber management...")
    
    # Add subscribers
    alert_manager.add_subscriber(123456789)
    alert_manager.add_subscriber(987654321)
    
    subscribers = alert_manager.get_subscribers()
    print(f"Subscribers: {subscribers}")
    
    # Remove subscriber
    alert_manager.remove_subscriber(123456789)
    subscribers = alert_manager.get_subscribers()
    print(f"Subscribers after removal: {subscribers}")
    
    # Cleanup
    alert_manager.remove_subscriber(987654321)
    
    return True

def test_alert_history(alert_manager: AlertManager):
    """Test alert history functionality"""
    print("Testing alert history...")
    
    # Add some alerts to history
    alert_manager.alert_history = [
        {'type': 'arbitrage', 'message': 'Test arbitrage alert', 'timestamp': time.time()},
        {'type': 'market_view', 'message': 'Test market view alert', 'timestamp': time.time()}
    ]
    
    history = alert_manager.get_alert_history()
    print(f"Alert history ({len(history)} items):")
    for item in history:
        print(f"  - {item['type']}: {item['message'][:30]}...")
        
    # Clear history
    alert_manager.clear_alert_history()
    history = alert_manager.get_alert_history()
    print(f"Alert history after clearing: {len(history)} items")
    
    return True

def main():
    """Main test function"""
    print("GoQuant Trading Bot - Alert Manager Test")
    print("=" * 40)
    
    # Initialize alert manager (we won't actually send messages in this test)
    alert_manager = AlertManager("dummy_token")
    
    # Run tests
    tests = [
        ("Alert Formatting", test_alert_formatting, alert_manager),
        ("Subscriber Management", test_subscriber_management, alert_manager),
        ("Alert History", test_alert_history, alert_manager)
    ]
    
    passed = 0
    total = 0
    
    for test_info in tests:
        test_name = test_info[0]
        test_func = test_info[1]
        args = test_info[2:]
        
        total += 1
        try:
            if test_func(*args):
                passed += 1
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())