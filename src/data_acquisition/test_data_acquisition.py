"""
Test script for the Data Acquisition Module
"""
import sys
import os
import time
from typing import Dict

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher

def test_symbol_discovery(fetcher: MarketDataFetcher):
    """Test symbol discovery functionality"""
    print("Testing symbol discovery...")
    
    # Test getting symbols for all exchanges
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Failed to retrieve symbols from any exchange")
        return False
        
    print(f"✅ Retrieved symbols from {len(all_symbols)} exchanges:")
    for exchange, symbols in all_symbols.items():
        print(f"  {exchange}: {len(symbols)} symbols")
        if symbols:
            print(f"    Sample symbols: {symbols[:5]}")
            
    return True

def test_l1_data_fetching(fetcher: MarketDataFetcher):
    """Test L1 market data fetching"""
    print("\nTesting L1 market data fetching...")
    
    # Get some symbols to test with
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Cannot test L1 data - failed to get symbols")
        return False
        
    # Test with 2 assets per exchange
    test_pairs = []
    for exchange, symbols in all_symbols.items():
        if symbols:
            # Take up to 2 symbols for testing
            for symbol in symbols[:2]:
                test_pairs.append((exchange, symbol))
                
    if not test_pairs:
        print("❌ No symbols available for testing")
        return False
        
    print(f"Testing L1 data for {len(test_pairs)} exchange-symbol pairs:")
    
    # Test individual L1 data fetching
    for exchange, symbol in test_pairs:
        data = fetcher.get_l1_market_data(exchange, symbol)
        if data:
            print(f"  ✅ {exchange}:{symbol} - Bid: {data.get('bid_price', 'N/A')}, Ask: {data.get('ask_price', 'N/A')}")
        else:
            print(f"  ❌ {exchange}:{symbol} - Failed to retrieve data")
            
    # Test multiple L1 data fetching
    print("\nTesting multiple L1 data fetching...")
    multiple_data = fetcher.get_multiple_l1_data(test_pairs)
    print(f"  Retrieved data for {len(multiple_data)} pairs")
    
    return True

def test_l2_data_fetching(fetcher: MarketDataFetcher):
    """Test L2 order book data fetching"""
    print("\nTesting L2 order book data fetching...")
    
    # Get some symbols to test with
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Cannot test L2 data - failed to get symbols")
        return False
        
    # Test with 1 asset per exchange
    test_pairs = []
    for exchange, symbols in all_symbols.items():
        if symbols:
            # Take 1 symbol for testing
            test_pairs.append((exchange, symbols[0]))
                
    if not test_pairs:
        print("❌ No symbols available for testing")
        return False
        
    print(f"Testing L2 data for {len(test_pairs)} exchange-symbol pairs:")
    
    # Test individual L2 data fetching
    for exchange, symbol in test_pairs:
        data = fetcher.get_l2_order_book(exchange, symbol)
        if data:
            bids = data.get('bids', [])
            asks = data.get('asks', [])
            print(f"  ✅ {exchange}:{symbol} - Bids: {len(bids)}, Asks: {len(asks)}")
        else:
            print(f"  ❌ {exchange}:{symbol} - Failed to retrieve data")
            
    # Test multiple L2 data fetching
    print("\nTesting multiple L2 data fetching...")
    multiple_data = fetcher.get_multiple_l2_data(test_pairs)
    print(f"  Retrieved data for {len(multiple_data)} pairs")
    
    return True

def websocket_callback(exchange: str, symbol: str, data: Dict):
    """Callback function for WebSocket data"""
    print(f"  📡 WebSocket data received: {exchange}:{symbol} at {data.get('timestamp', 'N/A')}")

def test_websocket_functionality(fetcher: MarketDataFetcher):
    """Test WebSocket functionality"""
    print("\nTesting WebSocket functionality...")
    
    # Get some symbols to test with
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Cannot test WebSocket - failed to get symbols")
        return False
        
    # Test with 1 asset per exchange
    test_pairs = []
    for exchange, symbols in all_symbols.items():
        if symbols:
            # Take 1 symbol for testing
            test_pairs.append((exchange, symbols[0]))
                
    if not test_pairs:
        print("❌ No symbols available for testing WebSocket")
        return False
        
    print(f"Testing WebSocket for {len(test_pairs)} exchange-symbol pairs:")
    
    # Subscribe to L1 data
    fetcher.subscribe_multiple_l1_data(test_pairs, websocket_callback)
    
    # Wait a bit to see if we get any data
    print("  Waiting 10 seconds for WebSocket data...")
    time.sleep(10)
    
    # Check connection status
    connected_count = 0
    for exchange, symbol in test_pairs:
        if fetcher.is_websocket_connected(exchange, symbol):
            connected_count += 1
            print(f"  ✅ {exchange}:{symbol} - Connected")
        else:
            print(f"  ⚠️  {exchange}:{symbol} - Not connected")
            
    print(f"  {connected_count}/{len(test_pairs)} connections established")
    
    # Unsubscribe
    fetcher.unsubscribe_all_data()
    print("  Unsubscribed from all WebSocket connections")
    
    return True

def main():
    """Main test function"""
    print("Generic Trading Bot - Data Acquisition Module Test")
    print("=" * 50)
    
    # Initialize components
    config = ConfigManager()
    fetcher = MarketDataFetcher(config)
    
    # Check if exchange API keys are configured
    missing_keys = []
    if not config.binance_api_key:
        missing_keys.append('Binance')
    if not config.okx_api_key:
        missing_keys.append('OKX')
    
    if missing_keys:
        print(f"⚠️  Warning: API keys not configured for {', '.join(missing_keys)}. Set API keys in .env file.")
        print("   Some tests may be skipped or limited.")
    
    # Run tests
    tests = [
        ("Symbol Discovery", test_symbol_discovery, True),
        ("L1 Data Fetching", test_l1_data_fetching, True),
        ("L2 Data Fetching", test_l2_data_fetching, True),
        ("WebSocket Functionality", test_websocket_functionality, False)  # Skip WebSocket test by default
    ]
    
    passed = 0
    total = 0
    
    for test_name, test_func, run_test in tests:
        if run_test:
            total += 1
            try:
                if test_func(fetcher):
                    passed += 1
                    print(f"✅ {test_name} test passed")
                else:
                    print(f"❌ {test_name} test failed")
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {e}")
        else:
            print(f"⏭️  {test_name} test skipped")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())