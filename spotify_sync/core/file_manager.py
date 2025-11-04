"""
File system operations for songs, playlists, and folders.
Handles downloading songs, managing folders, and file name normalization.
"""

import os
import glob
from typing import Set, Tuple, Optional
from spotify_sync.utils.utils import FilenameSanitizer


class FileManager:
    """Manages file and folder operations."""

    @staticmethod
    def get_downloaded_songs(download_folder: str) -> Set[str]:
        """
        Get set of downloaded songs (normalized filenames).
        
        Args:
            download_folder: Path to folder containing downloaded songs
            
        Returns:
            Set of normalized song filenames (lowercase, without extension)
        """
        downloaded = set()
        for file in glob.glob(os.path.join(download_folder, '*')):
            base = os.path.basename(file)
            name, _ = os.path.splitext(base)
            downloaded.add(name.lower())
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
    def is_song_downloaded(track: dict, downloaded_set: Set[str]) -> bool:
        """
        Check if a song is downloaded using fuzzy matching.
        Handles multiple artist formats and file name variations.
        
        Args:
            track: Track dictionary
            downloaded_set: Set of downloaded song filenames
            
        Returns:
            True if song is found in downloaded set
        """
        song_name = track['name']
        
        # Try exact match with first artist
        exact_match = FileManager.get_song_filename(track)
        if exact_match in downloaded_set:
            return True
        
        # Try with all artists combined
        all_artists = ", ".join([artist for artist in track['artists']])
        all_artists_match = f"{all_artists} - {song_name}".lower()
        if all_artists_match in downloaded_set:
            return True
        
        # Try matching just the song title
        for downloaded_file in downloaded_set:
            if song_name.lower() in downloaded_file:
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
