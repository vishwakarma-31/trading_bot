"""
Test script for the Arbitrage Detection Module
"""
import sys
import os
import time
from typing import Dict

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.arbitrage_detector import ArbitrageDetector

def test_threshold_configuration(detector: ArbitrageDetector):
    """Test threshold configuration functionality"""
    print("Testing threshold configuration...")
    
    # Test getting default thresholds
    thresholds = detector.get_thresholds()
    print(f"  Default thresholds: {thresholds}")
    
    # Test setting new thresholds
    detector.set_thresholds(min_profit_percentage=1.0, min_profit_absolute=2.0)
    new_thresholds = detector.get_thresholds()
    print(f"  Updated thresholds: {new_thresholds}")
    
    # Verify thresholds were updated
    assert new_thresholds.min_profit_percentage == 1.0
    assert new_thresholds.min_profit_absolute == 2.0
    print("  ✅ Threshold configuration test passed")
    
    return True

def test_arbitrage_detection(detector: ArbitrageDetector, fetcher: MarketDataFetcher):
    """Test basic arbitrage detection"""
    print("\nTesting arbitrage detection...")
    
    # Get some symbols to test with
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("  ❌ Cannot test arbitrage detection - failed to get symbols")
        return False
        
    # Test with one symbol
    test_symbol = None
    test_exchanges = []
    
    for exchange, symbols in all_symbols.items():
        if symbols:
            test_symbol = symbols[0]
            test_exchanges.append(exchange)
            if len(test_exchanges) >= 2:  # Need at least 2 exchanges
                break
                
    if not test_symbol or len(test_exchanges) < 2:
        print("  ❌ Not enough exchanges/symbols for testing")
        return False
        
    print(f"  Testing with symbol: {test_symbol}")
    print(f"  Testing with exchanges: {test_exchanges}")
    
    # Find arbitrage opportunities
    opportunities = detector.find_arbitrage_opportunities(test_exchanges, test_symbol)
    print(f"  Found {len(opportunities)} opportunities")
    
    # Display first opportunity if any found
    if opportunities:
        opp = opportunities[0]
        print(f"  Sample opportunity: {opp.symbol} - Buy on {opp.buy_exchange} at {opp.buy_price}, "
              f"Sell on {opp.sell_exchange} at {opp.sell_price}, "
              f"Profit: {opp.profit_percentage:.2f}% (${opp.profit_absolute:.2f})")
    
    print("  ✅ Basic arbitrage detection test completed")
    return True

def test_synthetic_arbitrage_detection(detector: ArbitrageDetector, fetcher: MarketDataFetcher):
    """Test synthetic arbitrage detection"""
    print("\nTesting synthetic arbitrage detection...")
    
    # This is a simplified test - in reality, we would need to identify
    # base assets and their quote assets properly
    base_asset = "BTC"
    quote_assets = ["USDT", "USDC"]
    
    opportunities = detector.find_synthetic_arbitrage_opportunities(base_asset, quote_assets)
    print(f"  Found {len(opportunities)} synthetic opportunities")
    
    if opportunities:
        opp = opportunities[0]
        print(f"  Sample synthetic opportunity: {opp.symbol} - "
              f"Profit: {opp.profit_percentage:.2f}% (${opp.profit_absolute:.2f})")
    
    print("  ✅ Synthetic arbitrage detection test completed")
    return True

def test_opportunity_tracking(detector: ArbitrageDetector, fetcher: MarketDataFetcher):
    """Test opportunity tracking functionality"""
    print("\nTesting opportunity tracking...")
    
    # Get some symbols to test with
    all_symbols = fetcher.get_all_symbols()
    
    if not all_symbols:
        print("  ❌ Cannot test opportunity tracking - failed to get symbols")
        return False
        
    # Test with one symbol
    test_symbol = None
    test_exchanges = []
    
    for exchange, symbols in all_symbols.items():
        if symbols:
            test_symbol = symbols[0]
            test_exchanges.append(exchange)
            if len(test_exchanges) >= 2:  # Need at least 2 exchanges
                break
                
    if not test_symbol or len(test_exchanges) < 2:
        print("  ❌ Not enough exchanges/symbols for testing")
        return False
        
    # Find some opportunities to track
    opportunities = detector.find_arbitrage_opportunities(test_exchanges, test_symbol)
    
    # Check active opportunities
    active_opps = detector.get_active_opportunities()
    print(f"  Active opportunities: {len(active_opps)}")
    
    # Check opportunity history
    history = detector.get_opportunity_history(limit=10)
    print(f"  Recent history entries: {len(history)}")
    
    # Check opportunity counts
    counts = detector.get_opportunity_count()
    print(f"  Opportunity counts by symbol: {counts}")
    
    print("  ✅ Opportunity tracking test completed")
    return True

def main():
    """Main test function"""
    print("GoQuant Trading Bot - Arbitrage Detection Module Test")
    print("=" * 55)
    
    # Initialize components
    config = ConfigManager()
    fetcher = MarketDataFetcher(config)
    detector = ArbitrageDetector(fetcher, config)
    
    # Check if API key is configured
    if not config.gomarket_api_key:
        print("⚠️  Warning: GoMarket API key not configured. Set GOMARKET_API_KEY in .env file.")
        print("   Some tests will be skipped or may fail.")
    
    # Run tests
    tests = [
        ("Threshold Configuration", test_threshold_configuration, detector),
        ("Basic Arbitrage Detection", test_arbitrage_detection, detector, fetcher),
        ("Synthetic Arbitrage Detection", test_synthetic_arbitrage_detection, detector, fetcher),
        ("Opportunity Tracking", test_opportunity_tracking, detector, fetcher)
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
    
    print("\n" + "=" * 55)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())