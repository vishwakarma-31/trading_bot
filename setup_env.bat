@echo off
echo Setting up Python virtual environment for GoQuant Trading Bot...
echo.

REM Create virtual environment
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    exit /b %errorlevel%
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment
    exit /b %errorlevel%
)

REM Upgrade pip
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Failed to upgrade pip
    exit /b %errorlevel%
)

REM Install dependencies
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    exit /b %errorlevel%
)

echo.
echo Virtual environment setup completed successfully!
echo To activate the environment in the future, run: venv\Scripts\activate.bat
echo To deactivate the environment, run: deactivate
echo.
pause