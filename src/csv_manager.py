"""
CSV operations for reading and writing playlist song metadata.
Stores download status (downloaded, missing, unable to be found).
"""

import os
import csv
from typing import Dict, List, Optional


class CSVManager:
    """Manages CSV file operations for playlists."""

    @staticmethod
    def get_csv_filepath(
        playlist_id: str,
        playlist_name: Optional[str] = None,
        output_folder: Optional[str] = None
    ) -> str:
        """
        Get the CSV filepath for a playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            playlist_name: Playlist name (preferred for filename)
            output_folder: Folder to store CSV files (if None, uses download folder)
            
        Returns:
            Path to CSV file
        """
        # Default to current directory if no output folder specified
        if output_folder is None:
            output_folder = "."
            
        if playlist_name:
            safe_name = "".join(c for c in playlist_name if c.isalnum() or c in (" ", "-", "_"))
            filename = os.path.join(output_folder, f"{safe_name.strip()}.csv")
        else:
            if "playlist/" in playlist_id:
                playlist_id = playlist_id.split("playlist/")[-1].split("?")[0]
            filename = os.path.join(output_folder, f"{playlist_id}.csv")
        
        return filename

    @staticmethod
    def read_csv_status(csv_filepath: str) -> Dict[str, str]:
        """
        Read the status of songs from an existing CSV file.
        
        Args:
            csv_filepath: Path to CSV file
            
        Returns:
            Dictionary mapping "Artist - Song Title" to status
        """
        status_map = {}
        
        if not os.path.exists(csv_filepath):
            return status_map
        
        try:
            with open(csv_filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Song Title') and row.get('Status'):
                        artist = row.get('Artist', 'Unknown')
                        song_title = row.get('Song Title')
                        song_key = f"{artist} - {song_title}".lower()
                        status_map[song_key] = row['Status']
        except Exception as e:
            print(f"Warning: Could not read CSV file {csv_filepath}: {e}")
        
        return status_map

    @staticmethod
    def write_playlist_songs(
        playlist_id: str,
        tracks: List[Dict],
        downloaded_set: set,
        is_song_downloaded_func,
        playlist_name: Optional[str] = None,
        output_folder: Optional[str] = None
    ) -> None:
        """
        Write playlist songs to a CSV file with their download status.
        
        Args:
            playlist_id: Spotify playlist ID
            tracks: List of track dictionaries
            downloaded_set: Set of downloaded song filenames
            is_song_downloaded_func: Function to check if song is downloaded
            playlist_name: Playlist name (for filename)
            output_folder: Folder to save CSV (if None, saves to current directory)
        """
        if output_folder is None:
            output_folder = "."
            
        os.makedirs(output_folder, exist_ok=True)
        filepath = CSVManager.get_csv_filepath(playlist_id, playlist_name, output_folder)
        
        with open(filepath, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Artist", "Song Title", "Status"])
            
            for track in tracks:
                artist = track['artists'][0] if track['artists'] else 'Unknown'
                
                # Determine status
                if is_song_downloaded_func(track, downloaded_set):
                    status = "downloaded"
                elif track.get('unable_to_find'):
                    status = "unable to be found"
                else:
                    status = "missing"
                
                writer.writerow([artist, track['name'], status])
        
        print(f"Wrote song list to {filepath}")

    @staticmethod
    def update_csv_file(csv_filepath: str, downloaded_set: set) -> int:
        """
        Update a CSV file with current download status.
        
        Args:
            csv_filepath: Path to CSV file
            downloaded_set: Set of downloaded song filenames
            
        Returns:
            Number of songs updated
        """
        if not os.path.exists(csv_filepath):
            print(f"CSV file not found: {csv_filepath}")
            return 0
        
        # Read the CSV file
        rows = []
        try:
            with open(csv_filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return 0
        
        # Update statuses
        updated_count = 0
        for row in rows:
            song_title = row.get('Song Title', '')
            artist = row.get('Artist', '')
            current_status = row.get('Status', 'missing')
            
            # Simple matching: check if song title is in any downloaded file
            is_downloaded = False
            for downloaded_file in downloaded_set:
                if song_title.lower() in downloaded_file:
                    is_downloaded = True
                    break
            
            if is_downloaded and current_status != 'downloaded':
                row['Status'] = 'downloaded'
                updated_count += 1
                print(f"  Updated to downloaded: {artist} - {song_title}")
        
        # Write back to CSV
        try:
            with open(csv_filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Artist', 'Song Title', 'Status'])
                writer.writeheader()
                writer.writerows(rows)
            print(f"Updated {updated_count} songs in {os.path.basename(csv_filepath)}")
            return updated_count
        except Exception as e:
            print(f"Error writing CSV: {e}")
            return 0
