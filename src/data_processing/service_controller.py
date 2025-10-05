"""
Service Controller for the GoQuant Trading Bot
Manages the lifecycle of both Arbitrage Signal Service and Market View Service
"""
import logging
import threading
import time
from typing import Dict, List, Optional, Set
from data_processing.arbitrage_detector import ArbitrageDetector
from data_processing.market_view import MarketViewManager
from data_processing.persistence_manager import PersistenceManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from config.config_manager import ConfigManager

class ServiceController:
    """Manages the lifecycle of both monitoring services"""
    
    def __init__(self, market_fetcher: MarketDataFetcher, config: ConfigManager):
        """Initialize service controller"""
        self.market_fetcher = market_fetcher
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.arbitrage_detector = ArbitrageDetector(market_fetcher, config)
        self.market_view_manager = MarketViewManager(market_fetcher)
        
        # Initialize persistence manager
        self.persistence_manager = PersistenceManager()
        
        # Service state tracking
        self.arbitrage_monitoring = False
        self.market_view_monitoring = False
        self.arbitrage_thread = None
        self.market_view_thread = None
        
        # Track active monitoring tasks
        self.arbitrage_assets: Dict[str, List[str]] = {}  # symbol -> exchanges
        self.market_view_symbols: Dict[str, List[str]] = {}  # symbol -> exchanges
        
        # Track last update timestamps
        self.last_arbitrage_update = 0
        self.last_market_view_update = 0
        
        # Load saved monitoring states
        self._load_saved_states()
        
        self.logger.info("Service controller initialized")
        
    def _load_saved_states(self):
        """Load saved monitoring states on startup"""
        try:
            # Load arbitrage state
            arb_state = self.persistence_manager.get_arbitrage_state()
            if arb_state.get('active', False):
                self.logger.info("Found saved arbitrage monitoring state, restoring...")
                # We don't automatically start monitoring on load, but we preserve the configuration
                self.arbitrage_assets = arb_state.get('assets', {})
                thresholds = arb_state.get('thresholds', {})
                if thresholds:
                    self.arbitrage_detector.set_thresholds(
                        thresholds.get('percentage', 0.5),
                        thresholds.get('absolute', 1.0)
                    )
                
            # Load market view state
            mv_state = self.persistence_manager.get_market_view_state()
            if mv_state.get('active', False):
                self.logger.info("Found saved market view monitoring state, restoring...")
                # We don't automatically start monitoring on load, but we preserve the configuration
                self.market_view_symbols = mv_state.get('symbols', {})
                
        except Exception as e:
            self.logger.error(f"Error loading saved states: {e}")
        
    # Arbitrage Signal Service Methods
    
    def start_arbitrage_monitoring(self, asset_exchanges: Dict[str, List[str]], 
                                 threshold_percentage: float = None, 
                                 threshold_absolute: float = None) -> bool:
        """
        Start arbitrage monitoring with user-specified parameters
        
        Args:
            asset_exchanges (Dict[str, List[str]]): Mapping of assets to exchange lists
            threshold_percentage (float): Minimum profit percentage threshold
            threshold_absolute (float): Minimum profit absolute value threshold
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.arbitrage_monitoring:
                self.logger.warning("Arbitrage monitoring is already running")
                return False
                
            # Set thresholds if provided
            if threshold_percentage is not None or threshold_absolute is not None:
                self.arbitrage_detector.set_thresholds(threshold_percentage, threshold_absolute)
                
            # Store monitoring configuration
            self.arbitrage_assets = asset_exchanges
            
            # Start monitoring
            self.arbitrage_monitoring = True
            self.logger.info(f"Starting arbitrage monitoring for {len(asset_exchanges)} assets")
            
            # Start monitoring thread
            self.arbitrage_thread = threading.Thread(target=self._arbitrage_monitoring_loop)
            self.arbitrage_thread.daemon = True
            self.arbitrage_thread.start()
            
            # Save monitoring state
            self.persistence_manager.update_arbitrage_state(
                active=True,
                assets=asset_exchanges,
                threshold_percentage=self.arbitrage_detector.thresholds.min_profit_percentage,
                threshold_absolute=self.arbitrage_detector.thresholds.min_profit_absolute
            )
            self.persistence_manager.save_persistence_data()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting arbitrage monitoring: {e}")
            self.arbitrage_monitoring = False
            return False
            
    def stop_arbitrage_monitoring(self) -> bool:
        """
        Stop arbitrage monitoring and clean up resources
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.arbitrage_monitoring:
                self.logger.info("Arbitrage monitoring is not running")
                return True
                
            # Stop monitoring
            self.arbitrage_monitoring = False
            
            # Wait for thread to finish
            if self.arbitrage_thread and self.arbitrage_thread.is_alive():
                self.arbitrage_thread.join(timeout=5)
                
            # Clear monitoring data
            self.arbitrage_assets.clear()
            
            # Save monitoring state
            self.persistence_manager.update_arbitrage_state(
                active=False,
                assets={}
            )
            self.persistence_manager.save_persistence_data()
            
            self.logger.info("Stopped arbitrage monitoring")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping arbitrage monitoring: {e}")
            return False
            
    def get_arbitrage_status(self) -> Dict:
        """
        Report current status of arbitrage service
        
        Returns:
            Dict with status information
        """
        try:
            # Get active opportunities from detector
            active_opps = self.arbitrage_detector.active_opportunities if hasattr(self.arbitrage_detector, 'active_opportunities') else {}
            
            return {
                'monitoring': self.arbitrage_monitoring,
                'monitored_assets': self.arbitrage_assets,
                'active_opportunities_count': len(active_opps),
                'last_update': self.last_arbitrage_update,
                'thresholds': {
                    'percentage': self.arbitrage_detector.thresholds.min_profit_percentage,
                    'absolute': self.arbitrage_detector.thresholds.min_profit_absolute
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting arbitrage status: {e}")
            return {
                'monitoring': self.arbitrage_monitoring,
                'monitored_assets': self.arbitrage_assets,
                'active_opportunities_count': 0,
                'last_update': self.last_arbitrage_update,
                'error': str(e)
            }
            
    def _arbitrage_monitoring_loop(self):
        """Background loop for arbitrage monitoring"""
        while self.arbitrage_monitoring:
            try:
                # Check for arbitrage opportunities for each asset
                for asset, exchanges in self.arbitrage_assets.items():
                    opportunities = self.arbitrage_detector.find_arbitrage_opportunities(exchanges, asset)
                    if opportunities:
                        self.logger.info(f"Found {len(opportunities)} opportunities for {asset}")
                        
                # Update timestamp
                self.last_arbitrage_update = time.time()
                
                # Sleep to avoid excessive CPU usage
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in arbitrage monitoring loop: {e}")
                time.sleep(5)  # Sleep longer on error
                
    # Market View Service Methods
    
    def start_market_view_monitoring(self, symbol_exchanges: Dict[str, List[str]]) -> bool:
        """
        Start market view monitoring with user-specified symbols and exchanges
        
        Args:
            symbol_exchanges (Dict[str, List[str]]): Mapping of symbols to exchange lists
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.market_view_monitoring:
                self.logger.warning("Market view monitoring is already running")
                return False
                
            # Store monitoring configuration
            self.market_view_symbols = symbol_exchanges
            
            # Start monitoring through market view manager
            self.market_view_manager.start_monitoring(symbol_exchanges)
            self.market_view_monitoring = True
            self.logger.info(f"Started market view monitoring for {len(symbol_exchanges)} symbols")
            
            # Save monitoring state
            self.persistence_manager.update_market_view_state(
                active=True,
                symbols=symbol_exchanges
            )
            self.persistence_manager.save_persistence_data()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting market view monitoring: {e}")
            self.market_view_monitoring = False
            return False
            
    def stop_market_view_monitoring(self) -> bool:
        """
        Stop market view monitoring and clean up resources
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.market_view_monitoring:
                self.logger.info("Market view monitoring is not running")
                return True
                
            # Stop monitoring through market view manager
            self.market_view_manager.stop_monitoring()
            self.market_view_monitoring = False
            
            # Clear monitoring data
            self.market_view_symbols.clear()
            
            # Save monitoring state
            self.persistence_manager.update_market_view_state(
                active=False,
                symbols={}
            )
            self.persistence_manager.save_persistence_data()
            
            self.logger.info("Stopped market view monitoring")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping market view monitoring: {e}")
            return False
            
    def get_market_view_status(self) -> Dict:
        """
        Report current status of market view service
        
        Returns:
            Dict with status information
        """
        try:
            # Get status from market view manager
            manager_status = self.market_view_manager.get_monitoring_status()
            
            return {
                'monitoring': self.market_view_monitoring,
                'monitored_symbols': self.market_view_symbols,
                'manager_status': manager_status,
                'last_update': self.last_market_view_update,
                'consolidated_views_count': len(self.market_view_manager.consolidated_views) if hasattr(self.market_view_manager, 'consolidated_views') else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting market view status: {e}")
            return {
                'monitoring': self.market_view_monitoring,
                'monitored_symbols': self.market_view_symbols,
                'last_update': self.last_market_view_update,
                'error': str(e)
            }
            
    # Service Management Methods
    
    def get_service_status(self) -> Dict:
        """
        Get overall status of both services
        
        Returns:
            Dict with status of both services
        """
        return {
            'arbitrage_service': self.get_arbitrage_status(),
            'market_view_service': self.get_market_view_status(),
            'timestamp': time.time()
        }
        
    def stop_all_services(self) -> bool:
        """
        Stop all monitoring services and clean up resources
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            success = True
            
            # Stop arbitrage monitoring
            if not self.stop_arbitrage_monitoring():
                success = False
                
            # Stop market view monitoring
            if not self.stop_market_view_monitoring():
                success = False
                
            self.logger.info("All services stopped")
            return success
            
        except Exception as e:
            self.logger.error(f"Error stopping all services: {e}")
            return False
            
    def is_service_running(self, service_name: str) -> bool:
        """
        Check if a specific service is running
        
        Args:
            service_name (str): Name of service ('arbitrage' or 'market_view')
            
        Returns:
            bool: True if service is running, False otherwise
        """
        if service_name == 'arbitrage':
            return self.arbitrage_monitoring
        elif service_name == 'market_view':
            return self.market_view_monitoring
        else:
            return False