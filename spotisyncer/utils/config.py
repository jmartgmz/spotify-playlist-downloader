"""
Centralized configuration and constants.
Manages default settings and application-wide configuration.
"""

import os


class Config:
    """Application configuration."""
    
    # Folder names
    DEFAULT_DOWNLOAD_FOLDER = "downloaded_songs"
    DEFAULT_PLAYLIST_FOLDER = "playlist_songs"
    DEFAULT_PLAYLISTS_FILE = "playlists.txt"
    DEFAULT_ENV_FILE = ".env"
    
    # Watch settings
    DEFAULT_CHECK_INTERVAL_MINUTES = 10
    MIN_CHECK_INTERVAL_MINUTES = 1
    MAX_CHECK_INTERVAL_MINUTES = 1440  # 24 hours
    
    # CSV settings
    CSV_HEADERS = ["Artist", "Song Title", "Status"]
    CSV_STATUS_DOWNLOADED = "downloaded"
    CSV_STATUS_MISSING = "missing"
    CSV_STATUS_UNABLE_TO_FIND = "unable to be found"
    
    # Download settings
    SPOTIFY_TRACK_LIMIT_PER_REQUEST = 50
    
    @staticmethod
    def get_downloads_folder() -> str:
        """Get the downloads folder path."""
        return os.getenv("SPOTIFY_DOWNLOADS_FOLDER", Config.DEFAULT_DOWNLOAD_FOLDER)
    
    @staticmethod
    def get_playlist_folder() -> str:
        """Get the playlist folder path."""
        return os.getenv("SPOTIFY_PLAYLIST_FOLDER", Config.DEFAULT_PLAYLIST_FOLDER)
    
    @staticmethod
    def get_playlists_file() -> str:
        """Get the playlists file path."""
        return os.getenv("SPOTIFY_PLAYLISTS_FILE", Config.DEFAULT_PLAYLISTS_FILE)
    
    @staticmethod
    def get_check_interval() -> int:
        """Get the check interval in minutes."""
        try:
            interval = int(os.getenv("SPOTIFY_CHECK_INTERVAL", Config.DEFAULT_CHECK_INTERVAL_MINUTES))
            return max(Config.MIN_CHECK_INTERVAL_MINUTES, min(Config.MAX_CHECK_INTERVAL_MINUTES, interval))
        except ValueError:
            return Config.DEFAULT_CHECK_INTERVAL_MINUTES
