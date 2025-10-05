"""
Unit tests for the Persistence Manager module
"""
import unittest
import os
import tempfile
import shutil
import json
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from persistence_manager import PersistenceManager

class TestPersistenceManager(unittest.TestCase):
    """Test cases for PersistenceManager"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.persistence_file = os.path.join(self.test_dir, "test_persistence.json")
        
    def tearDown(self):
        """Clean up test environment"""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_initialization(self):
        """Test PersistenceManager initialization"""
        # Initialize persistence manager
        pm = PersistenceManager(self.persistence_file)
        
        # Verify initial state
        arb_state = pm.get_arbitrage_state()
        mv_state = pm.get_market_view_state()
        
        self.assertFalse(arb_state.get('active', True))  # Should be False by default
        self.assertFalse(mv_state.get('active', True))   # Should be False by default
        self.assertEqual(arb_state.get('assets', {}), {})
        self.assertEqual(mv_state.get('symbols', {}), {})
        
    def test_update_arbitrage_state(self):
        """Test updating arbitrage monitoring state"""
        # Initialize persistence manager
        pm = PersistenceManager(self.persistence_file)
        
        # Update arbitrage state
        assets = {
            "BTC-USDT": ["binance", "okx"],
            "ETH-USDT": ["okx", "bybit"]
        }
        pm.update_arbitrage_state(
            active=True,
            assets=assets,
            threshold_percentage=1.0,
            threshold_absolute=2.0
        )
        
        # Verify state update
        arb_state = pm.get_arbitrage_state()
        self.assertTrue(arb_state.get('active'))
        self.assertEqual(arb_state.get('assets'), assets)
        self.assertEqual(arb_state['thresholds']['percentage'], 1.0)
        self.assertEqual(arb_state['thresholds']['absolute'], 2.0)
        self.assertIsNotNone(arb_state.get('start_time'))
        
    def test_update_market_view_state(self):
        """Test updating market view monitoring state"""
        # Initialize persistence manager
        pm = PersistenceManager(self.persistence_file)
        
        # Update market view state
        symbols = {
            "BTC-USDT": ["binance", "okx", "bybit"],
            "ETH-USDT": ["okx", "bybit", "deribit"]
        }
        pm.update_market_view_state(
            active=True,
            symbols=symbols
        )
        
        # Verify state update
        mv_state = pm.get_market_view_state()
        self.assertTrue(mv_state.get('active'))
        self.assertEqual(mv_state.get('symbols'), symbols)
        self.assertIsNotNone(mv_state.get('start_time'))
        
    def test_save_and_load_persistence_data(self):
        """Test saving and loading persistence data"""
        # Initialize first persistence manager and set some data
        pm1 = PersistenceManager(self.persistence_file)
        
        # Set arbitrage state
        assets = {"BTC-USDT": ["binance", "okx"]}
        pm1.update_arbitrage_state(
            active=True,
            assets=assets,
            threshold_percentage=1.5,
            threshold_absolute=3.0
        )
        
        # Set market view state
        symbols = {"ETH-USDT": ["okx", "bybit"]}
        pm1.update_market_view_state(
            active=True,
            symbols=symbols
        )
        
        # Save data
        self.assertTrue(pm1.save_persistence_data())
        
        # Initialize second persistence manager to load data
        pm2 = PersistenceManager(self.persistence_file)
        
        # Verify loaded data
        arb_state = pm2.get_arbitrage_state()
        mv_state = pm2.get_market_view_state()
        
        self.assertTrue(arb_state.get('active'))
        self.assertEqual(arb_state.get('assets'), assets)
        self.assertEqual(arb_state['thresholds']['percentage'], 1.5)
        self.assertEqual(arb_state['thresholds']['absolute'], 3.0)
        
        self.assertTrue(mv_state.get('active'))
        self.assertEqual(mv_state.get('symbols'), symbols)
        
    def test_clear_persistence_data(self):
        """Test clearing persistence data"""
        # Initialize persistence manager and set some data
        pm = PersistenceManager(self.persistence_file)
        
        # Set some data
        pm.update_arbitrage_state(
            active=True,
            assets={"BTC-USDT": ["binance", "okx"]}
        )
        pm.update_market_view_state(
            active=True,
            symbols={"ETH-USDT": ["okx", "bybit"]}
        )
        
        # Save data
        pm.save_persistence_data()
        
        # Clear data
        self.assertTrue(pm.clear_persistence_data())
        
        # Verify data is cleared
        arb_state = pm.get_arbitrage_state()
        mv_state = pm.get_market_view_state()
        
        self.assertFalse(arb_state.get('active'))
        self.assertEqual(arb_state.get('assets'), {})
        self.assertFalse(mv_state.get('active'))
        self.assertEqual(mv_state.get('symbols'), {})
        
    def test_file_backup(self):
        """Test file backup functionality"""
        # Create initial data file
        initial_data = {
            "arbitrage_monitoring": {
                "active": True,
                "assets": {"BTC-USDT": ["binance", "okx"]},
                "thresholds": {"percentage": 0.5, "absolute": 1.0},
                "start_time": "2023-01-01T00:00:00"
            },
            "market_view_monitoring": {
                "active": False,
                "symbols": {},
                "start_time": None
            },
            "last_updated": "2023-01-01T00:00:00"
        }
        
        with open(self.persistence_file, 'w') as f:
            json.dump(initial_data, f)
            
        # Initialize persistence manager
        pm = PersistenceManager(self.persistence_file)
        
        # Update some data and save (should create backup)
        pm.update_arbitrage_state(active=False, assets={})
        self.assertTrue(pm.save_persistence_data())
        
        # Check if backup file exists
        backup_file = f"{self.persistence_file}.backup"
        self.assertTrue(os.path.exists(backup_file))
        
        # Verify backup content matches original data
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
            
        self.assertEqual(backup_data, initial_data)

if __name__ == '__main__':
    unittest.main()