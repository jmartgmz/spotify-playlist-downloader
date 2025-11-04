"""
Downloader module for spotdl operations.
Handles downloading songs from Spotify/YouTube URLs.
"""

import subprocess
import shutil
import sys
import os
from typing import Optional, Dict
import urllib.request
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from spotify_sync.utils.utils import FilenameSanitizer


class SpotdlDownloader:
    """Manages spotdl download operations."""

    @staticmethod
    def find_spotdl() -> str:
        """
        Find spotdl executable in PATH or virtualenv.
        
        Returns:
            Path to spotdl executable
            
        Raises:
            RuntimeError: If spotdl is not found
        """
        spotdl_path = shutil.which('spotdl')
        if spotdl_path:
            return spotdl_path
        
        venv_spotdl = os.path.join(os.path.dirname(sys.executable), 'spotdl')
        if os.path.exists(venv_spotdl):
            return venv_spotdl
        
        raise RuntimeError("spotdl not found. Please install spotdl in your environment.")

    @staticmethod
    def get_youtube_url(track: dict, dont_filter: bool = False) -> Optional[str]:
        """
        Get the YouTube URL for a song using spotdl url command.
        
        Args:
            track: Track dictionary with 'url' key
            dont_filter: Whether to disable result filtering
            
        Returns:
            YouTube URL or None if not found
        """
        try:
            spotdl_path = SpotdlDownloader.find_spotdl()
            cmd = [spotdl_path, 'url', track['url']]
            if dont_filter:
                cmd.append('--dont-filter-results')
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            youtube_url = result.stdout.strip()
            return youtube_url if youtube_url else None
        except Exception as e:
            print(f"Failed to get YouTube URL for {track['name']}: {e}")
            return None

    @staticmethod
    def download_from_youtube(youtube_url: str, download_folder: str, track: Optional[Dict] = None) -> bool:
        """
        Download audio from YouTube URL using yt-dlp and apply Spotify metadata via ffmpeg.
        
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
                '-x',  # Extract audio only
                '--audio-format', 'mp3',
                '--audio-quality', '192',
                '-o', temp_file,
                youtube_url
            ]
            
            result = subprocess.run(yt_dlp_cmd, capture_output=True, text=True)
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
                    final_filename = f"{artist} - {safe_title}.mp3"
                    final_filepath = os.path.join(download_folder, final_filename)
                    
                    # Rename file first
                    os.rename(downloaded_file, final_filepath)
                    
                    # Apply metadata using EasyID3
                    try:
                        audio = EasyID3(final_filepath)
                    except Exception:
                        # If no ID3 tag exists, create one
                        audio = EasyID3()
                    
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
                            from mutagen.id3 import ID3
                            from mutagen.id3._frames import APIC
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
                                desc='',
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
    def download_from_spotify(track: dict, download_folder: str, dont_filter: bool = False) -> bool:
        """
        Download a song from Spotify URL using spotdl.
        
        Args:
            track: Track dictionary with 'url' key
            download_folder: Folder to save the download
            dont_filter: Whether to disable result filtering
            
        Returns:
            True if successful, False otherwise
        """
        try:
            spotdl_path = SpotdlDownloader.find_spotdl()
            cmd = [spotdl_path, track['url'], '--output', download_folder]
            if dont_filter:
                cmd.append('--dont-filter-results')
            
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            print(f"Failed to download {track['name']}: {e}")
            return False
