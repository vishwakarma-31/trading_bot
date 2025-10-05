# GoQuant Trading Bot Video Recording Checklist

## Pre-Recording Preparation

### Environment Setup
- [ ] Install latest version of OBS Studio or other screen recording software
- [ ] Configure dual monitor setup (Terminal + Telegram)
- [ ] Test audio recording quality
- [ ] Prepare clean desktop background
- [ ] Close unnecessary applications
- [ ] Ensure stable internet connection

### Bot Configuration
- [ ] Create new Telegram bot with BotFather for demo
- [ ] Obtain GoMarket API credentials
- [ ] Set up fresh project directory
- [ ] Configure .env file with demo credentials
- [ ] Test bot startup and basic functionality
- [ ] Prepare sample data for demonstrations

### Recording Setup
- [ ] Set up screen recording area (1920x1080 recommended)
- [ ] Configure audio input levels
- [ ] Test screen capture quality
- [ ] Prepare script and talking points
- [ ] Have documentation ready for reference
- [ ] Set up timer/stopwatch for timing sections

## Recording Sections

### 1. Introduction (1-2 minutes)
- [ ] Welcome and project overview
- [ ] Mention use of real GoMarket data
- [ ] Outline what will be demonstrated
- [ ] Estimated recording time: 15-20 minutes

### 2. System Setup Demonstration (5-7 minutes)

#### 2.1 Bot Creation with BotFather (2-3 minutes)
- [ ] Open Telegram and search for @BotFather
- [ ] Start new bot creation process
- [ ] Show step-by-step bot creation
- [ ] Receive and secure API token
- [ ] Explain token security importance

#### 2.2 Code Configuration (1-2 minutes)
- [ ] Show project directory structure
- [ ] Demonstrate copying .env.example to .env
- [ ] Show editing .env file with credentials
- [ ] Explain configuration parameters

#### 2.3 Starting the Application (1-2 minutes)
- [ ] Show virtual environment setup
- [ ] Demonstrate dependency installation
- [ ] Show bot startup command
- [ ] Display terminal output during initialization

#### 2.4 Bot Responding to /start Command (1 minute)
- [ ] Open Telegram conversation with bot
- [ ] Send /start command
- [ ] Show bot welcome message
- [ ] Demonstrate basic interaction

### 3. Arbitrage Signal Demonstration (5-7 minutes)

#### 3.1 Configuring Arbitrage Monitoring (2 minutes)
- [ ] Show /config command and menu navigation
- [ ] Navigate to arbitrage configuration
- [ ] Demonstrate asset selection
- [ ] Show exchange configuration
- [ ] Set threshold values

#### 3.2 Using Interactive Buttons (1-2 minutes)
- [ ] Show interactive button menus
- [ ] Demonstrate exchange selection with buttons
- [ ] Show threshold setting through buttons
- [ ] Explain button navigation

#### 3.3 Live Arbitrage Alerts (2-3 minutes)
- [ ] Start arbitrage monitoring with /monitor_arb
- [ ] Show live alert generation
- [ ] Demonstrate alert format
- [ ] Show multiple arbitrage opportunities
- [ ] Explain alert information

### 4. Market View Demonstration (5-7 minutes)

#### 4.1 Configuring Market View (1-2 minutes)
- [ ] Show /config_market command
- [ ] Demonstrate symbol selection
- [ ] Show exchange configuration
- [ ] Explain market view settings

#### 4.2 Requesting CBBO on Demand (1-2 minutes)
- [ ] Use /get_cbbo command
- [ ] Show CBBO data format
- [ ] Demonstrate for multiple symbols
- [ ] Explain CBBO information

#### 4.3 Live Market View Updates (2 minutes)
- [ ] Start market view monitoring
- [ ] Show live updates
- [ ] Demonstrate real-time data
- [ ] Show update frequency

#### 4.4 Venue Signaling in Action (1 minute)
- [ ] Show venue identification
- [ ] Demonstrate best bid/ask
- [ ] Show spread calculations
- [ ] Explain venue recommendations

### 5. Symbol Listing Demonstration (2-3 minutes)

#### 5.1 /list_symbols Command Usage (1 minute)
- [ ] Show /list_symbols syntax
- [ ] Demonstrate basic usage
- [ ] Explain command parameters

#### 5.2 Listing Symbols for Different Exchanges (1 minute)
- [ ] Show Binance symbols
- [ ] Show OKX symbols
- [ ] Show Bybit symbols
- [ ] Show Deribit symbols

#### 5.3 Interactive Presentation of Symbols (1 minute)
- [ ] Show symbol formatting
- [ ] Demonstrate pagination
- [ ] Explain symbol information

### 6. Code Walkthrough (10-15 minutes)

#### 6.1 Project Structure (2-3 minutes)
- [ ] Show overall directory structure
- [ ] Explain src organization
- [ ] Show documentation files
- [ ] Explain configuration files

#### 6.2 Key Components (5-7 minutes)

##### 6.2.1 Data Acquisition Module (1-2 minutes)
- [ ] Show market_data_fetcher.py
- [ ] Explain GoMarket integration
- [ ] Demonstrate symbol discovery
- [ ] Show data fetching mechanisms

##### 6.2.2 Arbitrage Detection Logic (1-2 minutes)
- [ ] Show arbitrage_detector.py
- [ ] Explain cross-exchange logic
- [ ] Demonstrate threshold implementation
- [ ] Show opportunity tracking

##### 6.2.3 Market View Calculation (1-2 minutes)
- [ ] Show market_view.py
- [ ] Explain CBBO calculation
- [ ] Demonstrate venue identification
- [ ] Show data consolidation

##### 6.2.4 Telegram Bot Implementation (2-3 minutes)
- [ ] Show bot_handler.py
- [ ] Explain command structure
- [ ] Demonstrate interactive features
- [ ] Show alert management

#### 6.3 Design Decisions (2-3 minutes)
- [ ] Explain modular architecture
- [ ] Discuss error handling approach
- [ ] Show configuration management
- [ ] Explain service controllers

#### 6.4 Error Handling Approach (1-2 minutes)
- [ ] Show error_handler.py
- [ ] Demonstrate exception handling
- [ ] Explain logging system
- [ ] Show graceful degradation

### 7. Conclusion (1 minute)
- [ ] Summarize key features
- [ ] Mention documentation availability
- [ ] Provide setup information
- [ ] Thank viewers

## Post-Recording Tasks

### Video Editing
- [ ] Review all recorded sections
- [ ] Trim unnecessary parts
- [ ] Add section titles
- [ ] Include callouts for important features
- [ ] Add transitions between sections
- [ ] Ensure smooth flow
- [ ] Check audio quality
- [ ] Add intro/outro if needed

### Final Review
- [ ] Watch complete video
- [ ] Check timing of sections
- [ ] Verify all requirements are met
- [ ] Ensure no sensitive information is visible
- [ ] Confirm video quality
- [ ] Test video playback

### Delivery Preparation
- [ ] Export final video in MP4 format
- [ ] Verify file size is reasonable
- [ ] Test video on different devices
- [ ] Prepare for private sharing
- [ ] Ensure video is not public on YouTube

## Technical Specifications

### Recording Settings
- Resolution: 1920x1080 (1080p)
- Frame Rate: 30 FPS
- Audio: 44.1 kHz, Stereo
- Format: MP4 (H.264)

### Screen Layout
- Left side: Terminal/Code Editor
- Right side: Telegram application
- Ensure both are clearly visible
- Use high contrast themes

### Audio Requirements
- Clear, professional narration
- Minimize background noise
- Consistent volume levels
- Speak clearly and at appropriate pace

## Timing Guidelines

| Section | Minimum | Target | Maximum |
|---------|---------|--------|---------|
| Introduction | 1 min | 1.5 min | 2 min |
| System Setup | 5 min | 6 min | 7 min |
| Arbitrage Signal | 5 min | 6 min | 7 min |
| Market View | 5 min | 6 min | 7 min |
| Symbol Listing | 2 min | 2.5 min | 3 min |
| Code Walkthrough | 10 min | 12.5 min | 15 min |
| Conclusion | 1 min | 1 min | 1 min |
| **Total** | **25 min** | **30 min** | **35 min** |

## Common Issues and Solutions

### Technical Issues
- **Audio problems**: Use external microphone, test levels before recording
- **Screen capture issues**: Update graphics drivers, restart recording software
- **Bot not responding**: Check internet connection, verify API keys
- **Missing dependencies**: Ensure virtual environment is activated

### Content Issues
- **Going over time**: Practice timing, cut non-essential details
- **Forgetting points**: Keep script handy, record sections separately
- **Poor demonstrations**: Prepare sample data, test commands beforehand

### Post-Production Issues
- **Large file sizes**: Use appropriate compression settings
- **Poor quality**: Record in higher quality initially, compress for delivery
- **Sync issues**: Use editing software to align audio/video if needed

## Success Criteria

- [ ] All required sections covered
- [ ] Total length within 25-35 minutes
- [ ] Clear screen recording with audio narration
- [ ] Terminal outputs and Telegram interface visible side-by-side
- [ ] Demonstrated with real GoMarket data
- [ ] Video is private (not public on YouTube)
- [ ] Professional quality presentation
- [ ] All requirements from assignment met