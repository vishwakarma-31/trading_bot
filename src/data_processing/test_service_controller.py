"""
Test script for the Service Controller
"""
import sys
import os
import time
import threading

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.service_controller import ServiceController

def test_service_controller_creation():
    """Test service controller creation"""
    print("Testing service controller creation...")
    
    # Create required components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    service_controller = ServiceController(market_fetcher, config)
    
    # Check that services are initialized
    assert service_controller.arbitrage_detector is not None
    assert service_controller.market_view_manager is not None
    assert not service_controller.arbitrage_monitoring
    assert not service_controller.market_view_monitoring
    
    print("  ✅ Service controller created successfully")
    print("  ✅ Arbitrage detector initialized")
    print("  ✅ Market view manager initialized")
    print("  ✅ Services are not running by default")
    
    return True

def test_arbitrage_service_control():
    """Test arbitrage service start/stop functionality"""
    print("\nTesting arbitrage service control...")
    
    # Create required components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    service_controller = ServiceController(market_fetcher, config)
    
    # Test starting arbitrage monitoring
    asset_exchanges = {
        'BTC-USDT': ['binance', 'okx'],
        'ETH-USDT': ['binance', 'bybit']
    }
    
    success = service_controller.start_arbitrage_monitoring(asset_exchanges, 0.5, 1.0)
    assert success
    assert service_controller.arbitrage_monitoring
    assert service_controller.arbitrage_assets == asset_exchanges
    
    print("  ✅ Arbitrage monitoring started successfully")
    
    # Test getting arbitrage status
    status = service_controller.get_arbitrage_status()
    assert status['monitoring']
    assert status['monitored_assets'] == asset_exchanges
    
    print("  ✅ Arbitrage status retrieved successfully")
    
    # Test stopping arbitrage monitoring
    success = service_controller.stop_arbitrage_monitoring()
    assert success
    assert not service_controller.arbitrage_monitoring
    
    print("  ✅ Arbitrage monitoring stopped successfully")
    
    return True

def test_market_view_service_control():
    """Test market view service start/stop functionality"""
    print("\nTesting market view service control...")
    
    # Create required components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    service_controller = ServiceController(market_fetcher, config)
    
    # Test starting market view monitoring
    symbol_exchanges = {
        'BTC-USDT': ['binance', 'okx'],
        'ETH-USDT': ['binance', 'bybit']
    }
    
    success = service_controller.start_market_view_monitoring(symbol_exchanges)
    assert success
    assert service_controller.market_view_monitoring
    assert service_controller.market_view_symbols == symbol_exchanges
    
    print("  ✅ Market view monitoring started successfully")
    
    # Test getting market view status
    status = service_controller.get_market_view_status()
    assert status['monitoring']
    assert status['monitored_symbols'] == symbol_exchanges
    
    print("  ✅ Market view status retrieved successfully")
    
    # Test stopping market view monitoring
    success = service_controller.stop_market_view_monitoring()
    assert success
    assert not service_controller.market_view_monitoring
    
    print("  ✅ Market view monitoring stopped successfully")
    
    return True

def test_concurrent_services():
    """Test that both services can run concurrently"""
    print("\nTesting concurrent service operation...")
    
    # Create required components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    service_controller = ServiceController(market_fetcher, config)
    
    # Start both services
    asset_exchanges = {'BTC-USDT': ['binance', 'okx']}
    symbol_exchanges = {'ETH-USDT': ['binance', 'bybit']}
    
    arb_success = service_controller.start_arbitrage_monitoring(asset_exchanges)
    mv_success = service_controller.start_market_view_monitoring(symbol_exchanges)
    
    assert arb_success
    assert mv_success
    assert service_controller.arbitrage_monitoring
    assert service_controller.market_view_monitoring
    
    print("  ✅ Both services started successfully")
    
    # Check that both services are running
    arb_status = service_controller.get_arbitrage_status()
    mv_status = service_controller.get_market_view_status()
    
    assert arb_status['monitoring']
    assert mv_status['monitoring']
    
    print("  ✅ Both services are running concurrently")
    
    # Stop both services
    service_controller.stop_all_services()
    assert not service_controller.arbitrage_monitoring
    assert not service_controller.market_view_monitoring
    
    print("  ✅ Both services stopped successfully")
    
    return True

def test_service_status():
    """Test overall service status reporting"""
    print("\nTesting service status reporting...")
    
    # Create required components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    service_controller = ServiceController(market_fetcher, config)
    
    # Get overall status
    status = service_controller.get_service_status()
    
    assert 'arbitrage_service' in status
    assert 'market_view_service' in status
    assert 'timestamp' in status
    
    arb_status = status['arbitrage_service']
    mv_status = status['market_view_service']
    
    assert not arb_status['monitoring']
    assert not mv_status['monitoring']
    
    print("  ✅ Overall service status retrieved successfully")
    
    return True

def run_all_tests():
    """Run all tests for the service controller"""
    print("Generic Trading Bot - Service Controller Test")
    print("=" * 50)
    
    tests = [
        test_service_controller_creation,
        test_arbitrage_service_control,
        test_market_view_service_control,
        test_concurrent_services,
        test_service_status
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
    
    print("=" * 50)
    print(f"Test Results: {passed}/{passed + failed} tests passed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"❌ {failed} tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()