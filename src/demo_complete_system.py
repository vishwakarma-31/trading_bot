"""
Demo script for the complete GoQuant Trading Bot system
This script demonstrates the integration of arbitrage detection and market view functionality.
"""
import sys
import os
import logging
import time

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.arbitrage_detector import ArbitrageDetector
from data_processing.market_view import MarketViewManager

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def demo_complete_system():
    """Demonstrate the complete system functionality"""
    print("GoQuant Trading Bot - Complete System Demo")
    print("=" * 45)
    
    # Initialize components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    arbitrage_detector = ArbitrageDetector(market_fetcher, config)
    market_view_manager = MarketViewManager(market_fetcher)
    
    print(f"Initialized complete system:")
    print(f"  - Market Data Fetcher")
    print(f"  - Arbitrage Detector")
    print(f"  - Market View Manager")
    
    # Get available symbols
    print("\n1. Discovering available symbols...")
    all_symbols = market_fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Failed to retrieve symbols. Please check your GoMarket API configuration.")
        return
        
    print(f"✅ Retrieved symbols from {len(all_symbols)} exchanges:")
    for exchange, symbols in all_symbols.items():
        print(f"   {exchange}: {len(symbols)} symbols")
        
    # Select symbols for testing
    test_symbols = []
    test_exchanges = []
    
    for exchange, symbols in all_symbols.items():
        if symbols:
            # Extract symbol names from the symbol dictionaries
            symbol_names = [symbol['name'] if isinstance(symbol, dict) else symbol for symbol in symbols[:2]]
            test_symbols.extend(symbol_names)  # Take up to 2 symbols per exchange
            test_exchanges.append(exchange)
        if len(test_symbols) >= 2 and len(test_exchanges) >= 2:  # Test with up to 2 symbols and 2 exchanges
            break
            
    test_symbols = list(set(test_symbols))[:2]  # Ensure unique symbols, max 2
    
    if not test_symbols or not test_exchanges:
        print("❌ No test symbols/exchanges available.")
        return
        
    print(f"\n2. Testing with symbols: {test_symbols}")
    print(f"   Testing with exchanges: {test_exchanges}")
    
    # Test arbitrage detection
    print("\n3. Testing arbitrage detection...")
    for symbol in test_symbols:
        opportunities = arbitrage_detector.find_arbitrage_opportunities(test_exchanges, symbol)
        print(f"   {symbol}: Found {len(opportunities)} opportunities")
        
        # Display first opportunity if any found
        if opportunities:
            opp = opportunities[0]
            print(f"     Sample: Buy on {opp.buy_exchange} at ${opp.buy_price:.4f}, "
                  f"Sell on {opp.sell_exchange} at ${opp.sell_price:.4f}, "
                  f"Profit: {opp.profit_percentage:.2f}% (${opp.profit_absolute:.4f})")
    
    # Test market view
    print("\n4. Testing market view...")
    for symbol in test_symbols[:1]:  # Test with first symbol
        consolidated_view = market_view_manager.get_consolidated_market_view(symbol, test_exchanges)
        
        if consolidated_view:
            print(f"   {symbol}:")
            print(f"     CBBO Bid: {consolidated_view.cbbo_bid_price:.4f} on {consolidated_view.cbbo_bid_exchange}")
            print(f"     CBBO Ask: {consolidated_view.cbbo_ask_price:.4f} on {consolidated_view.cbbo_ask_exchange}")
            print(f"     Spread: {consolidated_view.cbbo_ask_price - consolidated_view.cbbo_bid_price:.4f}")
        else:
            print(f"   {symbol}: Failed to retrieve consolidated market view")
    
    # Test threshold configuration
    print("\n5. Testing threshold configuration...")
    print(f"   Current arbitrage thresholds: {arbitrage_detector.get_thresholds()}")
    
    # Update thresholds
    arbitrage_detector.set_thresholds(min_profit_percentage=1.0, min_profit_absolute=2.0)
    print(f"   Updated arbitrage thresholds: {arbitrage_detector.get_thresholds()}")
    
    # Test system integration
    print("\n6. Testing system integration...")
    
    # Get some opportunities to track
    if test_symbols:
        symbol = test_symbols[0]
        opportunities = arbitrage_detector.find_arbitrage_opportunities(test_exchanges, symbol)
        
        # Check active opportunities
        active_opps = arbitrage_detector.get_active_opportunities()
        print(f"   Active arbitrage opportunities: {len(active_opps)}")
        
        # Get CBBO for the same symbol
        cbbo = market_view_manager.get_cbbo(symbol)
        if cbbo:
            print(f"   CBBO for {symbol}:")
            print(f"     Best Bid: {cbbo.cbbo_bid_price:.4f} on {cbbo.cbbo_bid_exchange}")
            print(f"     Best Ask: {cbbo.cbbo_ask_price:.4f} on {cbbo.cbbo_ask_exchange}")
    
    # Test monitoring status for both systems
    print("\n7. Testing monitoring status...")
    
    arb_status = "Active" if arbitrage_detector.monitoring else "Inactive"
    market_status = "Active" if market_view_manager.monitoring else "Inactive"
    
    print(f"   Arbitrage monitoring: {arb_status}")
    print(f"   Market view monitoring: {market_status}")
    
    print("\n" + "=" * 45)
    print("✅ Complete system demo completed successfully!")
    print("\nThe GoQuant Trading Bot provides:")
    print("  - Multi-exchange arbitrage detection")
    print("  - Consolidated market view with CBBO")
    print("  - Real-time monitoring capabilities")
    print("  - Telegram bot integration")
    print("\nTo use the full system:")
    print("1. Configure your Telegram bot token in .env")
    print("2. Run 'python src/main.py' to start the bot")
    print("3. Use Telegram commands to interact with both services")

if __name__ == "__main__":
    setup_logging()
    demo_complete_system()