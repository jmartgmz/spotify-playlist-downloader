@echo off
setlocal enabledelayedexpansion
REM Spotify Playlist Sync Launcher for Windows
REM This script activates the virtual environment and runs the interactive launcher



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

REM Check and guide user through .env creation
if not exist .env (
    echo.
    echo ========================================
    echo   .env Configuration Setup
    echo ========================================
    echo.
    echo No .env file found. Let's create one!
    echo.
    echo You'll need Spotify API credentials. If you don't have them:
    echo 1. Go to https://developer.spotify.com/dashboard
    echo 2. Create a new app
    echo 3. Add redirect URI: http://127.0.0.1:8888/callback
    echo 4. Copy your Client ID and Client Secret
    echo.
    echo See docs\GETTING_SPOTIFY_API.md for detailed instructions.
    echo.
    
    set /p HAS_CREDS="Do you have your Spotify API credentials? (y/n): "
    
    if /i "!HAS_CREDS!"=="n" (
        echo.
        echo Please get your credentials first, then run this script again.
        echo Opening documentation in your browser...
        start https://developer.spotify.com/dashboard
        pause
        exit /b 0
    )
    
    if /i "!HAS_CREDS!"=="y" (
        echo.
        echo Great! Let's set up your .env file.
        echo.
        
        set /p CLIENT_ID="Enter your Spotify Client ID: "
        set /p CLIENT_SECRET="Enter your Spotify Client Secret: "
        
        echo.
        echo Creating .env file...
        
        >".env" (
            echo # Spotify API Credentials
            echo # Get these from https://developer.spotify.com/dashboard
            echo SPOTIFY_CLIENT_ID=!CLIENT_ID!
            echo SPOTIFY_CLIENT_SECRET=!CLIENT_SECRET!
            echo SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
            echo.
            echo # Optional: Customize folders
            echo # SPOTIFY_DOWNLOADS_FOLDER=downloaded_songs
            echo # SPOTIFY_PLAYLIST_FOLDER=playlist_songs
            echo # SPOTIFY_PLAYLISTS_FILE=playlists.txt
            echo.
            echo # Optional: Watch interval (minutes^)
            echo # SPOTIFY_CHECK_INTERVAL=10
        )
        
        echo.
        echo .env file created successfully!
        echo.
        goto :env_created
    )
    
    echo.
    echo Invalid input. Please run the script again and enter 'y' or 'n'.
    pause
    exit /b 0
)
:env_created

python launcher.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
