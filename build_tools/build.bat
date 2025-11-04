@echo off
REM Spotify Playlist Sync - Build Script for Windows
REM Creates a standalone executable using PyInstaller

echo 🔨 Building Spotify Playlist Sync Executable...
echo.

REM Check if we're in the build_tools directory
if not exist "launcher.spec" (
    echo ❌ Error: Please run this script from the build_tools directory
    echo    cd build_tools ^&^& build.bat
    exit /b 1
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
cd ..
if exist ".venv" (
    call .venv\Scripts\activate
    echo ✅ Virtual environment activated
) else (
    echo ❌ Error: Virtual environment not found. Please run setup first.
    exit /b 1
)

REM Clean previous builds
echo 🧹 Cleaning previous builds...
cd build_tools
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

REM Build executable
echo 🚀 Building executable with PyInstaller...
echo This may take a few minutes...
echo.
pyinstaller launcher.spec

REM Check if build was successful
if exist "dist\SpotifyPlaylistSync.exe" (
    echo.
    echo 🎉 Build successful!
    echo.
    echo 📁 Executable location:
    dir dist\
    echo.
    echo 🚀 To run the executable:
    echo    .\build_tools\dist\SpotifyPlaylistSync.exe
    echo.
    echo 📋 Don't forget to:
    echo 1. Copy .env file to the same directory as the executable
    echo 2. Copy playlists.txt to the same directory as the executable
    echo 3. The executable is self-contained and includes all dependencies
    echo.
    echo 📦 Distribution package created:
    echo    cd dist\
    echo    SpotifyPlaylistSync-Distribution\ - Ready to distribute
    echo    SpotifyPlaylistSync-Distribution.zip - Compressed package
    echo.
    echo 🎯 The standalone executable includes:
    echo    • All Python dependencies bundled
    echo    • No Python installation required
    echo    • Self-contained and portable
    echo    • Ready to run on any compatible system
) else (
    echo.
    echo ❌ Build failed! Check the output above for errors.
    exit /b 1
)