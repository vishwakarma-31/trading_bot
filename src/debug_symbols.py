"""
Debug script to check symbol data structure
"""
import sys
import os

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher

def debug_symbols():
    """Debug symbol data structure"""
    print("GoQuant Trading Bot - Symbol Debug")
    print("=" * 35)
    
    # Initialize components
    config = ConfigManager()
    market_fetcher = MarketDataFetcher(config)
    
    # Get available symbols
    print("\n1. Discovering available symbols...")
    all_symbols = market_fetcher.get_all_symbols()
    
    if not all_symbols:
        print("❌ Failed to retrieve symbols.")
        return
        
    print(f"✅ Retrieved symbols from {len(all_symbols)} exchanges:")
    for exchange, symbols in all_symbols.items():
        print(f"   {exchange}: {len(symbols)} symbols")
        if symbols:
            print(f"     First symbol type: {type(symbols[0])}")
            print(f"     First symbol value: {symbols[0]}")
        break  # Just check the first exchange

if __name__ == "__main__":
    debug_symbols()