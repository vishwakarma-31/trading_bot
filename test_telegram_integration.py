import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test the symbol normalization logic that was added to the Telegram bot
def test_telegram_symbol_normalization():
    print("Testing Telegram bot symbol normalization logic...")
    
    # Sample symbols from different exchanges
    test_cases = [
        # (exchange, original_symbol, expected_normalized)
        ('binance', 'ETHBTC', 'ETH-BTC'),
        ('binance', 'BTCUSDT', 'BTC-USDT'),
        ('okx', 'USDT-SGD', 'USDT-SGD'),
        ('deribit', 'BTC_USDC', 'BTC-USDC'),
        ('bybit', 'BTCUSDT', 'BTC-USDT'),
        ('bybit', 'ETHUSDT', 'ETH-USDT'),
    ]
    
    print("\nTesting symbol normalization:")
    for exchange, symbol, expected in test_cases:
        # Normalize symbol format to BASE-QUOTE (logic from _list_symbols_command)
        if '_' in symbol:
            normalized_symbol = symbol.replace('_', '-')
        elif exchange in ['binance', 'bybit'] and len(symbol) > 5:
            # For Binance/Bybit, split the symbol (e.g., BTCUSDT -> BTC-USDT)
            if symbol.endswith('USDT'):
                base = symbol[:-4]
                quote = 'USDT'
                normalized_symbol = f"{base}-{quote}"
            elif symbol.endswith('USDC'):
                base = symbol[:-4]
                quote = 'USDC'
                normalized_symbol = f"{base}-{quote}"
            elif symbol.endswith('BTC'):
                base = symbol[:-3]
                quote = 'BTC'
                normalized_symbol = f"{base}-{quote}"
            elif symbol.endswith('BNB'):
                base = symbol[:-3]
                quote = 'BNB'
                normalized_symbol = f"{base}-{quote}"
            elif symbol.endswith('ETH'):
                base = symbol[:-3]
                quote = 'ETH'
                normalized_symbol = f"{base}-{quote}"
            else:
                # For other symbols, try to split intelligently
                # This is a simple heuristic - real implementation would use symbol discovery
                if len(symbol) > 6:
                    # Assume format like ETHBTC where base is variable length
                    # Try common quote currencies first
                    for quote_currency in ['USDT', 'USDC', 'BTC', 'BNB', 'ETH']:
                        if symbol.endswith(quote_currency):
                            base = symbol[:-len(quote_currency)]
                            normalized_symbol = f"{base}-{quote_currency}"
                            break
                    else:
                        # Default case - split in middle
                        mid = len(symbol) // 2
                        base = symbol[:mid]
                        quote = symbol[mid:]
                        normalized_symbol = f"{base}-{quote}"
                else:
                    normalized_symbol = symbol
        else:
            normalized_symbol = symbol
            
        print(f"  {exchange}: {symbol} -> {normalized_symbol} {'✓' if normalized_symbol == expected else '✗'}")

    print("\nTelegram bot symbol normalization test completed!")

if __name__ == "__main__":
    test_telegram_symbol_normalization()