#!/bin/bash

# Spotify Playlist Sync - Build Script for Linux/macOS
# Creates a standalone executable using PyInstaller

echo "🔨 Building Spotify Playlist Sync Executable..."
echo

# Check if we're in the build_tools directory
if [ ! -f "launcher.spec" ]; then
    echo "❌ Error: Please run this script from the build_tools directory"
    echo "   cd build_tools && ./build.sh"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
cd ..
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Error: Virtual environment not found. Please run setup first."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
cd build_tools
rm -rf build/ dist/

# Build executable
echo "🚀 Building executable with PyInstaller..."
echo "This may take a few minutes..."
echo
pyinstaller launcher.spec

# Check if build was successful
if [ -f "dist/SpotifyPlaylistSync" ]; then
    echo
    echo "🎉 Build successful!"
    echo
    echo "📁 Executable location:"
    ls -lah dist/
    echo
    echo "🚀 To run the executable:"
    echo "   ./build_tools/dist/SpotifyPlaylistSync"
    echo
    echo "📋 Don't forget to:"
    echo "1. Copy .env file to the same directory as the executable"
    echo "2. Copy playlists.txt to the same directory as the executable"
    echo "3. The executable is self-contained and includes all dependencies"
    echo
    
    # Create distribution package
    echo "📦 Distribution package created:"
    echo "   cd dist/"
    echo "   SpotifyPlaylistSync-Distribution/ - Ready to distribute"
    echo "   SpotifyPlaylistSync-Distribution.tar.gz - Compressed package"
    echo
    echo "🎯 The standalone executable includes:"
    echo "   • All Python dependencies bundled"
    echo "   • No Python installation required"
    echo "   • Self-contained and portable"
    echo "   • Ready to run on any compatible system"
else
    echo
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi