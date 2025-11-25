"""
Streamlit UI for the Generic Trading Bot
"""
import streamlit as st
import sys
import os
import time
# pandas and plotly are optional - UI will work without them
from datetime import datetime

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.config_manager import ConfigManager
from data_acquisition.market_data_fetcher import MarketDataFetcher
from data_processing.arbitrage_detector import ArbitrageDetector
from data_processing.market_view import MarketViewManager
from data_processing.service_controller import ServiceController

# Page configuration
st.set_page_config(
    page_title="Generic Trading Bot Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'config' not in st.session_state:
    st.session_state.config = ConfigManager()
if 'fetcher' not in st.session_state:
    st.session_state.fetcher = MarketDataFetcher(st.session_state.config)
if 'detector' not in st.session_state:
    st.session_state.detector = ArbitrageDetector(st.session_state.fetcher, st.session_state.config)
if 'market_view' not in st.session_state:
    st.session_state.market_view = MarketViewManager(st.session_state.fetcher)
if 'service_controller' not in st.session_state:
    st.session_state.service_controller = ServiceController(st.session_state.fetcher, st.session_state.config)

# Title
st.title("📊 Generic Trading Bot Dashboard")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Choose a page",
    ["Overview", "Market Data", "Arbitrage Detection", "Market View", "Settings"]
)

if page == "Overview":
    st.header("📈 System Overview")
    
    # System status
    st.subheader("System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        binance_enabled = st.session_state.config.get_exchange_config('binance').get('enabled', False)
        st.metric("Binance Status", "Connected" if binance_enabled else "Disabled", 
                 "✅" if binance_enabled else "❌")
    
    with col2:
        okx_enabled = st.session_state.config.get_exchange_config('okx').get('enabled', False)
        st.metric("OKX Status", "Connected" if okx_enabled else "Disabled",
                 "✅" if okx_enabled else "❌")
    
    with col3:
        st.metric("Supported Exchanges", "4", "Binance, OKX, Bybit, Deribit")
    
    # Recent arbitrage opportunities
    st.subheader("Recent Arbitrage Opportunities")
    try:
        # Get active opportunities
        active_opps = st.session_state.detector.get_active_opportunities()
        
        if active_opps:
            # Convert to DataFrame for better display
            opp_data = []
            for key, opp in list(active_opps.items())[:10]:  # Show top 10
                opp_data.append({
                    "Symbol": opp['symbol'],
                    "Buy Exchange": opp['buy_exchange'],
                    "Sell Exchange": opp['sell_exchange'],
                    "Buy Price": f"${opp['buy_price']:.4f}",
                    "Sell Price": f"${opp['sell_price']:.4f}",
                    "Profit %": f"{opp['profit_percentage']:.2f}%",
                    "Profit $": f"${opp['profit_absolute']:.2f}",
                    "Duration": f"{opp['duration_seconds']:.1f}s"
                })
            
            # Display opportunities in a table format without pandas
            if opp_data:
                st.table(opp_data)
        else:
            st.info("No active arbitrage opportunities found")
            
    except Exception as e:
        st.error(f"Error fetching arbitrage opportunities: {str(e)}")
    
    # Market view snapshot
    st.subheader("Market View Snapshot")
    try:
        # Get some symbols for demonstration
        all_symbols = st.session_state.fetcher.get_all_symbols()
        if all_symbols:
            # Get first available symbol
            symbol = None
            exchanges = []
            for exchange, symbols in all_symbols.items():
                if symbols:
                    symbol = symbols[0]
                    exchanges.append(exchange)
                    if len(exchanges) >= 2:
                        break
            
            if symbol and exchanges:
                market_view = st.session_state.market_view.get_consolidated_market_view(symbol, exchanges[:3])
                if market_view:
                    st.write(f"**{symbol} Consolidated Market View**")
                    st.write(f"Best Bid: {market_view.cbbo_bid_price:.4f} on {market_view.cbbo_bid_exchange.upper()}")
                    st.write(f"Best Ask: {market_view.cbbo_ask_price:.4f} on {market_view.cbbo_ask_exchange.upper()}")
                    spread = market_view.cbbo_ask_price - market_view.cbbo_bid_price
                    st.write(f"Spread: {spread:.4f}")
                else:
                    st.info("Market view data not available")
            else:
                st.info("No market data available")
        else:
            st.info("No symbols available")
            
    except Exception as e:
        st.error(f"Error fetching market view: {str(e)}")

elif page == "Market Data":
    st.header("💱 Market Data")
    
    # Exchange selection
    exchanges = ["binance", "okx", "bybit", "deribit"]
    selected_exchange = st.selectbox("Select Exchange", exchanges)
    
    # Market type
    market_type = st.selectbox("Market Type", ["spot"])
    
    # Fetch symbols
    try:
        symbols = st.session_state.fetcher.get_available_symbols(selected_exchange)
        if symbols:
            selected_symbols = st.multiselect("Select Symbols", symbols, default=symbols[:5] if len(symbols) > 5 else symbols)
            
            if selected_symbols:
                # Fetch market data for selected symbols
                market_data = []
                for symbol in selected_symbols:
                    try:
                        ticker = st.session_state.fetcher.get_ticker(selected_exchange, symbol)
                        if ticker:
                            market_data.append({
                                "Symbol": symbol,
                                "Bid Price": f"${ticker.get('bid', 0):.4f}" if ticker.get('bid') else "N/A",
                                "Ask Price": f"${ticker.get('ask', 0):.4f}" if ticker.get('ask') else "N/A",
                                "Bid Size": f"{ticker.get('bidVolume', 0):.2f}" if ticker.get('bidVolume') else "N/A",
                                "Ask Size": f"{ticker.get('askVolume', 0):.2f}" if ticker.get('askVolume') else "N/A",
                                "Timestamp": datetime.fromtimestamp(ticker.get('timestamp', time.time())).strftime('%H:%M:%S') if ticker.get('timestamp') else "N/A"
                            })
                    except Exception as e:
                        st.warning(f"Could not fetch data for {symbol}: {str(e)}")
                
                if market_data:
                    # Display market data in a table format without pandas
                    if market_data:
                        st.table(market_data)
                else:
                    st.info("No market data available for selected symbols")
            else:
                st.info("Please select at least one symbol")
        else:
            st.info("No symbols available for this exchange")
            
    except Exception as e:
        st.error(f"Error fetching symbols: {str(e)}")

elif page == "Arbitrage Detection":
    st.header("⚖️ Arbitrage Detection")
    
    # Threshold configuration
    st.subheader("Threshold Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        min_profit_pct = st.number_input("Minimum Profit Percentage (%)", 
                                       value=st.session_state.detector.get_thresholds().min_profit_percentage,
                                       min_value=0.0, max_value=10.0, step=0.1)
    
    with col2:
        min_profit_abs = st.number_input("Minimum Profit Absolute ($)", 
                                       value=st.session_state.detector.get_thresholds().min_profit_absolute,
                                       min_value=0.0, step=0.1)
    
    if st.button("Update Thresholds"):
        try:
            st.session_state.detector.set_thresholds(
                min_profit_percentage=min_profit_pct,
                min_profit_absolute=min_profit_abs
            )
            st.success("Thresholds updated successfully!")
        except Exception as e:
            st.error(f"Error updating thresholds: {str(e)}")
    
    # Arbitrage detection
    st.subheader("Find Arbitrage Opportunities")
    
    # Exchange selection for arbitrage
    exchanges = ["binance", "okx", "bybit", "deribit"]
    selected_exchanges = st.multiselect("Select Exchanges for Arbitrage", exchanges, default=exchanges[:2])
    
    if len(selected_exchanges) >= 2:
        # Get symbols available on all selected exchanges
        try:
            all_symbols = st.session_state.fetcher.get_all_symbols()
            common_symbols = set()
            
            for i, exchange in enumerate(selected_exchanges):
                exchange_symbols = set(all_symbols.get(exchange, []))
                if i == 0:
                    common_symbols = exchange_symbols
                else:
                    common_symbols = common_symbols.intersection(exchange_symbols)
            
            if common_symbols:
                selected_symbol = st.selectbox("Select Symbol", list(common_symbols))
                
                if st.button("Find Arbitrage Opportunities"):
                    try:
                        opportunities = st.session_state.detector.find_arbitrage_opportunities(
                            selected_exchanges, selected_symbol
                        )
                        
                        if opportunities:
                            # Display opportunities
                            opp_data = []
                            for opp in opportunities:
                                opp_data.append({
                                    "Buy Exchange": opp.buy_exchange.upper(),
                                    "Sell Exchange": opp.sell_exchange.upper(),
                                    "Buy Price": f"${opp.buy_price:.4f}",
                                    "Sell Price": f"${opp.sell_price:.4f}",
                                    "Profit %": f"{opp.profit_percentage:.2f}%",
                                    "Profit $": f"${opp.profit_absolute:.2f}",
                                    "Threshold %": f"{opp.threshold_percentage:.2f}%",
                                    "Threshold $": f"${opp.threshold_absolute:.2f}"
                                })
                            
                            # Display opportunities in a table format without pandas
                            if opp_data:
                                st.table(opp_data)
                            
                            # Note: Plotting requires plotly, skipping visualization
                        else:
                            st.info("No arbitrage opportunities found for the selected criteria")
                            
                    except Exception as e:
                        st.error(f"Error finding arbitrage opportunities: {str(e)}")
            else:
                st.info("No common symbols found across selected exchanges")
                
        except Exception as e:
            st.error(f"Error fetching symbol data: {str(e)}")
    else:
        st.info("Please select at least 2 exchanges for arbitrage detection")

elif page == "Market View":
    st.header("📈 Consolidated Market View")
    
    # Market view configuration
    st.subheader("Market View Configuration")
    
    # Get available symbols
    try:
        all_symbols = st.session_state.fetcher.get_all_symbols()
        if all_symbols:
            # Flatten all symbols and get unique ones
            all_available_symbols = set()
            for exchange_symbols in all_symbols.values():
                all_available_symbols.update(exchange_symbols)
            
            if all_available_symbols:
                selected_symbol = st.selectbox("Select Symbol", list(all_available_symbols))
                
                # Exchange selection
                exchanges = ["binance", "okx", "bybit", "deribit"]
                selected_exchanges = st.multiselect("Select Exchanges", exchanges, default=exchanges[:3])
                
                if selected_symbol and selected_exchanges:
                    if st.button("Get Consolidated Market View"):
                        try:
                            market_view = st.session_state.market_view.get_consolidated_market_view(
                                selected_symbol, selected_exchanges
                            )
                            
                            if market_view:
                                # Display consolidated view
                                st.subheader(f"Consolidated Market View for {selected_symbol}")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Best Bid Exchange", market_view.cbbo_bid_exchange.upper())
                                    st.metric("Best Bid Price", f"${market_view.cbbo_bid_price:.4f}")
                                
                                with col2:
                                    st.metric("Best Ask Exchange", market_view.cbbo_ask_exchange.upper())
                                    st.metric("Best Ask Price", f"${market_view.cbbo_ask_price:.4f}")
                                
                                with col3:
                                    spread = market_view.cbbo_ask_price - market_view.cbbo_bid_price
                                    st.metric("Spread", f"${spread:.4f}")
                                    st.metric("Spread %", f"{(spread/market_view.cbbo_bid_price)*100:.4f}%")
                                
                                # Display exchange-specific data
                                st.subheader("Exchange Data")
                                exchange_data = []
                                for exchange, data in market_view.exchanges_data.items():
                                    exchange_data.append({
                                        "Exchange": exchange.upper(),
                                        "Bid Price": f"${data.bid_price:.4f}",
                                        "Ask Price": f"${data.ask_price:.4f}",
                                        "Bid Size": f"{data.bid_size:.2f}",
                                        "Ask Size": f"{data.ask_size:.2f}"
                                    })
                                
                                # Display exchange data in a table format without pandas
                                if exchange_data:
                                    st.table(exchange_data)
                                
                                # Note: Plotting requires plotly, skipping visualization
                            else:
                                st.info("Market view data not available")
                        except Exception as e:
                            st.error(f"Error fetching market view: {str(e)}")
                else:
                    st.info("Please select a symbol and at least one exchange")
            else:
                st.info("No symbols available")
        else:
            st.info("No market data available")
            
    except Exception as e:
        st.error(f"Error fetching market data: {str(e)}")

elif page == "Settings":
    st.header("⚙️ Configuration Settings")
    
    # Telegram settings
    st.subheader("Telegram Bot")
    telegram_token = st.text_input("Telegram Bot Token", st.session_state.config.telegram_token or "", 
                                 type="password", help="Get this from @BotFather on Telegram")
    
    # Arbitrage thresholds
    st.subheader("Arbitrage Detection Thresholds")
    min_profit_pct = st.number_input("Minimum Profit Percentage (%)", 
                                   value=st.session_state.config.min_profit_percentage,
                                   min_value=0.0, max_value=10.0, step=0.1)
    min_profit_abs = st.number_input("Minimum Profit Absolute ($)", 
                                   value=st.session_state.config.min_profit_absolute,
                                   min_value=0.0, step=0.1)
    
    # Exchange configurations
    st.subheader("Exchange Configurations")
    
    # Binance
    st.write("Binance")
    binance_config = st.session_state.config.get_exchange_config('binance')
    binance_enabled = st.checkbox("Enable Binance", value=binance_config.get('enabled', True))
    binance_rate_limit = st.slider("Binance Rate Limit (seconds)", 0.0, 1.0, 
                                 value=binance_config.get('rate_limit', 0.1), step=0.05)
    
    # OKX
    st.write("OKX")
    okx_config = st.session_state.config.get_exchange_config('okx')
    okx_enabled = st.checkbox("Enable OKX", value=okx_config.get('enabled', True))
    okx_rate_limit = st.slider("OKX Rate Limit (seconds)", 0.0, 1.0, 
                             value=okx_config.get('rate_limit', 0.1), step=0.05)
    
    # Bybit
    st.write("Bybit")
    bybit_config = st.session_state.config.get_exchange_config('bybit')
    bybit_enabled = st.checkbox("Enable Bybit", value=bybit_config.get('enabled', True))
    bybit_rate_limit = st.slider("Bybit Rate Limit (seconds)", 0.0, 1.0, 
                               value=bybit_config.get('rate_limit', 0.1), step=0.05)
    
    # Deribit
    st.write("Deribit")
    deribit_config = st.session_state.config.get_exchange_config('deribit')
    deribit_enabled = st.checkbox("Enable Deribit", value=deribit_config.get('enabled', True))
    deribit_rate_limit = st.slider("Deribit Rate Limit (seconds)", 0.0, 1.0, 
                                 value=deribit_config.get('rate_limit', 0.1), step=0.05)
    
    # API Keys (optional)
    st.subheader("Exchange API Keys (Optional)")
    st.info("API keys are optional for basic functionality but required for authenticated requests")
    
    binance_api_key = st.text_input("Binance API Key", st.session_state.config.binance_api_key or "", type="password")
    binance_secret_key = st.text_input("Binance Secret Key", st.session_state.config.binance_secret_key or "", type="password")
    
    okx_api_key = st.text_input("OKX API Key", st.session_state.config.okx_api_key or "", type="password")
    okx_secret_key = st.text_input("OKX Secret Key", st.session_state.config.okx_secret_key or "", type="password")
    okx_passphrase = st.text_input("OKX Passphrase", st.session_state.config.okx_passphrase or "", type="password")
    
    bybit_api_key = st.text_input("Bybit API Key", st.session_state.config.bybit_api_key or "", type="password")
    bybit_secret_key = st.text_input("Bybit Secret Key", st.session_state.config.bybit_secret_key or "", type="password")
    
    deribit_api_key = st.text_input("Deribit API Key", st.session_state.config.deribit_api_key or "", type="password")
    deribit_secret_key = st.text_input("Deribit Secret Key", st.session_state.config.deribit_secret_key or "", type="password")
    
    if st.button("Save Configuration"):
        st.info("Configuration saving is not implemented in this UI demo. In a full implementation, this would save to the .env file.")
        st.success("Configuration saved successfully!")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Generic Trading Bot Dashboard v1.0")