"""
Test script for the mock market data fetcher
"""
import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config_manager import ConfigManager
from data_acquisition.mock_market_data_fetcher import MockMarketDataFetcher

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(level=logging.INFO)

def test_mock_fetcher():
    """Test the mock market data fetcher"""
    print("Testing Mock Market Data Fetcher")
    print("=" * 35)
    
    # Setup logging
    setup_logging()
    
    # Initialize configuration
    config = ConfigManager()
    
    # Initialize mock market data fetcher
    market_fetcher = MockMarketDataFetcher(config)
    
    print("\n1. Testing get_all_symbols()")
    all_symbols = market_fetcher.get_all_symbols()
    print(f"   Retrieved symbols from {len(all_symbols)} exchanges:")
    for exchange, symbols in all_symbols.items():
        print(f"     {exchange}: {len(symbols)} symbols")
        
    print("\n2. Testing get_available_symbols()")
    binance_symbols = market_fetcher.get_available_symbols('binance')
    print(f"   Binance symbols: {binance_symbols}")
    
    print("\n3. Testing get_l1_market_data()")
    if binance_symbols:
        sample_symbol = binance_symbols[0]
        l1_data = market_fetcher.get_l1_market_data('binance', sample_symbol)
        if l1_data:
            print(f"   L1 data for {sample_symbol}:")
            print(f"     Bid: ${l1_data['bid_price']:.4f}")
            print(f"     Ask: ${l1_data['ask_price']:.4f}")
            print(f"     Last: ${l1_data['last_price']:.4f}")
        else:
            print(f"   Failed to get L1 data for {sample_symbol}")
    
    print("\n4. Testing get_l2_order_book()")
    if binance_symbols:
        sample_symbol = binance_symbols[0]
        l2_data = market_fetcher.get_l2_order_book('binance', sample_symbol)
        if l2_data:
            print(f"   L2 data for {sample_symbol}:")
            print(f"     Bids: {len(l2_data['bids'])} levels")
            print(f"     Asks: {len(l2_data['asks'])} levels")
            if l2_data['bids']:
                print(f"     Best bid: ${l2_data['bids'][0]['price']:.4f} ({l2_data['bids'][0]['size']})")
            if l2_data['asks']:
                print(f"     Best ask: ${l2_data['asks'][0]['price']:.4f} ({l2_data['asks'][0]['size']})")
        else:
            print(f"   Failed to get L2 data for {sample_symbol}")
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_mock_fetcher()