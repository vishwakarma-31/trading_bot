@echo off
echo GoQuant Trading Bot - Mock Data Version
echo ======================================
echo Running with simulated market data
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Run the mock version of the trading bot
echo Starting the trading bot with mock data...
python src/main_mock.py

echo.
echo Press any key to exit...
pause >nul