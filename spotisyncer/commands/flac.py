#!/usr/bin/env python3
"""
FLAC Upgrade Script for Spotify playlists.
Hunts for downloaded .mp3 files and attempts to replace them with .flac
from SpotiFLAC. Updates CSVs accordingly.
"""

import warnings
warnings.simplefilter('ignore')
warnings.filterwarnings('ignore')

import os
import argparse
import sys
from spotify_sync.core.spotify_api import SpotifyClient
from spotify_sync.core.file_manager import FileManager
from spotify_sync.core.downloader import SpotiFLACDownloader
from spotify_sync.core.csv_manager import CSVManager
from spotify_sync.utils.utils import PlaylistReader
from spotify_sync.core.logger import Logger
from spotify_sync.utils.error_handler import ErrorHandler
from spotify_sync.core.settings_manager import settings, Config

def process_playlist(
    spotify_client: SpotifyClient,
    playlist_id: str,
    download_folder: str
) -> dict:
    Logger.section(f"Checking for Upgrades: {playlist_id}")
    
    stats = {
        'total_tracks': 0,
        'mp3_found': 0,
        'upgraded': 0,
        'failed': 0
    }
    
    try:
        tracks = spotify_client.get_playlist_tracks(playlist_id)
        stats['total_tracks'] = len(tracks)
        
        playlist_info = spotify_client.get_playlist_info(playlist_id)
        playlist_name = playlist_info.get('name') if playlist_info else None
        
        if playlist_name:
            Logger.info(f"Playlist: {playlist_name}")
            
        playlist_folder_name = FileManager.get_playlist_folder_name(playlist_id, playlist_name)
        playlist_download_folder = os.path.join(download_folder, playlist_folder_name)
        FileManager.create_folder(playlist_download_folder)
        
        downloaded = FileManager.get_downloaded_songs(playlist_download_folder)
        
        mp3_tracks = []
        for track in tracks:
            file_info = FileManager.find_downloaded_song(track, downloaded)
            if file_info and file_info.get('ext') == 'mp3':
                mp3_tracks.append((track, file_info))
                
        stats['mp3_found'] = len(mp3_tracks)
        
        if not mp3_tracks:
            Logger.success("No MP3 files found to upgrade in this playlist!")
            return stats
            
        Logger.start_progress("upgrading tracks")
        
        for idx, (track, file_info) in enumerate(mp3_tracks, 1):
            Logger.progress(idx, len(mp3_tracks), f"upgrading", show_eta=True)
            artist_str = ', '.join(track['artists']) if track['artists'] else 'Unknown'
            Logger.info(f"Attempting FLAC Upgrade: {track['name']} - {artist_str}")
            
            success, error_msg = SpotiFLACDownloader.download_from_spotify(track, playlist_download_folder)
            
            if success:
                Logger.success(f"Successfully Upgraded: {track['name']}")
                stats['upgraded'] += 1
                try:
                    os.remove(file_info['path'])
                    Logger.info(f"Deleted old MP3: {os.path.basename(file_info['path'])}")
                except Exception as e:
                    Logger.warning(f"Could not delete old MP3: {e}")
            else:
                error_suffix = f" ({error_msg})" if error_msg else ""
                Logger.error(f"Failed to upgrade: {track['name']}{error_suffix}")
                stats['failed'] += 1
                
            if idx < len(mp3_tracks):
                print()
                
        # Update CSV
        downloaded = FileManager.get_downloaded_songs(playlist_download_folder)
        CSVManager.write_playlist_songs(
            playlist_id,
            tracks,
            downloaded,
            FileManager.is_song_downloaded,
            playlist_name,
            playlist_download_folder
        )
        
        return stats

    except Exception as e:
        ErrorHandler.handle_exception(e, "Error processing playlist")
        return stats

def main():
    parser = argparse.ArgumentParser(description="Upgrade MP3 files to FLAC format")
    parser.add_argument("--download-folder", default=Config.get_downloads_folder(), help="Folder to download songs to")
    args = parser.parse_args()
    
    try:
        ErrorHandler.validate_folder(args.download_folder)
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Invalid download folder")
        return
        
    Logger.header("FLAC Upgrade Process")
    Logger.set_debug_mode(settings.is_debug_mode())
    Logger.set_timestamps(settings.get('ui', 'enable_timestamps'))
    
    try:
        spotify_client = SpotifyClient()
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Failed to initialize Spotify client")
        return
        
    try:
        playlists = PlaylistReader.read_playlists(Config.get_playlists_file())
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Failed to read playlists file")
        return
        
    if not playlists:
        Logger.warning("No playlists to process")
        return
        
    total_stats = {
        'mp3_found': 0,
        'upgraded': 0,
        'failed': 0
    }
    
    for idx, playlist_id in enumerate(playlists, 1):
        Logger.progress(idx, len(playlists), "processing playlists")
        stats = process_playlist(spotify_client, playlist_id, args.download_folder)
        
        total_stats['mp3_found'] += stats.get('mp3_found', 0)
        total_stats['upgraded'] += stats.get('upgraded', 0)
        total_stats['failed'] += stats.get('failed', 0)
        
    Logger.header("Upgrade Summary")
    Logger.summary('MP3 Files Found', str(total_stats['mp3_found']))
    Logger.summary('Successfully Upgraded to FLAC', str(total_stats['upgraded']))
    Logger.summary('Failed Upgrades', str(total_stats['failed']))
    Logger.success("FLAC upgrade complete!")

if __name__ == "__main__":
    main()
