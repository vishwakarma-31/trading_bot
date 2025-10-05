"""
Simple test script for the Application Controller (without Telegram dependencies)
"""
import sys
import os

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    
    # Test config module
    from config.config_manager import ConfigManager
    print("  ✅ ConfigManager imported successfully")
    
    # Test data acquisition module
    from data_acquisition.market_data_fetcher import MarketDataFetcher
    print("  ✅ MarketDataFetcher imported successfully")
    
    # Test data processing modules
    from data_processing.arbitrage_detector import ArbitrageDetector
    from data_processing.service_controller import ServiceController
    print("  ✅ Data processing modules imported successfully")
    
    # Test logging module
    from logging_module.logging_config import setup_logging, get_logger
    print("  ✅ Logging modules imported successfully")
    
    # Test utils module
    from utils.error_handler import handle_exception
    print("  ✅ Utils modules imported successfully")
    
    return True

def test_app_controller_structure():
    """Test application controller structure"""
    print("\nTesting application controller structure...")
    
    # Read the app_controller file and check for key components
    with open(os.path.join(os.path.dirname(__file__), 'app_controller.py'), 'r') as f:
        content = f.read()
        
    # Check for key classes
    assert 'class ApplicationController' in content
    assert 'class ApplicationError' in content
    assert 'class ApplicationInitializationError' in content
    assert 'class ApplicationRuntimeError' in content
    
    # Check for key methods
    assert 'def initialize' in content
    assert 'def start' in content
    assert 'def stop' in content
    assert 'def _main_loop' in content
    assert 'def _signal_handler' in content
    assert 'def is_running' in content
    
    print("  ✅ ApplicationController class structure verified")
    print("  ✅ All required methods present")
    
    return True

def run_all_tests():
    """Run all tests for the application controller"""
    print("GoQuant Trading Bot - Simple Application Controller Test")
    print("=" * 55)
    
    tests = [
        test_imports,
        test_app_controller_structure
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
    
    print("=" * 55)
    print(f"Test Results: {passed}/{passed + failed} tests passed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"❌ {failed} tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()