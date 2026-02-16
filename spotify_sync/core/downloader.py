"""
Downloader module for SpotiFLAC operations.
Handles downloading songs from Spotify URLs in FLAC format.
"""

import warnings
# Suppress warnings before any subprocess calls
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning,ignore::DeprecationWarning'

import subprocess
import shutil
import sys
from typing import Optional, Dict
import urllib.request
from mutagen.flac import FLAC
from spotify_sync.utils.utils import FilenameSanitizer
import contextlib
import io

try:
    from SpotiFLAC import SpotiFLAC  # type: ignore
    SPOTIFLAC_AVAILABLE = True
except ImportError:
    SpotiFLAC = None  # type: ignore
    SPOTIFLAC_AVAILABLE = False


class SpotiFLACDownloader:
    """Manages SpotiFLAC download operations."""

    @staticmethod
    def check_spotiflac_available() -> bool:
        """
        Check if SpotiFLAC module is available.
        
        Returns:
            True if SpotiFLAC is available, False otherwise
        """
        return SPOTIFLAC_AVAILABLE

    @staticmethod
    def get_youtube_url(track: dict, dont_filter: bool = False) -> Optional[str]:
        """
        Deprecated: SpotiFLAC downloads directly from Spotify, not YouTube.
        This method is kept for backwards compatibility but returns None.
        
        Args:
            track: Track dictionary with 'url' key
            dont_filter: Whether to disable result filtering (unused)
            
        Returns:
            None (not applicable for SpotiFLAC)
        """
        # SpotiFLAC downloads directly from Spotify, no YouTube URL needed
        return None

    @staticmethod
    def download_from_youtube(youtube_url: str, download_folder: str, track: Optional[Dict] = None) -> bool:
        """
        Deprecated: SpotiFLAC downloads directly from Spotify, not YouTube.
        This method is kept for backwards compatibility but returns False.
        
        Args:
            youtube_url: YouTube URL (unused)
            download_folder: Folder to save the downloaded file
            track: Optional track dict from Spotify with metadata
            
        Returns:
            False (not supported)
        """
        print("⚠ YouTube downloads not supported with SpotiFLAC. Use download_from_spotify instead.")
        return False

    @staticmethod
    def download_from_spotify(track: dict, download_folder: str, dont_filter: bool = False) -> tuple[bool, str]:
        """
        Download a song from Spotify URL using SpotiFLAC Python module.
        
        Args:
            track: Track dictionary with 'url' key
            download_folder: Folder to save the download
            dont_filter: Whether to disable result filtering (unused for SpotiFLAC)
            
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            # Check if SpotiFLAC is available
            if not SPOTIFLAC_AVAILABLE or SpotiFLAC is None:
                return False, "SpotiFLAC module not installed. Install with: pip install git+https://github.com/jelte1/SpotiFLAC-Command-Line-Interface.git"
            
            # Get list of existing FLAC files before download
            existing_flacs = set()
            if os.path.exists(download_folder):
                for file in os.listdir(download_folder):
                    if file.endswith('.flac'):
                        existing_flacs.add(file)
            
            # Get track metadata for filename
            artists_list = track.get('artists', [])
            artist = ', '.join(artists_list) if isinstance(artists_list, list) else str(artists_list)
            if not artist:
                artist = 'Unknown'
            
            title = track.get('name', 'Unknown')
            
            # Suppress SpotiFLAC's verbose output
            # Redirect stdout and stderr to suppress all the download progress messages
            
            # Use SpotiFLAC Python module to download
            # SpotiFLAC will try multiple services: tidal, qobuz, deezer, amazon
            try:
                # Suppress all output from SpotiFLAC
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    SpotiFLAC(  # type: ignore
                        url=track['url'],
                        output_dir=download_folder,
                        services=["tidal", "qobuz", "deezer", "amazon"],
                        filename_format="{artist} - {title}",
                        use_track_numbers=False,
                        use_artist_subfolders=False,
                        use_album_subfolders=False,
                        loop=None
                    )
            except Exception as e:
                error_msg = str(e)
                if 'not found' in error_msg.lower():
                    return False, "Track not available on any service"
                elif 'authentication' in error_msg.lower() or 'credentials' in error_msg.lower():
                    return False, "Authentication error"
                elif 'rate limit' in error_msg.lower():
                    return False, "Rate limit reached"
                else:
                    return False, f"Download failed: {error_msg}"
            
            # Verify that a new FLAC file was actually created
            current_flacs = set()
            if os.path.exists(download_folder):
                for file in os.listdir(download_folder):
                    if file.endswith('.flac'):
                        current_flacs.add(file)
            
            new_flacs = current_flacs - existing_flacs
            
            # If download failed, return error
            if len(new_flacs) == 0:
                return False, "No FLAC file was created"
            
            # File was successfully downloaded - no need to print here, caller handles it
            # Return True if at least one new FLAC was created
            return True, ""
            
        except Exception as e:
            return False, str(e)
