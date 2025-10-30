@echo off
REM run.bat - Shortcut to run scripts with virtual environment activated (Windows)

IF NOT EXIST .venv (
    echo Error: Virtual environment not found. Run setup.bat first.
    exit /b 1
)

CALL .venv\Scripts\activate.bat

REM Check which script to run
IF "%~1"=="" (
    echo Usage: run.bat ^<command^> [options]
    echo.
    echo Commands:
    echo   check [options]          - One-time playlist checker
    echo   watch [options]          - Background watcher
    echo   update                   - Auto-discover Spotify playlists
    echo   update-csv [options]     - Quick CSV updater (checks downloaded songs)
    echo.
    echo Examples:
    echo   run.bat check
    echo   run.bat check --download-folder C:\\Users\\...\\Music
    echo   run.bat check --manual-verify
    echo   run.bat check --manual-link
    echo   run.bat watch --interval 5
    echo   run.bat update
    echo   run.bat update-csv --download-folder C:\\Users\\...\\Music
    exit /b 0
)

SET SCRIPT=%1
SHIFT

IF /I "%SCRIPT%"=="check" (
    python src\check.py %*
) ELSE IF /I "%SCRIPT%"=="watch" (
    python src\watch.py %*
) ELSE IF /I "%SCRIPT%"=="update" (
    python src\update_playlists_txt.py %*
) ELSE IF /I "%SCRIPT%"=="update-csv" (
    python src\update_csv.py %*
) ELSE (
    echo Unknown command: %SCRIPT%
    echo Run 'run.bat' with no arguments for help.
    exit /b 1
)
