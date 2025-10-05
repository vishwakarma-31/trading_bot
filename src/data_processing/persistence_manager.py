"""
Persistence Manager for the GoQuant Trading Bot
Handles saving and restoring monitoring states and configurations.
"""
import json
import os
import logging
import threading
import time
from typing import Dict, List, Any
from datetime import datetime

class PersistenceManager:
    """Manages persistence of monitoring states and configurations"""
    
    def __init__(self, persistence_file: str = "persistence_data.json"):
        """Initialize persistence manager"""
        self.persistence_file = persistence_file
        self.logger = logging.getLogger(__name__)
        self.monitoring_data = {
            'arbitrage_monitoring': {
                'active': False,
                'assets': {},
                'thresholds': {
                    'percentage': 0.5,
                    'absolute': 1.0
                },
                'start_time': None
            },
            'market_view_monitoring': {
                'active': False,
                'symbols': {},
                'start_time': None
            },
            'last_updated': None
        }
        self.save_thread = None
        self.save_interval = 30  # Save every 30 seconds
        self.running = False
        
        # Load existing persistence data
        self.load_persistence_data()
        
    def start_auto_save(self):
        """Start automatic saving of monitoring states"""
        if not self.running:
            self.running = True
            self.save_thread = threading.Thread(target=self._auto_save_loop)
            self.save_thread.daemon = True
            self.save_thread.start()
            self.logger.info("Persistence auto-save started")
        
    def stop_auto_save(self):
        """Stop automatic saving"""
        self.running = False
        if self.save_thread and self.save_thread.is_alive():
            self.save_thread.join()
        self.logger.info("Persistence auto-save stopped")
        
    def _auto_save_loop(self):
        """Background loop for automatic saving"""
        while self.running:
            try:
                self.save_persistence_data()
                time.sleep(self.save_interval)
            except Exception as e:
                self.logger.error(f"Error in auto-save loop: {e}")
                
    def update_arbitrage_state(self, active: bool, assets: Dict[str, List[str]], 
                             threshold_percentage: float = 0.5, 
                             threshold_absolute: float = 1.0):
        """
        Update arbitrage monitoring state
        
        Args:
            active (bool): Whether arbitrage monitoring is active
            assets (Dict[str, List[str]]): Assets being monitored
            threshold_percentage (float): Profit percentage threshold
            threshold_absolute (float): Profit absolute threshold
        """
        self.monitoring_data['arbitrage_monitoring'] = {
            'active': active,
            'assets': assets,
            'thresholds': {
                'percentage': threshold_percentage,
                'absolute': threshold_absolute
            },
            'start_time': datetime.now().isoformat() if active else None
        }
        self.monitoring_data['last_updated'] = datetime.now().isoformat()
        
    def update_market_view_state(self, active: bool, symbols: Dict[str, List[str]]):
        """
        Update market view monitoring state
        
        Args:
            active (bool): Whether market view monitoring is active
            symbols (Dict[str, List[str]]): Symbols being monitored
        """
        self.monitoring_data['market_view_monitoring'] = {
            'active': active,
            'symbols': symbols,
            'start_time': datetime.now().isoformat() if active else None
        }
        self.monitoring_data['last_updated'] = datetime.now().isoformat()
        
    def get_arbitrage_state(self) -> Dict[str, Any]:
        """
        Get saved arbitrage monitoring state
        
        Returns:
            Dict with arbitrage monitoring state
        """
        return self.monitoring_data.get('arbitrage_monitoring', {})
        
    def get_market_view_state(self) -> Dict[str, Any]:
        """
        Get saved market view monitoring state
        
        Returns:
            Dict with market view monitoring state
        """
        return self.monitoring_data.get('market_view_monitoring', {})
        
    def save_persistence_data(self) -> bool:
        """
        Save monitoring states to file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create backup of existing file
            if os.path.exists(self.persistence_file):
                backup_file = f"{self.persistence_file}.backup"
                os.replace(self.persistence_file, backup_file)
                
            # Save current data
            with open(self.persistence_file, 'w') as f:
                json.dump(self.monitoring_data, f, indent=2)
                
            self.logger.info(f"Monitoring states saved to {self.persistence_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving monitoring states to {self.persistence_file}: {e}")
            return False
            
    def load_persistence_data(self) -> bool:
        """
        Load monitoring states from file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'r') as f:
                    self.monitoring_data = json.load(f)
                    
                self.logger.info(f"Monitoring states loaded from {self.persistence_file}")
                return True
            else:
                self.logger.info(f"Monitoring states file {self.persistence_file} not found, using defaults")
                return True
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing monitoring states file {self.persistence_file}: {e}")
            # Try to load from backup
            backup_file = f"{self.persistence_file}.backup"
            if os.path.exists(backup_file):
                self.logger.info(f"Attempting to load from backup file {backup_file}")
                try:
                    with open(backup_file, 'r') as f:
                        self.monitoring_data = json.load(f)
                    self.logger.info(f"Monitoring states loaded from backup {backup_file}")
                    return True
                except Exception as backup_error:
                    self.logger.error(f"Error loading backup monitoring states: {backup_error}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error loading monitoring states from {self.persistence_file}: {e}")
            return False
            
    def clear_persistence_data(self) -> bool:
        """
        Clear all saved monitoring states
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.monitoring_data = {
                'arbitrage_monitoring': {
                    'active': False,
                    'assets': {},
                    'thresholds': {
                        'percentage': 0.5,
                        'absolute': 1.0
                    },
                    'start_time': None
                },
                'market_view_monitoring': {
                    'active': False,
                    'symbols': {},
                    'start_time': None
                },
                'last_updated': None
            }
            
            # Save cleared data
            return self.save_persistence_data()
            
        except Exception as e:
            self.logger.error(f"Error clearing monitoring states: {e}")
            return False