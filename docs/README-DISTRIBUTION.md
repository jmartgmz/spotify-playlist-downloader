# Spotify Playlist Sync - Portable Executable

🎵 **Automatically download songs from your Spotify playlists using YouTube as the source**

## Quick Start

1. **Place the executable anywhere** - It's completely portable!
2. **Run it** - Double-click or use terminal: `./SpotifyPlaylistSync`
3. **Follow the setup wizard** - It will guide you through everything on first run

That's it! No Python installation required.

## What You'll Need

- **Spotify Developer Account** (free) - The setup wizard will guide you
- **Internet connection** - For downloading songs
- **5 minutes** - For initial setup

## First Run Setup

When you run the executable for the first time, it will:

1. **Guide you through Spotify API setup** - No technical knowledge required
2. **Create all necessary files** - `.env`, `playlists.txt`, download folders
3. **Configure your preferences** - Download location, playlist discovery
4. **Provide helpful instructions** - How to use each feature

## Features

### 🚀 Core Functions
- **One-time sync** - Download missing songs from your playlists
- **Background watcher** - Continuously monitor for new songs
- **Auto-discovery** - Automatically find all your Spotify playlists
- **Smart updates** - Only download new/missing songs

### 🛠️ Advanced Options
- **Custom download locations** - Put music wherever you want
- **Manual verification** - Review each song before downloading
- **Cleanup management** - Handle songs removed from playlists
- **Multiple formats** - High-quality audio downloads

### 📊 Smart Management
- **CSV tracking** - Keeps track of what's downloaded
- **Duplicate prevention** - Won't download the same song twice
- **Error handling** - Gracefully handles network issues
- **Progress tracking** - See download progress in real-time

## Commands

After setup, you can use these commands:

- **`sync`** - Download missing songs from playlists
- **`watch`** - Monitor playlists continuously for new songs
- **`discover`** - Auto-discover your Spotify playlists
- **`refresh`** - Update tracking files
- **`help`** - Show detailed help

## File Structure

After first run, you'll have:

```
📁 your-folder/
├── SpotifyPlaylistSync     # The executable
├── .env                   # Your Spotify credentials (keep private!)
├── playlists.txt          # Your playlist URLs/IDs
├── downloaded_songs/      # Your music files
└── playlist_songs/        # Tracking files (CSV)
```

## Requirements

- **Operating System**: Linux, Windows, or macOS
- **Disk Space**: ~30MB for the app + space for your music
- **Internet**: Required for downloading songs
- **Spotify Account**: Free account works fine

## Spotify API Setup (Detailed)

The setup wizard will guide you, but here are the detailed steps:

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in:
   - **App name**: "My Playlist Sync" (or anything you want)
   - **App description**: "Personal playlist downloader"
5. Click "Show Client Secret"
6. Copy your **Client ID** and **Client Secret**
7. Click "Edit Settings"
8. Add this **Redirect URI**: `http://127.0.0.1:8888/callback`
9. Save settings

The setup wizard will ask for these credentials and save them securely.

## Troubleshooting

### Common Issues

**"No module named..."**
- The executable is self-contained. If you see this, please report it as a bug.

**"Invalid client_id"**
- Check your Spotify API credentials in the `.env` file
- Make sure you copied them correctly from the Spotify Developer Dashboard

**"Can't find YouTube video"**
- Some songs might not be available on YouTube
- The app will skip unavailable songs and continue

**Permission denied**
- Make sure the executable has permission to run: `chmod +x SpotifyPlaylistSync`

### Getting Help

If you encounter issues:

1. Run `./SpotifyPlaylistSync` and type `help` for command details
2. Check that your `.env` file has the correct Spotify credentials
3. Make sure your `playlists.txt` has valid Spotify playlist URLs

## Security & Privacy

- **Your credentials stay local** - Never sent anywhere except Spotify's official API
- **No data collection** - This app doesn't collect or send any personal data
- **Open source** - You can inspect the code for transparency

## Advanced Usage

### Custom Download Locations
```bash
./SpotifyPlaylistSync
>>> sync --download-folder /path/to/your/music
```

### Manual Verification Mode
```bash
>>> sync --manual-verify
```

### Background Monitoring
```bash
>>> watch --interval 10  # Check every 10 minutes
```

---

**Enjoy your music! 🎵**

*This app respects artists and encourages supporting them through official channels. Use responsibly and in accordance with your local laws.*