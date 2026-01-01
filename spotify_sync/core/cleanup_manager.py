"""
Cleanup manager for handling removed songs from playlists.
Detects songs that were previously downloaded but are no longer in the playlist,
and orphaned files that exist but were never tracked in the CSV.
"""

import os
import csv
import glob
from typing import Set, List, Dict, Tuple, Optional
from spotify_sync.core.csv_manager import CSVManager
from spotify_sync.core.file_manager import FileManager
from spotify_sync.utils.utils import UserInput, FilenameSanitizer
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

    @staticmethod
    def _normalize_title(title: str) -> str:
        """
        Normalize song titles for better matching.
        
        Args:
            title: Song title to normalize
            
        Returns:
            Normalized title
        """
        normalized = title.replace('/', '-')
        normalized = normalized.replace('\\', '-')
        normalized = normalized.replace(':', '-')
        normalized = normalized.replace('|', '-')
        normalized = normalized.replace('?', '')
        normalized = normalized.replace('*', '')
        normalized = normalized.replace('"', '')
        normalized = normalized.replace('<', '')
        normalized = normalized.replace('>', '')
        normalized = normalized.replace(' / ', ' ')
        normalized = ' '.join(normalized.split())
        return normalized

    @staticmethod
    def find_orphaned_files(
        csv_filepath: str,
        download_folder: str,
        current_tracks: Optional[List[dict]] = None
    ) -> List[str]:
        """
        Find files in the folder that are NOT tracked in the CSV or current playlist.
        These are orphaned files that may have been manually added or left from failed operations.
        
        Args:
            csv_filepath: Path to CSV file
            download_folder: Download folder to scan
            current_tracks: Optional list of current tracks in the playlist
            
        Returns:
            List of orphaned file paths
        """
        if not os.path.exists(download_folder):
            return []
        
        # Get all tracked song titles from CSV AND current tracks
        tracked_titles = set()
        
        # Add titles from CSV if it exists
        if os.path.exists(csv_filepath):
            try:
                with open(csv_filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        title = row.get('Song Title', '')
                        
                        if title:
                            # Sanitize and store the title
                            safe_title = FilenameSanitizer.sanitize(title)
                            tracked_titles.add(safe_title.lower())
            except Exception as e:
                Logger.warning(f"Error reading CSV for orphaned file check: {e}")
        
        # Add titles from current tracks (including newly downloaded ones)
        if current_tracks:
            for track in current_tracks:
                title = track.get('name', '')
                if title:
                    safe_title = FilenameSanitizer.sanitize(title)
                    tracked_titles.add(safe_title.lower())
        
        # Get all audio files in folder
        audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']
        folder_files = []
        
        for file in os.listdir(download_folder):
            file_path = os.path.join(download_folder, file)
            if os.path.isfile(file_path):
                name, ext = os.path.splitext(file)
                if ext.lower() in audio_extensions:
                    folder_files.append((name, file_path))
        
        # Find orphaned files (files not in CSV or current tracks)
        orphaned_files = []
        
        for filename, file_path in folder_files:
            # Extract the title from the filename (everything after " - ")
            if " - " in filename:
                file_title = filename.split(" - ", 1)[1].lower()
            else:
                file_title = filename.lower()
            
            # Check if this song title is tracked
            found_match = False
            for tracked_title in tracked_titles:
                if tracked_title in file_title or file_title in tracked_title:
                    found_match = True
                    break
            
            if not found_match:
                orphaned_files.append(file_path)
        
        return orphaned_files

    @staticmethod
    def cleanup_orphaned_files(
        csv_filepath: str,
        download_folder: str,
        auto_delete: bool = True,
        current_tracks: Optional[List[dict]] = None
    ) -> Dict:
        """
        Clean up orphaned files (files not tracked in CSV or current playlist).
        
        Args:
            csv_filepath: Path to CSV file
            download_folder: Download folder to scan
            auto_delete: If True, automatically delete orphaned files
            current_tracks: Optional list of current tracks in the playlist
            
        Returns:
            Dictionary with cleanup stats
        """
        orphaned_files = CleanupManager.find_orphaned_files(csv_filepath, download_folder, current_tracks)
        
        stats = {
            'orphaned_files_found': len(orphaned_files),
            'orphaned_files_deleted': 0
        }
        
        if not orphaned_files:
            return stats
        
        Logger.info(f"Found {len(orphaned_files)} orphaned file(s) not tracked in CSV")
        
        if auto_delete:
            successful = 0
            failed = 0
            
            for file_path in orphaned_files:
                try:
                    os.remove(file_path)
                    Logger.success(f"Deleted orphaned: {os.path.basename(file_path)}")
                    successful += 1
                except Exception as e:
                    Logger.error(f"Failed to delete {os.path.basename(file_path)}: {e}")
                    failed += 1
            
            stats['orphaned_files_deleted'] = successful
            
            if successful > 0:
                Logger.success(f"Cleaned up {successful} orphaned file(s)")
        
        return stats
