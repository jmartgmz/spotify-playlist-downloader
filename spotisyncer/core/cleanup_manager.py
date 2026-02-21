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
import re
from mutagen.easyid3 import EasyID3
from mutagen import File as MutagenFile


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
        Uses metadata comparison to handle filename sanitization issues.
        
        Args:
            current_tracks: List of current tracks in the playlist
            csv_filepath: Path to playlist CSV file
            download_folder: Download folder path
            
        Returns:
            Tuple of (removed_song_data, removed_files_found)
        """
        if not os.path.exists(csv_filepath):
            return [], []
        
        # Build set of current tracks using (artist, title) tuples
        current_songs = set()
        for track in current_tracks:
            artist = track['artists'][0].lower().strip() if track.get('artists') else ''
            title = track.get('name', '').lower().strip()
            if title:
                current_songs.add((artist, title))
        
        # Read previous CSV data
        csv_songs = []
        try:
            with open(csv_filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    artist = row.get('Artist', '').lower().strip()
                    title = row.get('Song Title', '').lower().strip()
                    status = row.get('Status', '')
                    if title and status == 'downloaded':
                        csv_songs.append({
                            'artist': artist,
                            'title': title,
                            'artist_original': row.get('Artist', ''),
                            'title_original': row.get('Song Title', '')
                        })
        except Exception as e:
            Logger.warning(f"Error reading CSV for removed songs check: {e}")
            return [], []
        
        removed_songs = []
        removed_files = []
        
        # Check each CSV song against current playlist
        for csv_song in csv_songs:
            artist = csv_song['artist']
            title = csv_song['title']
            
            # Check if this song is still in the current playlist
            if (artist, title) not in current_songs:
                # Song was removed from playlist, find the actual file
                song_data = {
                    'artist': csv_song['artist_original'],
                    'title': csv_song['title_original'],
                    'status': 'downloaded'
                }
                removed_songs.append(song_data)
                
                # Find matching files by metadata
                audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']
                for file in os.listdir(download_folder):
                    file_path = os.path.join(download_folder, file)
                    if not os.path.isfile(file_path):
                        continue
                    
                    name, ext = os.path.splitext(file)
                    if ext.lower() not in audio_extensions:
                        continue
                    
                    # Check metadata
                    metadata = CleanupManager._get_file_metadata(file_path)
                    if metadata and metadata['title'] == title:
                        # Match on title (artist might vary slightly)
                        removed_files.append(file_path)
                        break
        
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
    def _get_file_metadata(file_path: str) -> Optional[Dict[str, str]]:
        """
        Extract metadata (artist, title) from an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with 'artist' and 'title' keys, or None if unable to read
        """
        try:
            audio = MutagenFile(file_path, easy=True)
            if audio is None:
                return None
            
            # Get title and artist from tags
            title = audio.get('title', [None])[0] if 'title' in audio else None
            artist = audio.get('artist', [None])[0] if 'artist' in audio else None
            
            if title:
                return {
                    'title': title.lower().strip(),
                    'artist': artist.lower().strip() if artist else ''
                }
            return None
        except Exception as e:
            # If we can't read metadata, return None
            return None

    @staticmethod
    def find_orphaned_files(
        csv_filepath: str,
        download_folder: str,
        current_tracks: Optional[List[dict]] = None
    ) -> List[str]:
        """
        Find files in the folder that are NOT tracked in the CSV or current playlist.
        Uses metadata (ID3 tags) comparison instead of filename comparison for reliability.
        
        Args:
            csv_filepath: Path to CSV file
            download_folder: Download folder to scan
            current_tracks: Optional list of current tracks in the playlist
            
        Returns:
            List of orphaned file paths
        """
        if not os.path.exists(download_folder):
            return []
        
        # Build a set of tracked songs using (artist, title) tuples from CSV and current tracks
        tracked_songs = set()
        
        # Add songs from CSV if it exists
        if os.path.exists(csv_filepath):
            try:
                with open(csv_filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        artist = row.get('Artist', '').lower().strip()
                        title = row.get('Song Title', '').lower().strip()
                        if title:
                            tracked_songs.add((artist, title))
                            # Also add just the title for partial matching
                            tracked_songs.add(('', title))
            except Exception as e:
                Logger.warning(f"Error reading CSV for orphaned file check: {e}")
        
        # Add songs from current tracks (including newly downloaded ones)
        if current_tracks:
            for track in current_tracks:
                artist = track['artists'][0].lower().strip() if track.get('artists') else ''
                title = track.get('name', '').lower().strip()
                if title:
                    tracked_songs.add((artist, title))
                    # Also add just the title for partial matching
                    tracked_songs.add(('', title))
        
        # Get all audio files in folder
        audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']
        orphaned_files = []
        
        for file in os.listdir(download_folder):
            file_path = os.path.join(download_folder, file)
            if not os.path.isfile(file_path):
                continue
            
            name, ext = os.path.splitext(file)
            if ext.lower() not in audio_extensions:
                continue
            
            # Read metadata from the file
            metadata = CleanupManager._get_file_metadata(file_path)
            
            if metadata is None:
                # If we can't read metadata, fall back to filename matching as last resort
                file_title = name.split(" - ", 1)[1].lower().strip() if " - " in name else name.lower().strip()
                
                def simplify(text: str) -> str:
                    return re.sub(r'[\W_]+', '', str(text).lower()) if text else ""
                
                simp_file_title = simplify(file_title)
                simp_tracked_songs = {(simplify(a), simplify(t)) for a, t in tracked_songs}
                
                # Check if any tracked song title matches
                is_tracked = any(simp_file_title == tracked_title or tracked_title in simp_file_title 
                               for _, tracked_title in simp_tracked_songs if tracked_title)
                if not is_tracked:
                    orphaned_files.append(file_path)
                continue
            
            # Check if this file's metadata matches any tracked song
            file_artist = metadata['artist']
            file_title = metadata['title']
            
            # Use regex to strip away punctuation for reliable comparisons
            def simplify(text: str) -> str:
                return re.sub(r'[\W_]+', '', str(text).lower()) if text else ""
            
            simp_file_title = simplify(file_title)
            simp_file_artist = simplify(file_artist)
            
            # Reconstruct the tracked list using simplified strings dynamically
            simp_tracked_songs = {(simplify(a), simplify(t)) for a, t in tracked_songs}
            
            # Try exact match with artist + title (both simplified)
            is_tracked = (simp_file_artist, simp_file_title) in simp_tracked_songs
            
            # Also try title-only match (in case artist format differs)
            if not is_tracked:
                is_tracked = ('', simp_file_title) in simp_tracked_songs
            
            # If still not matched, try partial title match
            if not is_tracked:
                is_tracked = any(tracked_title and (tracked_title in simp_file_title or simp_file_title in tracked_title)
                               for _, tracked_title in simp_tracked_songs if tracked_title)
            
            # If STILL not matched, the metadata might be localized/romanized differently than Spotify
            # Fall back to using the physical filename (which was built from Spotify data)
            if not is_tracked:
                filename_title = name.split(" - ", 1)[1].lower().strip() if " - " in name else name.lower().strip()
                simp_filename_title = simplify(filename_title)
                is_tracked = any(simp_filename_title == tracked_title or tracked_title in simp_filename_title
                               for _, tracked_title in simp_tracked_songs if tracked_title)

            if not is_tracked:
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
