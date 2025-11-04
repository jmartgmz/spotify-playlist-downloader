# Spotify Playlist Sync# Spotify Playlist Sync



🎵 **Automatically download songs from your Spotify playlists using YouTube as the source**Automatically sync your Spotify playlists with local downloads. Features intelligent downloading, cleanup of removed songs, and continuous monitoring.



## Quick Start (Portable Executable)## ✨ Quick Start



**Want to use it right away? Download the portable executable:****1. Run the setup script (easiest way):**

```bash

1. Download `SpotifyPlaylistSync-Portable-Final.tar.gz` from the `dist/` folder./setup.sh

2. Extract and run `./SpotifyPlaylistSync````

3. Follow the setup wizard - no Python installation needed!

This automatically:

## Development Setup- ✅ Creates a Python virtual environment

- ✅ Installs all dependencies

If you want to run from source or contribute:- ✅ Creates `settings.json` and `playlists.txt` templates

- ✅ Shows next steps

### Prerequisites

**2. Add your Spotify credentials:**

- Python 3.8+Edit `settings.json` and add your Spotify API credentials from https://developer.spotify.com/dashboard

- Spotify Developer Account (free)

**3. Add playlists:**

### InstallationRun auto-discovery:

```bash

1. **Clone the repository**source .venv/bin/activate

   ```bash./run.sh discover

   git clone https://github.com/jmartgmz/spotify-playlist-automatic.git```

   cd spotify-playlist-automaticOr manually edit `playlists.txt` with playlist URLs/IDs

   ```

## 🎵 Commands

2. **Set up virtual environment**

   ```bash**Main Commands:**

   python -m venv .venv- `sync` (s) - One-time sync: Download missing songs from playlists

   source .venv/bin/activate  # Linux/Mac- `watch` (w) - Background watcher: Monitor for new songs continuously  

   # or- `discover` (d) - Auto-discover Spotify playlists and update playlists.txt

   .venv\Scripts\activate     # Windows- `refresh` (r) - Quick refresh: Update CSV files with current downloads

   ```

**Using the launcher (recommended):**

3. **Install dependencies**```bash

   ```bash./run.sh sync

   pip install -r config/requirements.txt# Or on Windows:

   ```run.bat sync

```

4. **Configure Spotify API**

   ```bash**Direct execution:**

   cp .env.example .env```bash

   # Edit .env with your Spotify credentialssource .venv/bin/activate  # Linux/macOS

   ```.venv\Scripts\activate     # Windows



5. **Run the application**python src/check.py        # Direct script execution

   ```bash```

   python launcher.py

   ```## 🔧 Sync Options



## Project Structure- `--download-folder FOLDER` - Save downloads to custom location

- `--manual-verify` - Show YouTube match and ask to confirm before downloading

```- `--manual-link` - Manually provide YouTube links for each song

📁 spotify-playlist-automatic/- `--cleanup-removed` - Prompt to clean up songs removed from playlists

├── 🎵 spotify_sync/          # Core application package- `--auto-delete-removed` - Automatically delete files for removed songs

│   ├── core/                 # Core functionality- `--keep-removed` - Keep files for removed songs without prompting

│   │   ├── spotify_api.py    # Spotify API integration- `--dont-filter-results` - Disable spotdl result filtering

│   │   ├── downloader.py     # YouTube download logic

│   │   ├── file_manager.py   # File operations## 🎯 Examples

│   │   ├── csv_manager.py    # Download tracking

│   │   └── cleanup_manager.py # Cleanup operations```bash

│   ├── commands/             # CLI commands# Basic sync

│   │   ├── check.py          # Sync command./run.sh sync

│   │   ├── watch.py          # Background monitoring

│   │   └── update_*.py       # Update commands# Sync with cleanup prompts

│   └── utils/                # Utilities./run.sh sync --cleanup-removed

├── 🛠️ build_tools/            # Executable building

│   ├── launcher.spec         # PyInstaller config# Watch for changes every 5 minutes

│   ├── build.sh             # Linux build script./run.sh watch --interval 5

│   └── build.bat            # Windows build script

├── 📦 dist/                  # Distribution files# Custom download folder with auto-cleanup

│   ├── SpotifyPlaylistSync-Portable-Final.tar.gz./run.sh sync --download-folder /path/to/music --auto-delete-removed

│   └── SpotifyPlaylistSync-Distribution-Final/

├── 📚 docs/                  # Documentation# Manual verification mode

│   ├── README-DISTRIBUTION.md # User guide for portable version./run.sh sync --manual-verify

│   └── development/          # Development docs

├── ⚙️ config/                 # Configuration files# Auto-discover your playlists

│   ├── requirements.txt      # Python dependencies./run.sh discover

│   └── settings.json         # Default settings```

├── 🚀 launcher.py            # Main application launcher

└── 📋 .env.example           # Environment template## ⚙️ Configuration

```

The app now uses `settings.json` for easy configuration:

## Features

```json

### 🚀 Core Functions{

- **One-time sync** - Download missing songs from your playlists    "spotify": {

- **Background watcher** - Continuously monitor for new songs        "client_id": "your_client_id_here",

- **Auto-discovery** - Automatically find all your Spotify playlists        "client_secret": "your_client_secret_here"

- **Smart updates** - Only download new/missing songs    },

    "paths": {

### 🛠️ Advanced Options        "downloads_folder": "downloaded_songs",

- **Custom download locations**        "playlists_file": "playlists.txt"

- **Manual verification mode**    },

- **Cleanup management** for removed songs    "ui": {

- **Multiple audio formats**        "enable_colors": true,

- **Progress tracking**        "enable_timestamps": true,

        "enable_debug_mode": false

### 📊 Smart Management    }

- **CSV tracking** - Keeps track of downloads}

- **Duplicate prevention**```

- **Error handling** and retry logic

- **Portable configuration**## 📁 Output



## Building Executable- **Downloaded songs:** `downloaded_songs/` (organized by playlist)

- **Status reports:** `playlist_songs/` (CSV files with download status)

To create a standalone executable:- **Configuration:** `settings.json` (user-friendly settings)



```bash## 🚀 New Features

cd build_tools/

./build.sh    # Linux/Mac- **🎨 Better UI**: Color-coded output, progress bars, timestamps

# or- **🔄 Smart Cleanup**: Handle songs removed from playlists

build.bat     # Windows- **⌨️ Command Aliases**: Use short commands (s, w, d, r)

```- **📋 Help System**: Built-in help with examples

- **⚙️ Easy Config**: JSON-based settings instead of environment variables

This creates a ~30MB portable executable with all dependencies bundled.- **🕐 Progress Tracking**: ETA estimates and better progress indicators



## Commands## 📚 Documentation



- **`sync`** - Download missing songs from playlists- 📋 **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project layout and module descriptions

- **`watch`** - Monitor playlists continuously- 🔑 **[GETTING_SPOTIFY_API.md](GETTING_SPOTIFY_API.md)** - Detailed Spotify API setup guide

- **`discover`** - Auto-discover your Spotify playlists- 🧹 **[CLEANUP_FEATURE.md](CLEANUP_FEATURE.md)** - Cleanup removed songs feature guide

- **`refresh`** - Update tracking files

- **`setup`** - Run setup wizard## 💡 Tips

- **`help`** - Show detailed help

- **WSL users**: Use Windows paths like `C:\Users\...\Downloads`

## Configuration- **Watcher**: Runs forever; press `Ctrl+C` to stop

- **Organization**: Songs are organized into subfolders by playlist name

### Spotify API Setup- **Backward compatibility**: Old commands (`check`, `update`, `update-csv`) still work

- **Shortcuts**: Type `help` in the launcher for detailed command info

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Requirements

- **Python**: 3.8+
- **Dependencies**: See `config/requirements.txt`
- **Storage**: ~30MB for app + space for music
- **Internet**: Required for downloads

## License

This project is for personal use. Please respect artists and support them through official channels.

## Troubleshooting

### Common Issues

**"Invalid client_id"**
- Check your Spotify API credentials in `.env`

**"Can't find YouTube video"**
- Some songs might not be available on YouTube
- The app will skip and continue

**Permission errors**
- Make sure you have write permissions to the download folder

For more help, see the documentation in `docs/` or open an issue.

---

**Enjoy your music! 🎵**