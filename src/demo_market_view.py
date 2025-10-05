"""
Demo script for the Market View Module
This script demonstrates the complete functionality of the market view system.
"""
import sys
import os
import logging

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.market_view import MarketViewManager

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def demo_market_view():
    """Demonstrate the market view functionality"""
    print("GoQuant Trading Bot - Market View Demo")
    print("=" * 40)
    
    # Initialize components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    market_view_manager = MarketViewManager(market_fetcher)
    
    print(f"Initialized Market View Manager")
    
    # Get available symbols
    print("\n1. Discovering available symbols...")
    all_symbols = market_fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Failed to retrieve symbols. Please check your GoMarket API configuration.")
        return
        
    print(f"✅ Retrieved symbols from {len(all_symbols)} exchanges:")
    for exchange, symbols in all_symbols.items():
        print(f"   {exchange}: {len(symbols)} symbols")
        
    # Select a symbol for testing
    test_symbol = None
    test_exchanges = []
    
    for exchange, symbols in all_symbols.items():
        if symbols:
            test_symbol = symbols[0]
            test_exchanges.append(exchange)
            if len(test_exchanges) >= 3:  # Test with up to 3 exchanges
                break
    
    if not test_symbol or not test_exchanges:
        print("❌ No test symbols/exchanges available.")
        return
        
    print(f"\n2. Testing with symbol: {test_symbol}")
    print(f"   Testing with exchanges: {test_exchanges}")
    
    # Test market data fetching
    print("\n3. Testing market data fetching...")
    for exchange in test_exchanges[:2]:  # Test with first 2 exchanges
        market_data = market_view_manager.get_market_data(exchange, test_symbol)
        if market_data:
            print(f"   {exchange}: Bid ${market_data.bid_price:.4f} ({market_data.bid_size}), "
                  f"Ask ${market_data.ask_price:.4f} ({market_data.ask_size})")
        else:
            print(f"   {exchange}: Failed to retrieve data")
    
    # Test consolidated market view
    print("\n4. Testing consolidated market view...")
    consolidated_view = market_view_manager.get_consolidated_market_view(test_symbol, test_exchanges)
    
    if consolidated_view:
        print(f"   Symbol: {consolidated_view.symbol}")
        print(f"   CBBO Bid: {consolidated_view.cbbo_bid_price:.4f} on {consolidated_view.cbbo_bid_exchange}")
        print(f"   CBBO Ask: {consolidated_view.cbbo_ask_price:.4f} on {consolidated_view.cbbo_ask_exchange}")
        print(f"   Spread: {consolidated_view.cbbo_ask_price - consolidated_view.cbbo_bid_price:.4f}")
        print(f"   Exchanges data: {len(consolidated_view.exchanges_data)}")
    else:
        print("   ❌ Failed to retrieve consolidated market view")
    
    # Test CBBO
    print("\n5. Testing CBBO (Consolidated Best Bid/Offer)...")
    cbbo = market_view_manager.get_cbbo(test_symbol)
    
    if cbbo:
        print(f"   Symbol: {cbbo.symbol}")
        print(f"   Best Bid: {cbbo.cbbo_bid_price:.4f} on {cbbo.cbbo_bid_exchange}")
        print(f"   Best Ask: {cbbo.cbbo_ask_price:.4f} on {cbbo.cbbo_ask_exchange}")
        print(f"   Spread: {cbbo.cbbo_ask_price - cbbo.cbbo_bid_price:.4f}")
    else:
        print("   ❌ Failed to retrieve CBBO")
    
    # Test monitoring status
    print("\n6. Testing monitoring status...")
    status = market_view_manager.get_monitoring_status()
    print(f"   Monitoring: {status['monitoring']}")
    print(f"   Monitored symbols: {status['monitored_symbols']}")
    print(f"   Latest data count: {status['latest_data_count']}")
    print(f"   Consolidated views count: {status['consolidated_views_count']}")
    
    print("\n" + "=" * 40)
    print("✅ Demo completed successfully!")
    print("\nNext steps:")
    print("1. Configure your Telegram bot token in .env")
    print("2. Run 'python src/main.py' to start the full bot")
    print("3. Use Telegram commands to interact with the bot:")
    print("   - /view_market <symbol> <exchange1> <exchange2> ...")
    print("   - /get_cbbo <symbol>")
    print("   - /status_market")

if __name__ == "__main__":
    setup_logging()
    demo_market_view()