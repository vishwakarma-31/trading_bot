"""
Test script for the Market View Module
"""
import sys
import os
import time

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.market_view import MarketViewManager

def test_market_data_fetching(manager: MarketViewManager, fetcher: MarketDataFetcher):
    """Test market data fetching functionality"""
    print("Testing market data fetching...")
    
    # Get some symbols to test with
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Cannot test market data fetching - failed to get symbols")
        return False
        
    # Test with one symbol
    test_symbol = None
    test_exchange = None
    
    for exchange, symbols in all_symbols.items():
        if symbols:
            test_symbol = symbols[0]
            test_exchange = exchange
            break
                
    if not test_symbol or not test_exchange:
        print("❌ No symbols/exchanges available for testing")
        return False
        
    print(f"Testing with symbol: {test_symbol} on exchange: {test_exchange}")
    
    # Get market data
    market_data = manager.get_market_data(test_exchange, test_symbol)
    
    if market_data:
        print(f"✅ Retrieved market data: {market_data}")
    else:
        print("❌ Failed to retrieve market data")
        return False
    
    return True

def test_consolidated_market_view(manager: MarketViewManager, fetcher: MarketDataFetcher):
    """Test consolidated market view functionality"""
    print("\nTesting consolidated market view...")
    
    # Get some symbols to test with
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Cannot test consolidated market view - failed to get symbols")
        return False
        
    # Test with one symbol across multiple exchanges
    test_symbol = None
    test_exchanges = []
    
    for exchange, symbols in all_symbols.items():
        if symbols:
            test_symbol = symbols[0]
            test_exchanges.append(exchange)
            if len(test_exchanges) >= 2:  # Need at least 2 exchanges
                break
                
    if not test_symbol or len(test_exchanges) < 2:
        print("❌ Not enough exchanges for testing")
        return False
        
    print(f"Testing with symbol: {test_symbol} on exchanges: {test_exchanges}")
    
    # Get consolidated market view
    consolidated_view = manager.get_consolidated_market_view(test_symbol, test_exchanges)
    
    if consolidated_view:
        print(f"✅ Retrieved consolidated market view:")
        print(f"   Symbol: {consolidated_view.symbol}")
        print(f"   CBBO Bid: {consolidated_view.cbbo_bid_price} on {consolidated_view.cbbo_bid_exchange}")
        print(f"   CBBO Ask: {consolidated_view.cbbo_ask_price} on {consolidated_view.cbbo_ask_exchange}")
        print(f"   Exchanges data: {len(consolidated_view.exchanges_data)}")
    else:
        print("❌ Failed to retrieve consolidated market view")
        return False
    
    return True

def test_cbbo(manager: MarketViewManager, fetcher: MarketDataFetcher):
    """Test CBBO functionality"""
    print("\nTesting CBBO functionality...")
    
    # Get some symbols to test with
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Cannot test CBBO - failed to get symbols")
        return False
        
    # Test with one symbol
    test_symbol = None
    
    for exchange, symbols in all_symbols.items():
        if symbols:
            test_symbol = symbols[0]
            break
                
    if not test_symbol:
        print("❌ No symbols available for testing")
        return False
        
    print(f"Testing CBBO for symbol: {test_symbol}")
    
    # Get CBBO
    cbbo = manager.get_cbbo(test_symbol)
    
    if cbbo:
        print(f"✅ Retrieved CBBO:")
        print(f"   Symbol: {cbbo.symbol}")
        print(f"   Best Bid: {cbbo.cbbo_bid_price} on {cbbo.cbbo_bid_exchange}")
        print(f"   Best Ask: {cbbo.cbbo_ask_price} on {cbbo.cbbo_ask_exchange}")
    else:
        print("❌ Failed to retrieve CBBO")
        return False
    
    return True

def test_monitoring_status(manager: MarketViewManager):
    """Test monitoring status functionality"""
    print("\nTesting monitoring status...")
    
    # Get monitoring status
    status = manager.get_monitoring_status()
    print(f"✅ Monitoring status: {status}")
    
    return True

def main():
    """Main test function"""
    print("GoQuant Trading Bot - Market View Module Test")
    print("=" * 45)
    
    # Initialize components
    config = ConfigManager()
    fetcher = MarketDataFetcher(config)
    manager = MarketViewManager(fetcher)
    
    # Check if API key is configured
    if not config.gomarket_api_key:
        print("⚠️  Warning: GoMarket API key not configured. Set GOMARKET_API_KEY in .env file.")
        print("   Some tests will be skipped or may fail.")
    
    # Run tests
    tests = [
        ("Market Data Fetching", test_market_data_fetching, manager, fetcher),
        ("Consolidated Market View", test_consolidated_market_view, manager, fetcher),
        ("CBBO Functionality", test_cbbo, manager, fetcher),
        ("Monitoring Status", test_monitoring_status, manager)
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
    
    print("\n" + "=" * 45)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())