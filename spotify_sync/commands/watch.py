#!/usr/bin/env python3
"""
Continuous background watcher for Spotify playlists.
Periodically checks playlists for new songs and downloads them.

Usage:
    python watch.py --download-folder "/path/to/folder" --interval 10
    python watch.py  # Uses defaults: downloaded_songs folder, 10-minute intervals
"""

import os
import time
import argparse
from datetime import datetime
from spotify_sync.core.spotify_api import SpotifyClient
from spotify_sync.core.file_manager import FileManager
from spotify_sync.core.downloader import SpotdlDownloader
from spotify_sync.core.csv_manager import CSVManager
from spotify_sync.utils.utils import PlaylistReader
from spotify_sync.core.logger import Logger
from spotify_sync.utils.error_handler import ErrorHandler, SpotifyError
from spotify_sync.core.settings_manager import settings, Config


def process_playlist_watch(
    spotify_client: SpotifyClient,
    playlist_id: str,
    download_folder: str
) -> int:
    """
    Check a playlist for new songs and download them.
    
    Args:
        spotify_client: SpotifyClient instance
        playlist_id: Spotify playlist ID or URL
        download_folder: Base folder for downloads
        
    Returns:
        Number of new songs downloaded
    """
    try:
        Logger.info(f"Checking: {playlist_id}")
        
        # Fetch playlist info and tracks
        tracks = spotify_client.get_playlist_tracks(playlist_id)
        playlist_info = spotify_client.get_playlist_info(playlist_id)
        playlist_name = playlist_info.get('name') if playlist_info else None
        
        # Setup playlist folder
        playlist_folder_name = FileManager.get_playlist_folder_name(playlist_id, playlist_name)
        playlist_download_folder = os.path.join(download_folder, playlist_folder_name)
        FileManager.create_folder(playlist_download_folder)
        
        # Get current downloads
        downloaded = FileManager.get_downloaded_songs(playlist_download_folder)
        
        # Find missing songs
        missing_tracks = []
        for track in tracks:
            if not FileManager.is_song_downloaded(track, downloaded):
                missing_tracks.append(track)
        
        # Download new songs
        if missing_tracks:
            Logger.success(f"Found {len(missing_tracks)} new songs")
            
            for idx, track in enumerate(missing_tracks, 1):
                Logger.progress(idx, len(missing_tracks), "downloading")
                artist_str = ', '.join(track['artists']) if track['artists'] else 'Unknown'
                Logger.info(f"Downloading: {track['name']} - {artist_str}")
                
                if not SpotdlDownloader.download_from_spotify(track, playlist_download_folder):
                    track['unable_to_find'] = True
                    Logger.warning(f"Could not find: {track['name']}")
        else:
            Logger.info("No new songs")
        
        # Refresh downloads
        downloaded = FileManager.get_downloaded_songs(playlist_download_folder)
        
        # Update CSV
        CSVManager.write_playlist_songs(
            playlist_id,
            tracks,
            downloaded,
            FileManager.is_song_downloaded,
            playlist_name,
            playlist_download_folder
        )
        
        return len(missing_tracks)
    
    except SpotifyError as e:
        ErrorHandler.handle_exception(e, f"Spotify API error for playlist {playlist_id}")
        return 0
    except Exception as e:
        ErrorHandler.handle_exception(e, f"Error processing playlist {playlist_id}")
        return 0


def main_loop(playlists: list, download_folder: str, check_interval: int) -> None:
    """
    Continuously check playlists for new songs.
    
    Args:
        playlists: List of playlist IDs/URLs
        download_folder: Base folder for downloads
        check_interval: Check interval in minutes
    """
    try:
        spotify_client = SpotifyClient()
        Logger.success(f"Connected to Spotify")
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Failed to connect to Spotify")
        return
    
    Logger.header(f"Starting Playlist Watcher")
    Logger.info(f"Checking every {check_interval} minute(s)")
    Logger.info(f"Monitoring {len(playlists)} playlists")
    Logger.info("Press Ctrl+C to stop\n")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Logger.section(f"Check #{iteration} - {timestamp}")
            
            total_new = 0
            successful_checks = 0
            
            for idx, playlist_id in enumerate(playlists, 1):
                Logger.progress(idx, len(playlists), "checking playlists")
                new_songs = process_playlist_watch(spotify_client, playlist_id, download_folder)
                total_new += new_songs
                successful_checks += 1
            
            # Summary for this iteration
            Logger.success(f"Check complete: Found {total_new} new songs")
            Logger.info(f"Next check in {check_interval} minute(s) at {datetime.now().strftime('%H:%M:%S')}")
            
            time.sleep(check_interval * 60)
    
    except KeyboardInterrupt:
        Logger.warning("\nWatcher stopped by user")
        Logger.info(f"Total checks performed: {iteration}")


def main():
    """Main entry point for playlist watcher."""
    parser = argparse.ArgumentParser(description="Continuous Spotify Playlist Watcher")
    parser.add_argument("--download-folder", default=Config.get_downloads_folder(), help="Folder to download songs to")
    parser.add_argument("--interval", type=int, default=Config.DEFAULT_CHECK_INTERVAL_MINUTES, help="Check interval in minutes")
    
    args = parser.parse_args()
    
    # Validate interval
    if args.interval < Config.MIN_CHECK_INTERVAL_MINUTES or args.interval > Config.MAX_CHECK_INTERVAL_MINUTES:
        Logger.error(f"Invalid interval: {args.interval} (must be {Config.MIN_CHECK_INTERVAL_MINUTES}-{Config.MAX_CHECK_INTERVAL_MINUTES})")
        return
    
    # Validate folder
    try:
        ErrorHandler.validate_folder(args.download_folder)
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Invalid download folder")
        return
    
    # Read playlists
    try:
        Logger.info(f"Reading playlists from {Config.get_playlists_file()}...")
        playlists = PlaylistReader.read_playlists(Config.get_playlists_file())
        Logger.success(f"Found {len(playlists)} playlists")
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Failed to read playlists file")
        return
    
    if not playlists:
        Logger.warning("No playlists to watch")
        return
    
    # Start watcher
    main_loop(playlists, args.download_folder, args.interval)


if __name__ == "__main__":
    main()
