@echo off
REM Windows startup script for Banking Assistant
REM This script sets up the environment and starts the Streamlit app

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Banking Assistant Startup
echo   CrewAI + Streamlit
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

echo.
echo [3/4] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check requirements.txt and your internet connection
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [4/4] Initializing database...
python database_setup.py
if errorlevel 1 (
    echo WARNING: Database initialization had issues
    echo The app will try to initialize on first run
)

echo.
echo ========================================
echo   Starting Streamlit Application
echo ========================================
echo.
echo The app will open in your browser at:
echo   http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
