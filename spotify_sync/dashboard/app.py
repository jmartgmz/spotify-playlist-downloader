"""
Flask web dashboard for Spotify Playlist Sync.
Provides a web interface for monitoring and controlling playlist syncing.
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from queue import Queue, Empty
from flask import Flask, render_template, jsonify, request, Response
from spotify_sync.core.spotify_api import SpotifyClient
from spotify_sync.core.file_manager import FileManager
from spotify_sync.core.csv_manager import CSVManager
from spotify_sync.utils.config import Config
from spotify_sync.utils.utils import PlaylistReader
from spotify_sync.commands.check import process_playlist
from spotify_sync.commands.watch import process_playlist_watch

app = Flask(__name__)

# Global state
watch_thread = None
watch_running = False
log_queue = Queue()
stats_data = {
    'total_playlists': 0,
    'total_tracks': 0,
    'total_downloaded': 0,
    'total_missing': 0,
    'last_sync': None,
    'watch_status': 'stopped'
}

class DashboardLogger:
    """Logger that sends messages to the web dashboard."""
    
    @staticmethod
    def log(level, message):
        """Add log message to queue for streaming to dashboard."""
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'message': message
        }
        log_queue.put(log_entry)
    
    @staticmethod
    def info(message):
        DashboardLogger.log('info', message)
    
    @staticmethod
    def success(message):
        DashboardLogger.log('success', message)
    
    @staticmethod
    def warning(message):
        DashboardLogger.log('warning', message)
    
    @staticmethod
    def error(message):
        DashboardLogger.log('error', message)

@app.route('/')
def index():
    """Render main dashboard page."""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get current statistics."""
    try:
        playlists = PlaylistReader.read_playlists(Config.get_playlists_file())
        stats_data['total_playlists'] = len(playlists)
        
        # Calculate stats from CSV files
        total_tracks = 0
        total_downloaded = 0
        total_missing = 0
        
        download_folder = Config.get_downloads_folder()
        
        for playlist_id in playlists:
            try:
                spotify_client = SpotifyClient()
                playlist_info = spotify_client.get_playlist_info(playlist_id)
                playlist_name = playlist_info.get('name') if playlist_info else None
                
                playlist_folder = FileManager.get_playlist_folder_name(playlist_id, playlist_name)
                playlist_path = os.path.join(download_folder, playlist_folder)
                csv_path = CSVManager.get_csv_filepath(playlist_id, playlist_name, playlist_path)
                
                if os.path.exists(csv_path):
                    csv_status = CSVManager.read_csv_status(csv_path)
                    total_tracks += len(csv_status)
                    
                    for status in csv_status.values():
                        if status == 'downloaded':
                            total_downloaded += 1
                        elif status == 'missing':
                            total_missing += 1
            except:
                continue
        
        stats_data['total_tracks'] = total_tracks
        stats_data['total_downloaded'] = total_downloaded
        stats_data['total_missing'] = total_missing
        
    except Exception as e:
        DashboardLogger.error(f"Error getting stats: {e}")
    
    return jsonify(stats_data)

@app.route('/api/playlists')
def get_playlists():
    """Get list of all playlists with their status."""
    try:
        playlists = PlaylistReader.read_playlists(Config.get_playlists_file())
        playlist_data = []
        
        download_folder = Config.get_downloads_folder()
        spotify_client = SpotifyClient()
        
        for playlist_id in playlists:
            try:
                playlist_info = spotify_client.get_playlist_info(playlist_id)
                playlist_name = playlist_info.get('name', 'Unknown') if playlist_info else 'Unknown'
                
                playlist_folder = FileManager.get_playlist_folder_name(playlist_id, playlist_name)
                playlist_path = os.path.join(download_folder, playlist_folder)
                csv_path = CSVManager.get_csv_filepath(playlist_id, playlist_name, playlist_path)
                
                tracks_count = 0
                downloaded_count = 0
                missing_count = 0
                
                if os.path.exists(csv_path):
                    csv_status = CSVManager.read_csv_status(csv_path)
                    tracks_count = len(csv_status)
                    
                    for status in csv_status.values():
                        if status == 'downloaded':
                            downloaded_count += 1
                        elif status == 'missing':
                            missing_count += 1
                
                playlist_data.append({
                    'id': playlist_id,
                    'name': playlist_name,
                    'tracks': tracks_count,
                    'downloaded': downloaded_count,
                    'missing': missing_count
                })
            except:
                continue
        
        return jsonify(playlist_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playlist/<path:playlist_id>/details')
def get_playlist_details(playlist_id):
    """Get detailed track list for a specific playlist."""
    try:
        DashboardLogger.info(f"Loading details for playlist: {playlist_id}")
        
        spotify_client = SpotifyClient()
        playlist_info = spotify_client.get_playlist_info(playlist_id)
        playlist_name = playlist_info.get('name', 'Unknown') if playlist_info else 'Unknown'
        
        download_folder = Config.get_downloads_folder()
        playlist_folder = FileManager.get_playlist_folder_name(playlist_id, playlist_name)
        playlist_path = os.path.join(download_folder, playlist_folder)
        csv_path = CSVManager.get_csv_filepath(playlist_id, playlist_name, playlist_path)
        
        DashboardLogger.info(f"CSV path: {csv_path}")
        
        tracks = []
        
        if os.path.exists(csv_path):
            csv_status = CSVManager.read_csv_status(csv_path)
            DashboardLogger.info(f"Found {len(csv_status)} tracks in CSV")
            
            for song_key, status in csv_status.items():
                # song_key format is "Artist - Title"
                if " - " in song_key:
                    artist, title = song_key.split(" - ", 1)
                else:
                    artist = "Unknown"
                    title = song_key
                
                # Get file info if downloaded
                file_info = None
                if status == 'downloaded':
                    filename = f"{song_key}.mp3"
                    filepath = os.path.join(playlist_path, filename)
                    if os.path.exists(filepath):
                        file_size = os.path.getsize(filepath)
                        file_size_mb = round(file_size / 1024 / 1024, 2)
                        file_info = {
                            'size_mb': file_size_mb,
                            'exists': True
                        }
                    else:
                        file_info = {'exists': False}
                
                tracks.append({
                    'artist': artist,
                    'title': title,
                    'status': status,
                    'file_info': file_info
                })
        else:
            DashboardLogger.warning(f"CSV file not found: {csv_path}")
        
        return jsonify({
            'playlist_name': playlist_name,
            'playlist_id': playlist_id,
            'tracks': tracks
        })
    except Exception as e:
        DashboardLogger.error(f"Error loading playlist details: {e}")
        import traceback
        DashboardLogger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def stream_logs():
    """Stream logs to dashboard using Server-Sent Events."""
    def generate():
        while True:
            try:
                log_entry = log_queue.get(timeout=1)
                yield f"data: {json.dumps(log_entry)}\n\n"
            except Empty:
                yield f"data: {json.dumps({'keepalive': True})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/sync', methods=['POST'])
def sync_playlists():
    """Manually trigger playlist sync."""
    global stats_data
    
    try:
        DashboardLogger.info("Starting manual sync...")
        
        # Get download folder from request if provided
        data = request.get_json() or {}
        download_folder = data.get('download_folder')
        
        # Use default if not provided or empty
        if not download_folder or not download_folder.strip():
            download_folder = Config.get_downloads_folder()
        else:
            download_folder = download_folder.strip()
            DashboardLogger.info(f"Using custom download folder: {download_folder}")
        
        playlists = PlaylistReader.read_playlists(Config.get_playlists_file())
        spotify_client = SpotifyClient()
        
        total_downloaded = 0
        
        for idx, playlist_id in enumerate(playlists, 1):
            DashboardLogger.info(f"Processing playlist {idx}/{len(playlists)}")
            
            try:
                stats = process_playlist(
                    spotify_client,
                    playlist_id,
                    download_folder
                )
                
                total_downloaded += stats.get('downloaded', 0)
                
                if stats.get('downloaded', 0) > 0:
                    DashboardLogger.success(f"Downloaded {stats['downloaded']} new songs")
                
                if stats.get('files_deleted', 0) > 0:
                    DashboardLogger.info(f"Cleaned up {stats['files_deleted']} files")
                
            except Exception as e:
                DashboardLogger.error(f"Error processing playlist: {e}")
        
        stats_data['last_sync'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        DashboardLogger.success(f"Sync complete! Downloaded {total_downloaded} songs")
        
        return jsonify({'success': True, 'downloaded': total_downloaded})
    except Exception as e:
        DashboardLogger.error(f"Sync failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/discover', methods=['POST'])
def discover_playlists():
    """Auto-discover Spotify playlists."""
    try:
        DashboardLogger.info("Starting playlist discovery...")
        
        from spotify_sync.commands.update_playlists_txt import main as discover_main
        
        # Run discover command
        import sys
        original_argv = sys.argv
        sys.argv = ['dashboard']
        
        try:
            discover_main()
            DashboardLogger.success("Playlist discovery complete!")
            return jsonify({'success': True})
        finally:
            sys.argv = original_argv
            
    except Exception as e:
        DashboardLogger.error(f"Discover failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/watch/start', methods=['POST'])
def start_watch():
    """Start watch mode."""
    global watch_thread, watch_running, stats_data
    
    if watch_running:
        return jsonify({'success': False, 'error': 'Watch mode already running'})
    
    interval = request.json.get('interval', 10)
    
    def watch_loop():
        global watch_running
        watch_running = True
        stats_data['watch_status'] = 'running'
        
        DashboardLogger.success(f"Watch mode started (checking every {interval} minutes)")
        
        try:
            playlists = PlaylistReader.read_playlists(Config.get_playlists_file())
            spotify_client = SpotifyClient()
            download_folder = Config.get_downloads_folder()
            
            iteration = 0
            
            while watch_running:
                iteration += 1
                DashboardLogger.info(f"Check #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
                
                total_new = 0
                for playlist_id in playlists:
                    try:
                        new_songs = process_playlist_watch(spotify_client, playlist_id, download_folder)
                        total_new += new_songs
                    except Exception as e:
                        DashboardLogger.error(f"Error checking playlist: {e}")
                
                if total_new > 0:
                    DashboardLogger.success(f"Found {total_new} new songs")
                else:
                    DashboardLogger.info("No new songs found")
                
                stats_data['last_sync'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if watch_running:
                    time.sleep(interval * 60)
                    
        except Exception as e:
            DashboardLogger.error(f"Watch mode error: {e}")
        finally:
            watch_running = False
            stats_data['watch_status'] = 'stopped'
            DashboardLogger.warning("Watch mode stopped")
    
    watch_thread = threading.Thread(target=watch_loop, daemon=True)
    watch_thread.start()
    
    return jsonify({'success': True})

@app.route('/api/watch/stop', methods=['POST'])
def stop_watch():
    """Stop watch mode."""
    global watch_running, stats_data
    
    if not watch_running:
        return jsonify({'success': False, 'error': 'Watch mode not running'})
    
    watch_running = False
    stats_data['watch_status'] = 'stopped'
    DashboardLogger.info("Stopping watch mode...")
    
    return jsonify({'success': True})

@app.route('/api/watch/status')
def watch_status():
    """Get watch mode status."""
    return jsonify({
        'running': watch_running,
        'status': stats_data['watch_status']
    })

def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask dashboard."""
    DashboardLogger.info(f"Dashboard starting at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    # Check if running in Docker
    in_docker = os.path.exists('/.dockerenv')
    debug_mode = not in_docker  # Only enable debug mode outside Docker
    host = '0.0.0.0' if in_docker else '127.0.0.1'
    run_dashboard(host=host, debug=debug_mode)
