@echo off
echo Starting GoQuant Trading Bot...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup_env.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment
    exit /b %errorlevel%
)

REM Run the bot
python src/main.py
if %errorlevel% neq 0 (
    echo Failed to start the bot
    exit /b %errorlevel%
)

echo.
echo Bot stopped.
pause