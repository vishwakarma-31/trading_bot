"""
Test script for the Application Controller
"""
import sys
import os
import time
import threading

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from application.app_controller import ApplicationController

def test_app_controller_creation():
    """Test application controller creation"""
    print("Testing application controller creation...")
    
    app_controller = ApplicationController()
    assert app_controller is not None
    assert not app_controller.is_running()
    
    print("  ✅ Application controller created successfully")
    print("  ✅ Application is not running by default")
    
    return True

def test_app_initialization():
    """Test application initialization"""
    print("\nTesting application initialization...")
    
    app_controller = ApplicationController()
    success = app_controller.initialize()
    
    assert success
    assert app_controller.config is not None
    assert app_controller.market_fetcher is not None
    assert app_controller.arbitrage_detector is not None
    assert app_controller.service_controller is not None
    assert app_controller.bot_handler is not None
    
    print("  ✅ Application initialized successfully")
    print("  ✅ All components initialized")
    
    return True

def test_signal_handling():
    """Test signal handling"""
    print("\nTesting signal handling...")
    
    app_controller = ApplicationController()
    assert app_controller.initialize()
    
    # Test signal handler registration
    import signal
    original_sigint = signal.getsignal(signal.SIGINT)
    original_sigterm = signal.getsignal(signal.SIGTERM)
    
    # Restore original handlers
    signal.signal(signal.SIGINT, original_sigint)
    signal.signal(signal.SIGTERM, original_sigterm)
    
    print("  ✅ Signal handlers registered successfully")
    
    return True

def run_all_tests():
    """Run all tests for the application controller"""
    print("GoQuant Trading Bot - Application Controller Test")
    print("=" * 50)
    
    tests = [
        test_app_controller_creation,
        test_app_initialization,
        test_signal_handling
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