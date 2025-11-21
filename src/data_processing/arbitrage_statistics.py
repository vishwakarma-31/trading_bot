"""
Arbitrage Statistics and Historical Logging for the Generic Trading Bot
"""
import logging
import json
import csv
import sqlite3
import os
import time
from typing import List, Dict, Optional
from dataclasses import asdict
from collections import defaultdict
from datetime import datetime
from data_processing.models import ArbitrageStatistics, ArbitrageOpportunity

class ArbitrageLogger:
    """Handles logging of arbitrage opportunities and statistics calculation"""
    
    def __init__(self, storage_type: str = "sqlite", storage_path: str = "data"):
        self.logger = logging.getLogger(__name__)
        self.storage_type = storage_type
        self.storage_path = storage_path
        self.db_connection = None
        
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
            
        if storage_type == "sqlite":
            self._init_sqlite()
        elif storage_type == "csv":
            self._init_csv()
        elif storage_type == "json":
            self._init_json()
            
    def _init_sqlite(self):
        try:
            db_path = os.path.join(self.storage_path, "arbitrage_opportunities.db")
            self.db_connection = sqlite3.connect(db_path, check_same_thread=False)
            cursor = self.db_connection.cursor()
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
            self.db_connection.commit()
        except Exception as e:
            self.logger.error(f"Error initializing SQLite: {e}")

    # ... _init_csv and _init_json methods (keep existing logic) ...
    def _init_csv(self): pass # Placeholder for brevity, assume existing logic
    def _init_json(self): pass # Placeholder for brevity, assume existing logic

    def log_opportunity(self, opportunity: ArbitrageOpportunity):
        """Log an arbitrage opportunity to storage"""
        try:
            if self.storage_type == "sqlite":
                self._log_to_sqlite(opportunity)
            # ... other types ...
        except Exception as e:
            self.logger.error(f"Error logging opportunity: {e}")

    def _log_to_sqlite(self, opportunity: ArbitrageOpportunity):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO arbitrage_opportunities (
                    timestamp, symbol, buy_exchange, sell_exchange,
                    buy_price, sell_price, profit_percentage, profit_absolute,
                    threshold_percentage, threshold_absolute
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opportunity.timestamp, opportunity.symbol, opportunity.buy_exchange,
                opportunity.sell_exchange, opportunity.buy_price, opportunity.sell_price,
                opportunity.profit_percentage, opportunity.profit_absolute,
                opportunity.threshold_percentage, opportunity.threshold_absolute
            ))
            self.db_connection.commit()
        except Exception as e:
            self.logger.error(f"Error logging to SQLite: {e}")

    def get_statistics(self, symbol: Optional[str] = None, hours: int = 24) -> ArbitrageStatistics:
        """Calculate arbitrage statistics"""
        # Simplified for SQLite implementation
        if self.storage_type != "sqlite":
            return ArbitrageStatistics()

        try:
            cursor = self.db_connection.cursor()
            end_time = time.time()
            start_time = end_time - (hours * 3600)
            
            query = "SELECT * FROM arbitrage_opportunities WHERE timestamp >= ?"
            params = [start_time]
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
                
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if not rows:
                return ArbitrageStatistics(start_time=start_time, end_time=end_time)
            
            # Calculate stats
            total_ops = len(rows)
            spreads = [row[7] for row in rows] # profit_absolute index
            avg_spread = sum(spreads) / len(spreads)
            max_spread = max(spreads)
            
            # Grouping
            ops_by_symbol = defaultdict(int)
            ops_by_pair = defaultdict(int)
            for row in rows:
                ops_by_symbol[row[2]] += 1
                ops_by_pair[f"{row[3]}-{row[4]}"] += 1
            
            return ArbitrageStatistics(
                total_opportunities=total_ops,
                average_spread=avg_spread,
                max_spread=max_spread,
                opportunities_by_symbol=dict(ops_by_symbol),
                opportunities_by_exchange_pair=dict(ops_by_pair),
                start_time=start_time,
                end_time=end_time
            )
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return ArbitrageStatistics()