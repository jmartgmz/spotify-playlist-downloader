@echo off
REM setup.bat - Setup script for Spotify Playlist Automatic Downloader (Windows)

SETLOCAL ENABLEDELAYEDEXPANSION

REM Check for Python 3
where python >nul 2>nul
IF ERRORLEVEL 1 (
    echo Error: Python 3 is not installed. Please install it first.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
    echo ✓ Virtual environment created
) ELSE (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
CALL .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if ERRORLEVEL 1 (
    echo Error installing dependencies.
    exit /b 1
)
echo ✓ Dependencies installed

REM Check if .env exists
IF NOT EXIST .env (
    echo.
    echo Setting up .env file...
    IF EXIST .env.example (
        copy .env.example .env >nul
        echo ✓ Created .env from template
        echo.
        echo Please edit .env and add your Spotify credentials:
        echo   - SPOTIFY_CLIENT_ID
        echo   - SPOTIFY_CLIENT_SECRET
        echo   - SPOTIFY_REDIRECT_URI (optional)
        echo.
    )
) ELSE (
    echo ✓ .env file already exists
)

REM Check if playlists.txt exists
IF NOT EXIST playlists.txt (
    echo.
    echo Creating playlists.txt...
    echo # Add your Spotify playlist URLs or IDs below, one per line > playlists.txt
    echo # Lines starting with # are comments >> playlists.txt
    echo # Example: >> playlists.txt
    echo # https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M >> playlists.txt
    echo ✓ Created playlists.txt
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env with your Spotify API credentials
