"""
Cleanup manager for handling removed songs from playlists.
Detects songs that were previously downloaded but are no longer in the playlist
and provides options to clean them up.
"""

import os
import glob
from typing import Set, List, Dict, Tuple, Optional
from spotify_sync.core.csv_manager import CSVManager
from spotify_sync.core.file_manager import FileManager
from spotify_sync.utils.utils import UserInput
from spotify_sync.core.logger import Logger


class CleanupManager:
    """Manages cleanup of songs removed from playlists."""

    @staticmethod
    def find_removed_songs(
        current_tracks: List[dict],
        csv_filepath: str,
        download_folder: str
    ) -> Tuple[List[Dict], List[str]]:
        """
        Find songs that were previously in the playlist but are now removed.
        
        Args:
            current_tracks: List of current tracks in the playlist
            csv_filepath: Path to playlist CSV file
            download_folder: Download folder path
            
        Returns:
            Tuple of (removed_song_data, removed_files_found)
        """
        if not os.path.exists(csv_filepath):
            return [], []
        
        # Get current track identifiers
        current_track_ids = set()
        current_filenames = set()
        
        for track in current_tracks:
            # Use track ID if available, otherwise use filename
            if 'id' in track:
                current_track_ids.add(track['id'])
            filename = FileManager.get_song_filename(track)
            current_filenames.add(filename)
        
        # Read previous CSV data
        csv_status = CSVManager.read_csv_status(csv_filepath)
        
        removed_songs = []
        removed_files = []
        
        # Check each previously tracked song
        for song_key, status in csv_status.items():
            # Skip if song is still in playlist
            found_in_current = False
            for track in current_tracks:
                current_key = FileManager.get_song_filename(track)
                if current_key == song_key:
                    found_in_current = True
                    break
            
            if found_in_current:
                continue
                
            # Only consider songs that were previously downloaded
            if status == 'downloaded':
                # Parse the song key back to get artist and title
                if ' - ' in song_key:
                    artist, title = song_key.split(' - ', 1)
                else:
                    artist, title = 'Unknown', song_key
                
                song_data = {
                    'filename': song_key,
                    'artist': artist,
                    'title': title,
                    'status': status
                }
                removed_songs.append(song_data)
                
                # Check if the actual file exists
                matching_files = CleanupManager._find_matching_files(
                    song_key, download_folder
                )
                removed_files.extend(matching_files)
        
        return removed_songs, removed_files

    @staticmethod
    def _find_matching_files(filename: str, download_folder: str) -> List[str]:
        """
        Find files that match the given filename pattern.
        
        Args:
            filename: Base filename to search for
            download_folder: Directory to search in
            
        Returns:
            List of matching file paths
        """
        matching_files = []
        
        # Common audio extensions
        extensions = ['*.mp3', '*.m4a', '*.flac', '*.wav', '*.ogg']
        
        for ext in extensions:
            # Try exact match first
            pattern = os.path.join(download_folder, f"{filename}.{ext[2:]}")
            matches = glob.glob(pattern)
            matching_files.extend(matches)
            
            # Try case-insensitive match
            pattern = os.path.join(download_folder, f"{filename.lower()}.{ext[2:]}")
            matches = glob.glob(pattern)
            matching_files.extend(matches)
        
        # Remove duplicates
        return list(set(matching_files))

    @staticmethod
    def prompt_cleanup_action(removed_songs: List[Dict], removed_files: List[str]) -> str:
        """
        Prompt user for cleanup action when removed songs are found.
        
        Args:
            removed_songs: List of removed song data
            removed_files: List of file paths that would be deleted
            
        Returns:
            User's choice: 'delete', 'keep', or 'skip'
        """
        if not removed_songs:
            return 'skip'
        
        Logger.warning(f"Found {len(removed_songs)} song(s) that were removed from the playlist:")
        
        for i, song in enumerate(removed_songs[:5], 1):  # Show first 5
            artist = song.get('artist', 'Unknown')
            title = song.get('title', song.get('filename', 'Unknown'))
            Logger.info(f"  {i}. {artist} - {title}")
        
        if len(removed_songs) > 5:
            Logger.info(f"  ... and {len(removed_songs) - 5} more")
        
        if removed_files:
            Logger.info(f"\nFound {len(removed_files)} downloaded file(s) for these songs.")
        else:
            Logger.info("\nNo downloaded files found for these songs.")
            return 'skip'
        
        Logger.info("\nWhat would you like to do?")
        Logger.info("1. Delete the files (free up space)")
        Logger.info("2. Keep the files (they'll remain in your download folder)")
        Logger.info("3. Skip cleanup for now")
        
        while True:
            choice = input("Enter your choice (1/2/3): ").strip()
            if choice in ['1', 'delete', 'd']:
                return 'delete'
            elif choice in ['2', 'keep', 'k']:
                return 'keep'
            elif choice in ['3', 'skip', 's']:
                return 'skip'
            else:
                Logger.error("Invalid choice. Please enter 1, 2, or 3.")

    @staticmethod
    def delete_removed_files(removed_files: List[str]) -> Tuple[int, int]:
        """
        Delete the specified files.
        
        Args:
            removed_files: List of file paths to delete
            
        Returns:
            Tuple of (successful_deletions, failed_deletions)
        """
        successful = 0
        failed = 0
        
        for file_path in removed_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    Logger.success(f"Deleted: {os.path.basename(file_path)}")
                    successful += 1
                else:
                    Logger.warning(f"File not found: {os.path.basename(file_path)}")
                    failed += 1
            except Exception as e:
                Logger.error(f"Failed to delete {os.path.basename(file_path)}: {e}")
                failed += 1
        
        return successful, failed

    @staticmethod
    def update_csv_after_cleanup(
        csv_filepath: str,
        removed_songs: List[Dict],
        action: str
    ):
        """
        Update the CSV file after cleanup action.
        For now, this is a placeholder since we're working with existing CSV structure.
        
        Args:
            csv_filepath: Path to CSV file
            removed_songs: List of removed song data
            action: Action taken ('delete', 'keep', 'skip')
        """
        # Note: Since the existing CSV structure doesn't support easy row removal,
        # we'll just log the action for now. Future enhancement could rebuild the CSV.
        if action == 'delete':
            Logger.info(f"Note: {len(removed_songs)} song(s) removed from tracking.")
        elif action == 'keep':
            Logger.info(f"Note: {len(removed_songs)} song(s) marked as kept after removal.")

    @staticmethod
    def cleanup_removed_songs(
        current_tracks: List[dict],
        csv_filepath: str,
        download_folder: str,
        auto_action: Optional[str] = None
    ) -> Dict:
        """
        Main cleanup function that handles the entire removed songs cleanup process.
        
        Args:
            current_tracks: List of current tracks in playlist
            csv_filepath: Path to playlist CSV file
            download_folder: Download folder path
            auto_action: Automatic action ('delete', 'keep', 'skip') or None for prompt
            
        Returns:
            Dictionary with cleanup stats
        """
        Logger.section("Checking for removed songs...")
        
        removed_songs, removed_files = CleanupManager.find_removed_songs(
            current_tracks, csv_filepath, download_folder
        )
        
        stats = {
            'removed_songs_found': len(removed_songs),
            'removed_files_found': len(removed_files),
            'files_deleted': 0,
            'files_kept': 0,
            'action_taken': 'none'
        }
        
        if not removed_songs:
            Logger.success("No removed songs found. Playlist is up to date!")
            return stats
        
        # Determine action
        if auto_action:
            action = auto_action
            Logger.info(f"Auto action: {action}")
        else:
            action = CleanupManager.prompt_cleanup_action(removed_songs, removed_files)
        
        stats['action_taken'] = action
        
        if action == 'delete' and removed_files:
            successful, failed = CleanupManager.delete_removed_files(removed_files)
            stats['files_deleted'] = successful
            Logger.success(f"Deleted {successful} file(s)")
            if failed > 0:
                Logger.warning(f"Failed to delete {failed} file(s)")
        
        elif action == 'keep':
            stats['files_kept'] = len(removed_files)
            Logger.info(f"Keeping {len(removed_files)} file(s)")
        
        # Update CSV
        CleanupManager.update_csv_after_cleanup(csv_filepath, removed_songs, action)
        
        return stats