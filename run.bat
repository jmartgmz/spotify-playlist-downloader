@echo off
REM Spotify Playlist Sync Launcher for Windows
REM This script activates the virtual environment and runs the interactive launcher

echo.
echo ========================================
echo   Spotify Playlist Sync - Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found!
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Setting up...
    echo.
    
    REM Create virtual environment
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment!
        echo Continuing with system Python...
        echo.
    ) else (
        echo Virtual environment created!
        call .venv\Scripts\activate.bat
        
        REM Install dependencies
        echo.
        echo Installing dependencies...
        python -m pip install --upgrade pip >nul 2>&1
        pip install -r requirements.txt
        if errorlevel 1 (
            echo Warning: Some dependencies may not have installed correctly.
            echo.
        ) else (
            echo Dependencies installed successfully!
            echo.
        )
    )
)

REM Check if required files exist
if not exist launcher.py (
    echo Error: launcher.py not found!
    echo Please run this script from the project directory.
    pause
    exit /b 1
)

if not exist .env (
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and configure your Spotify credentials.
    echo.
    pause
)

REM Run the launcher
echo Starting Spotify Playlist Sync...
echo.
python launcher.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
