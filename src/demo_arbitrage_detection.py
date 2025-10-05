"""
Demo script for the Arbitrage Detection Module
This script demonstrates the complete functionality of the arbitrage detection system.
"""
import sys
import os
import time
import logging

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.arbitrage_detector import ArbitrageDetector

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def demo_arbitrage_detection():
    """Demonstrate the arbitrage detection functionality"""
    print("GoQuant Trading Bot - Arbitrage Detection Demo")
    print("=" * 50)
    
    # Initialize components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    arbitrage_detector = ArbitrageDetector(market_fetcher, config)
    
    # Set initial thresholds
    arbitrage_detector.set_thresholds(
        min_profit_percentage=config.min_profit_percentage,
        min_profit_absolute=config.min_profit_absolute
    )
    
    print(f"Initialized with thresholds: {config.min_profit_percentage}% or ${config.min_profit_absolute}")
    
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
    for exchange, symbols in all_symbols.items():
        if symbols:
            test_symbols.extend(symbols[:2])  # Take up to 2 symbols per exchange
        if len(test_symbols) >= 4:  # Test with up to 4 symbols
            break
            
    test_symbols = list(set(test_symbols))[:2]  # Ensure unique symbols, max 2
    
    if not test_symbols:
        print("❌ No test symbols available.")
        return
        
    print(f"\n2. Testing with symbols: {test_symbols}")
    
    # Test basic arbitrage detection
    print("\n3. Testing basic arbitrage detection...")
    for symbol in test_symbols:
        opportunities = arbitrage_detector.find_arbitrage_opportunities(
            ['binance', 'okx', 'bybit', 'deribit'], 
            symbol
        )
        print(f"   {symbol}: Found {len(opportunities)} opportunities")
        
        # Display first opportunity if any found
        if opportunities:
            opp = opportunities[0]
            print(f"     Sample: Buy on {opp.buy_exchange} at ${opp.buy_price:.4f}, "
                  f"Sell on {opp.sell_exchange} at ${opp.sell_price:.4f}, "
                  f"Profit: {opp.profit_percentage:.2f}% (${opp.profit_absolute:.4f})")
    
    # Test synthetic arbitrage detection
    print("\n4. Testing synthetic arbitrage detection...")
    # This is a simplified test - in reality, we would need to identify
    # base assets and their quote assets properly
    base_asset = "BTC"
    quote_assets = ["USDT", "USDC"]
    
    synthetic_opportunities = arbitrage_detector.find_synthetic_arbitrage_opportunities(
        base_asset, quote_assets
    )
    print(f"   Found {len(synthetic_opportunities)} synthetic opportunities")
    
    # Test threshold configuration
    print("\n5. Testing threshold configuration...")
    print(f"   Current thresholds: {arbitrage_detector.get_thresholds()}")
    
    # Update thresholds
    arbitrage_detector.set_thresholds(
        min_profit_percentage=1.0,
        min_profit_absolute=2.0
    )
    print(f"   Updated thresholds: {arbitrage_detector.get_thresholds()}")
    
    # Test opportunity tracking
    print("\n6. Testing opportunity tracking...")
    
    # Get some opportunities to track
    if test_symbols:
        symbol = test_symbols[0]
        opportunities = arbitrage_detector.find_arbitrage_opportunities(
            ['binance', 'okx', 'bybit', 'deribit'], 
            symbol
        )
        
        # Check active opportunities
        active_opps = arbitrage_detector.get_active_opportunities()
        print(f"   Active opportunities: {len(active_opps)}")
        
        # Check opportunity history
        history = arbitrage_detector.get_opportunity_history(limit=5)
        print(f"   Recent history entries: {len(history)}")
        
        # Check opportunity counts
        counts = arbitrage_detector.get_opportunity_count()
        print(f"   Opportunity counts: {counts}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\nNext steps:")
    print("1. Configure your Telegram bot token in .env")
    print("2. Run 'python src/main.py' to start the full bot")
    print("3. Use Telegram commands to interact with the bot:")
    print("   - /threshold - View current thresholds")
    print("   - /threshold <percent> <absolute> - Set thresholds")
    print("   - /arbitrage - View current opportunities")

if __name__ == "__main__":
    setup_logging()
    demo_arbitrage_detection()