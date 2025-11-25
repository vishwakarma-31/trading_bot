"""
Test script for error handling and logging utilities
"""
import sys
import os
import logging

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.error_handler import (
    TradingBotError, DataAcquisitionError, DataProcessingError, TelegramBotError,
    APIConnectionError, DataParsingError, WebSocketError, RateLimitError, AuthenticationError,
    InvalidDataError, MissingDataError, CalculationError, ThresholdValidationError,
    MessageSendingError, CommandParsingError, InvalidUserInputError, BotAPIError,
    handle_exception, log_exception, safe_execute
)

def test_custom_exceptions():
    """Test custom exception classes"""
    print("Testing custom exception classes...")
    
    # Test base exception
    try:
        raise TradingBotError("Test trading bot error")
    except TradingBotError as e:
        assert str(e) == "Test trading bot error"
        print("  ✅ TradingBotError works correctly")
    
    # Test data acquisition errors
    try:
        raise APIConnectionError("Test API connection error")
    except APIConnectionError as e:
        assert str(e) == "Test API connection error"
        print("  ✅ APIConnectionError works correctly")
        
    try:
        raise DataParsingError("Test data parsing error")
    except DataParsingError as e:
        assert str(e) == "Test data parsing error"
        print("  ✅ DataParsingError works correctly")
        
    # Test data processing errors
    try:
        raise InvalidDataError("Test invalid data error")
    except InvalidDataError as e:
        assert str(e) == "Test invalid data error"
        print("  ✅ InvalidDataError works correctly")
        
    try:
        raise CalculationError("Test calculation error")
    except CalculationError as e:
        assert str(e) == "Test calculation error"
        print("  ✅ CalculationError works correctly")
        
    # Test Telegram bot errors
    try:
        raise InvalidUserInputError("Test invalid user input error")
    except InvalidUserInputError as e:
        assert str(e) == "Test invalid user input error"
        print("  ✅ InvalidUserInputError works correctly")
        
    return True

def test_handle_exception_decorator():
    """Test handle_exception decorator"""
    print("\nTesting handle_exception decorator...")
    
    # Set up logger
    logging.basicConfig(level=logging.INFO)
    test_logger = logging.getLogger("test_logger")
    
    @handle_exception(logger_name="test_logger", reraise=False, default_return="default")
    def function_that_raises():
        raise ValueError("Test value error")
    
    result = function_that_raises()
    assert result == "default"
    print("  ✅ handle_exception decorator works correctly (no reraise)")
    
    return True

def test_log_exception():
    """Test log_exception function"""
    print("\nTesting log_exception function...")
    
    # Set up logger
    logging.basicConfig(level=logging.INFO)
    test_logger = logging.getLogger("test_logger")
    
    try:
        raise ValueError("Test value error")
    except ValueError as e:
        log_exception(test_logger, e, "Test context")
        print("  ✅ log_exception function works correctly")
    
    return True

def test_safe_execute():
    """Test safe_execute function"""
    print("\nTesting safe_execute function...")
    
    # Set up logger
    logging.basicConfig(level=logging.INFO)
    test_logger = logging.getLogger("test_logger")
    
    def risky_function(x, y):
        return x / y
    
    # Test successful execution
    result = safe_execute(risky_function, test_logger, None, 10, 2)
    assert result == 5
    print("  ✅ safe_execute works correctly (success case)")
    
    # Test failed execution
    result = safe_execute(risky_function, test_logger, "default", 10, 0)
    assert result == "default"
    print("  ✅ safe_execute works correctly (error case)")
    
    return True

def run_all_tests():
    """Run all tests for error handling utilities"""
    print("Generic Trading Bot - Error Handling Utilities Test")
    print("=" * 55)
    
    tests = [
        test_custom_exceptions,
        test_handle_exception_decorator,
        test_log_exception,
        test_safe_execute
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