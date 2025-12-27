# Spotify Playlist Sync

🎵 **Automatically download songs from your Spotify playlists using YouTube as the source**

Automatically sync your Spotify playlists with local downloads. Features intelligent downloading, cleanup of removed songs, and continuous monitoring.

## ✨ Quick Start

### Prerequisites
- Python 3.8+
- Spotify Developer Account (free)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jmartgmz/spotify-playlist-downloader.git
   cd spotify-playlist-downloader
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Spotify API**
   ```bash
   cp .env.example .env
   # Edit .env with your Spotify credentials
   ```

5. **Add playlists**
   
   Edit `playlists.txt` with your Spotify playlist URLs or IDs (one per line)

## 🎵 Commands

**Main Commands:**
- **sync** - One-time sync: Download missing songs from playlists (auto-cleans removed songs)
- **watch** - Background watcher: Monitor for new songs continuously (auto-cleans removed songs)
- **discover** - Auto-discover Spotify playlists and update playlists.txt
- **refresh** - Quick refresh: Update CSV files with current downloads

**Using the launcher (recommended):**
```bash
python launcher.py
# Then type commands interactively:
# sync, watch, discover, refresh
```

**Direct execution:**
```bash
python -m spotify_sync.commands.check      # sync
python -m spotify_sync.commands.watch      # watch
python -m spotify_sync.commands.update_playlists_txt  # discover
python -m spotify_sync.commands.update_csv # refresh
```

## 🔧 Sync Options

- `--download-folder FOLDER` - Save downloads to custom location
- `--manual-verify` - Show YouTube match and ask to confirm before downloading
- `--manual-link` - Manually provide YouTube links for each song
- `--dont-filter-results` - Disable spotdl result filtering

**Note:** Cleanup is automatic! Songs removed from Spotify playlists are automatically deleted locally to keep your library in perfect sync.

## 🎯 Usage Examples

```bash
# Basic sync (automatically cleans removed songs)
python launcher.py
# > sync

# Custom download folder
python launcher.py
# > sync --download-folder C:\Music

# Watch for changes every 5 minutes (automatically cleans removed songs)
python launcher.py
# > watch --interval 5

# Manual verification mode
python launcher.py
# > sync --manual-verify

# Auto-discover your playlists
python launcher.py
# > discover
```

## 📁 Project Structure

```
spotify-playlist-downloader/
├── spotify_sync/             # Core application package
│   ├── core/                 # Core functionality
│   │   ├── spotify_api.py    # Spotify API integration
│   │   ├── downloader.py     # YouTube download logic
│   │   ├── file_manager.py   # File operations
│   │   ├── csv_manager.py    # Download tracking
│   │   └── cleanup_manager.py # Cleanup operations
│   ├── commands/             # CLI commands
│   │   ├── check.py          # Sync command
│   │   ├── watch.py          # Background monitoring
│   │   └── update_*.py       # Update commands
│   └── utils/                # Utilities
├── docs/                     # Documentation
│   ├── GETTING_SPOTIFY_API.md
│   ├── CLEANUP_FEATURE.md
│   └── example.playlists.txt
├── requirements.txt          # Python dependencies
├── playlists.txt             # Your playlist URLs
└── .env                      # Spotify API credentials
```

## Features

### 🚀 Core Functions
- **One-time sync** - Download missing songs from your playlists
- **Background watcher** - Continuously monitor for new songs
- **Auto-discovery** - Automatically find all your Spotify playlists
- **Smart updates** - Only download new/missing songs

### 🛠️ Advanced Options
- **Custom download locations**
- **Manual verification mode**
- **Cleanup management** for removed songs
- **Multiple audio formats**
- **Progress tracking**

### 📊 Smart Management
- **CSV tracking** - Keeps track of downloads
- **Duplicate prevention**
- **Error handling** and retry logic

## 📁 Output

- **Downloaded songs:** `downloaded_songs/` (organized by playlist)
- **Status reports:** `playlist_songs/` (CSV files with download status)

## 📚 Documentation

- 📋 **[GETTING_SPOTIFY_API.md](docs/GETTING_SPOTIFY_API.md)** - Detailed Spotify API setup guide
- 🧹 **[CLEANUP_FEATURE.md](docs/CLEANUP_FEATURE.md)** - Cleanup removed songs feature guide

## Configuration

### Spotify API Setup

1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Add redirect URI: `http://127.0.0.1:8888/callback`
4. Copy Client ID and Secret to `.env`

### Environment Variables

```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

## 💡 Tips

- **Organization**: Songs are organized into subfolders by playlist name
- **Watcher**: Runs continuously; press `Ctrl+C` to stop
- **WSL users**: Use Windows paths like `C:\Users\...\Downloads`

## Requirements

- **Python**: 3.8+
- **Dependencies**: See `requirements.txt`
- **Internet**: Required for downloads

## Troubleshooting

### Common Issues

**"Invalid client_id"**
- Check your Spotify API credentials in `.env`

**"Can't find YouTube video"**
- Some songs might not be available on YouTube
- The app will skip and continue

**Permission errors**
- Make sure you have write permissions to the download folder

## License

This project is for personal use. Please respect artists and support them through official channels.

---

**Enjoy your music! 🎵**
