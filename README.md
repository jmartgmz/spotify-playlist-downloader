# Spotify Playlist Sync

🎵 **Automatically download songs from your Spotify playlists using YouTube as the source**

Sync your Spotify playlists with local downloads. Features intelligent downloading, automatic cleanup of removed songs, and continuous monitoring.

## ✨ Quick Start

### Prerequisites
- **Docker** (recommended) OR **Python 3.8+**
- **Spotify Developer Account** (free) - [Setup Guide](docs/GETTING_SPOTIFY_API.md)

### 🐳 Docker (Recommended)

1. **Clone and configure**
   ```bash
   git clone https://github.com/jmartgmz/spotify-playlist-downloader.git
   cd spotify-playlist-downloader
   cp docs/.env.example .env
   # Edit .env with your Spotify credentials
   ```

2. **Add your playlists**
   ```bash
   # Edit playlists.txt with Spotify playlist URLs (one per line)
   ```

3. **Run**
   ```bash
   docker-compose up -d
   docker attach spotify-playlist-sync
   # Now use commands: sync, watch, discover, refresh
   ```

📖 **[Full Docker Guide →](docs/DOCKER.md)**

### 🐍 Python

#### Windows
**Double-click `run.bat`** - Automatically sets up virtual environment and launches!

#### Linux/Mac
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

## 🎵 Commands

| Command | Description |
|---------|-------------|
| `sync` | Download missing songs from playlists |
| `watch` | Monitor for new songs continuously |
| `discover` | Auto-discover your Spotify playlists |
| `refresh` | Update CSV files with current downloads |

```bash
python launcher.py
# Then type commands interactively
```

### Options

- `--download-folder FOLDER` - Custom download location
- `--manual-verify` - Confirm YouTube matches before downloading
- `--manual-link` - Manually provide YouTube links
- `--dont-filter-results` - Disable result filtering

**Note:** Songs removed from Spotify are automatically deleted locally.

## 📁 Project Structure

```
spotify-playlist-downloader/
├── spotify_sync/           # Core application
│   ├── core/              # Core functionality
│   ├── commands/          # CLI commands
│   ├── dashboard/         # Web interface
│   └── utils/             # Utilities
├── docs/                  # Documentation
│   ├── .env.example       # Environment template
│   ├── DOCKER.md
│   ├── GETTING_SPOTIFY_API.md
│   └── playlists.txt.example
├── downloaded_songs/      # Your music library
│   └── [Playlist Name]/
│       ├── *.mp3          # Music files
│       └── *.csv          # Download tracking
├── launcher.py            # Interactive CLI
├── run.bat                # Windows quick start
├── docker-compose.yml     # Docker setup
└── playlists.txt          # Your playlists
```

## ✨ Features

- ✅ **Auto-sync** playlists with local downloads
- 🔄 **Auto-cleanup** removed songs
- 🔍 **Auto-discovery** of your Spotify playlists
- 📊 **CSV tracking** for download management
- 🐳 **Docker support** for easy deployment
- ⚙️ **Manual verification** mode available

## ⚙️ Configuration

1. Get Spotify API credentials from https://developer.spotify.com/dashboard
2. Create app with redirect URI: `http://127.0.0.1:8888/callback`
3. Copy `docs/.env.example` to `.env` and add your credentials:

```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

📖 **Detailed guide:** [docs/GETTING_SPOTIFY_API.md](docs/GETTING_SPOTIFY_API.md)

## 💡 Tips

- **Windows**: Double-click `run.bat` for automatic setup
- **Organization**: Songs organized by playlist name
- **Watcher**: Press `Ctrl+C` to stop
- **Docker**: See [docs/DOCKER.md](docs/DOCKER.md) for containerized deployment

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid client_id" | Check Spotify credentials in `.env` |
| "Can't find YouTube video" | Song not available on YouTube (will skip) |
| Permission errors | Ensure write permissions for download folder |

## 📄 License

Personal use only. Support artists through official channels.

---

🎵 **Enjoy your music!**
