"""
Spotify Playlist Sync - Automatically sync your Spotify playlists with local downloads.

This package provides tools for downloading, organizing, and maintaining
a local music library synchronized with your Spotify playlists.
"""

__version__ = "2.0.0"
__author__ = "Spotify Sync Contributors"
__description__ = "Automatically sync your Spotify playlists with local downloads"

# Import core components
try:
    from spotify_sync.core.settings_manager import settings
    from spotify_sync.core.logger import Logger
    
    # Configure logger with settings
    Logger.set_timestamps(settings.get('ui', 'enable_timestamps'))
    Logger.set_debug_mode(settings.get('ui', 'enable_debug_mode'))
    
    __all__ = ['settings', 'Logger']
except ImportError as e:
    # Handle import errors gracefully during development/transition
    print(f"Warning: Could not import core components: {e}")
    __all__ = []