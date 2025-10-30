"""
Spotify API interactions using spotipy.
Handles authentication and playlist/track retrieval.
"""

import os
from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv


class SpotifyClient:
    """Wrapper for Spotify API operations."""

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
            )
        )

    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """
        Fetch all tracks from a Spotify playlist.
        
        Args:
            playlist_id: Spotify playlist ID or URL
            
        Returns:
            List of track dictionaries with name, artists, id, url, album, cover_art
        """
        results = self.client.playlist_items(playlist_id)
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
            
            results = self.client.next(results) if results['next'] else None
        
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
            playlist_info = self.client.playlist(playlist_id)
            return playlist_info if playlist_info and 'name' in playlist_info else None
        except Exception:
            return None
