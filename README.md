# Spotify Playlist Sync

Automatically download songs from your Spotify playlists in high-quality FLAC format.

## Prerequisites

- Python 3.8+
- Spotify Developer Account - [Setup Guide](docs/GETTING_SPOTIFY_API.md)

## Installation

### Windows
Double-click `run.bat` to automatically set up and launch.

### Linux/Mac
```bash
git clone https://github.com/jmartgmz/spotify-playlist-downloader.git
cd spotify-playlist-downloader
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp docs/.env.example .env
# Edit .env with your Spotify credentials
python launcher.py
```

## Usage

Run the launcher and use commands interactively:

```bash
python launcher.py
```

### Available Commands

| Command | Description |
|---------|-------------|
| `sync` | Download missing songs from playlists |
| `watch` | Monitor for new songs continuously |
| `discover` | Auto-discover your Spotify playlists |
| `refresh` | Update CSV files with current downloads |
| `help` | Show detailed help |
| `quit` | Exit launcher |

### Command Options

- `--download-folder FOLDER` - Custom download location
- `--manual-verify` - Confirm matches before downloading
- `--manual-link` - Manually provide YouTube links (downloads as MP3)
- `--dont-filter-results` - Disable result filtering

## Configuration

1. Get Spotify API credentials from https://developer.spotify.com/dashboard
2. Create app with redirect URI: `http://127.0.0.1:8888/callback`
3. Copy `docs/.env.example` to `.env` and add your credentials:

```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

See [docs/GETTING_SPOTIFY_API.md](docs/GETTING_SPOTIFY_API.md) for detailed instructions.

## Features

- Auto-sync playlists with local downloads
- Auto-cleanup of removed songs
- Auto-discovery of your Spotify playlists
- CSV tracking for download management
- High-quality FLAC downloads
- Manual verification mode

## Project Structure

```
spotify-playlist-downloader/
├── spotify_sync/           # Core application
│   ├── core/              # Core functionality
│   ├── commands/          # CLI commands
│   └── utils/             # Utilities
├── docs/                  # Documentation
├── downloaded_songs/      # Your music library
├── launcher.py            # Interactive CLI
└── playlists.txt          # Your playlists
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid client_id" | Check Spotify credentials in `.env` |
| "Track not found" | Song not available on any service |
| Permission errors | Ensure write permissions for download folder |

## Notes

- Songs removed from Spotify playlists are automatically deleted locally
- **Default mode**: Downloads FLAC from Tidal, Qobuz, Deezer, or Amazon Music
- **Manual link mode** (`--manual-link`): Downloads MP3 from YouTube with Spotify metadata
- Manual link is useful when a track isn't available on streaming services

## License

Personal use only. Support artists through official channels.
