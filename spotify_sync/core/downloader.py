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
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC
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
        Download audio from YouTube URL using yt-dlp and apply Spotify metadata.
        Downloads as MP3 format for manual link mode.
        
        Args:
            youtube_url: YouTube URL to download from
            download_folder: Folder to save the downloaded file
            track: Optional track dict from Spotify with metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get list of existing files before download
            existing_files = set(os.listdir(download_folder))
            
            # Step 1: Download audio from YouTube using yt-dlp
            temp_file = os.path.join(download_folder, '%(title)s.%(ext)s')
            yt_dlp_cmd = [
                'yt-dlp',
                '-q',  # Quiet mode
                '--no-warnings',  # No warnings
                '-x',  # Extract audio only
                '--audio-format', 'mp3',
                '--audio-quality', '192',
                '-o', temp_file,
                youtube_url
            ]
            
            result = subprocess.run(yt_dlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"✗ Failed to download from YouTube: {result.stderr}")
                return False
            
            # Get the newly downloaded file (the one that wasn't there before)
            current_files = set(os.listdir(download_folder))
            new_files = current_files - existing_files
            mp3_files = [f for f in new_files if f.endswith('.mp3')]
            
            if not mp3_files:
                print("✗ No MP3 file found after download")
                return False
            
            downloaded_file = os.path.join(download_folder, mp3_files[0])  # Get the newly downloaded file
            
            # Step 2: Apply Spotify metadata using mutagen if track info provided
            if track and isinstance(track, dict):
                try:
                    # Handle artists - list of strings
                    artists_list = track.get('artists', [])
                    artist = ', '.join(artists_list) if isinstance(artists_list, list) else str(artists_list)
                    if not artist:
                        artist = 'Unknown'
                    
                    # Get other metadata
                    title = track.get('name', 'Unknown')
                    album = track.get('album', 'Unknown')
                    album_year = track.get('album_year', '')
                    
                    # Sanitize filename using centralized sanitizer
                    safe_title = FilenameSanitizer.sanitize(title)
                    safe_artist = FilenameSanitizer.sanitize(artist)
                    final_filename = f"{safe_artist} - {safe_title}.mp3"
                    final_filepath = os.path.join(download_folder, final_filename)
                    
                    # Rename file first
                    if downloaded_file != final_filepath:
                        if os.path.exists(final_filepath):
                            os.remove(downloaded_file)  # Remove duplicate
                            return True
                        os.rename(downloaded_file, final_filepath)
                    
                    # Apply metadata using EasyID3
                    try:
                        audio = EasyID3(final_filepath)
                    except Exception:
                        # If no ID3 tag exists, create one
                        audio = MP3(final_filepath)
                        audio.add_tags()
                        audio.save()
                        audio = EasyID3(final_filepath)
                    
                    # Set metadata
                    audio['title'] = [title]
                    audio['artist'] = [artist]
                    audio['album'] = [album]
                    if album_year:
                        audio['date'] = [album_year]
                    
                    # Save basic metadata
                    audio.save()
                    
                    # Now add cover art using mutagen's ID3 directly
                    cover_art_url = track.get('cover_art_url')
                    if cover_art_url:
                        try:
                            cover_path = os.path.join(download_folder, 'cover_temp.jpg')
                            urllib.request.urlretrieve(cover_art_url, cover_path)
                            
                            with open(cover_path, 'rb') as cover_file:
                                cover_data = cover_file.read()
                            
                            # Get or create ID3 tags
                            try:
                                id3 = ID3(final_filepath)
                            except Exception:
                                id3 = ID3()
                            
                            # Add cover art
                            id3.add(APIC(
                                encoding=3,
                                mime='image/jpeg',
                                type=3,
                                desc='Cover',
                                data=cover_data
                            ))
                            id3.save(final_filepath, v2_version=3)
                            os.remove(cover_path)
                        except Exception as e:
                            print(f"⚠ Could not add cover art: {str(e)}")
                    
                    print(f"✓ Downloaded: {final_filename}")
                    
                except Exception as e:
                    print(f"⚠ Could not apply metadata: {str(e)}")
                    # File is still downloaded and renamed, just without proper metadata
                    return True
            else:
                print(f"✓ Downloaded: {os.path.basename(downloaded_file)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error downloading from YouTube: {str(e)}")
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
