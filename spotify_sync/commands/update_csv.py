#!/usr/bin/env python3
"""
Quick CSV updater that checks downloaded songs against the CSV file.
Much faster than running check.py as it doesn't query Spotify API.

Usage:
    python update_csv.py --download-folder "/path/to/folder"
    python update_csv.py  # Uses default downloaded_songs folder
"""

import os
import os
import argparse
import glob
from spotify_sync.core.spotify_api import SpotifyClient
from spotify_sync.core.file_manager import FileManager
from spotify_sync.core.csv_manager import CSVManager
from spotify_sync.utils.utils import PlaylistReader
from spotify_sync.core.logger import Logger
from spotify_sync.utils.error_handler import ErrorHandler
from spotify_sync.core.settings_manager import settings, Config


def find_csv_files(playlist_folder: str) -> list:
    """
    Find all CSV files in the playlist_songs folder.
    
    Args:
        playlist_folder: Path to folder containing CSV files
        
    Returns:
        List of CSV file paths
    """
    csv_files = []
    try:
        if os.path.exists(playlist_folder):
            for file in glob.glob(os.path.join(playlist_folder, '*.csv')):
                csv_files.append(file)
    except Exception as e:
        ErrorHandler.handle_exception(e, "Error scanning CSV folder")
    
    return csv_files


def main():
    """Main entry point for CSV updater."""
    parser = argparse.ArgumentParser(
        description="Quick CSV Updater - Updates CSV files based on downloaded songs"
    )
    parser.add_argument(
        '--download-folder',
        type=str,
        default=Config.get_downloads_folder(),
        help="Folder with downloaded songs"
    )
    parser.add_argument(
        '--playlist-folder',
        type=str,
        default=Config.get_playlist_folder(),
        help="Folder with CSV files"
    )
    args = parser.parse_args()
    
    download_folder = args.download_folder
    playlist_folder = args.playlist_folder
    
    Logger.header("CSV Updater")
    
    # Validate download folder
    try:
        ErrorHandler.validate_folder(download_folder)
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Invalid download folder")
        return
    
    # Find all CSV files
    Logger.info(f"Scanning for CSV files in {playlist_folder}...")
    csv_files = find_csv_files(playlist_folder)
    
    if not csv_files:
        Logger.warning(f"No CSV files found in {playlist_folder}")
        return
    
    Logger.success(f"Found {len(csv_files)} CSV file(s)")
    
    # Update each CSV file
    total_updated = 0
    failed_updates = 0
    
    for idx, csv_file in enumerate(csv_files, 1):
        try:
            Logger.progress(idx, len(csv_files), "updating CSV files")
            
            playlist_name = os.path.basename(csv_file).replace('.csv', '')
            playlist_download_folder = os.path.join(download_folder, playlist_name)
            
            if not os.path.exists(playlist_download_folder):
                Logger.warning(f"Skipped (folder not found): {playlist_name}")
                continue
            
            Logger.info(f"Updating: {playlist_name}")
            downloaded = FileManager.get_downloaded_songs(playlist_download_folder)
            updated_count = CSVManager.update_csv_file(csv_file, downloaded)
            
            if updated_count >= 0:
                Logger.success(f"Updated {playlist_name}")
                total_updated += 1
            else:
                Logger.error(f"Failed to update: {playlist_name}")
                failed_updates += 1
        
        except Exception as e:
            csv_name = os.path.basename(csv_file).replace('.csv', '')
            ErrorHandler.handle_exception(e, f"Error updating CSV for {csv_name}")
            failed_updates += 1
            continue
    
    # Print summary
    Logger.header("Update Summary")
    Logger.summary("Total CSV Files", str(len(csv_files)))
    Logger.summary("Successfully Updated", str(total_updated))
    Logger.summary("Failed", str(failed_updates))
    
    if failed_updates == 0:
        Logger.success("All CSV files updated!")
    else:
        Logger.warning(f"{failed_updates} file(s) failed to update")


if __name__ == "__main__":
    main()
