"""
Utilities for reading playlist files, user interactions, and filename handling.
"""

from typing import List


class PlaylistReader:
    """Reads playlist IDs from text files."""

    @staticmethod
    def read_playlists(filename: str) -> List[str]:
        """
        Read playlist IDs/URLs from a text file.
        Ignores empty lines and comments (lines starting with #).
        
        Args:
            filename: Path to playlists text file
            
        Returns:
            List of playlist IDs/URLs
        """
        playlists = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    playlists.append(line)
        return playlists


class FilenameSanitizer:
    """Handles filename sanitization for compatibility across systems."""
    
    # Characters that are invalid in filenames on most filesystems
    INVALID_CHARS = {
        ':': '-',
        '/': '-',
        '\\': '-',
        '|': '-',
        '?': '',
        '*': '',
        '"': '',
        '<': '',
        '>': ''
    }
    
    @staticmethod
    def sanitize(filename: str) -> str:
        """
        Remove or replace invalid filename characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename safe for all filesystems
        """
        for invalid_char, replacement in FilenameSanitizer.INVALID_CHARS.items():
            filename = filename.replace(invalid_char, replacement)
        return filename


class UserInput:
    """Handles user input and confirmations."""

    @staticmethod
    def confirm_download(song_name: str) -> bool:
        """
        Ask user to confirm download of a song.
        
        Args:
            song_name: Name of the song
            
        Returns:
            True if user confirms, False otherwise
        """
        while True:
            user_input = input(f"    Download {song_name}? (y/n): ").strip().lower()
            if user_input in ['y', 'yes']:
                return True
            elif user_input in ['n', 'no']:
                return False
            else:
                print("    Please enter 'y' or 'n'")

    @staticmethod
    def get_youtube_url() -> str:
        """
        Prompt user to provide a YouTube URL.
        
        Returns:
            YouTube URL entered by user, or empty string to skip
        """
        return input("    Paste YouTube URL (or press Enter to skip): ").strip()
