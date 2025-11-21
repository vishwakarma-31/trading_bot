"""
Arbitrage Statistics and Historical Logging for the GoQuant Trading Bot
"""
import logging
import json
import csv
import sqlite3
import os
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime, timedelta
from data_processing.models import ArbitrageStatistics

class ArbitrageLogger:
    """Handles logging of arbitrage opportunities and statistics calculation"""
    
    def __init__(self, storage_type: str = "sqlite", storage_path: str = "data"):
        """Initialize arbitrage logger
        
        Args:
            storage_type (str): Type of storage ("csv", "json", or "sqlite")
            storage_path (str): Path to store data files
        """
        self.logger = logging.getLogger(__name__)
        self.storage_type = storage_type
        self.storage_path = storage_path
        self.db_connection = None
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
            
        # Initialize storage
        if storage_type == "sqlite":
            self._init_sqlite()
        elif storage_type == "csv":
            self._init_csv()
        elif storage_type == "json":
            self._init_json()
            
    def _init_sqlite(self):
        """Initialize SQLite database"""
        try:
            db_path = os.path.join(self.storage_path, "arbitrage_opportunities.db")
            self.db_connection = sqlite3.connect(db_path, check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    symbol TEXT NOT NULL,
                    buy_exchange TEXT NOT NULL,
                    sell_exchange TEXT NOT NULL,
                    buy_price REAL NOT NULL,
                    sell_price REAL NOT NULL,
                    profit_percentage REAL NOT NULL,
                    profit_absolute REAL NOT NULL,
                    threshold_percentage REAL NOT NULL,
                    threshold_absolute REAL NOT NULL
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol ON arbitrage_opportunities (symbol)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON arbitrage_opportunities (timestamp)
            ''')
            
            self.db_connection.commit()
            self.logger.info("SQLite database initialized for arbitrage logging")
            
        except Exception as e:
            self.logger.error(f"Error initializing SQLite database: {e}")
            raise
            
    def _init_csv(self):
        """Initialize CSV file"""
        try:
            self.csv_file_path = os.path.join(self.storage_path, "arbitrage_opportunities.csv")
            # Create file with headers if it doesn't exist
            if not os.path.exists(self.csv_file_path):
                with open(self.csv_file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        'timestamp', 'symbol', 'buy_exchange', 'sell_exchange',
                        'buy_price', 'sell_price', 'profit_percentage', 'profit_absolute',
                        'threshold_percentage', 'threshold_absolute'
                    ])
            self.logger.info("CSV file initialized for arbitrage logging")
        except Exception as e:
            self.logger.error(f"Error initializing CSV file: {e}")
            raise
            
    def _init_json(self):
        """Initialize JSON file"""
        try:
            self.json_file_path = os.path.join(self.storage_path, "arbitrage_opportunities.json")
            # Create empty file if it doesn't exist
            if not os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'w') as jsonfile:
                    json.dump([], jsonfile)
            self.logger.info("JSON file initialized for arbitrage logging")
        except Exception as e:
            self.logger.error(f"Error initializing JSON file: {e}")
            raise
            
    def log_opportunity(self, opportunity):
        """Log an arbitrage opportunity to storage
        
        Args:
            opportunity (ArbitrageOpportunity): The opportunity to log
        """
        try:
            if self.storage_type == "sqlite":
                self._log_to_sqlite(opportunity)
            elif self.storage_type == "csv":
                self._log_to_csv(opportunity)
            elif self.storage_type == "json":
                self._log_to_json(opportunity)
                
        except Exception as e:
            self.logger.error(f"Error logging arbitrage opportunity: {e}")
            raise
            
    def _log_to_sqlite(self, opportunity):
        """Log opportunity to SQLite database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO arbitrage_opportunities (
                    timestamp, symbol, buy_exchange, sell_exchange,
                    buy_price, sell_price, profit_percentage, profit_absolute,
                    threshold_percentage, threshold_absolute
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opportunity.timestamp,
                opportunity.symbol,
                opportunity.buy_exchange,
                opportunity.sell_exchange,
                opportunity.buy_price,
                opportunity.sell_price,
                opportunity.profit_percentage,
                opportunity.profit_absolute,
                opportunity.threshold_percentage,
                opportunity.threshold_absolute
            ))
            self.db_connection.commit()
        except Exception as e:
            self.logger.error(f"Error logging to SQLite: {e}")
            raise
            
    def _log_to_csv(self, opportunity):
        """Log opportunity to CSV file"""
        try:
            with open(self.csv_file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    opportunity.timestamp,
                    opportunity.symbol,
                    opportunity.buy_exchange,
                    opportunity.sell_exchange,
                    opportunity.buy_price,
                    opportunity.sell_price,
                    opportunity.profit_percentage,
                    opportunity.profit_absolute,
                    opportunity.threshold_percentage,
                    opportunity.threshold_absolute
                ])
        except Exception as e:
            self.logger.error(f"Error logging to CSV: {e}")
            raise
            
    def _log_to_json(self, opportunity):
        """Log opportunity to JSON file"""
        try:
            # Read existing data
            with open(self.json_file_path, 'r') as jsonfile:
                data = json.load(jsonfile)
                
            # Add new opportunity
            data.append(asdict(opportunity))
            
            # Write back to file
            with open(self.json_file_path, 'w') as jsonfile:
                json.dump(data, jsonfile, indent=2)
        except Exception as e:
            self.logger.error(f"Error logging to JSON: {e}")
            raise
            
    def get_statistics(self, symbol: Optional[str] = None, hours: int = 24) -> ArbitrageStatistics:
        """Calculate arbitrage statistics
        
        Args:
            symbol (str, optional): Filter by specific symbol
            hours (int): Time period in hours to calculate statistics for
            
        Returns:
            ArbitrageStatistics: Calculated statistics
        """
        try:
            if self.storage_type == "sqlite":
                return self._get_statistics_sqlite(symbol, hours)
            elif self.storage_type == "csv":
                return self._get_statistics_csv(symbol, hours)
            elif self.storage_type == "json":
                return self._get_statistics_json(symbol, hours)
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {e}")
            raise
            
    def _get_statistics_sqlite(self, symbol: Optional[str] = None, hours: int = 24) -> ArbitrageStatistics:
        """Calculate statistics from SQLite database"""
        try:
            cursor = self.db_connection.cursor()
            
            # Calculate time range
            end_time = time.time()
            start_time = end_time - (hours * 3600)
            
            # Build query
            if symbol:
                cursor.execute('''
                    SELECT * FROM arbitrage_opportunities 
                    WHERE symbol = ? AND timestamp >= ? AND timestamp <= ?
                ''', (symbol, start_time, end_time))
            else:
                cursor.execute('''
                    SELECT * FROM arbitrage_opportunities 
                    WHERE timestamp >= ? AND timestamp <= ?
                ''', (start_time, end_time))
                
            rows = cursor.fetchall()
            
            if not rows:
                return ArbitrageStatistics(
                    total_opportunities=0,
                    average_spread=0.0,
                    max_spread=0.0,
                    opportunities_by_symbol={},
                    opportunities_by_exchange_pair={},
                    start_time=start_time,
                    end_time=end_time
                )
                
            # Calculate statistics
            total_opportunities = len(rows)
            spreads = [row[7] for row in rows]  # profit_absolute column
            average_spread = sum(spreads) / len(spreads) if spreads else 0.0
            max_spread = max(spreads) if spreads else 0.0
            
            # Count opportunities by symbol
            opportunities_by_symbol = defaultdict(int)
            opportunities_by_exchange_pair = defaultdict(int)
            
            for row in rows:
                opportunities_by_symbol[row[2]] += 1  # symbol column
                exchange_pair = f"{row[3]}-{row[4]}"  # buy_exchange-sell_exchange
                opportunities_by_exchange_pair[exchange_pair] += 1
                
            return ArbitrageStatistics(
                total_opportunities=total_opportunities,
                average_spread=average_spread,
                max_spread=max_spread,
                opportunities_by_symbol=dict(opportunities_by_symbol),
                opportunities_by_exchange_pair=dict(opportunities_by_exchange_pair),
                start_time=start_time,
                end_time=end_time
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating SQLite statistics: {e}")
            raise
            
    def _get_statistics_csv(self, symbol: Optional[str] = None, hours: int = 24) -> ArbitrageStatistics:
        """Calculate statistics from CSV file"""
        try:
            opportunities = []
            start_time = time.time() - (hours * 3600)
            end_time = time.time()
            
            with open(self.csv_file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    timestamp = float(row['timestamp'])
                    if timestamp >= start_time and timestamp <= end_time:
                        if symbol is None or row['symbol'] == symbol:
                            opportunities.append(row)
                            
            if not opportunities:
                return ArbitrageStatistics(
                    total_opportunities=0,
                    average_spread=0.0,
                    max_spread=0.0,
                    opportunities_by_symbol={},
                    opportunities_by_exchange_pair={},
                    start_time=start_time,
                    end_time=end_time
                )
                
            # Calculate statistics
            total_opportunities = len(opportunities)
            spreads = [float(opp['profit_absolute']) for opp in opportunities]
            average_spread = sum(spreads) / len(spreads) if spreads else 0.0
            max_spread = max(spreads) if spreads else 0.0
            
            # Count opportunities by symbol and exchange pair
            opportunities_by_symbol = defaultdict(int)
            opportunities_by_exchange_pair = defaultdict(int)
            
            for opp in opportunities:
                opportunities_by_symbol[opp['symbol']] += 1
                exchange_pair = f"{opp['buy_exchange']}-{opp['sell_exchange']}"
                opportunities_by_exchange_pair[exchange_pair] += 1
                
            return ArbitrageStatistics(
                total_opportunities=total_opportunities,
                average_spread=average_spread,
                max_spread=max_spread,
                opportunities_by_symbol=dict(opportunities_by_symbol),
                opportunities_by_exchange_pair=dict(opportunities_by_exchange_pair),
                start_time=start_time,
                end_time=end_time
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating CSV statistics: {e}")
            raise
            
    def _get_statistics_json(self, symbol: Optional[str] = None, hours: int = 24) -> ArbitrageStatistics:
        """Calculate statistics from JSON file"""
        try:
            start_time = time.time() - (hours * 3600)
            end_time = time.time()
            
            with open(self.json_file_path, 'r') as jsonfile:
                all_opportunities = json.load(jsonfile)
                
            # Filter opportunities by time and symbol
            opportunities = []
            for opp in all_opportunities:
                if opp['timestamp'] >= start_time and opp['timestamp'] <= end_time:
                    if symbol is None or opp['symbol'] == symbol:
                        opportunities.append(opp)
                        
            if not opportunities:
                return ArbitrageStatistics(
                    total_opportunities=0,
                    average_spread=0.0,
                    max_spread=0.0,
                    opportunities_by_symbol={},
                    opportunities_by_exchange_pair={},
                    start_time=start_time,
                    end_time=end_time
                )
                
            # Calculate statistics
            total_opportunities = len(opportunities)
            spreads = [opp['profit_absolute'] for opp in opportunities]
            average_spread = sum(spreads) / len(spreads) if spreads else 0.0
            max_spread = max(spreads) if spreads else 0.0
            
            # Count opportunities by symbol and exchange pair
            opportunities_by_symbol = defaultdict(int)
            opportunities_by_exchange_pair = defaultdict(int)
            
            for opp in opportunities:
                opportunities_by_symbol[opp['symbol']] += 1
                exchange_pair = f"{opp['buy_exchange']}-{opp['sell_exchange']}"
                opportunities_by_exchange_pair[exchange_pair] += 1
                
            return ArbitrageStatistics(
                total_opportunities=total_opportunities,
                average_spread=average_spread,
                max_spread=max_spread,
                opportunities_by_symbol=dict(opportunities_by_symbol),
                opportunities_by_exchange_pair=dict(opportunities_by_exchange_pair),
                start_time=start_time,
                end_time=end_time
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating JSON statistics: {e}")
            raise
            
    def close(self):
        """Close any open connections"""
        try:
            if self.db_connection:
                self.db_connection.close()
                self.logger.info("SQLite database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database connection: {e}")