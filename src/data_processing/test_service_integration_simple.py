"""
Simple test script for service controller integration
"""
import sys
import os

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
    
    # Create service controller
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

def test_service_controller_methods():
    """Test service controller methods"""
    print("\nTesting service controller methods...")
    
    # Create required components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    
    # Create service controller
    service_controller = ServiceController(market_fetcher, config)
    
    # Test service status methods
    arb_status = service_controller.get_arbitrage_status()
    mv_status = service_controller.get_market_view_status()
    overall_status = service_controller.get_service_status()
    
    assert isinstance(arb_status, dict)
    assert isinstance(mv_status, dict)
    assert isinstance(overall_status, dict)
    assert 'arbitrage_service' in overall_status
    assert 'market_view_service' in overall_status
    
    print("  ✅ Status methods work correctly")
    
    # Test service control methods
    assert service_controller.is_service_running('arbitrage') == False
    assert service_controller.is_service_running('market_view') == False
    assert service_controller.is_service_running('invalid') == False
    
    print("  ✅ Service state checking works correctly")
    
    return True

def run_all_tests():
    """Run all tests for service controller integration"""
    print("GoQuant Trading Bot - Simple Service Controller Integration Test")
    print("=" * 65)
    
    tests = [
        test_service_controller_creation,
        test_service_controller_methods
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
    
    print("=" * 65)
    print(f"Test Results: {passed}/{passed + failed} tests passed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"❌ {failed} tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()