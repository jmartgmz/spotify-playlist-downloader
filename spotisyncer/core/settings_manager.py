"""
Settings manager for user-friendly configuration.
Handles both settings.json and environment variables with fallbacks.
"""

import os
import json
from typing import Any, Dict, Optional

# Import logger safely - avoid circular imports
def _get_logger():
    """Safely get logger instance, avoiding circular imports."""
    try:
        from spotify_sync.core.logger import Logger
        return Logger
    except ImportError:
        # Fallback logger for development/transition
        class FallbackLogger:
            @staticmethod
            def debug(msg):
                print(f"[DEBUG] {msg}")
            @staticmethod
            def warning(msg):
                print(f"[WARNING] {msg}")
            @staticmethod
            def error(msg):
                print(f"[ERROR] {msg}")
            @staticmethod
            def info(msg):
                print(f"[INFO] {msg}")
            @staticmethod
            def success(msg):
                print(f"[SUCCESS] {msg}")
        return FallbackLogger


class SettingsManager:
    """Manages application settings from JSON file and environment variables."""
    
    _instance = None
    _settings = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._settings is None:
            self._load_settings()
    
    def _load_settings(self):
        """Load settings from settings.json and environment variables."""
        self._settings = self._get_default_settings()
        
        # Try to load from settings.json
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    json_settings = json.load(f)
                    self._merge_settings(self._settings, json_settings)
                Logger = _get_logger()
                Logger.debug(f"Loaded settings from {settings_file}")
            except Exception as e:
                Logger = _get_logger()
                Logger.warning(f"Could not load settings.json: {e}")
        
        # Override with environment variables
        self._load_from_environment()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings structure."""
        return {
            "spotify": {
                "client_id": "",
                "client_secret": "",
                "redirect_uri": "http://127.0.0.1:8888/callback"
            },
            "paths": {
                "downloads_folder": "downloaded_songs",
                "playlists_file": "playlists.txt",
                "csv_folder": "playlist_songs"
            },
            "download": {
                "quality": "192",
                "format": "mp3",
                "include_metadata": True,
                "include_cover_art": True,
                "organize_by_playlist": True
            },
            "watcher": {
                "default_interval_minutes": 10,
                "min_interval_minutes": 1,
                "max_interval_minutes": 1440
            },
            "ui": {
                "enable_colors": True,
                "enable_timestamps": True,
                "enable_progress_bars": True,
                "enable_debug_mode": False
            },
            "advanced": {
                "auto_filter_results": True,
                "max_retries": 3,
                "timeout_seconds": 30,
                "parallel_downloads": False
            }
        }
    
    def _merge_settings(self, target: Dict, source: Dict):
        """Recursively merge source settings into target."""
        for key, value in source.items():
            if key.startswith('_'):  # Skip comments/instructions
                continue
                
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._merge_settings(target[key], value)
            else:
                target[key] = value
    
    def _load_from_environment(self):
        """Load settings from environment variables (.env file)."""
        # Load from .env file if it exists
        if os.path.exists('.env'):
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                Logger = _get_logger()
                Logger.debug("python-dotenv not available, skipping .env file")
        
        # Override with environment variables
        env_mapping = {
            'SPOTIFY_CLIENT_ID': ('spotify', 'client_id'),
            'SPOTIFY_CLIENT_SECRET': ('spotify', 'client_secret'),
            'SPOTIFY_REDIRECT_URI': ('spotify', 'redirect_uri'),
            'SPOTIFY_DOWNLOADS_FOLDER': ('paths', 'downloads_folder'),
            'SPOTIFY_PLAYLISTS_FILE': ('paths', 'playlists_file'),
            'SPOTIFY_CHECK_INTERVAL': ('watcher', 'default_interval_minutes'),
        }
        
        for env_var, (section, key) in env_mapping.items():
            value = os.getenv(env_var)
            if value and self._settings and section in self._settings and isinstance(self._settings[section], dict) and key in self._settings[section]:
                # Convert to appropriate type
                if isinstance(self._settings[section][key], int):
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif isinstance(self._settings[section][key], bool):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                self._settings[section][key] = value
                Logger = _get_logger()
                Logger.debug(f"Override from env: {env_var} = {value}")
    
    def get(self, *path) -> Any:
        """Get a setting value by path (e.g., get('spotify', 'client_id'))."""
        if not self._settings:
            return None
            
        current = self._settings
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def set(self, *path_and_value) -> None:
        """Set a setting value by path (e.g., set('spotify', 'client_id', 'value'))."""
        if len(path_and_value) < 2:
            raise ValueError("set() requires at least a path and value")
        
        if not self._settings:
            self._settings = {}
        
        path = path_and_value[:-1]
        value = path_and_value[-1]
        
        current = self._settings
        for key in path[:-1]:
            if not isinstance(current, dict):
                current = {}
            if key not in current:
                current[key] = {}
            current = current[key]
        
        if isinstance(current, dict):
            current[path[-1]] = value
    
    def save(self, file_path: str = "settings.json") -> bool:
        """Save current settings to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=4, ensure_ascii=False)
            Logger = _get_logger()
            Logger.success(f"Settings saved to {file_path}")
            return True
        except Exception as e:
            Logger = _get_logger()
            Logger.error(f"Failed to save settings: {e}")
            return False
    
    def reload(self):
        """Reload settings from file."""
        self._settings = None
        self._load_settings()
    
    # Convenience methods for common settings
    def get_spotify_credentials(self) -> Dict[str, str]:
        """Get Spotify API credentials."""
        return {
            'client_id': self.get('spotify', 'client_id') or '',
            'client_secret': self.get('spotify', 'client_secret') or '',
            'redirect_uri': self.get('spotify', 'redirect_uri') or 'http://127.0.0.1:8888/callback'
        }
    
    def get_downloads_folder(self) -> str:
        """Get downloads folder path."""
        return self.get('paths', 'downloads_folder') or 'downloaded_songs'
    
    def get_playlists_file(self) -> str:
        """Get playlists file path."""
        return self.get('paths', 'playlists_file') or 'playlists.txt'
    
    def get_csv_folder(self) -> str:
        """Get CSV folder path."""
        return self.get('paths', 'csv_folder') or 'playlist_songs'
    
    def get_check_interval(self) -> int:
        """Get watcher check interval in minutes."""
        interval = self.get('watcher', 'default_interval_minutes') or 10
        min_val = self.get('watcher', 'min_interval_minutes') or 1
        max_val = self.get('watcher', 'max_interval_minutes') or 1440
        return max(min_val, min(max_val, interval))
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get('ui', 'enable_debug_mode') or False


# Global settings instance
settings = SettingsManager()


# Legacy compatibility functions (for gradual migration)
class Config:
    """Legacy Config class for backward compatibility."""
    
    @staticmethod
    def get_downloads_folder() -> str:
        return settings.get_downloads_folder()
    
    @staticmethod
    def get_playlists_file() -> str:
        return settings.get_playlists_file()
    
    @staticmethod
    def get_playlist_folder() -> str:
        return settings.get_csv_folder()
    
    @staticmethod
    def get_check_interval() -> int:
        return settings.get_check_interval()
    
    # Constants for CSV status
    CSV_STATUS_DOWNLOADED = "downloaded"
    CSV_STATUS_MISSING = "missing"
    CSV_STATUS_UNABLE_TO_FIND = "unable to be found"
    
    # Other constants
    DEFAULT_CHECK_INTERVAL_MINUTES = 10
    MIN_CHECK_INTERVAL_MINUTES = 1
    MAX_CHECK_INTERVAL_MINUTES = 1440