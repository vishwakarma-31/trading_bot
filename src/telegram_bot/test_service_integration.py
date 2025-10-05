"""
Test script for service controller integration with Telegram bot
"""
import sys
import os
import time

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from telegram_bot.bot_handler import TelegramBotHandler

def test_service_controller_integration():
    """Test service controller integration with Telegram bot handler"""
    print("Testing service controller integration with Telegram bot handler...")
    
    # Create required components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    
    # Create bot handler with service controller
    bot_handler = TelegramBotHandler(config, market_fetcher=market_fetcher)
    
    # Check that service controller is initialized
    assert bot_handler.service_controller is not None
    print("  ✅ Service controller initialized in bot handler")
    
    # Check that service controller has access to both services
    assert bot_handler.service_controller.arbitrage_detector is not None
    assert bot_handler.service_controller.market_view_manager is not None
    print("  ✅ Both services are accessible through service controller")
    
    # Test service controller methods
    status = bot_handler.service_controller.get_service_status()
    assert 'arbitrage_service' in status
    assert 'market_view_service' in status
    print("  ✅ Service status reporting works correctly")
    
    print("✅ Service controller integration test passed")
    return True

def run_all_tests():
    """Run all tests for service controller integration"""
    print("GoQuant Trading Bot - Service Controller Integration Test")
    print("=" * 60)
    
    tests = [
        test_service_controller_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"✅ {test.__name__} passed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed: {e}")
    
    print("=" * 60)
    print(f"Test Results: {passed}/{passed + failed} tests passed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"❌ {failed} tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()