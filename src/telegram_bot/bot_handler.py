"""
Telegram Bot Handler for the GoQuant Trading Bot
"""
import logging
import re
import time
import threading
from datetime import datetime
from typing import List, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler
from telegram.ext import filters as Filters
from config.config_manager import ConfigManager
from config.user_config_manager import UserConfigManager
from data_processing.arbitrage_detector import ArbitrageDetector
from data_processing.market_view import MarketViewManager
from data_processing.service_controller import ServiceController
from data_acquisition.market_data_fetcher import MarketDataFetcher
from telegram_bot.alert_manager import AlertManager
from utils.error_handler import (
    TelegramBotError, MessageSendingError, CommandParsingError, 
    InvalidUserInputError, BotAPIError, log_exception, handle_exception
)

class TelegramBotHandler:
    """Handles all Telegram bot interactions"""
    
    def __init__(self, config: ConfigManager, arbitrage_detector: ArbitrageDetector = None, 
                 market_fetcher: MarketDataFetcher = None):
        """Initialize Telegram bot handler"""
        self.config = config
        self.user_config_manager = UserConfigManager(config)
        self.arbitrage_detector = arbitrage_detector
        self.market_fetcher = market_fetcher
        self.service_controller = ServiceController(market_fetcher, config) if market_fetcher else None
        self.market_view_manager = MarketViewManager(market_fetcher) if market_fetcher else None
        self.alert_manager = AlertManager(config.telegram_token) if config.telegram_token else None
        self.updater = None
        self.logger = logging.getLogger(__name__)
        self.supported_exchanges = ['okx', 'deribit', 'bybit', 'binance']
        self.arbitrage_monitoring_symbols = []  # Track symbols being monitored for arbitrage
        self.market_view_symbols = {}  # Track symbols being monitored for market view
        self.user_states = {}  # Track user interaction states
        self.live_messages = {}  # Track live updating messages
        self.monitoring_alerts = True  # Whether to send alerts during monitoring
        self.market_view_update_interval = 30  # Seconds between market view updates
        self.last_market_view_update = 0  # Timestamp of last market view update
        
    def start(self):
        """Start the Telegram bot"""
        try:
            if not self.config.telegram_token:
                self.logger.error("Telegram bot token not configured!")
                return
                
            self.updater = Updater(token=self.config.telegram_token, use_context=True)
            dispatcher = self.updater.dispatcher
            
            # Register command handlers
            dispatcher.add_handler(CommandHandler('start', self._start_command))
            dispatcher.add_handler(CommandHandler('help', self._help_command))
            dispatcher.add_handler(CommandHandler('status', self._status_command))
            dispatcher.add_handler(CommandHandler('list_symbols', self._list_symbols_command))
            dispatcher.add_handler(CommandHandler('menu', self._main_menu_command))
            dispatcher.add_handler(CommandHandler('alerts', self._alerts_command))
            dispatcher.add_handler(CommandHandler('config', self._config_command))
            
            if self.arbitrage_detector:
                dispatcher.add_handler(CommandHandler('threshold', self._threshold_command))
                dispatcher.add_handler(CommandHandler('arbitrage', self._arbitrage_command))
                dispatcher.add_handler(CommandHandler('monitor_arb', self._monitor_arb_command))
                dispatcher.add_handler(CommandHandler('stop_arb', self._stop_arb_command))
                dispatcher.add_handler(CommandHandler('config_arb', self._config_arb_command))
                dispatcher.add_handler(CommandHandler('status_arb', self._status_arb_command))
                dispatcher.add_handler(CommandHandler('arb_stats', self._arb_stats_command))
                
            if self.market_view_manager:
                dispatcher.add_handler(CommandHandler('view_market', self._view_market_command))
                dispatcher.add_handler(CommandHandler('stop_market', self._stop_market_command))
                dispatcher.add_handler(CommandHandler('get_cbbo', self._get_cbbo_command))
                dispatcher.add_handler(CommandHandler('config_market', self._config_market_command))
                dispatcher.add_handler(CommandHandler('status_market', self._status_market_command))
            
            # Register callback query handler for interactive buttons
            dispatcher.add_handler(CallbackQueryHandler(self._button_callback))
            
            # Register message handler
            dispatcher.add_handler(MessageHandler(Filters.TEXT & (~Filters.COMMAND), self._echo_message))
            
            # Start the bot
            self.updater.start_polling()
            self.logger.info("Telegram bot started successfully")
            
            # Add this chat to alert subscribers
            # Note: We'll add subscribers when they interact with the bot
            
        except Exception as e:
            log_exception(self.logger, e, "Failed to start Telegram bot")
            raise TelegramBotError(f"Failed to start Telegram bot: {e}")
            
    def stop(self):
        """Stop the Telegram bot"""
        try:
            if self.updater:
                self.updater.stop()
                self.logger.info("Telegram bot stopped")
                # Save user configurations
                self.user_config_manager.save_config()
        except Exception as e:
            log_exception(self.logger, e, "Error stopping Telegram bot")
            raise TelegramBotError(f"Error stopping Telegram bot: {e}")
            
    def _validate_exchange(self, exchange: str) -> bool:
        """Validate exchange name"""
        try:
            if not exchange:
                return False
            return exchange.lower() in self.supported_exchanges
        except Exception as e:
            self.logger.error(f"Error validating exchange {exchange}: {e}")
            return False
        
    def _validate_symbol(self, symbol: str) -> bool:
        """Validate symbol format"""
        try:
            if not symbol:
                return False
            # Basic validation: should contain letters, numbers, and hyphens/underscores
            pattern = re.compile(r'^[A-Za-z0-9\-_]+$')
            return bool(pattern.match(symbol))
        except Exception as e:
            self.logger.error(f"Error validating symbol {symbol}: {e}")
            return False
        
    def _parse_threshold(self, threshold_str: str) -> float:
        """Parse threshold value"""
        try:
            if not threshold_str:
                raise InvalidUserInputError("No threshold value provided")
            value = float(threshold_str)
            if value < 0:
                raise InvalidUserInputError(f"Threshold value must be non-negative: {value}")
            return value
        except ValueError:
            raise InvalidUserInputError(f"Invalid threshold value. Please use a number: {threshold_str}")
        except Exception as e:
            raise InvalidUserInputError(f"Error parsing threshold value {threshold_str}: {e}")
            
    def _format_error_message(self, error: Exception) -> str:
        """Format error message for user display"""
        try:
            return f"❌ Error: {str(error)}"
        except Exception as e:
            self.logger.error(f"Error formatting error message: {e}")
            return "❌ An unexpected error occurred"
        
    def _get_user_id(self, update: Update) -> int:
        """Get user ID from update"""
        try:
            return update.effective_user.id if update.effective_user else update.effective_chat.id
        except Exception as e:
            self.logger.error(f"Error getting user ID from update: {e}")
            raise TelegramBotError(f"Error getting user ID: {e}")
        
    @handle_exception(logger_name=__name__, reraise=False)
    def _start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            
            # Add chat to alert subscribers
            if self.alert_manager:
                self.alert_manager.add_subscriber(chat_id)
                
            # Initialize user configuration
            self.user_config_manager.get_user_config(user_id)
                
            welcome_text = """
Welcome to the GoQuant Trading Bot! 🚀

I'm here to help you monitor arbitrage opportunities and market views across multiple exchanges.

Use /help to see all available commands.
Use /menu to access the interactive menu.
Use /alerts to manage alert settings.
Use /config to manage your configuration.
"""
            context.bot.send_message(chat_id=chat_id, text=welcome_text)
            
        except Exception as e:
            log_exception(self.logger, e, "Error in /start command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
                
    @handle_exception(logger_name=__name__, reraise=False)
    def _help_command(self, update: Update, context: CallbackContext):
        """Handle /help command"""
        try:
            chat_id = update.effective_chat.id
            help_text = """
🤖 *GoQuant Trading Bot Commands*

*Basic Commands:*
/start - Welcome message and bot introduction
/help - List all available commands
/status - Check bot status
/list_symbols <exchange> <market_type> - List available symbols
/menu - Open interactive menu
/alerts - Manage alert settings
/config - Manage user configuration

"""
            
            if self.arbitrage_detector:
                help_text += """*Arbitrage Signal Service:*
/monitor_arb <asset1_on_exchangeA> <asset2_on_exchangeB> <threshold> - Start monitoring
/stop_arb - Stop arbitrage monitoring
/config_arb - Configure arbitrage settings
/status_arb - Show current arbitrage monitoring status
/threshold - Get current arbitrage thresholds
/threshold <percent> <absolute> - Set arbitrage thresholds
/arbitrage - Get current arbitrage opportunities
/arb_stats - Show overall statistics
/arb_stats <symbol> - Show statistics for specific symbol

"""
                
            if self.market_view_manager:
                help_text += """*Consolidated Market View:*
/view_market <symbol> <exchange1> <exchange2> ... - Start market view monitoring
/stop_market - Stop market view monitoring
/get_cbbo <symbol> - Query current CBBO on demand
/config_market - Configure market view settings
/status_market - Show current market view status
"""
                
            context.bot.send_message(chat_id=chat_id, text=help_text, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error in /help command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
                
    @handle_exception(logger_name=__name__, reraise=False)
    def _config_command(self, update: Update, context: CallbackContext):
        """Handle /config command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            self._show_config_menu(user_id, chat_id, context)
        except Exception as e:
            log_exception(self.logger, e, "Error in /config command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
                
    def _show_config_menu(self, user_id: int, chat_id: int, context: CallbackContext):
        """Show main configuration menu"""
        try:
            menu_text = "⚙️ *User Configuration*\n\nSelect a configuration category:"
            
            keyboard = [
                [InlineKeyboardButton("⚖️ Arbitrage Settings", callback_data='config_arb_menu')],
                [InlineKeyboardButton("📈 Market View Settings", callback_data='config_market_menu')],
                [InlineKeyboardButton("👤 User Preferences", callback_data='config_prefs_menu')],
                [InlineKeyboardButton("💾 Save Configuration", callback_data='config_save')],
                [InlineKeyboardButton("🔄 Reset to Defaults", callback_data='config_reset')],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing config menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
                
    def _show_arbitrage_config_menu(self, user_id: int, chat_id: int, context: CallbackContext):
        """Show arbitrage configuration menu"""
        try:
            arb_config = self.user_config_manager.get_arbitrage_config(user_id)
            
            menu_text = "⚙️ *Arbitrage Configuration*\n\n"
            menu_text += f"Assets: {', '.join(arb_config['assets']) or 'None'}\n"
            menu_text += f"Exchanges: {', '.join(arb_config['exchanges'])}\n"
            menu_text += f"Threshold: {arb_config['threshold_percentage']}% or ${arb_config['threshold_absolute']}\n"
            menu_text += f"Max Monitors: {arb_config['max_monitors']}\n"
            menu_text += f"Enabled: {'✅' if arb_config['enabled'] else '❌'}\n\n"
            menu_text += "Select an option:"
            
            keyboard = [
                [InlineKeyboardButton("📝 Manage Assets", callback_data='config_arb_assets')],
                [InlineKeyboardButton("📋 Manage Exchanges", callback_data='config_arb_exchanges')],
                [InlineKeyboardButton("🔢 Set Thresholds", callback_data='config_arb_thresholds')],
                [InlineKeyboardButton("🔢 Set Max Monitors", callback_data='config_arb_max_monitors')],
                [InlineKeyboardButton("✅ Enable" if not arb_config['enabled'] else "❌ Disable", 
                                    callback_data='config_arb_toggle')],
                [InlineKeyboardButton("⬅️ Back", callback_data='config_main')],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing arbitrage config menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
                
    def _show_market_view_config_menu(self, user_id: int, chat_id: int, context: CallbackContext):
        """Show market view configuration menu"""
        try:
            mv_config = self.user_config_manager.get_market_view_config(user_id)
            
            menu_text = "⚙️ *Market View Configuration*\n\n"
            menu_text += f"Symbols: {', '.join(mv_config['symbols']) or 'None'}\n"
            menu_text += f"Exchanges: {', '.join(mv_config['exchanges'])}\n"
            menu_text += f"Update Frequency: {mv_config['update_frequency']}s\n"
            menu_text += f"Significant Change: {mv_config['significant_change_threshold']}%\n"
            menu_text += f"Enabled: {'✅' if mv_config['enabled'] else '❌'}\n\n"
            menu_text += "Select an option:"
            
            keyboard = [
                [InlineKeyboardButton("📝 Manage Symbols", callback_data='config_mv_symbols')],
                [InlineKeyboardButton("📋 Manage Exchanges", callback_data='config_mv_exchanges')],
                [InlineKeyboardButton("⏱️ Set Update Frequency", callback_data='config_mv_frequency')],
                [InlineKeyboardButton("🔢 Set Change Threshold", callback_data='config_mv_threshold')],
                [InlineKeyboardButton("✅ Enable" if not mv_config['enabled'] else "❌ Disable", 
                                    callback_data='config_mv_toggle')],
                [InlineKeyboardButton("⬅️ Back", callback_data='config_main')],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing market view config menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
                
    def _show_preferences_menu(self, user_id: int, chat_id: int, context: CallbackContext):
        """Show preferences configuration menu"""
        try:
            prefs = self.user_config_manager.get_preferences(user_id)
            
            menu_text = "👤 *User Preferences*\n\n"
            menu_text += f"Alert Frequency: {prefs['alert_frequency']}\n"
            menu_text += f"Message Format: {prefs['message_format']}\n"
            menu_text += f"Timezone: {prefs['timezone']}\n\n"
            menu_text += "Select an option:"
            
            keyboard = [
                [InlineKeyboardButton("🔔 Alert Frequency", callback_data='config_prefs_alert_freq')],
                [InlineKeyboardButton("📄 Message Format", callback_data='config_prefs_msg_format')],
                [InlineKeyboardButton("🌍 Timezone", callback_data='config_prefs_timezone')],
                [InlineKeyboardButton("⬅️ Back", callback_data='config_main')],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing preferences menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _alerts_command(self, update: Update, context: CallbackContext):
        """Handle /alerts command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            self._show_alerts_menu(user_id, chat_id, context)
        except Exception as e:
            log_exception(self.logger, e, "Error in /alerts command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _show_alerts_menu(self, user_id: int, chat_id: int, context: CallbackContext):
        """Show alerts configuration menu"""
        try:
            if not self.alert_manager:
                context.bot.send_message(chat_id=chat_id, text="Alert manager not available.")
                return
                
            is_subscriber = chat_id in self.alert_manager.get_subscribers()
            
            menu_text = "🔔 *Alert Settings*\n\n"
            menu_text += f"Status: {'✅ Enabled' if is_subscriber else '❌ Disabled'}\n\n"
            menu_text += "Select an option:"
            
            keyboard = [
                [InlineKeyboardButton("🔔 Enable Alerts" if not is_subscriber else "🔕 Disable Alerts", 
                                    callback_data='alerts_toggle')],
                [InlineKeyboardButton("📋 Alert History", callback_data='alerts_history')],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing alerts menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _main_menu_command(self, update: Update, context: CallbackContext):
        """Handle /menu command - main interactive menu"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            self._show_main_menu(user_id, chat_id, context)
        except Exception as e:
            log_exception(self.logger, e, "Error in /menu command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _show_main_menu(self, user_id: int, chat_id: int, context: CallbackContext):
        """Show main interactive menu"""
        try:
            menu_text = "🤖 *GoQuant Trading Bot Menu*\n\nPlease select an option:"
            
            keyboard = [
                [InlineKeyboardButton("⚖️ Arbitrage Service", callback_data='menu_arb')],
                [InlineKeyboardButton("📈 Market View Service", callback_data='menu_market')],
                [InlineKeyboardButton("🔔 Alert Settings", callback_data='menu_alerts')],
                [InlineKeyboardButton("⚙️ Configuration", callback_data='menu_config')],
                [InlineKeyboardButton("📊 Status", callback_data='menu_status')],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing main menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _status_command(self, update: Update, context: CallbackContext):
        """Handle /status command"""
        try:
            chat_id = update.effective_chat.id
            status_text = "📊 *GoQuant Trading Bot Status*\n\n"
            status_text += "✅ Running\n"
            status_text += f"📡 Supported exchanges: Binance, OKX, Bybit, Deribit\n"
            status_text += f"🔑 GoMarket access code: {self.config.gomarket_access_code}\n"
            status_text += f"🕐 Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if self.arbitrage_detector:
                status_text += "\n⚖️ *Arbitrage Service*: "
                status_text += "Active" if self.arbitrage_monitoring_symbols else "Inactive"
                
            if self.market_view_manager:
                status_text += "\n📈 *Market View Service*: "
                status_text += "Active" if self.market_view_symbols else "Inactive"
                
            # Add navigation buttons
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data='refresh_status')],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            context.bot.send_message(chat_id=chat_id, text=status_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error in /status command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _list_symbols_command(self, update: Update, context: CallbackContext):
        """Handle /list_symbols command"""
        try:
            chat_id = update.effective_chat.id
            
            if not context.args:
                context.bot.send_message(
                    chat_id=chat_id, 
                    text="Usage: /list_symbols <exchange> <market_type>\nExample: /list_symbols okx spot"
                )
                return
                
            if len(context.args) < 2:
                context.bot.send_message(
                    chat_id=chat_id, 
                    text="Please provide both exchange and market type.\nExample: /list_symbols okx spot"
                )
                return
                
            exchange = context.args[0].lower()
            market_type = context.args[1].lower()
            
            # Validate exchange
            if not self._validate_exchange(exchange):
                context.bot.send_message(
                    chat_id=chat_id, 
                    text=f"Invalid exchange. Supported exchanges: {', '.join(self.supported_exchanges)}"
                )
                return
                
            # Validate market type
            if market_type != 'spot':
                context.bot.send_message(
                    chat_id=chat_id, 
                    text="Only 'spot' market type is currently supported."
                )
                return
                
            # Get symbols
            if not self.market_fetcher:
                context.bot.send_message(chat_id=chat_id, text="Market data fetcher not available.")
                return
                
            try:
                symbols = self.market_fetcher.get_available_symbols(exchange)
                
                if not symbols:
                    context.bot.send_message(chat_id=chat_id, text=f"No symbols found for {exchange} spot market.")
                    return
                    
                # Format symbols list
                symbols_text = f"📋 *Available symbols for {exchange.upper()} SPOT:*\n\n"
                
                # Show first 20 symbols to avoid message length limits
                for i, symbol in enumerate(symbols[:20]):
                    symbols_text += f"{i+1}. {symbol}\n"
                    
                if len(symbols) > 20:
                    symbols_text += f"\n... and {len(symbols) - 20} more symbols."
                    
                # Add navigation buttons
                keyboard = [
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                    
                context.bot.send_message(chat_id=chat_id, text=symbols_text, reply_markup=reply_markup, parse_mode='Markdown')
                
            except Exception as e:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
                
        except Exception as e:
            log_exception(self.logger, e, "Error in /list_symbols command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
            
    def _threshold_command(self, update: Update, context: CallbackContext):
        """Handle /threshold command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            
            if not self.arbitrage_detector:
                context.bot.send_message(chat_id=chat_id, text="Arbitrage detector not available.")
                return
                
            if context.args:
                # Set thresholds
                try:
                    if len(context.args) >= 2:
                        percent = self._parse_threshold(context.args[0])
                        absolute = self._parse_threshold(context.args[1])
                        self.arbitrage_detector.set_thresholds(
                            min_profit_percentage=percent,
                            min_profit_absolute=absolute
                        )
                        # Also update user config
                        self.user_config_manager.update_arbitrage_config(
                            user_id,
                            threshold_percentage=percent,
                            threshold_absolute=absolute
                        )
                        context.bot.send_message(
                            chat_id=chat_id, 
                            text=f"✅ Thresholds updated:\nMinimum profit: {percent}% or ${absolute}"
                        )
                    else:
                        context.bot.send_message(
                            chat_id=chat_id, 
                            text="Usage: /threshold <percent> <absolute>\nExample: /threshold 1.0 2.0"
                        )
                except ValueError as e:
                    context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            else:
                # Get current thresholds
                thresholds = self.arbitrage_detector.get_thresholds()
                context.bot.send_message(
                    chat_id=chat_id, 
                    text=f"📊 *Current thresholds:*\nMinimum profit: {thresholds.min_profit_percentage}% or ${thresholds.min_profit_absolute}",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            log_exception(self.logger, e, "Error in /threshold command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
            
    def _arbitrage_command(self, update: Update, context: CallbackContext):
        """Handle /arbitrage command"""
        try:
            chat_id = update.effective_chat.id
            
            if not self.arbitrage_detector:
                context.bot.send_message(chat_id=chat_id, text="Arbitrage detector not available.")
                return
                
            # Get active opportunities
            active_opps = self.arbitrage_detector.get_active_opportunities()
            
            if not active_opps:
                context.bot.send_message(chat_id=chat_id, text="🔍 No active arbitrage opportunities found.")
                return
                
            # Format opportunities for display
            opp_text = f"💰 *Active Arbitrage Opportunities* ({len(active_opps)} found):\n\n"
            
            # Show first 5 opportunities
            count = 0
            for key, opp in list(active_opps.items())[:5]:
                count += 1
                opp_text += f"{count}. {opp['symbol']}\n"
                opp_text += f"   ➕ Buy on {opp['buy_exchange']} at ${opp['buy_price']:.4f}\n"
                opp_text += f"   ➖ Sell on {opp['sell_exchange']} at ${opp['sell_price']:.4f}\n"
                opp_text += f"   💹 Profit: {opp['profit_percentage']:.2f}% (${opp['profit_absolute']:.4f})\n"
                opp_text += f"   🕒 Duration: {opp['duration_seconds']:.1f}s\n\n"
                
            if len(active_opps) > 5:
                opp_text += f"... and {len(active_opps) - 5} more opportunities."
                
            # Add navigation buttons
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data='refresh_arbitrage')],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            context.bot.send_message(chat_id=chat_id, text=opp_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error in /arbitrage command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _monitor_arb_command(self, update: Update, context: CallbackContext):
        """Handle /monitor_arb command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            
            if not self.service_controller:
                context.bot.send_message(chat_id=chat_id, text="Service controller not available.")
                return
                
            # Add chat to alert subscribers
            if self.alert_manager:
                self.alert_manager.add_subscriber(chat_id)
                
            if not context.args:
                context.bot.send_message(
                    chat_id=chat_id, 
                    text="Usage: /monitor_arb <asset1_on_exchangeA> <asset2_on_exchangeB> <threshold>\nExample: /monitor_arb BTC-USDT_on_binance BTC-USDT_on_okx 1.5"
                )
                return
                
            if len(context.args) < 3:
                context.bot.send_message(
                    chat_id=chat_id, 
                    text="Please provide at least two assets and a threshold.\nExample: /monitor_arb BTC-USDT_on_binance BTC-USDT_on_okx 1.5"
                )
                return
                
            try:
                # Parse assets and threshold
                assets = context.args[:-1]  # All args except the last one (threshold)
                threshold = self._parse_threshold(context.args[-1])
                
                # Parse asset_exchange pairs
                asset_exchanges = {}
                for asset in assets:
                    if '_on_' not in asset:
                        context.bot.send_message(
                            chat_id=chat_id, 
                            text=f"Invalid asset format: {asset}. Use format: SYMBOL_on_EXCHANGE"
                        )
                        return
                        
                    symbol, exchange = asset.split('_on_')
                    exchange = exchange.lower()
                    
                    # Validate exchange
                    if not self._validate_exchange(exchange):
                        context.bot.send_message(
                            chat_id=chat_id, 
                            text=f"Invalid exchange: {exchange}. Supported exchanges: {', '.join(self.supported_exchanges)}"
                        )
                        return
                        
                    # Validate symbol
                    if not self._validate_symbol(symbol):
                        context.bot.send_message(
                            chat_id=chat_id, 
                            text=f"Invalid symbol format: {symbol}"
                        )
                        return
                        
                    # Add to asset_exchanges mapping
                    if symbol not in asset_exchanges:
                        asset_exchanges[symbol] = []
                    asset_exchanges[symbol].append(exchange)
                    
                # Start monitoring through service controller
                success = self.service_controller.start_arbitrage_monitoring(
                    asset_exchanges, 
                    threshold_percentage=threshold
                )
                
                if success:
                    # Update user configuration
                    symbols_to_monitor = list(asset_exchanges.keys())
                    self.user_config_manager.update_arbitrage_config(
                        user_id,
                        assets=symbols_to_monitor,
                        threshold_percentage=threshold,
                        enabled=True
                    )
                    
                    # Store monitored symbols
                    self.arbitrage_monitoring_symbols = symbols_to_monitor
                    
                    # Create live updating message for arbitrage opportunities
                    message = context.bot.send_message(
                        chat_id=chat_id, 
                        text=f"✅ Started arbitrage monitoring for: {', '.join(symbols_to_monitor)}\nThreshold: {threshold}%\n\n🔄 Monitoring for opportunities..."
                    )
                    
                    # Store message for live updates
                    self.live_messages[f"arb_{chat_id}"] = {
                        'message_id': message.message_id,
                        'chat_id': chat_id,
                        'type': 'arbitrage',
                        'symbols': symbols_to_monitor
                    }
                    
                    # Start alert monitoring thread
                    alert_thread = threading.Thread(target=self._arbitrage_alert_monitoring, args=(chat_id, symbols_to_monitor))
                    alert_thread.daemon = True
                    alert_thread.start()
                    
                    context.bot.send_message(chat_id=chat_id, text="✅ Arbitrage monitoring started successfully!")
                else:
                    context.bot.send_message(chat_id=chat_id, text="❌ Failed to start arbitrage monitoring.")
                    
            except ValueError as e:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as e:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
                
        except Exception as e:
            log_exception(self.logger, e, "Error in /monitor_arb command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
            
    def _stop_arb_command(self, update: Update, context: CallbackContext):
        """Handle /stop_arb command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            
            if not self.service_controller:
                context.bot.send_message(chat_id=chat_id, text="Service controller not available.")
                return
                
            try:
                success = self.service_controller.stop_arbitrage_monitoring()
                
                if success:
                    self.arbitrage_monitoring_symbols = []
                    
                    # Update user configuration
                    self.user_config_manager.update_arbitrage_config(user_id, enabled=False)
                    
                    # Remove live message if exists
                    if f"arb_{chat_id}" in self.live_messages:
                        del self.live_messages[f"arb_{chat_id}"]
                        
                    context.bot.send_message(chat_id=chat_id, text="⏹️ Stopped arbitrage monitoring.")
                else:
                    context.bot.send_message(chat_id=chat_id, text="❌ Failed to stop arbitrage monitoring.")
            except Exception as e:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
                
        except Exception as e:
            log_exception(self.logger, e, "Error in /stop_arb command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
            
    def _status_arb_command(self, update: Update, context: CallbackContext):
        """Handle /status_arb command"""
        try:
            chat_id = update.effective_chat.id
            
            if not self.service_controller:
                context.bot.send_message(chat_id=chat_id, text="Service controller not available.")
                return
                
            # Get status from service controller
            status = self.service_controller.get_arbitrage_status()
            
            status_text = "📊 *Arbitrage Monitoring Status*\n\n"
            
            if status['monitoring']:
                status_text += f"✅ *Active*\n"
                monitored_assets = status['monitored_assets']
                asset_list = []
                for asset, exchanges in monitored_assets.items():
                    asset_list.append(f"{asset} ({', '.join(exchanges)})")
                status_text += f"Monitoring assets: {', '.join(asset_list)}\n"
                
                # Get current thresholds
                thresholds = status['thresholds']
                status_text += f"Thresholds: {thresholds['percentage']}% or ${thresholds['absolute']}\n"
                
                # Get opportunity count
                opp_count = status['active_opportunities_count']
                status_text += f"Active opportunities: {opp_count}\n"
                status_text += f"Last updated: {time.strftime('%H:%M:%S', time.localtime(status['last_update']))}"
            else:
                status_text += "⏸️ *Inactive*\nNo arbitrage monitoring currently running."
                
            # Add navigation buttons
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data='refresh_arb_status')],
                [InlineKeyboardButton("⏹️ Stop Monitoring", callback_data='stop_arb')],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            context.bot.send_message(chat_id=chat_id, text=status_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error in /status_arb command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
                
    def _arb_stats_command(self, update: Update, context: CallbackContext):
        """Handle /arb_stats command"""
        try:
            chat_id = update.effective_chat.id
            
            if not self.arbitrage_detector:
                context.bot.send_message(chat_id=chat_id, text="Arbitrage detector not available.")
                return
                
            # Check if a symbol was specified
            symbol = None
            if context.args:
                symbol = context.args[0]
                
            try:
                # Get statistics (last 24 hours by default)
                stats = self.arbitrage_detector.get_historical_statistics(symbol, hours=24)
                
                # Format statistics for display
                if symbol:
                    stats_text = f"📊 *Arbitrage Statistics for {symbol} (Last 24 Hours)*\n\n"
                else:
                    stats_text = f"📊 *Overall Arbitrage Statistics (Last 24 Hours)*\n\n"
                    
                stats_text += f"Total Opportunities: {stats.total_opportunities}\n"
                stats_text += f"Average Spread: {stats.average_spread:.4f}\n"
                stats_text += f"Maximum Spread: {stats.max_spread:.4f}\n"
                
                # Add opportunities by symbol if no specific symbol was requested
                if not symbol and stats.opportunities_by_symbol:
                    stats_text += "\n Opportunities by Symbol:\n"
                    for sym, count in list(stats.opportunities_by_symbol.items())[:10]:  # Limit to top 10
                        stats_text += f"  • {sym}: {count}\n"
                        
                # Add opportunities by exchange pair
                if stats.opportunities_by_exchange_pair:
                    stats_text += "\n Opportunities by Exchange Pair:\n"
                    # Sort by count and show top 10
                    sorted_pairs = sorted(stats.opportunities_by_exchange_pair.items(), 
                                        key=lambda x: x[1], reverse=True)[:10]
                    for pair, count in sorted_pairs:
                        stats_text += f"  • {pair}: {count}\n"
                        
                # Add time period information
                start_time = datetime.fromtimestamp(stats.start_time).strftime('%Y-%m-%d %H:%M:%S')
                end_time = datetime.fromtimestamp(stats.end_time).strftime('%Y-%m-%d %H:%M:%S')
                stats_text += f"\n Time Period: {start_time} to {end_time}\n"
                stats_text += f" Sample Size: {stats.total_opportunities} opportunities"
                
                # Add navigation buttons
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data='refresh_stats')],
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                context.bot.send_message(chat_id=chat_id, text=stats_text, reply_markup=reply_markup, parse_mode='Markdown')
                
            except Exception as e:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
                
        except Exception as e:
            log_exception(self.logger, e, "Error in /arb_stats command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _view_market_command(self, update: Update, context: CallbackContext):
        """Handle /view_market command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            
            if not self.service_controller:
                context.bot.send_message(chat_id=chat_id, text="Service controller not available.")
                return
                
            # Add chat to alert subscribers
            if self.alert_manager:
                self.alert_manager.add_subscriber(chat_id)
                
            if not context.args:
                context.bot.send_message(
                    chat_id=chat_id, 
                    text="Usage: /view_market <symbol> <exchange1> <exchange2> ...\nExample: /view_market BTC-USDT binance okx bybit"
                )
                return
                
            if len(context.args) < 2:
                context.bot.send_message(
                    chat_id=chat_id, 
                    text="Please provide a symbol and at least one exchange.\nExample: /view_market BTC-USDT binance okx"
                )
                return
                
            try:
                symbol = context.args[0]
                
                # Validate symbol
                if not self._validate_symbol(symbol):
                    context.bot.send_message(chat_id=chat_id, text=f"Invalid symbol format: {symbol}")
                    return
                    
                # Parse exchanges
                exchanges = []
                for exchange in context.args[1:]:
                    exchange = exchange.lower()
                    
                    # Validate exchange
                    if not self._validate_exchange(exchange):
                        context.bot.send_message(
                            chat_id=chat_id, 
                            text=f"Invalid exchange: {exchange}. Supported exchanges: {', '.join(self.supported_exchanges)}"
                        )
                        return
                        
                    exchanges.append(exchange)
                    
                # Start monitoring through service controller
                symbol_exchanges = {symbol: exchanges}
                success = self.service_controller.start_market_view_monitoring(symbol_exchanges)
                
                if success:
                    # Update user configuration
                    self.user_config_manager.update_market_view_config(
                        user_id,
                        symbols=[symbol],
                        exchanges=exchanges,
                        enabled=True
                    )
                    
                    # Store monitored symbols
                    self.market_view_symbols[symbol] = exchanges
                    
                    # Create live updating message for market view
                    message = context.bot.send_message(
                        chat_id=chat_id, 
                        text=f"✅ Started market view monitoring for {symbol} on: {', '.join(exchanges)}\n\n🔄 Fetching market data..."
                    )
                    
                    # Store message for live updates
                    self.live_messages[f"market_{chat_id}"] = {
                        'message_id': message.message_id,
                        'chat_id': chat_id,
                        'type': 'market',
                        'symbol': symbol,
                        'exchanges': exchanges
                    }
                    
                    # Start market view alert monitoring thread
                    alert_thread = threading.Thread(target=self._market_view_alert_monitoring, args=(chat_id, symbol, exchanges))
                    alert_thread.daemon = True
                    alert_thread.start()
                    
                    context.bot.send_message(chat_id=chat_id, text="✅ Market view monitoring started successfully!")
                else:
                    context.bot.send_message(chat_id=chat_id, text="❌ Failed to start market view monitoring.")
                    
            except Exception as e:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
                
        except Exception as e:
            log_exception(self.logger, e, "Error in /view_market command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
            
    def _market_view_alert_monitoring(self, chat_id: int, symbol: str, exchanges: List[str]):
        """Monitor market view and send periodic alerts"""
        try:
            if not self.market_view_manager or not self.alert_manager:
                return
                
            while chat_id in [lm['chat_id'] for lm in self.live_messages.values() if lm['type'] == 'market' and lm['symbol'] == symbol]:
                current_time = time.time()
                
                # Send periodic updates
                if current_time - self.last_market_view_update >= self.market_view_update_interval:
                    # Get consolidated market view
                    market_view = self.market_view_manager.get_consolidated_market_view(symbol, exchanges)
                    
                    if market_view:
                        # Send alert
                        self.alert_manager.send_market_view_alert(market_view)
                        
                    self.last_market_view_update = current_time
                    
                # Sleep to avoid excessive CPU usage
                time.sleep(5)  # Check every 5 seconds
                
        except Exception as e:
            self.logger.error(f"Error in market view alert monitoring: {e}")
            
    def _stop_market_command(self, update: Update, context: CallbackContext):
        """Handle /stop_market command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            
            if not self.service_controller:
                context.bot.send_message(chat_id=chat_id, text="Service controller not available.")
                return
                
            try:
                success = self.service_controller.stop_market_view_monitoring()
                
                if success:
                    self.market_view_symbols = {}
                    
                    # Update user configuration
                    self.user_config_manager.update_market_view_config(user_id, enabled=False)
                    
                    # Remove live message if exists
                    if f"market_{chat_id}" in self.live_messages:
                        del self.live_messages[f"market_{chat_id}"]
                        
                    context.bot.send_message(chat_id=chat_id, text="⏹️ Stopped market view monitoring.")
                else:
                    context.bot.send_message(chat_id=chat_id, text="❌ Failed to stop market view monitoring.")
            except Exception as e:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
                
        except Exception as e:
            log_exception(self.logger, e, "Error in /stop_market command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
            
    def _get_cbbo_command(self, update: Update, context: CallbackContext):
        """Handle /get_cbbo command"""
        try:
            chat_id = update.effective_chat.id
            
            if not self.market_view_manager:
                context.bot.send_message(chat_id=chat_id, text="Market view manager not available.")
                return
                
            if not context.args:
                context.bot.send_message(
                    chat_id=chat_id, 
                    text="Usage: /get_cbbo <symbol>\nExample: /get_cbbo BTC-USDT"
                )
                return
                
            try:
                symbol = context.args[0]
                
                # Validate symbol
                if not self._validate_symbol(symbol):
                    context.bot.send_message(chat_id=chat_id, text=f"Invalid symbol format: {symbol}")
                    return
                    
                # Get CBBO
                cbbo = self.market_view_manager.get_cbbo(symbol)
                
                if not cbbo:
                    context.bot.send_message(chat_id=chat_id, text=f"❌ Failed to retrieve CBBO for {symbol}")
                    return
                    
                # Format CBBO data
                cbbo_text = f"📊 *Consolidated Best Bid/Offer for {symbol}*\n"
                cbbo_text += f"🕐 Updated: {time.strftime('%H:%M:%S')}\n\n"
                cbbo_text += f"💰 Best Bid: {cbbo.cbbo_bid_price:.4f} on {cbbo.cbbo_bid_exchange.upper()}\n"
                cbbo_text += f"💵 Best Ask: {cbbo.cbbo_ask_price:.4f} on {cbbo.cbbo_ask_exchange.upper()}\n"
                cbbo_text += f"📈 Spread: {cbbo.cbbo_ask_price - cbbo.cbbo_bid_price:.4f}\n"
                cbbo_text += f"📊 Exchanges: {len(cbbo.exchanges_data)} monitored"
                
                # Add navigation buttons
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data=f'refresh_cbbo_{symbol}')],
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                context.bot.send_message(chat_id=chat_id, text=cbbo_text, reply_markup=reply_markup, parse_mode='Markdown')
                
            except Exception as e:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
                
        except Exception as e:
            log_exception(self.logger, e, "Error in /get_cbbo command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
            
    def _config_market_command(self, update: Update, context: CallbackContext):
        """Handle /config_market command"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            self._show_market_view_config_menu(user_id, chat_id, context)
        except Exception as e:
            log_exception(self.logger, e, "Error in /config_market command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _status_market_command(self, update: Update, context: CallbackContext):
        """Handle /status_market command"""
        try:
            chat_id = update.effective_chat.id
            
            if not self.service_controller:
                context.bot.send_message(chat_id=chat_id, text="Service controller not available.")
                return
                
            # Get status from service controller
            status = self.service_controller.get_market_view_status()
            
            status_text = "📊 *Market View Monitoring Status*\n"
            status_text += f"🕐 Updated: {time.strftime('%H:%M:%S', time.localtime(status['last_update']))}\n\n"
            
            if status['monitoring']:
                status_text += f"✅ *Active*\n"
                status_text += f"Monitored symbols: {len(status['monitored_symbols'])}\n"
                status_text += f"Consolidated views: {status['consolidated_views_count']}\n"
                
                # List monitored symbols
                if self.market_view_symbols:
                    status_text += "\n📋 *Currently Monitoring:*\n"
                    for symbol, exchanges in self.market_view_symbols.items():
                        status_text += f"• {symbol} on {', '.join(exchanges)}\n"
            else:
                status_text += "⏸️ *Inactive*\nNo market view monitoring currently running."
                
            # Add navigation buttons
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data='refresh_market_status')],
                [InlineKeyboardButton("⏹️ Stop Monitoring", callback_data='stop_market')],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data='menu_main')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            context.bot.send_message(chat_id=chat_id, text=status_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error in /status_market command")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _show_exchange_selection_menu(self, user_id: int, chat_id: int, context: CallbackContext, callback_prefix: str):
        """Show exchange selection menu"""
        try:
            menu_text = "📋 *Select Exchanges*\n\nChoose one or more exchanges:"
            
            # Create buttons for each exchange
            keyboard = []
            for exchange in self.supported_exchanges:
                keyboard.append([InlineKeyboardButton(exchange.upper(), callback_data=f'{callback_prefix}_{exchange}')])
                
            # Add done button
            keyboard.append([InlineKeyboardButton("✅ Done", callback_data=f'{callback_prefix}_done')])
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data='config_main')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing exchange selection menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _show_symbol_selection_menu(self, user_id: int, chat_id: int, context: CallbackContext, callback_prefix: str):
        """Show symbol selection menu"""
        try:
            menu_text = "📝 *Select Symbols*\n\nChoose symbols to monitor:"
            
            # Get some sample symbols for selection
            sample_symbols = []
            if self.market_fetcher:
                all_symbols = self.market_fetcher.get_all_symbols()
                for exchange, symbols in all_symbols.items():
                    sample_symbols.extend(symbols[:3])  # Take first 3 symbols from each exchange
                    if len(sample_symbols) >= 3:
                        break
                sample_symbols = list(set(sample_symbols))[:6]  # Ensure unique, max 6 symbols
                
            # Create buttons for sample symbols
            keyboard = []
            if sample_symbols:
                for symbol in sample_symbols:
                    keyboard.append([InlineKeyboardButton(symbol, callback_data=f'{callback_prefix}_{symbol}')])
                keyboard.append([InlineKeyboardButton("➕ Add Custom Symbol", callback_data=f'{callback_prefix}_custom')])
            else:
                keyboard.append([InlineKeyboardButton("➕ Add Custom Symbol", callback_data=f'{callback_prefix}_custom')])
                
            # Add done button
            keyboard.append([InlineKeyboardButton("✅ Done", callback_data=f'{callback_prefix}_done')])
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data='config_main')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing symbol selection menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _show_threshold_input_menu(self, user_id: int, chat_id: int, context: CallbackContext, threshold_type: str):
        """Show threshold input menu"""
        try:
            if threshold_type == 'percent':
                menu_text = "🔢 *Set Percentage Threshold*\n\nEnter minimum profit percentage (e.g., 1.5 for 1.5%):"
            else:  # absolute
                menu_text = "💵 *Set Absolute Threshold*\n\nEnter minimum profit in USD (e.g., 2.0 for $2.00):"
                
            # Add back button
            keyboard = [
                [InlineKeyboardButton("⬅️ Back", callback_data='config_arb_menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            context.bot.send_message(chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode='Markdown')
            
            # Set user state to expect threshold input
            self.user_states[chat_id] = {
                'state': f'waiting_threshold_{threshold_type}',
                'user_id': user_id,
                'timestamp': time.time()
            }
            
        except Exception as e:
            log_exception(self.logger, e, "Error showing threshold input menu")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
        
    def _button_callback(self, update: Update, context: CallbackContext):
        """Handle button callbacks"""
        try:
            query = update.callback_query
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            
            # Answer the callback query to remove loading indicator
            query.answer()
            
            data = query.data
            
            # Main menu navigation
            if data == 'menu_main':
                self._show_main_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            # Menu navigation
            elif data == 'menu_arb':
                self._show_arbitrage_config_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            elif data == 'menu_market':
                self._show_market_view_config_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            elif data == 'menu_alerts':
                self._show_alerts_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            elif data == 'menu_config':
                self._show_config_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            elif data == 'menu_status':
                self._status_command(update, context)
                query.delete_message()
                return
                
            # Configuration menu navigation
            elif data == 'config_main':
                self._show_config_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            elif data == 'config_arb_menu':
                self._show_arbitrage_config_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            elif data == 'config_market_menu':
                self._show_market_view_config_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            elif data == 'config_prefs_menu':
                self._show_preferences_menu(user_id, chat_id, context)
                query.delete_message()
                return
                
            elif data == 'config_save':
                success = self.user_config_manager.save_config()
                if success:
                    query.edit_message_text(text="✅ Configuration saved successfully!")
                else:
                    query.edit_message_text(text="❌ Failed to save configuration.")
                return
                
            elif data == 'config_reset':
                success = self.user_config_manager.reset_user_config(user_id)
                if success:
                    query.edit_message_text(text="✅ Configuration reset to defaults!")
                else:
                    query.edit_message_text(text="❌ Failed to reset configuration.")
                return
                
            # Arbitrage configuration
            elif data == 'config_arb_assets':
                # TODO: Implement asset management
                query.edit_message_text(text="Asset management (coming soon)")
                return
                
            elif data == 'config_arb_exchanges':
                self._show_exchange_selection_menu(user_id, chat_id, context, 'config_arb_exchange')
                query.delete_message()
                return
                
            elif data == 'config_arb_thresholds':
                # Show threshold setting options
                keyboard = [
                    [InlineKeyboardButton("🔢 Percentage Threshold", callback_data='config_arb_threshold_percent')],
                    [InlineKeyboardButton("💵 Absolute Threshold", callback_data='config_arb_threshold_absolute')],
                    [InlineKeyboardButton("⬅️ Back", callback_data='config_arb_menu')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Select threshold type to configure:",
                    reply_markup=reply_markup
                )
                return
                
            elif data == 'config_arb_threshold_percent':
                self._show_threshold_input_menu(user_id, chat_id, context, 'percent')
                query.delete_message()
                return
                
            elif data == 'config_arb_threshold_absolute':
                self._show_threshold_input_menu(user_id, chat_id, context, 'absolute')
                query.delete_message()
                return
                
            elif data == 'config_arb_max_monitors':
                # TODO: Implement max monitors setting
                query.edit_message_text(text="Max monitors setting (coming soon)")
                return
                
            elif data == 'config_arb_toggle':
                arb_config = self.user_config_manager.get_arbitrage_config(user_id)
                new_state = not arb_config.get('enabled', False)
                self.user_config_manager.update_arbitrage_config(user_id, enabled=new_state)
                query.edit_message_text(text=f"{'✅' if new_state else '❌'} Arbitrage monitoring {'enabled' if new_state else 'disabled'}")
                return
                
            # Market view configuration
            elif data == 'config_mv_symbols':
                self._show_symbol_selection_menu(user_id, chat_id, context, 'config_mv_symbol')
                query.delete_message()
                return
                
            elif data == 'config_mv_exchanges':
                self._show_exchange_selection_menu(user_id, chat_id, context, 'config_mv_exchange')
                query.delete_message()
                return
                
            elif data == 'config_mv_frequency':
                # Show frequency options
                keyboard = [
                    [InlineKeyboardButton("⏱️ 15 seconds", callback_data='config_mv_freq_15')],
                    [InlineKeyboardButton("⏱️ 30 seconds", callback_data='config_mv_freq_30')],
                    [InlineKeyboardButton("⏱️ 60 seconds", callback_data='config_mv_freq_60')],
                    [InlineKeyboardButton("⏱️ 120 seconds", callback_data='config_mv_freq_120')],
                    [InlineKeyboardButton("⬅️ Back", callback_data='config_market_menu')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Select update frequency:",
                    reply_markup=reply_markup
                )
                return
                
            elif data.startswith('config_mv_freq_'):
                freq_str = data.split('_')[3]
                freq = int(freq_str)
                self.user_config_manager.update_market_view_config(user_id, update_frequency=freq)
                self.market_view_update_interval = freq
                query.edit_message_text(text=f"✅ Market view update frequency set to {freq} seconds")
                return
                
            elif data == 'config_mv_threshold':
                # TODO: Implement change threshold setting
                query.edit_message_text(text="Change threshold setting (coming soon)")
                return
                
            elif data == 'config_mv_toggle':
                mv_config = self.user_config_manager.get_market_view_config(user_id)
                new_state = not mv_config.get('enabled', False)
                self.user_config_manager.update_market_view_config(user_id, enabled=new_state)
                query.edit_message_text(text=f"{'✅' if new_state else '❌'} Market view monitoring {'enabled' if new_state else 'disabled'}")
                return
                
            # Preferences configuration
            elif data == 'config_prefs_alert_freq':
                # Show alert frequency options
                keyboard = [
                    [InlineKeyboardButton("🔔 Immediate", callback_data='config_prefs_alert_immediate')],
                    [InlineKeyboardButton("⏰ Hourly", callback_data='config_prefs_alert_hourly')],
                    [InlineKeyboardButton("📅 Daily", callback_data='config_prefs_alert_daily')],
                    [InlineKeyboardButton("⬅️ Back", callback_data='config_prefs_menu')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Select alert frequency:",
                    reply_markup=reply_markup
                )
                return
                
            elif data.startswith('config_prefs_alert_'):
                freq = data.split('_')[3]
                self.user_config_manager.update_preferences(user_id, alert_frequency=freq)
                query.edit_message_text(text=f"✅ Alert frequency set to {freq}")
                return
                
            elif data == 'config_prefs_msg_format':
                # Show message format options
                keyboard = [
                    [InlineKeyboardButton("📄 Simple", callback_data='config_prefs_msg_simple')],
                    [InlineKeyboardButton("📝 Detailed", callback_data='config_prefs_msg_detailed')],
                    [InlineKeyboardButton("⬅️ Back", callback_data='config_prefs_menu')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(
                    text="Select message format:",
                    reply_markup=reply_markup
                )
                return
                
            elif data.startswith('config_prefs_msg_'):
                format_type = data.split('_')[3]
                self.user_config_manager.update_preferences(user_id, message_format=format_type)
                query.edit_message_text(text=f"✅ Message format set to {format_type}")
                return
                
            elif data == 'config_prefs_timezone':
                # TODO: Implement timezone setting
                query.edit_message_text(text="Timezone setting (coming soon)")
                return
                
            # Alerts menu
            elif data == 'alerts_toggle':
                if self.alert_manager:
                    is_subscriber = chat_id in self.alert_manager.get_subscribers()
                    if is_subscriber:
                        self.alert_manager.remove_subscriber(chat_id)
                        query.edit_message_text(text="🔕 Alerts disabled for this chat.")
                    else:
                        self.alert_manager.add_subscriber(chat_id)
                        query.edit_message_text(text="🔔 Alerts enabled for this chat.")
                return
                
            elif data == 'alerts_history':
                if self.alert_manager:
                    history = self.alert_manager.get_alert_history(5)
                    if history:
                        history_text = "📋 *Recent Alerts*\n\n"
                        for item in history:
                            alert_type = item['type'].title()
                            timestamp = time.strftime('%H:%M:%S', time.gmtime(item['timestamp']))
                            # Truncate message for display
                            message_preview = item['message'].split('\n')[0]  # First line only
                            history_text += f"• {alert_type} ({timestamp}): {message_preview}\n"
                    else:
                        history_text = "📋 *Alert History*\n\nNo recent alerts."
                        
                    # Add back button
                    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='menu_alerts')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    query.edit_message_text(text=history_text, reply_markup=reply_markup, parse_mode='Markdown')
                return
                
            # Refresh handlers
            elif data == 'refresh_status':
                self._status_command(update, context)
                query.delete_message()
                return
                
            elif data == 'refresh_arbitrage':
                self._arbitrage_command(update, context)
                query.delete_message()
                return
                
            elif data == 'refresh_arb_status':
                self._status_arb_command(update, context)
                query.delete_message()
                return
                
            elif data == 'refresh_market_status':
                self._status_market_command(update, context)
                query.delete_message()
                return
                
            elif data == 'stop_arb':
                # Handle stop arbitrage from button
                self._stop_arb_command(update, context)
                query.edit_message_text(text="⏹️ Stopped arbitrage monitoring.")
                return
                
            elif data == 'stop_market':
                # Handle stop market view from button
                self._stop_market_command(update, context)
                query.edit_message_text(text="⏹️ Stopped market view monitoring.")
                return
                
            elif data.startswith('refresh_cbbo_'):
                symbol = data.split('_')[2]
                # Simulate context.args for get_cbbo_command
                update.message = type('Message', (), {'text': f'/get_cbbo {symbol}'})()
                context.args = [symbol]
                self._get_cbbo_command(update, context)
                query.delete_message()
                return
                
            elif data == 'refresh_stats':
                # Simulate context.args for arb_stats_command (no args for overall stats)
                update.message = type('Message', (), {'text': '/arb_stats'})()
                context.args = []
                self._arb_stats_command(update, context)
                query.delete_message()
                return
                
            # Exchange selection
            elif data.startswith('config_arb_exchange_') or data.startswith('config_mv_exchange_'):
                # Handle exchange selection (for now, just acknowledge)
                exchange = data.split('_')[-1]
                if exchange != 'done':
                    query.answer(f"Selected exchange: {exchange.upper()}")
                else:
                    query.edit_message_text(text="✅ Exchange selection updated.")
                    
            # Symbol selection
            elif data.startswith('config_mv_symbol_'):
                # Handle symbol selection (for now, just acknowledge)
                symbol_part = data.split('_', 2)[2]
                if symbol_part != 'done':
                    query.answer(f"Selected symbol: {symbol_part}")
                else:
                    query.edit_message_text(text="✅ Symbol selection updated.")
                    
            # Custom symbol input
            elif data.endswith('_custom'):
                query.edit_message_text(text="Please enter a custom symbol:")
                # Set user state to expect symbol input
                self.user_states[chat_id] = {
                    'state': 'waiting_custom_symbol',
                    'user_id': user_id,
                    'callback_prefix': data.replace('_custom', ''),
                    'timestamp': time.time()
                }
                
        except Exception as e:
            log_exception(self.logger, e, "Error in button callback")
            try:
                query.edit_message_text(text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
            
    def _echo_message(self, update: Update, context: CallbackContext):
        """Handle text messages (including custom inputs)"""
        try:
            user_id = self._get_user_id(update)
            chat_id = update.effective_chat.id
            message_text = update.message.text
            
            # Add chat to alert subscribers
            if self.alert_manager:
                self.alert_manager.add_subscriber(chat_id)
            
            # Check if we're waiting for user input
            if chat_id in self.user_states:
                user_state = self.user_states[chat_id]
                
                # Check if state is still valid (not expired)
                if time.time() - user_state['timestamp'] < 300:  # 5 minutes timeout
                    
                    # Handle threshold input
                    if user_state['state'] == 'waiting_threshold_percent':
                        try:
                            threshold = self._parse_threshold(message_text)
                            if self.arbitrage_detector:
                                self.arbitrage_detector.set_thresholds(min_profit_percentage=threshold)
                                self.user_config_manager.update_arbitrage_config(
                                    user_state['user_id'],
                                    threshold_percentage=threshold
                                )
                                context.bot.send_message(
                                    chat_id=chat_id, 
                                    text=f"✅ Percentage threshold set to {threshold}%"
                                )
                        except ValueError as e:
                            context.bot.send_message(
                                chat_id=chat_id, 
                                text=self._format_error_message(e)
                            )
                        finally:
                            del self.user_states[chat_id]
                        return
                        
                    elif user_state['state'] == 'waiting_threshold_absolute':
                        try:
                            threshold = self._parse_threshold(message_text)
                            if self.arbitrage_detector:
                                self.arbitrage_detector.set_thresholds(min_profit_absolute=threshold)
                                self.user_config_manager.update_arbitrage_config(
                                    user_state['user_id'],
                                    threshold_absolute=threshold
                                )
                                context.bot.send_message(
                                    chat_id=chat_id, 
                                    text=f"✅ Absolute threshold set to ${threshold}"
                                )
                        except ValueError as e:
                            context.bot.send_message(
                                chat_id=chat_id, 
                                text=self._format_error_message(e)
                            )
                        finally:
                            del self.user_states[chat_id]
                        return
                        
                    # Handle custom symbol input
                    elif user_state['state'] == 'waiting_custom_symbol':
                        if self._validate_symbol(message_text):
                            context.bot.send_message(
                                chat_id=chat_id, 
                                text=f"✅ Custom symbol '{message_text}' accepted"
                            )
                        else:
                            context.bot.send_message(
                                chat_id=chat_id, 
                                text=f"❌ Invalid symbol format: {message_text}"
                            )
                        del self.user_states[chat_id]
                        return
                        
            # Default echo response
            context.bot.send_message(
                chat_id=chat_id, 
                text=f"💬 You said: {message_text}\nUse /help to see available commands or /menu for interactive options."
            )
            
        except Exception as e:
            log_exception(self.logger, e, "Error in echo message")
            try:
                context.bot.send_message(chat_id=chat_id, text=self._format_error_message(e))
            except Exception as send_error:
                self.logger.error(f"Failed to send error message: {send_error}")
