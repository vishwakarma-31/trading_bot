# GoQuant Trading Bot Video Demonstration Script

## Overview
This document outlines the complete script and structure for the video demonstration of the GoQuant Trading Bot. The video will be approximately 30 minutes long and will cover all required sections.

## Video Structure

### 1. Introduction (1-2 minutes)
- Brief introduction to the GoQuant Trading Bot
- Overview of what will be demonstrated
- Mention of the use of real GoMarket data

### 2. System Setup Demonstration (5-7 minutes)

#### 2.1 Bot Creation with BotFather (2-3 minutes)
- Open Telegram and search for @BotFather
- Demonstrate creating a new bot
- Show receiving the API token
- Explain token security

#### 2.2 Code Configuration (1-2 minutes)
- Show project directory structure
- Demonstrate creating .env file from .env.example
- Show configuring TELEGRAM_BOT_TOKEN and GOMARKET_API_KEY
- Explain other configuration options

#### 2.3 Starting the Application (1-2 minutes)
- Show virtual environment activation
- Demonstrate running the bot with python src/main.py
- Show terminal output during startup

#### 2.4 Bot Responding to /start Command (1 minute)
- Open Telegram and interact with the bot
- Show /start command response
- Demonstrate basic bot functionality

### 3. Arbitrage Signal Demonstration (5-7 minutes)

#### 3.1 Configuring Arbitrage Monitoring (2 minutes)
- Show /config_arb command
- Demonstrate interactive configuration menu
- Show setting up assets and exchanges
- Demonstrate setting thresholds

#### 3.2 Using Interactive Buttons (1-2 minutes)
- Show interactive button navigation
- Demonstrate selecting exchanges with buttons
- Show threshold configuration through buttons

#### 3.3 Live Arbitrage Alerts (2-3 minutes)
- Start arbitrage monitoring with /monitor_arb
- Show live alerts being generated
- Demonstrate alert format and information
- Show multiple arbitrage opportunities

### 4. Market View Demonstration (5-7 minutes)

#### 4.1 Configuring Market View (1-2 minutes)
- Show /config_market command
- Demonstrate market view configuration
- Show symbol and exchange selection

#### 4.2 Requesting CBBO on Demand (1-2 minutes)
- Use /get_cbbo command
- Show CBBO data format
- Demonstrate for different symbols

#### 4.3 Live Market View Updates (2 minutes)
- Start market view monitoring with /view_market
- Show live updates
- Demonstrate venue signaling

#### 4.4 Venue Signaling in Action (1 minute)
- Show best bid/ask identification
- Demonstrate venue recommendations
- Show spread calculations

### 5. Symbol Listing Demonstration (2-3 minutes)

#### 5.1 /list_symbols Command Usage (1 minute)
- Show /list_symbols command syntax
- Demonstrate with different exchanges

#### 5.2 Listing Symbols for Different Exchanges (1 minute)
- Show symbols for Binance
- Show symbols for OKX
- Show symbols for Bybit
- Show symbols for Deribit

#### 5.3 Interactive Presentation of Symbols (1 minute)
- Show how symbols are presented
- Demonstrate pagination if needed

### 6. Code Walkthrough (10-15 minutes)

#### 6.1 Project Structure (2-3 minutes)
- Show overall directory structure
- Explain src directory organization
- Show documentation files
- Explain config and data directories

#### 6.2 Key Components (5-7 minutes)

##### 6.2.1 Data Acquisition Module (1-2 minutes)
- Show market_data_fetcher.py
- Explain GoMarket API integration
- Demonstrate symbol discovery
- Show data fetching mechanisms

##### 6.2.2 Arbitrage Detection Logic (1-2 minutes)
- Show arbitrage_detector.py
- Explain cross-exchange comparison
- Demonstrate threshold logic
- Show opportunity tracking

##### 6.2.3 Market View Calculation (1-2 minutes)
- Show market_view.py
- Explain CBBO calculation
- Demonstrate venue identification
- Show data consolidation

##### 6.2.4 Telegram Bot Implementation (2-3 minutes)
- Show bot_handler.py
- Explain command structure
- Demonstrate interactive features
- Show alert management

#### 6.3 Design Decisions (2-3 minutes)
- Explain modular architecture
- Discuss error handling approach
- Show configuration management
- Explain service controllers

#### 6.4 Error Handling Approach (1-2 minutes)
- Show error_handler.py
- Demonstrate exception handling
- Explain logging system
- Show graceful degradation

### 7. Conclusion (1 minute)
- Summarize key features demonstrated
- Mention availability of documentation
- Provide information about setup and deployment

## Screen Recording Setup

### Terminal and Telegram Side-by-Side
- Split screen with terminal on left and Telegram on right
- Ensure both are clearly visible
- Use high contrast themes for readability

### Audio Narration
- Clear, professional narration
- Explain what's happening on screen
- Point out important details
- Maintain consistent pace

### Demonstration with Real GoMarket Data
- Use actual GoMarket API credentials
- Show real-time data fetching
- Demonstrate with actual arbitrage opportunities
- Show real market view data

## Technical Requirements

### Recording Software
- Use screen recording software that supports high-quality video
- Record in at least 1080p resolution
- Ensure good audio quality

### Video Editing
- Add titles for each section
- Include callouts for important features
- Add transitions between sections
- Ensure smooth flow between demonstrations

### File Delivery
- Export as MP4 format
- Keep file size reasonable for sharing
- Ensure video plays smoothly

## Timeline

| Section | Estimated Time | Status |
|---------|----------------|--------|
| Introduction | 1-2 minutes | Pending |
| System Setup | 5-7 minutes | Pending |
| Arbitrage Signal | 5-7 minutes | Pending |
| Market View | 5-7 minutes | Pending |
| Symbol Listing | 2-3 minutes | Pending |
| Code Walkthrough | 10-15 minutes | Pending |
| Conclusion | 1 minute | Pending |
| **Total** | **25-35 minutes** | |

## Notes for Recording

1. Ensure all API keys are removed from screen recordings
2. Use test environment where possible
3. Prepare sample data for consistent demonstrations
4. Have documentation ready for reference during walkthrough
5. Test all commands before recording
6. Record each section separately for easier editing
7. Keep a script handy for consistent narration