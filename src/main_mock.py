"""
Main entry point for the Generic Trading Bot with Mock Data
This version uses simulated market data.
"""
import sys
import os
import logging
from telegram_bot.bot_handler import TelegramBotHandler
from config.config_manager import ConfigManager
from data_acquisition.mock_market_data_fetcher import MockMarketDataFetcher
from data_processing.arbitrage_detector import ArbitrageDetector
from data_processing.market_view import MarketViewManager

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main entry point for the trading bot with mock data"""
    print("Generic Trading Bot - Mock Data Version")
    print("=" * 40)
    print("Running with simulated market data")
    print()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration
        config = ConfigManager()
        
        # Check if Telegram token is configured
        if not config.telegram_token:
            print("⚠️  Telegram bot token not configured in .env")
            print("   You can still run the system, but Telegram bot features will be disabled")
            print()
        
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
            print(f"   Available symbols from {len(all_symbols)} exchanges:")
            for exchange, symbols in all_symbols.items():
                print(f"     {exchange}: {len(symbols)} symbols")
        else:
            print("   ⚠️  No mock symbols available")
            
        # Test arbitrage detection with a sample symbol
        test_exchange = 'binance'
        test_symbol = 'BTCUSDT'
        
        if test_exchange in all_symbols and test_symbol in all_symbols[test_exchange]:
            opportunities = arbitrage_detector.find_arbitrage_opportunities(
                ['binance', 'okx', 'bybit', 'deribit'], 
                test_symbol
            )
            print(f"\n   Arbitrage test for {test_symbol}:")
            print(f"     Found {len(opportunities)} opportunities")
            
            if opportunities:
                opp = opportunities[0]
                print(f"     Sample: Buy on {opp.buy_exchange} at ${opp.buy_price:.4f}, "
                      f"Sell on {opp.sell_exchange} at ${opp.sell_price:.4f}, "
                      f"Profit: {opp.profit_percentage:.2f}% (${opp.profit_absolute:.4f})")
        else:
            print(f"\n   ⚠️  Test symbol {test_symbol} not available on {test_exchange}")
            
        # Test market view
        consolidated_view = market_view_manager.get_consolidated_market_view(
            test_symbol, 
            ['binance', 'okx', 'bybit', 'deribit']
        )
        
        if consolidated_view:
            print(f"\n   Market view test for {test_symbol}:")
            print(f"     CBBO Bid: {consolidated_view.cbbo_bid_price:.4f} on {consolidated_view.cbbo_bid_exchange}")
            print(f"     CBBO Ask: {consolidated_view.cbbo_ask_price:.4f} on {consolidated_view.cbbo_ask_exchange}")
            print(f"     Spread: {consolidated_view.cbbo_ask_price - consolidated_view.cbbo_bid_price:.4f}")
        else:
            print(f"\n   ⚠️  Failed to retrieve consolidated market view for {test_symbol}")
            
        # Start Telegram bot if token is available
        if config.telegram_token:
            print("\n🚀 Starting Telegram bot...")
            bot_handler = TelegramBotHandler(
                config=config,
                arbitrage_detector=arbitrage_detector,
                market_fetcher=market_fetcher
            )
            
            try:
                print("   Bot is now running. Press Ctrl+C to stop.")
                bot_handler.start()
            except KeyboardInterrupt:
                print("\n   Stopping bot...")
                bot_handler.stop()
                print("   Bot stopped.")
            except Exception as e:
                logger.error(f"Bot error: {e}")
                print(f"   ❌ Bot error: {e}")
        else:
            print("\nℹ️  Telegram bot token not configured.")
            print("   To use the Telegram bot:")
            print("   1. Create a bot with @BotFather on Telegram")
            print("   2. Add your bot token to the .env file")
            print("   3. Run this script again")
            print()
            print("   The system is running with mock data only.")
            print("   Press Enter to exit...")
            input()
            
    except Exception as e:
        logger.error(f"Failed to start trading bot: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()