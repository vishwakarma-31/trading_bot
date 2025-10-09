import unittest
from unittest.mock import Mock, patch
import requests
from typing import List, Dict
from data_acquisition.symbol_discovery import (
    SymbolDiscovery, 
    SymbolDiscoveryError, 
    InvalidExchangeError, 
    APIConnectionError,
    SymbolNotFoundError,
    SymbolFormatError
)
from config.config_manager import ConfigManager


class TestSymbolDiscovery(unittest.TestCase):
    """Test cases for SymbolDiscovery class"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = Mock(spec=ConfigManager)
        self.discovery = SymbolDiscovery(config)
        
        # Sample symbol data for testing
        self.sample_binance_symbols = [
            {
                "name": "ETHBTC",
                "base": "ETH",
                "quote": "BTC",
                "instrument_type": "spot",
                "min_size": "0.001",
                "tick_size": "0.000001",
                "lot_size": "0.001"
            },
            {
                "name": "BTCUSDT",
                "base": "BTC",
                "quote": "USDT",
                "instrument_type": "spot",
                "min_size": "0.00001",
                "tick_size": "0.1",
                "lot_size": "0.00001"
            }
        ]
        
        self.sample_okx_symbols = [
            {
                "name": "USDT-SGD",
                "base": "USDT",
                "quote": "SGD",
                "instrument_type": "spot",
                "min_size": "0.1",
                "tick_size": "0.0001",
                "lot_size": "0.1"
            },
            {
                "name": "BTC-USDT",
                "base": "BTC",
                "quote": "USDT",
                "instrument_type": "spot",
                "min_size": "0.0001",
                "tick_size": "0.1",
                "lot_size": "0.0001"
            }
        ]
        
        self.sample_deribit_symbols = [
            {
                "name": "BTC_USDC",
                "base": "BTC",
                "quote": "USDC",
                "instrument_type": "spot",
                "min_size": "0.0001",
                "tick_size": "0.1",
                "lot_size": "0.0001"
            },
            {
                "name": "ETH_USDC",
                "base": "ETH",
                "quote": "USDC",
                "instrument_type": "spot",
                "min_size": "0.001",
                "tick_size": "0.01",
                "lot_size": "0.001"
            }
        ]
        
        self.sample_bybit_symbols = [
            {
                "name": "BTCUSDT",
                "base": "BTC",
                "quote": "USDT",
                "instrument_type": "spot",
                "min_size": "0.0001",
                "tick_size": "0.1",
                "lot_size": "0.0001"
            },
            {
                "name": "ETHUSDT",
                "base": "ETH",
                "quote": "USDT",
                "instrument_type": "spot",
                "min_size": "0.001",
                "tick_size": "0.01",
                "lot_size": "0.001"
            }
        ]
    
    def test_normalize_binance_symbol(self):
        """Test normalization of Binance symbol format"""
        result = self.discovery.normalize_symbol('binance', 'ETHBTC', 'ETH', 'BTC')
        self.assertEqual(result, 'ETH-BTC')
        
        result = self.discovery.normalize_symbol('binance', 'BTCUSDT', 'BTC', 'USDT')
        self.assertEqual(result, 'BTC-USDT')
    
    def test_normalize_okx_symbol(self):
        """Test normalization of OKX symbol format"""
        result = self.discovery.normalize_symbol('okx', 'USDT-SGD', 'USDT', 'SGD')
        self.assertEqual(result, 'USDT-SGD')
        
        result = self.discovery.normalize_symbol('okx', 'BTC-USDT', 'BTC', 'USDT')
        self.assertEqual(result, 'BTC-USDT')
    
    def test_normalize_deribit_symbol(self):
        """Test normalization of Deribit symbol format"""
        result = self.discovery.normalize_symbol('deribit', 'BTC_USDC', 'BTC', 'USDC')
        self.assertEqual(result, 'BTC-USDC')
        
        result = self.discovery.normalize_symbol('deribit', 'ETH_USDC', 'ETH', 'USDC')
        self.assertEqual(result, 'ETH-USDC')
    
    def test_normalize_bybit_symbol(self):
        """Test normalization of Bybit symbol format"""
        result = self.discovery.normalize_symbol('bybit', 'BTCUSDT', 'BTC', 'USDT')
        self.assertEqual(result, 'BTC-USDT')
        
        result = self.discovery.normalize_symbol('bybit', 'ETHUSDT', 'ETH', 'USDT')
        self.assertEqual(result, 'ETH-USDT')
    
    def test_denormalize_binance_symbol(self):
        """Test denormalization to Binance symbol format"""
        result = self.discovery.denormalize_symbol('binance', 'ETH-BTC')
        self.assertEqual(result, 'ETHBTC')
        
        result = self.discovery.denormalize_symbol('binance', 'BTC-USDT')
        self.assertEqual(result, 'BTCUSDT')
    
    def test_denormalize_okx_symbol(self):
        """Test denormalization to OKX symbol format"""
        result = self.discovery.denormalize_symbol('okx', 'USDT-SGD')
        self.assertEqual(result, 'USDT-SGD')
        
        result = self.discovery.denormalize_symbol('okx', 'BTC-USDT')
        self.assertEqual(result, 'BTC-USDT')
    
    def test_denormalize_deribit_symbol(self):
        """Test denormalization to Deribit symbol format"""
        result = self.discovery.denormalize_symbol('deribit', 'BTC-USDC')
        self.assertEqual(result, 'BTC_USDC')
        
        result = self.discovery.denormalize_symbol('deribit', 'ETH-USDC')
        self.assertEqual(result, 'ETH_USDC')
    
    def test_denormalize_bybit_symbol(self):
        """Test denormalization to Bybit symbol format"""
        result = self.discovery.denormalize_symbol('bybit', 'BTC-USDT')
        self.assertEqual(result, 'BTCUSDT')
        
        result = self.discovery.denormalize_symbol('bybit', 'ETH-USDT')
        self.assertEqual(result, 'ETHUSDT')
    
    def test_normalize_invalid_exchange(self):
        """Test normalization with invalid exchange"""
        with self.assertRaises(InvalidExchangeError):
            self.discovery.normalize_symbol('invalid_exchange', 'BTCUSDT', 'BTC', 'USDT')
    
    def test_denormalize_invalid_exchange(self):
        """Test denormalization with invalid exchange"""
        with self.assertRaises(InvalidExchangeError):
            self.discovery.denormalize_symbol('invalid_exchange', 'BTC-USDT')
    
    def test_denormalize_invalid_format(self):
        """Test denormalization with invalid symbol format"""
        with self.assertRaises(SymbolFormatError):
            self.discovery.denormalize_symbol('binance', 'INVALID_FORMAT')  # No dash
    
    @patch('data_acquisition.symbol_discovery.requests.Session.get')
    def test_get_available_symbols_success(self, mock_get):
        """Test successful symbol fetching"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = self.sample_binance_symbols
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test fetching symbols
        symbols = self.discovery.get_available_symbols('binance')
        
        # Verify results
        self.assertEqual(len(symbols), 2)
        self.assertEqual(symbols[0]['exchange'], 'binance')
        self.assertEqual(symbols[0]['original_name'], 'ETHBTC')
        self.assertEqual(symbols[0]['normalized_name'], 'ETH-BTC')
        self.assertEqual(symbols[0]['base'], 'ETH')
        self.assertEqual(symbols[0]['quote'], 'BTC')
    
    @patch('data_acquisition.symbol_discovery.requests.Session.get')
    def test_get_available_symbols_invalid_exchange(self, mock_get):
        """Test symbol fetching with invalid exchange"""
        with self.assertRaises(InvalidExchangeError):
            self.discovery.get_available_symbols('invalid_exchange')
    
    @patch('data_acquisition.symbol_discovery.requests.Session.get')
    def test_get_available_symbols_api_error(self, mock_get):
        """Test symbol fetching with API error"""
        # Mock connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with self.assertRaises(APIConnectionError):
            self.discovery.get_available_symbols('binance')
    
    @patch('data_acquisition.symbol_discovery.requests.Session.get')
    def test_get_available_symbols_json_error(self, mock_get):
        """Test symbol fetching with JSON parsing error"""
        # Mock JSON parsing error
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with self.assertRaises(SymbolDiscoveryError):
            self.discovery.get_available_symbols('binance')
    
    def test_get_symbol_names_normalized(self):
        """Test getting normalized symbol names"""
        # Mock the get_available_symbols method
        with patch.object(self.discovery, 'get_available_symbols') as mock_get_symbols:
            mock_get_symbols.return_value = [
                {
                    'exchange': 'binance',
                    'original_name': 'ETHBTC',
                    'normalized_name': 'ETH-BTC',
                    'base': 'ETH',
                    'quote': 'BTC',
                    'instrument_type': 'spot',
                    'min_size': '0.001',
                    'tick_size': '0.000001',
                    'lot_size': '0.001'
                },
                {
                    'exchange': 'binance',
                    'original_name': 'BTCUSDT',
                    'normalized_name': 'BTC-USDT',
                    'base': 'BTC',
                    'quote': 'USDT',
                    'instrument_type': 'spot',
                    'min_size': '0.00001',
                    'tick_size': '0.1',
                    'lot_size': '0.00001'
                }
            ]
            
            # Test getting normalized names
            names = self.discovery.get_symbol_names('binance', normalized=True)
            self.assertEqual(names, ['ETH-BTC', 'BTC-USDT'])
    
    def test_get_symbol_names_original(self):
        """Test getting original symbol names"""
        # Mock the get_available_symbols method
        with patch.object(self.discovery, 'get_available_symbols') as mock_get_symbols:
            mock_get_symbols.return_value = [
                {
                    'exchange': 'binance',
                    'original_name': 'ETHBTC',
                    'normalized_name': 'ETH-BTC',
                    'base': 'ETH',
                    'quote': 'BTC',
                    'instrument_type': 'spot',
                    'min_size': '0.001',
                    'tick_size': '0.000001',
                    'lot_size': '0.001'
                },
                {
                    'exchange': 'binance',
                    'original_name': 'BTCUSDT',
                    'normalized_name': 'BTC-USDT',
                    'base': 'BTC',
                    'quote': 'USDT',
                    'instrument_type': 'spot',
                    'min_size': '0.00001',
                    'tick_size': '0.1',
                    'lot_size': '0.00001'
                }
            ]
            
            # Test getting original names
            names = self.discovery.get_symbol_names('binance', normalized=False)
            self.assertEqual(names, ['ETHBTC', 'BTCUSDT'])
    
    def test_get_all_symbol_names(self):
        """Test getting all symbol names"""
        # Mock the get_all_symbols method
        with patch.object(self.discovery, 'get_all_symbols') as mock_get_all:
            mock_get_all.return_value = {
                'binance': [
                    {
                        'exchange': 'binance',
                        'original_name': 'ETHBTC',
                        'normalized_name': 'ETH-BTC',
                        'base': 'ETH',
                        'quote': 'BTC',
                        'instrument_type': 'spot',
                        'min_size': '0.001',
                        'tick_size': '0.000001',
                        'lot_size': '0.001'
                    }
                ],
                'okx': [
                    {
                        'exchange': 'okx',
                        'original_name': 'BTC-USDT',
                        'normalized_name': 'BTC-USDT',
                        'base': 'BTC',
                        'quote': 'USDT',
                        'instrument_type': 'spot',
                        'min_size': '0.0001',
                        'tick_size': '0.1',
                        'lot_size': '0.0001'
                    }
                ]
            }
            
            # Test getting normalized names
            all_names = self.discovery.get_all_symbol_names(normalized=True)
            self.assertIn('binance', all_names)
            self.assertIn('okx', all_names)
            self.assertEqual(all_names['binance'], ['ETH-BTC'])
            self.assertEqual(all_names['okx'], ['BTC-USDT'])
            
            # Test getting original names
            all_names = self.discovery.get_all_symbol_names(normalized=False)
            self.assertEqual(all_names['binance'], ['ETHBTC'])
            self.assertEqual(all_names['okx'], ['BTC-USDT'])
    
    def test_validate_symbol_normalized(self):
        """Test symbol validation with normalized name"""
        # Mock the get_available_symbols method
        with patch.object(self.discovery, 'get_available_symbols') as mock_get_symbols:
            mock_get_symbols.return_value = [
                {
                    'exchange': 'binance',
                    'original_name': 'ETHBTC',
                    'normalized_name': 'ETH-BTC',
                    'base': 'ETH',
                    'quote': 'BTC',
                    'instrument_type': 'spot',
                    'min_size': '0.001',
                    'tick_size': '0.000001',
                    'lot_size': '0.001'
                }
            ]
            
            # Test valid symbol
            result = self.discovery.validate_symbol('binance', 'ETH-BTC', is_normalized=True)
            self.assertTrue(result)
            
            # Test invalid symbol
            result = self.discovery.validate_symbol('binance', 'INVALID-SYMBOL', is_normalized=True)
            self.assertFalse(result)
    
    def test_validate_symbol_original(self):
        """Test symbol validation with original name"""
        # Mock the get_available_symbols method
        with patch.object(self.discovery, 'get_available_symbols') as mock_get_symbols:
            mock_get_symbols.return_value = [
                {
                    'exchange': 'binance',
                    'original_name': 'ETHBTC',
                    'normalized_name': 'ETH-BTC',
                    'base': 'ETH',
                    'quote': 'BTC',
                    'instrument_type': 'spot',
                    'min_size': '0.001',
                    'tick_size': '0.000001',
                    'lot_size': '0.001'
                }
            ]
            
            # Test valid symbol
            result = self.discovery.validate_symbol('binance', 'ETHBTC', is_normalized=False)
            self.assertTrue(result)
            
            # Test invalid symbol
            result = self.discovery.validate_symbol('binance', 'INVALIDSYMBOL', is_normalized=False)
            self.assertFalse(result)
    
    def test_get_symbol_info(self):
        """Test getting symbol information"""
        # Mock the get_available_symbols method
        with patch.object(self.discovery, 'get_available_symbols') as mock_get_symbols:
            mock_get_symbols.return_value = [
                {
                    'exchange': 'binance',
                    'original_name': 'ETHBTC',
                    'normalized_name': 'ETH-BTC',
                    'base': 'ETH',
                    'quote': 'BTC',
                    'instrument_type': 'spot',
                    'min_size': '0.001',
                    'tick_size': '0.000001',
                    'lot_size': '0.001'
                }
            ]
            
            # Test getting info for valid symbol
            info = self.discovery.get_symbol_info('binance', 'ETH-BTC', is_normalized=True)
            self.assertIsNotNone(info)
            if info is not None:
                self.assertEqual(info['original_name'], 'ETHBTC')
                self.assertEqual(info['normalized_name'], 'ETH-BTC')
            
            # Test getting info for invalid symbol
            info = self.discovery.get_symbol_info('binance', 'INVALID-SYMBOL', is_normalized=True)
            self.assertIsNone(info)
    
    def test_find_common_symbols(self):
        """Test finding common symbols across exchanges"""
        # Mock the get_symbol_names method
        def mock_get_symbol_names(exchange, normalized=True):
            if exchange == 'binance':
                return ['ETH-BTC', 'BTC-USDT', 'BNB-USDT']
            elif exchange == 'okx':
                return ['ETH-BTC', 'BTC-USDT', 'LTC-USDT']
            elif exchange == 'bybit':
                return ['ETH-BTC', 'BTC-USDT', 'XRP-USDT']
            elif exchange == 'deribit':
                return ['BTC-USDT', 'ETH-USDT']
            return []
        
        with patch.object(self.discovery, 'get_symbol_names', side_effect=mock_get_symbol_names):
            # Test finding common symbols across all exchanges
            common_symbols = self.discovery.find_common_symbols()
            self.assertIn('BTC-USDT', common_symbols)
            self.assertEqual(len(common_symbols), 1)
    
    def test_find_common_symbols_specific_exchanges(self):
        """Test finding common symbols across specific exchanges"""
        # Mock the get_symbol_names method
        def mock_get_symbol_names(exchange, normalized=True):
            if exchange == 'binance':
                return ['ETH-BTC', 'BTC-USDT']
            elif exchange == 'okx':
                return ['ETH-BTC', 'BTC-USDT', 'LTC-USDT']
            return []
        
        with patch.object(self.discovery, 'get_symbol_names', side_effect=mock_get_symbol_names):
            # Test finding common symbols across specific exchanges
            common_symbols = self.discovery.find_common_symbols(['binance', 'okx'])
            self.assertIn('ETH-BTC', common_symbols)
            self.assertIn('BTC-USDT', common_symbols)
            self.assertEqual(len(common_symbols), 2)
    
    def test_find_common_symbols_invalid_exchange(self):
        """Test finding common symbols with invalid exchange"""
        with self.assertRaises(InvalidExchangeError):
            self.discovery.find_common_symbols(['invalid_exchange'])
    
    def test_cache_functionality(self):
        """Test caching functionality"""
        # Mock the API call
        with patch('data_acquisition.symbol_discovery.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_binance_symbols
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # First call should hit the API
            symbols1 = self.discovery.get_available_symbols('binance')
            
            # Second call should use cache
            symbols2 = self.discovery.get_available_symbols('binance')
            
            # Both should return the same data
            self.assertEqual(symbols1, symbols2)
            # Should only have been called once
            self.assertEqual(mock_get.call_count, 1)
    
    def test_clear_cache(self):
        """Test clearing cache"""
        # Mock the API call
        with patch('data_acquisition.symbol_discovery.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_binance_symbols
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Make a call to populate cache
            self.discovery.get_available_symbols('binance')
            
            # Clear cache for specific exchange
            self.discovery.clear_cache('binance')
            
            # Make another call - should hit API again
            self.discovery.get_available_symbols('binance')
            
            # Should have been called twice now
            self.assertEqual(mock_get.call_count, 2)
            
            # Clear all cache
            self.discovery.clear_cache()
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        # Mock the API call and time
        with patch('data_acquisition.symbol_discovery.requests.Session.get') as mock_get, \
             patch('data_acquisition.symbol_discovery.time') as mock_time:
            
            mock_response = Mock()
            mock_response.json.return_value = self.sample_binance_symbols
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Set time for first call
            mock_time.time.return_value = 1000000
            
            # First call should hit the API
            symbols1 = self.discovery.get_available_symbols('binance')
            
            # Set time to simulate cache expiration (1 hour + 1 second)
            mock_time.time.return_value = 1000000 + 3601
            
            # Second call should hit API again due to expiration
            symbols2 = self.discovery.get_available_symbols('binance')
            
            # Both should return the same data
            self.assertEqual(symbols1, symbols2)
            # Should have been called twice
            self.assertEqual(mock_get.call_count, 2)


if __name__ == '__main__':
    unittest.main()