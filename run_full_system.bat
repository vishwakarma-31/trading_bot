@echo off
echo Starting Generic Trading Bot - Full System
echo ========================================
echo This will start both the backend and frontend components
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Run the full system
echo Starting the full trading bot system...
python run_full_system.py

echo.
echo Press any key to exit...
pause >nul