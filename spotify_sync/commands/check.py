#!/usr/bin/env python3
"""
One-time checker for Spotify playlists.
Fetches all songs from specified playlists, checks which are downloaded,
and downloads any missing songs using spotdl.

Usage:
    python check.py --download-folder "/path/to/folder"
    python check.py --manual-verify --dont-filter-results
    python check.py --manual-link
"""

import os
import argparse
import sys
from spotify_sync.core.spotify_api import SpotifyClient
from spotify_sync.core.file_manager import FileManager
from spotify_sync.core.downloader import SpotdlDownloader
from spotify_sync.core.csv_manager import CSVManager
from spotify_sync.core.cleanup_manager import CleanupManager
from spotify_sync.utils.utils import PlaylistReader, UserInput
from spotify_sync.core.logger import Logger
from spotify_sync.utils.error_handler import ErrorHandler, ValidationError, SpotifyError
from spotify_sync.core.settings_manager import settings, Config


def process_playlist(
    spotify_client: SpotifyClient,
    playlist_id: str,
    download_folder: str,
    manual_verify: bool = False,
    manual_link: bool = False,
    dont_filter: bool = False,
    cleanup_removed: bool = False,
    auto_delete_removed: bool = False,
    keep_removed: bool = False
) -> dict:
    """
    Process a single playlist: fetch tracks, check downloads, download missing songs.
    
    Args:
        spotify_client: SpotifyClient instance
        playlist_id: Spotify playlist ID or URL
        download_folder: Base folder for downloads
        manual_verify: Show YouTube URL and ask for confirmation
        manual_link: Manually provide YouTube links
        dont_filter: Disable spotdl result filtering
        cleanup_removed: Check for and handle removed songs
        auto_delete_removed: Automatically delete files for removed songs
        keep_removed: Keep files for removed songs without prompting
        
    Returns:
        Dictionary with stats (total_tracks, missing, downloaded, skipped, failed)
    """
    Logger.section(f"Processing: {playlist_id}")
    
    stats = {
        'total_tracks': 0,
        'missing': 0,
        'downloaded': 0,
        'skipped': 0,
        'failed': 0
    }
    
    try:
        # Fetch playlist info and tracks
        tracks = spotify_client.get_playlist_tracks(playlist_id)
        stats['total_tracks'] = len(tracks)
        Logger.info(f"Found {len(tracks)} songs in playlist")
        
        playlist_info = spotify_client.get_playlist_info(playlist_id)
        playlist_name = playlist_info.get('name') if playlist_info else None
        
        if playlist_name:
            Logger.info(f"Playlist: {playlist_name}")
        
        # Setup playlist folder
        playlist_folder_name = FileManager.get_playlist_folder_name(playlist_id, playlist_name)
        playlist_download_folder = os.path.join(download_folder, playlist_folder_name)
        FileManager.create_folder(playlist_download_folder)
        
        # Get current downloads and CSV status
        downloaded = FileManager.get_downloaded_songs(playlist_download_folder)
        csv_filepath = CSVManager.get_csv_filepath(playlist_id, playlist_name)
        csv_status_map = CSVManager.read_csv_status(csv_filepath)
        
        # Find missing songs
        missing_tracks = []
        for track in tracks:
            song_key = f"{track['artists'][0] if track['artists'] else 'Unknown'} - {track['name']}".lower()
            
            # Skip if already downloaded
            if FileManager.is_song_downloaded(track, downloaded):
                continue
            
            # Skip if previously marked as unable to find
            if csv_status_map.get(song_key) == Config.CSV_STATUS_UNABLE_TO_FIND:
                Logger.warning(f"Skipped (previously unable to find): {track['name']}")
                track['unable_to_find'] = True
                stats['skipped'] += 1
                continue
            
            missing_tracks.append(track)
        
        stats['missing'] = len(missing_tracks)
        
        if not missing_tracks:
            Logger.success("All songs already downloaded!")
            return stats
        
        Logger.start_progress("downloading songs")
        
        # Download missing songs
        for idx, track in enumerate(missing_tracks, 1):
            Logger.progress(idx, len(missing_tracks), f"downloading", show_eta=True)
            artist_str = ', '.join(track['artists']) if track['artists'] else 'Unknown'
            Logger.info(f"Downloading: {track['name']} - {artist_str}")
            
            success = False
            
            if manual_link:
                # Manual YouTube link mode
                Logger.info(f"Need YouTube link for: {track['name']} - {artist_str}")
                youtube_url = UserInput.get_youtube_url()
                if not youtube_url:
                    Logger.warning(f"Skipped: {track['name']}")
                    track['manually_skipped'] = True
                    stats['skipped'] += 1
                elif SpotdlDownloader.download_from_youtube(youtube_url, playlist_download_folder, track):
                    Logger.success(f"Downloaded: {track['name']}")
                    success = True
                    stats['downloaded'] += 1
                else:
                    Logger.error(f"Failed to download: {track['name']}")
                    track['unable_to_find'] = True
                    stats['failed'] += 1
            
            elif manual_verify:
                # Manual verification mode
                yt_url = SpotdlDownloader.get_youtube_url(track, dont_filter=dont_filter)
                if yt_url:
                    Logger.info(f"YouTube match: {yt_url}")
                
                if UserInput.confirm_download(track['name']):
                    if SpotdlDownloader.download_from_spotify(track, playlist_download_folder, dont_filter=dont_filter):
                        Logger.success(f"Downloaded: {track['name']}")
                        success = True
                        stats['downloaded'] += 1
                    else:
                        Logger.error(f"Failed to download: {track['name']}")
                        track['unable_to_find'] = True
                        stats['failed'] += 1
                else:
                    Logger.warning(f"Skipped: {track['name']}")
                    track['manually_skipped'] = True
                    stats['skipped'] += 1
            
            else:
                # Automatic mode
                if SpotdlDownloader.download_from_spotify(track, playlist_download_folder, dont_filter=dont_filter):
                    Logger.success(f"Downloaded: {track['name']}")
                    success = True
                    stats['downloaded'] += 1
                else:
                    Logger.error(f"Failed to download: {track['name']}")
                    track['unable_to_find'] = True
                    stats['failed'] += 1
        
        # Refresh downloads and update CSV
        downloaded = FileManager.get_downloaded_songs(playlist_download_folder)
        csv_filepath = CSVManager.get_csv_filepath(playlist_id, playlist_name, playlist_download_folder)
        CSVManager.write_playlist_songs(
            playlist_id,
            tracks,
            downloaded,
            FileManager.is_song_downloaded,
            playlist_name,
            playlist_download_folder
        )
        
        # Handle cleanup of removed songs if requested
        if cleanup_removed or auto_delete_removed or keep_removed:
            auto_action = None
            if auto_delete_removed:
                auto_action = 'delete'
            elif keep_removed:
                auto_action = 'keep'
            
            cleanup_stats = CleanupManager.cleanup_removed_songs(
                tracks,
                csv_filepath,
                playlist_download_folder,
                auto_action
            )
            
            # Add cleanup info to stats (as separate key to avoid type conflicts)
            stats.update({
                'cleanup_performed': True,
                'removed_songs_found': cleanup_stats['removed_songs_found'],
                'removed_files_found': cleanup_stats['removed_files_found'],
                'files_deleted': cleanup_stats['files_deleted'],
                'files_kept': cleanup_stats['files_kept']
            })
        
        return stats
    
    except Exception as e:
        ErrorHandler.handle_exception(e, "Error processing playlist")
        return stats


def main():
    """
    Main entry point for playlist checker.
    Parses arguments, validates environment, and processes playlists.
    """
    parser = argparse.ArgumentParser(description="Check and download songs from Spotify playlists")
    parser.add_argument("--download-folder", default=Config.get_downloads_folder(), help="Folder to download songs to")
    parser.add_argument("--manual-verify", action="store_true", help="Manually verify each YouTube link before downloading")
    parser.add_argument("--dont-filter-results", action="store_true", help="Don't filter spotdl search results")
    parser.add_argument("--manual-link", action="store_true", help="Manually provide YouTube links for each song")
    parser.add_argument("--cleanup-removed", action="store_true", help="Check for songs removed from playlists and ask to delete files")
    parser.add_argument("--auto-delete-removed", action="store_true", help="Automatically delete files for songs removed from playlists")
    parser.add_argument("--keep-removed", action="store_true", help="Keep files for songs removed from playlists (no prompt)")
    
    args = parser.parse_args()
    
    # Validate folder
    try:
        ErrorHandler.validate_folder(args.download_folder)
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Invalid download folder")
        return
    
    # Initialize clients
    Logger.header("Spotify Playlist Sync")
    
    # Configure logger based on settings
    Logger.set_debug_mode(settings.is_debug_mode())
    Logger.set_timestamps(settings.get('ui', 'enable_timestamps'))
    
    try:
        Logger.info("Initializing Spotify client...")
        spotify_client = SpotifyClient()
        Logger.success("Connected to Spotify")
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Failed to initialize Spotify client")
        return
    
    # Read playlists
    try:
        Logger.info(f"Reading playlists from {Config.get_playlists_file()}...")
        playlists = PlaylistReader.read_playlists(Config.get_playlists_file())
        Logger.success(f"Found {len(playlists)} playlists to process")
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Failed to read playlists file")
        return
    
    if not playlists:
        Logger.warning("No playlists to process")
        return
    
    # Process each playlist
    Logger.header(f"Processing {len(playlists)} Playlists")
    
    total_stats = {
        'total_playlists': len(playlists),
        'total_tracks': 0,
        'total_missing': 0,
        'total_downloaded': 0,
        'total_skipped': 0,
        'total_failed': 0,
        'total_removed_songs': 0,
        'total_files_deleted': 0,
        'total_files_kept': 0
    }
    
    for idx, playlist_id in enumerate(playlists, 1):
        try:
            Logger.progress(idx, len(playlists), "processing playlists")
            
            stats = process_playlist(
                spotify_client,
                playlist_id,
                args.download_folder,
                manual_verify=args.manual_verify,
                manual_link=args.manual_link,
                dont_filter=args.dont_filter_results,
                cleanup_removed=args.cleanup_removed,
                auto_delete_removed=args.auto_delete_removed,
                keep_removed=args.keep_removed
            )
            
            # Accumulate stats
            total_stats['total_tracks'] += stats['total_tracks']
            total_stats['total_missing'] += stats['missing']
            total_stats['total_downloaded'] += stats['downloaded']
            total_stats['total_skipped'] += stats['skipped']
            total_stats['total_failed'] += stats['failed']
            
            # Accumulate cleanup stats if present
            if 'cleanup_performed' in stats:
                total_stats['total_removed_songs'] += stats.get('removed_songs_found', 0)
                total_stats['total_files_deleted'] += stats.get('files_deleted', 0)
                total_stats['total_files_kept'] += stats.get('files_kept', 0)
            
        except Exception as e:
            ErrorHandler.handle_exception(e, f"Error processing playlist {playlist_id}")
            continue
    
    # Print summary
    Logger.header("Download Summary")
    Logger.summary('Total Playlists', str(total_stats['total_playlists']))
    Logger.summary('Total Tracks Found', str(total_stats['total_tracks']))
    Logger.summary('Missing Tracks', str(total_stats['total_missing']))
    Logger.summary('Successfully Downloaded', str(total_stats['total_downloaded']))
    Logger.summary('Skipped', str(total_stats['total_skipped']))
    Logger.summary('Failed', str(total_stats['total_failed']))
    
    # Print cleanup summary if any cleanup was performed
    if total_stats['total_removed_songs'] > 0:
        Logger.header("Cleanup Summary")
        Logger.summary('Removed Songs Found', str(total_stats['total_removed_songs']))
        Logger.summary('Files Deleted', str(total_stats['total_files_deleted']))
        Logger.summary('Files Kept', str(total_stats['total_files_kept']))
    
    Logger.success("Playlist check complete!")


if __name__ == "__main__":
    main()
