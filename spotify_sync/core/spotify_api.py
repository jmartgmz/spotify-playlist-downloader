"""
Spotify API interactions using spotipy.
Handles authentication and playlist/track retrieval.
"""

import os
import time
import logging
from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from dotenv import load_dotenv

# Suppress spotipy rate limit warnings
logging.getLogger('spotipy').setLevel(logging.ERROR)


class SpotifyClient:
    """Wrapper for Spotify API operations with rate limiting."""

    def __init__(self):
        """Initialize Spotify client with credentials from .env"""
        load_dotenv()
        
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise RuntimeError(
                "Spotify API credentials not set. "
                "Please create a .env file with SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."
            )
        
        self.client = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            ),
            retries=3,
            backoff_factor=0.5
        )
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

    def _rate_limit(self):
        """Enforce rate limiting between API calls."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()

    def _api_call_with_retry(self, func, *args, **kwargs):
        """
        Execute an API call with retry logic for rate limits.
        
        Args:
            func: Function to call
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Result of function call
        """
        max_retries = 5
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                return func(*args, **kwargs)
            except SpotifyException as e:
                if e.http_status == 429:  # Rate limit error
                    retry_after = int(e.headers.get('Retry-After', retry_delay))
                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        retry_delay *= 2
                        continue
                raise
        
        raise RuntimeError(f"Failed after {max_retries} retries")

    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """
        Fetch all tracks from a Spotify playlist.
        
        Args:
            playlist_id: Spotify playlist ID or URL
            
        Returns:
            List of track dictionaries with name, artists, id, url, album, cover_art
        """
        results = self._api_call_with_retry(self.client.playlist_items, playlist_id)
        tracks = []
        
        while results:
            for item in results['items']:
                track = item['track']
                
                # Get album info
                album_data = track.get('album', {})
                album_name = album_data.get('name', 'Unknown')
                album_year = album_data.get('release_date', '')[:4] if album_data.get('release_date') else ''
                
                # Get cover art (highest resolution)
                cover_art_url = None
                images = album_data.get('images', [])
                if images:
                    cover_art_url = images[0]['url']  # First image is largest
                
                tracks.append({
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'id': track['id'],
                    'url': track['external_urls']['spotify'],
                    'album': album_name,
                    'album_year': album_year,
                    'cover_art_url': cover_art_url
                })
            
            if results['next']:
                results = self._api_call_with_retry(self.client.next, results)
            else:
                results = None
        
        return tracks

    def get_playlist_info(self, playlist_id: str) -> Optional[Dict]:
        """
        Get playlist name and metadata.
        
        Args:
            playlist_id: Spotify playlist ID or URL
            
        Returns:
            Playlist info dict with 'name' key, or None if not found
        """
        try:
            playlist_info = self._api_call_with_retry(self.client.playlist, playlist_id)
            return playlist_info if playlist_info and 'name' in playlist_info else None
        except Exception:
            return None
