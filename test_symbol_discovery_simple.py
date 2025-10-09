import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_acquisition.symbol_discovery import SymbolDiscovery
from config.config_manager import ConfigManager

def test_symbol_discovery():
    print("Testing SymbolDiscovery implementation...")
    
    # Create a mock config
    config = ConfigManager()
    
    # Create symbol discovery instance
    discovery = SymbolDiscovery(config)
    
    # Test symbol normalization
    print("\n1. Testing symbol normalization:")
    test_cases = [
        ('binance', 'ETHBTC', 'ETH', 'BTC'),
        ('okx', 'USDT-SGD', 'USDT', 'SGD'),
        ('deribit', 'BTC_USDC', 'BTC', 'USDC'),
        ('bybit', 'BTCUSDT', 'BTC', 'USDT')
    ]
    
    for exchange, symbol_name, base, quote in test_cases:
        normalized = discovery.normalize_symbol(exchange, symbol_name, base, quote)
        print(f"  {exchange}: {symbol_name} -> {normalized}")
    
    # Test symbol denormalization
    print("\n2. Testing symbol denormalization:")
    denormalize_cases = [
        ('binance', 'ETH-BTC'),
        ('okx', 'USDT-SGD'),
        ('deribit', 'BTC-USDC'),
        ('bybit', 'BTC-USDT')
    ]
    
    for exchange, normalized_symbol in denormalize_cases:
        denormalized = discovery.denormalize_symbol(exchange, normalized_symbol)
        print(f"  {exchange}: {normalized_symbol} -> {denormalized}")
    
    print("\nSymbolDiscovery implementation test completed successfully!")

if __name__ == "__main__":
    test_symbol_discovery()