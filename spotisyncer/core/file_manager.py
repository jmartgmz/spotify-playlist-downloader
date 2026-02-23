"""
File system operations for songs, playlists, and folders.
Handles downloading songs, managing folders, and file name normalization.
"""

import os
import glob
from typing import Set, Tuple, Optional, Dict
from spotisyncer.utils.utils import FilenameSanitizer
from mutagen import File as MutagenFile


class FileManager:
    """Manages file and folder operations."""

    @staticmethod
    def get_downloaded_songs(download_folder: str) -> Dict[str, dict]:
        """
        Get dictionary of downloaded songs with their metadata.
        
        Args:
            download_folder: Path to folder containing downloaded songs
            
        Returns:
            Dictionary mapping song title (lowercase) to metadata dict with 'title', 'artist', 'path'
        """
        downloaded = {}
        audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']
        
        for file in os.listdir(download_folder):
            file_path = os.path.join(download_folder, file)
            if not os.path.isfile(file_path):
                continue
            
            name, ext = os.path.splitext(file)
            if ext.lower() not in audio_extensions:
                continue
            
            # Try to read metadata
            try:
                audio = MutagenFile(file_path, easy=True)
                if audio and 'title' in audio:
                    title = audio.get('title', [None])[0]
                    artist = audio.get('artist', [None])[0] if 'artist' in audio else None
                    
                    if title:
                        # Store by lowercase title for matching
                        downloaded[title.lower().strip()] = {
                            'title': title,
                            'artist': artist if artist else '',
                            'path': file_path
                        }
                        continue
            except:
                pass
            
            # Fallback: use filename if metadata not available
            downloaded[name.lower()] = {
                'title': name,
                'artist': '',
                'path': file_path
            }
        
        return downloaded

    @staticmethod
    def get_song_filename(track: dict) -> str:
        """
        Return normalized filename for a track.
        Sanitizes special characters that are invalid in filenames.
        
        Args:
            track: Track dictionary with 'artists' and 'name' keys
            
        Returns:
            Normalized filename string "Artist - Song Name" (lowercase, sanitized)
        """
        artist = track['artists'][0] if track['artists'] else 'Unknown'
        name = track['name']
        
        # Sanitize the song name to match filenames that were actually created
        safe_name = FilenameSanitizer.sanitize(name)
        
        return f"{artist} - {safe_name}".lower()

    @staticmethod
    def is_song_downloaded(track: dict, downloaded_dict: Dict[str, dict]) -> bool:
        """
        Check if a song is downloaded by comparing metadata.
        
        Args:
            track: Track dictionary with 'name' and 'artists' keys
            downloaded_dict: Dictionary of downloaded songs from get_downloaded_songs()
            
        Returns:
            True if song is found in downloaded dict
        """
        track_title = track.get('name', '').lower().strip()
        
        if not track_title:
            return False
        
        # Direct title match (most reliable)
        if track_title in downloaded_dict:
            return True
        
        # Partial title match as fallback
        for downloaded_title in downloaded_dict.keys():
            if track_title in downloaded_title or downloaded_title in track_title:
                return True
        
        return False

    @staticmethod
    def get_playlist_folder_name(playlist_id: str, playlist_name: Optional[str] = None) -> str:
        """
        Get a safe folder name for a playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            playlist_name: Playlist name (if available)
            
        Returns:
            Safe folder name (alphanumeric, hyphens, underscores, spaces)
        """
        if playlist_name:
            safe_name = "".join(c for c in playlist_name if c.isalnum() or c in (" ", "-", "_"))
            return safe_name.strip()
        
        # Extract ID from URL if needed
        if "playlist/" in playlist_id:
            playlist_id = playlist_id.split("playlist/")[-1].split("?")[0]
        
        return playlist_id

    @staticmethod
    def create_folder(folder_path: str) -> None:
        """
        Create folder if it doesn't exist.
        
        Args:
            folder_path: Path to folder to create
        """
        os.makedirs(folder_path, exist_ok=True)

