"""
Unit tests for the Arbitrage Statistics module
"""
import unittest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from arbitrage_statistics import ArbitrageLogger, ArbitrageStatistics
# We can't import ArbitrageOpportunity directly due to circular imports
from dataclasses import dataclass

@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity"""
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    profit_percentage: float
    profit_absolute: float
    timestamp: float
    threshold_percentage: float
    threshold_absolute: float

class TestArbitrageStatistics(unittest.TestCase):
    """Test cases for ArbitrageLogger and statistics calculation"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_sqlite_storage(self):
        """Test SQLite storage functionality"""
        # Initialize logger with SQLite storage
        logger = ArbitrageLogger(storage_type="sqlite", storage_path=self.test_dir)
        
        # Create a test opportunity
        opportunity = ArbitrageOpportunity(
            symbol="BTC-USDT",
            buy_exchange="binance",
            sell_exchange="okx",
            buy_price=50000.0,
            sell_price=50100.0,
            profit_percentage=0.2,
            profit_absolute=100.0,
            timestamp=datetime.now().timestamp(),
            threshold_percentage=0.1,
            threshold_absolute=50.0
        )
        
        # Log the opportunity
        logger.log_opportunity(opportunity)
        
        # Get statistics
        stats = logger.get_statistics()
        
        # Verify statistics
        self.assertEqual(stats.total_opportunities, 1)
        self.assertEqual(stats.average_spread, 100.0)
        self.assertEqual(stats.max_spread, 100.0)
        self.assertIn("BTC-USDT", stats.opportunities_by_symbol)
        self.assertEqual(stats.opportunities_by_symbol["BTC-USDT"], 1)
        self.assertIn("binance-okx", stats.opportunities_by_exchange_pair)
        self.assertEqual(stats.opportunities_by_exchange_pair["binance-okx"], 1)
        
        # Close the logger
        logger.close()
        
    def test_csv_storage(self):
        """Test CSV storage functionality"""
        # Initialize logger with CSV storage
        logger = ArbitrageLogger(storage_type="csv", storage_path=self.test_dir)
        
        # Create test opportunities
        opportunities = [
            ArbitrageOpportunity(
                symbol="BTC-USDT",
                buy_exchange="binance",
                sell_exchange="okx",
                buy_price=50000.0,
                sell_price=50100.0,
                profit_percentage=0.2,
                profit_absolute=100.0,
                timestamp=datetime.now().timestamp(),
                threshold_percentage=0.1,
                threshold_absolute=50.0
            ),
            ArbitrageOpportunity(
                symbol="ETH-USDT",
                buy_exchange="okx",
                sell_exchange="bybit",
                buy_price=3000.0,
                sell_price=3010.0,
                profit_percentage=0.33,
                profit_absolute=10.0,
                timestamp=datetime.now().timestamp(),
                threshold_percentage=0.1,
                threshold_absolute=5.0
            )
        ]
        
        # Log the opportunities
        for opp in opportunities:
            logger.log_opportunity(opp)
        
        # Get statistics
        stats = logger.get_statistics()
        
        # Verify statistics
        self.assertEqual(stats.total_opportunities, 2)
        self.assertEqual(stats.average_spread, 55.0)  # (100 + 10) / 2
        self.assertEqual(stats.max_spread, 100.0)
        self.assertIn("BTC-USDT", stats.opportunities_by_symbol)
        self.assertIn("ETH-USDT", stats.opportunities_by_symbol)
        self.assertEqual(stats.opportunities_by_symbol["BTC-USDT"], 1)
        self.assertEqual(stats.opportunities_by_symbol["ETH-USDT"], 1)
        self.assertIn("binance-okx", stats.opportunities_by_exchange_pair)
        self.assertIn("okx-bybit", stats.opportunities_by_exchange_pair)
        self.assertEqual(stats.opportunities_by_exchange_pair["binance-okx"], 1)
        self.assertEqual(stats.opportunities_by_exchange_pair["okx-bybit"], 1)
        
    def test_json_storage(self):
        """Test JSON storage functionality"""
        # Initialize logger with JSON storage
        logger = ArbitrageLogger(storage_type="json", storage_path=self.test_dir)
        
        # Create a test opportunity
        opportunity = ArbitrageOpportunity(
            symbol="BTC-USDT",
            buy_exchange="binance",
            sell_exchange="okx",
            buy_price=50000.0,
            sell_price=50100.0,
            profit_percentage=0.2,
            profit_absolute=100.0,
            timestamp=datetime.now().timestamp(),
            threshold_percentage=0.1,
            threshold_absolute=50.0
        )
        
        # Log the opportunity
        logger.log_opportunity(opportunity)
        
        # Get statistics
        stats = logger.get_statistics()
        
        # Verify statistics
        self.assertEqual(stats.total_opportunities, 1)
        self.assertEqual(stats.average_spread, 100.0)
        self.assertEqual(stats.max_spread, 100.0)
        self.assertIn("BTC-USDT", stats.opportunities_by_symbol)
        self.assertEqual(stats.opportunities_by_symbol["BTC-USDT"], 1)
        self.assertIn("binance-okx", stats.opportunities_by_exchange_pair)
        self.assertEqual(stats.opportunities_by_exchange_pair["binance-okx"], 1)
        
    def test_symbol_filtering(self):
        """Test statistics filtering by symbol"""
        # Initialize logger with SQLite storage
        logger = ArbitrageLogger(storage_type="sqlite", storage_path=self.test_dir)
        
        # Create test opportunities with different symbols
        opportunities = [
            ArbitrageOpportunity(
                symbol="BTC-USDT",
                buy_exchange="binance",
                sell_exchange="okx",
                buy_price=50000.0,
                sell_price=50100.0,
                profit_percentage=0.2,
                profit_absolute=100.0,
                timestamp=datetime.now().timestamp(),
                threshold_percentage=0.1,
                threshold_absolute=50.0
            ),
            ArbitrageOpportunity(
                symbol="ETH-USDT",
                buy_exchange="okx",
                sell_exchange="bybit",
                buy_price=3000.0,
                sell_price=3010.0,
                profit_percentage=0.33,
                profit_absolute=10.0,
                timestamp=datetime.now().timestamp(),
                threshold_percentage=0.1,
                threshold_absolute=5.0
            ),
            ArbitrageOpportunity(
                symbol="BTC-USDT",
                buy_exchange="bybit",
                sell_exchange="deribit",
                buy_price=49900.0,
                sell_price=50050.0,
                profit_percentage=0.3,
                profit_absolute=150.0,
                timestamp=datetime.now().timestamp(),
                threshold_percentage=0.1,
                threshold_absolute=50.0
            )
        ]
        
        # Log the opportunities
        for opp in opportunities:
            logger.log_opportunity(opp)
        
        # Get statistics for BTC-USDT only
        stats = logger.get_statistics(symbol="BTC-USDT")
        
        # Verify filtered statistics
        self.assertEqual(stats.total_opportunities, 2)
        self.assertEqual(stats.average_spread, 125.0)  # (100 + 150) / 2
        self.assertEqual(stats.max_spread, 150.0)
        self.assertIn("BTC-USDT", stats.opportunities_by_symbol)
        self.assertEqual(len(stats.opportunities_by_symbol), 1)  # Only BTC-USDT
        self.assertEqual(stats.opportunities_by_symbol["BTC-USDT"], 2)
        
        # Close the logger
        logger.close()
        
    def test_time_filtering(self):
        """Test statistics filtering by time period"""
        # Initialize logger with SQLite storage
        logger = ArbitrageLogger(storage_type="sqlite", storage_path=self.test_dir)
        
        # Create test opportunities with different timestamps
        now = datetime.now().timestamp()
        one_hour_ago = now - 3600
        two_hours_ago = now - 7200
        one_day_ago = now - 86400
        
        opportunities = [
            ArbitrageOpportunity(
                symbol="BTC-USDT",
                buy_exchange="binance",
                sell_exchange="okx",
                buy_price=50000.0,
                sell_price=50100.0,
                profit_percentage=0.2,
                profit_absolute=100.0,
                timestamp=now,
                threshold_percentage=0.1,
                threshold_absolute=50.0
            ),
            ArbitrageOpportunity(
                symbol="ETH-USDT",
                buy_exchange="okx",
                sell_exchange="bybit",
                buy_price=3000.0,
                sell_price=3010.0,
                profit_percentage=0.33,
                profit_absolute=10.0,
                timestamp=one_hour_ago,
                threshold_percentage=0.1,
                threshold_absolute=5.0
            ),
            ArbitrageOpportunity(
                symbol="BTC-USDT",
                buy_exchange="bybit",
                sell_exchange="deribit",
                buy_price=49900.0,
                sell_price=50050.0,
                profit_percentage=0.3,
                profit_absolute=150.0,
                timestamp=two_hours_ago,
                threshold_percentage=0.1,
                threshold_absolute=50.0
            ),
            ArbitrageOpportunity(
                symbol="LTC-USDT",
                buy_exchange="binance",
                sell_exchange="deribit",
                buy_price=150.0,
                sell_price=151.0,
                profit_percentage=0.67,
                profit_absolute=1.0,
                timestamp=one_day_ago,
                threshold_percentage=0.1,
                threshold_absolute=0.5
            )
        ]
        
        # Log the opportunities
        for opp in opportunities:
            logger.log_opportunity(opp)
        
        # Get statistics for last 3 hours (should exclude the one from a day ago)
        stats = logger.get_statistics(hours=3)
        
        # Verify time-filtered statistics
        self.assertEqual(stats.total_opportunities, 3)
        self.assertEqual(stats.average_spread, 86.67)  # (100 + 10 + 150) / 3
        self.assertEqual(stats.max_spread, 150.0)
        self.assertIn("BTC-USDT", stats.opportunities_by_symbol)
        self.assertIn("ETH-USDT", stats.opportunities_by_symbol)
        self.assertNotIn("LTC-USDT", stats.opportunities_by_symbol)  # Should be filtered out
        
        # Close the logger
        logger.close()

if __name__ == '__main__':
    unittest.main()