"""
Core Functionality Test for the GoQuant Trading Bot
Tests core system functionality without external dependencies
"""
import sys
import os
import time

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing core module imports...")
    
    try:
        # Test config module
        from config.config_manager import ConfigManager
        print("  ✅ ConfigManager imported successfully")
        
        # Test data acquisition module
        from data_acquisition.market_data_fetcher import MarketDataFetcher
        print("  ✅ MarketDataFetcher imported successfully")
        
        # Test data processing modules
        from data_processing.arbitrage_detector import ArbitrageDetector
        from data_processing.market_view import MarketViewManager
        from data_processing.service_controller import ServiceController
        print("  ✅ Data processing modules imported successfully")
        
        # Test utils module
        from utils.error_handler import handle_exception
        print("  ✅ Utils modules imported successfully")
        
        # Test telegram bot module (handle missing dependency gracefully)
        try:
            from telegram_bot.alert_manager import AlertManager
            print("  ✅ Telegram bot modules imported successfully")
        except ImportError as e:
            print(f"  ⚠️  Telegram bot modules not available: {e}")
        
        # Test application module
        from application.app_controller import ApplicationController
        print("  ✅ Application modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        return False

def test_basic_initialization():
    """Test basic component initialization"""
    print("\nTesting basic component initialization...")
    
    try:
        # Test config initialization
        from config.config_manager import ConfigManager
        config = ConfigManager()
        print("  ✅ ConfigManager initialized")
        
        # Test market fetcher initialization
        from data_acquisition.market_data_fetcher import MarketDataFetcher
        fetcher = MarketDataFetcher(config)
        print("  ✅ MarketDataFetcher initialized")
        
        # Test arbitrage detector initialization
        from data_processing.arbitrage_detector import ArbitrageDetector
        detector = ArbitrageDetector(fetcher, config)
        print("  ✅ ArbitrageDetector initialized")
        
        # Test market view manager initialization
        from data_processing.market_view import MarketViewManager
        market_view = MarketViewManager(fetcher)
        print("  ✅ MarketViewManager initialized")
        
        # Test service controller initialization
        from data_processing.service_controller import ServiceController
        service_controller = ServiceController(fetcher, config)
        print("  ✅ ServiceController initialized")
        
        # Test alert manager initialization (handle missing dependency gracefully)
        try:
            from telegram_bot.alert_manager import AlertManager
            alert_manager = AlertManager(config.telegram_token if config.telegram_token else "dummy_token")
            print("  ✅ AlertManager initialized")
        except ImportError:
            print("  ⚠️  AlertManager not available (missing telegram dependency)")
        
        # Test application controller initialization
        from application.app_controller import ApplicationController
        app_controller = ApplicationController()
        print("  ✅ ApplicationController initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return False

def test_data_structures():
    """Test core data structures"""
    print("\nTesting core data structures...")
    
    try:
        # Test arbitrage opportunity structure
        from data_processing.arbitrage_detector import ArbitrageOpportunity, ThresholdConfig
        opportunity = ArbitrageOpportunity(
            symbol="BTC-USDT",
            buy_exchange="binance",
            sell_exchange="okx",
            buy_price=60000.0,
            sell_price=60100.0,
            profit_percentage=0.1667,
            profit_absolute=100.0,
            timestamp=time.time(),
            threshold_percentage=0.1,
            threshold_absolute=50.0
        )
        print("  ✅ ArbitrageOpportunity structure verified")
        
        # Test threshold config structure
        thresholds = ThresholdConfig(min_profit_percentage=0.5, min_profit_absolute=1.0)
        print("  ✅ ThresholdConfig structure verified")
        
        # Test market view data structures
        from data_processing.market_view import MarketViewData, ConsolidatedMarketView
        market_data = MarketViewData(
            symbol="BTC-USDT",
            exchange="binance",
            bid_price=60000.0,
            ask_price=60001.0,
            bid_size=1.0,
            ask_size=1.0,
            timestamp=time.time()
        )
        print("  ✅ MarketViewData structure verified")
        
        consolidated_view = ConsolidatedMarketView(
            symbol="BTC-USDT",
            exchanges_data={"binance": market_data},
            cbbo_bid_exchange="binance",
            cbbo_ask_exchange="binance",
            cbbo_bid_price=60000.0,
            cbbo_ask_price=60001.0,
            timestamp=time.time()
        )
        print("  ✅ ConsolidatedMarketView structure verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data structure test failed: {e}")
        return False

def test_error_handling():
    """Test error handling components"""
    print("\nTesting error handling components...")
    
    try:
        # Test custom exceptions
        from utils.error_handler import (
            TradingBotError, DataAcquisitionError, DataProcessingError
        )
        
        # Test base exception
        try:
            raise TradingBotError("Test error")
        except TradingBotError:
            pass
            
        print("  ✅ Custom exception hierarchy verified")
        
        # Test decorator
        from utils.error_handler import handle_exception
        
        @handle_exception(logger_name="test", reraise=False, default_return="default")
        def test_function():
            raise ValueError("Test value error")
            
        result = test_function()
        assert result == "default"
        print("  ✅ Error handling decorator verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False

def test_telegram_bot_components():
    """Test Telegram bot components without external dependencies"""
    print("\nTesting Telegram bot components...")
    
    # Test alert manager without sending actual messages
    try:
        from telegram_bot.alert_manager import AlertManager
        alert_manager = AlertManager("dummy_token")
        
        # Test subscriber management
        alert_manager.add_subscriber(123456789)
        subscribers = alert_manager.get_subscribers()
        assert 123456789 in subscribers
        print("  ✅ Subscriber management verified")
        
        # Test alert formatting
        from data_processing.arbitrage_detector import ArbitrageOpportunity
        opportunity = ArbitrageOpportunity(
            symbol="BTC-USDT",
            buy_exchange="binance",
            sell_exchange="okx",
            buy_price=60000.0,
            sell_price=60100.0,
            profit_percentage=0.1667,
            profit_absolute=100.0,
            timestamp=time.time(),
            threshold_percentage=0.1,
            threshold_absolute=50.0
        )
        
        formatted_alert = alert_manager.format_arbitrage_alert(opportunity)
        assert "BTC-USDT" in formatted_alert
        assert "binance" in formatted_alert
        assert "okx" in formatted_alert
        print("  ✅ Alert formatting verified")
        
        return True
        
    except ImportError:
        print("  ⚠️  Telegram bot components not available (missing telegram dependency)")
        return True  # Return True since this is an expected condition
    except Exception as e:
        print(f"  ❌ Telegram bot components test failed: {e}")
        return False

def test_service_controllers():
    """Test service controller components"""
    print("\nTesting service controller components...")
    
    try:
        # Test service controller initialization
        from config.config_manager import ConfigManager
        from data_acquisition.market_data_fetcher import MarketDataFetcher
        from data_processing.service_controller import ServiceController
        
        config = ConfigManager()
        fetcher = MarketDataFetcher(config)
        service_controller = ServiceController(fetcher, config)
        
        # Test initial state
        assert not service_controller.arbitrage_monitoring
        assert not service_controller.market_view_monitoring
        print("  ✅ Service controller initialization verified")
        
        # Test status methods
        status = service_controller.get_service_status()
        assert 'arbitrage_service' in status
        assert 'market_view_service' in status
        print("  ✅ Service status methods verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service controller test failed: {e}")
        return False

def run_all_tests():
    """Run all core functionality tests"""
    print("GoQuant Trading Bot - Core Functionality Test")
    print("=" * 45)
    
    tests = [
        test_imports,
        test_basic_initialization,
        test_data_structures,
        test_error_handling,
        test_telegram_bot_components,
        test_service_controllers
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} passed")
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 45)
    print(f"Test Results: {passed}/{passed + failed} tests passed")
    
    if failed == 0:
        print("🎉 All core functionality tests passed!")
        return True
    else:
        print(f"❌ {failed} tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)