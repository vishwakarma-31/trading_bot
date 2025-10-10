"""
Demo script for the GoQuant Trading Bot with Mock Data
This demonstrates the core functionality without requiring the GoMarket API.
"""
import sys
import os
import logging
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config_manager import ConfigManager
from data_acquisition.mock_market_data_fetcher import MockMarketDataFetcher
from data_processing.arbitrage_detector import ArbitrageDetector
from data_processing.market_view import MarketViewManager

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def demo_mock_system():
    """Demonstrate the system functionality with mock data"""
    print("GoQuant Trading Bot - Mock System Demo")
    print("=" * 40)
    print("Demonstrating core functionality with simulated market data")
    print()
    
    # Setup logging
    setup_logging()
    
    try:
        # Initialize configuration
        config = ConfigManager()
        
        # Initialize mock market data fetcher
        market_fetcher = MockMarketDataFetcher(config)
        
        # Initialize core components
        arbitrage_detector = ArbitrageDetector(market_fetcher, config)
        market_view_manager = MarketViewManager(market_fetcher)
        
        # Set initial thresholds
        arbitrage_detector.set_thresholds(
            min_profit_percentage=config.min_profit_percentage,
            min_profit_absolute=config.min_profit_absolute
        )
        
        print("✅ System components initialized:")
        print(f"   - Mock Market Data Fetcher")
        print(f"   - Arbitrage Detector (thresholds: {config.min_profit_percentage}% or ${config.min_profit_absolute})")
        print(f"   - Market View Manager")
        
        # Test the components with mock data
        print("\n🔍 Testing system with mock data...")
        
        # Get available symbols
        all_symbols = market_fetcher.get_all_symbols()
        if all_symbols:
            print(f"\n1. Available symbols from {len(all_symbols)} exchanges:")
            for exchange, symbols in all_symbols.items():
                print(f"     {exchange}: {len(symbols)} symbols")
        else:
            print("\n1. ⚠️  No mock symbols available")
            
        # Test arbitrage detection with a sample symbol
        test_exchange = 'binance'
        test_symbol = 'BTCUSDT'
        
        print(f"\n2. Arbitrage detection test for {test_symbol}:")
        if test_exchange in all_symbols and test_symbol in all_symbols[test_exchange]:
            opportunities = arbitrage_detector.find_arbitrage_opportunities(
                ['binance', 'okx', 'bybit', 'deribit'], 
                test_symbol
            )
            print(f"   Found {len(opportunities)} opportunities")
            
            if opportunities:
                opp = opportunities[0]
                print(f"   Sample opportunity:")
                print(f"     Buy on {opp.buy_exchange} at ${opp.buy_price:.4f}")
                print(f"     Sell on {opp.sell_exchange} at ${opp.sell_price:.4f}")
                print(f"     Profit: {opp.profit_percentage:.2f}% (${opp.profit_absolute:.4f})")
        else:
            print(f"   ⚠️  Test symbol {test_symbol} not available on {test_exchange}")
            
        # Test market view
        print(f"\n3. Market view test for {test_symbol}:")
        consolidated_view = market_view_manager.get_consolidated_market_view(
            test_symbol, 
            ['binance', 'okx', 'bybit', 'deribit']
        )
        
        if consolidated_view:
            print(f"   Consolidated Best Bid/Offer:")
            print(f"     Best Bid: {consolidated_view.cbbo_bid_price:.4f} on {consolidated_view.cbbo_bid_exchange}")
            print(f"     Best Ask: {consolidated_view.cbbo_ask_price:.4f} on {consolidated_view.cbbo_ask_exchange}")
            print(f"     Spread: {consolidated_view.cbbo_ask_price - consolidated_view.cbbo_bid_price:.4f}")
        else:
            print(f"   ⚠️  Failed to retrieve consolidated market view for {test_symbol}")
            
        # Test threshold configuration
        print(f"\n4. Threshold configuration test:")
        current_thresholds = arbitrage_detector.get_thresholds()
        print(f"   Current thresholds: {current_thresholds.min_profit_percentage}% or ${current_thresholds.min_profit_absolute}")
        
        # Update thresholds
        arbitrage_detector.set_thresholds(
            min_profit_percentage=1.0,
            min_profit_absolute=2.0
        )
        updated_thresholds = arbitrage_detector.get_thresholds()
        print(f"   Updated thresholds: {updated_thresholds.min_profit_percentage}% or ${updated_thresholds.min_profit_absolute}")
        
        # Test opportunity tracking
        print(f"\n5. Opportunity tracking test:")
        active_opps = arbitrage_detector.get_active_opportunities()
        print(f"   Active opportunities: {len(active_opps)}")
        
        # Test with multiple symbols
        print(f"\n6. Testing multiple symbols:")
        test_symbols = ['BTCUSDT', 'ETHUSDT']
        for symbol in test_symbols:
            if symbol in all_symbols.get('binance', []):
                opportunities = arbitrage_detector.find_arbitrage_opportunities(
                    ['binance', 'okx'], 
                    symbol
                )
                print(f"   {symbol}: {len(opportunities)} opportunities")
        
        print("\n" + "=" * 40)
        print("✅ Demo completed successfully!")
        print("\nTo use the full system with Telegram bot:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Add your bot token to the .env file")
        print("3. Run 'python src/main_mock.py' to start the full system")
        
    except Exception as e:
        logging.error(f"Demo failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    demo_mock_system()