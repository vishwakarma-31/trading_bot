"""
Alert Manager for the GoQuant Trading Bot
Handles sending formatted notifications to Telegram for arbitrage and market view services.
"""
import logging
import time
import threading
from typing import Dict, List, Optional
from telegram import Bot
from telegram.error import TelegramError
from data_processing.arbitrage_detector import ArbitrageOpportunity
from data_processing.market_view import ConsolidatedMarketView

class AlertManager:
    """Manages alert notifications for the Telegram bot"""
    
    def __init__(self, bot_token: str):
        """Initialize alert manager"""
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token)
        self.logger = logging.getLogger(__name__)
        self.subscribers = set()  # Chat IDs to send alerts to
        self.sent_alerts = {}  # Track sent alert messages for editing
        self.alert_history = []  # Keep track of recent alerts
        self.max_history = 100  # Maximum number of alerts to keep in history
        self.rate_limit_delay = 1.0  # Seconds between messages to avoid rate limiting
        self.last_message_time = 0  # Track last message send time
        
    def add_subscriber(self, chat_id: int):
        """Add a chat ID to receive alerts"""
        self.subscribers.add(chat_id)
        self.logger.info(f"Added subscriber: {chat_id}")
        
    def remove_subscriber(self, chat_id: int):
        """Remove a chat ID from receiving alerts"""
        self.subscribers.discard(chat_id)
        self.logger.info(f"Removed subscriber: {chat_id}")
        
    def get_subscribers(self) -> set:
        """Get all subscribers"""
        return self.subscribers.copy()
        
    def _rate_limit_check(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
            
        self.last_message_time = time.time()
        
    def _send_message_to_subscribers(self, message: str, parse_mode: str = 'Markdown') -> Dict[int, int]:
        """
        Send message to all subscribers
        
        Args:
            message (str): Message to send
            parse_mode (str): Parse mode for Telegram (Markdown/HTML)
            
        Returns:
            Dict mapping chat_id to message_id
        """
        sent_messages = {}
        
        for chat_id in self.subscribers:
            try:
                self._rate_limit_check()
                msg = self.bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
                sent_messages[chat_id] = msg.message_id
                self.logger.info(f"Sent alert to chat {chat_id}")
            except TelegramError as e:
                self.logger.error(f"Failed to send message to {chat_id}: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error sending message to {chat_id}: {e}")
                
        return sent_messages
        
    def _edit_message_for_subscriber(self, chat_id: int, message_id: int, new_message: str, 
                                   parse_mode: str = 'Markdown') -> bool:
        """
        Edit a previously sent message for a subscriber
        
        Args:
            chat_id (int): Chat ID
            message_id (int): Message ID to edit
            new_message (str): New message content
            parse_mode (str): Parse mode for Telegram
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_message,
                parse_mode=parse_mode
            )
            self.logger.info(f"Updated alert message for chat {chat_id}")
            return True
        except TelegramError as e:
            self.logger.error(f"Failed to edit message for {chat_id}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error editing message for {chat_id}: {e}")
            return False
            
    def format_arbitrage_alert(self, opportunity: ArbitrageOpportunity) -> str:
        """
        Format arbitrage opportunity as an alert message
        
        Args:
            opportunity (ArbitrageOpportunity): Arbitrage opportunity to format
            
        Returns:
            str: Formatted alert message
        """
        # Convert timestamp to readable format
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(opportunity.timestamp))
        
        alert_message = f"""
🔔 *ARBITRAGE OPPORTUNITY DETECTED*

Asset: {opportunity.symbol}
Exchange A: {opportunity.buy_exchange.upper()} @ ${opportunity.buy_price:,.2f}
Exchange B: {opportunity.sell_exchange.upper()} @ ${opportunity.sell_price:,.2f}
Spread: ${opportunity.profit_absolute:,.2f} ({opportunity.profit_percentage:.2f}%)
Threshold: {opportunity.threshold_percentage:.2f}%
Time: {timestamp}
"""
        return alert_message.strip()
        
    def format_market_view_alert(self, market_view: ConsolidatedMarketView) -> str:
        """
        Format market view as an alert message
        
        Args:
            market_view (ConsolidatedMarketView): Market view to format
            
        Returns:
            str: Formatted alert message
        """
        # Calculate CBBO mid price
        cbbo_mid = (market_view.cbbo_bid_price + market_view.cbbo_ask_price) / 2
        
        # Convert timestamp to readable format
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(market_view.timestamp))
        
        alert_message = f"""
📊 *MARKET VIEW UPDATE*

Symbol: {market_view.symbol}
Best Bid: {market_view.cbbo_bid_exchange.upper()} @ ${market_view.cbbo_bid_price:,.2f}
Best Offer: {market_view.cbbo_ask_exchange.upper()} @ ${market_view.cbbo_ask_price:,.2f}
CBBO Mid: ${cbbo_mid:,.2f}
Time: {timestamp}
"""
        return alert_message.strip()
        
    def send_arbitrage_alert(self, opportunity: ArbitrageOpportunity) -> Dict[int, int]:
        """
        Send arbitrage opportunity alert to all subscribers
        
        Args:
            opportunity (ArbitrageOpportunity): Arbitrage opportunity to alert about
            
        Returns:
            Dict mapping chat_id to message_id
        """
        alert_message = self.format_arbitrage_alert(opportunity)
        message_ids = self._send_message_to_subscribers(alert_message)
        
        # Track this alert for potential updates
        alert_key = f"arb_{opportunity.symbol}_{opportunity.buy_exchange}_{opportunity.sell_exchange}"
        self.sent_alerts[alert_key] = {
            'message_ids': message_ids,
            'opportunity': opportunity,
            'timestamp': time.time()
        }
        
        # Add to history
        self.alert_history.append({
            'type': 'arbitrage',
            'message': alert_message,
            'timestamp': time.time()
        })
        
        # Maintain history size
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
            
        return message_ids
        
    def send_market_view_alert(self, market_view: ConsolidatedMarketView) -> Dict[int, int]:
        """
        Send market view alert to all subscribers
        
        Args:
            market_view (ConsolidatedMarketView): Market view to alert about
            
        Returns:
            Dict mapping chat_id to message_id
        """
        alert_message = self.format_market_view_alert(market_view)
        message_ids = self._send_message_to_subscribers(alert_message)
        
        # Track this alert for potential updates
        alert_key = f"market_{market_view.symbol}"
        self.sent_alerts[alert_key] = {
            'message_ids': message_ids,
            'market_view': market_view,
            'timestamp': time.time()
        }
        
        # Add to history
        self.alert_history.append({
            'type': 'market_view',
            'message': alert_message,
            'timestamp': time.time()
        })
        
        # Maintain history size
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
            
        return message_ids
        
    def update_arbitrage_alert(self, opportunity: ArbitrageOpportunity) -> int:
        """
        Update an existing arbitrage alert with new information
        
        Args:
            opportunity (ArbitrageOpportunity): Updated arbitrage opportunity
            
        Returns:
            int: Number of successfully updated messages
        """
        alert_key = f"arb_{opportunity.symbol}_{opportunity.buy_exchange}_{opportunity.sell_exchange}"
        
        if alert_key not in self.sent_alerts:
            # If no existing alert, send a new one
            self.send_arbitrage_alert(opportunity)
            return 0
            
        # Update existing alert
        alert_info = self.sent_alerts[alert_key]
        updated_message = self.format_arbitrage_alert(opportunity)
        
        success_count = 0
        for chat_id, message_id in alert_info['message_ids'].items():
            if self._edit_message_for_subscriber(chat_id, message_id, updated_message):
                success_count += 1
                
        # Update tracking info
        alert_info['opportunity'] = opportunity
        alert_info['timestamp'] = time.time()
        
        return success_count
        
    def update_market_view_alert(self, market_view: ConsolidatedMarketView) -> int:
        """
        Update an existing market view alert with new information
        
        Args:
            market_view (ConsolidatedMarketView): Updated market view
            
        Returns:
            int: Number of successfully updated messages
        """
        alert_key = f"market_{market_view.symbol}"
        
        if alert_key not in self.sent_alerts:
            # If no existing alert, send a new one
            self.send_market_view_alert(market_view)
            return 0
            
        # Update existing alert
        alert_info = self.sent_alerts[alert_key]
        updated_message = self.format_market_view_alert(market_view)
        
        success_count = 0
        for chat_id, message_id in alert_info['message_ids'].items():
            if self._edit_message_for_subscriber(chat_id, message_id, updated_message):
                success_count += 1
                
        # Update tracking info
        alert_info['market_view'] = market_view
        alert_info['timestamp'] = time.time()
        
        return success_count
        
    def get_alert_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent alert history
        
        Args:
            limit (int): Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alert_history[-limit:] if self.alert_history else []
        
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history.clear()
        self.logger.info("Cleared alert history")