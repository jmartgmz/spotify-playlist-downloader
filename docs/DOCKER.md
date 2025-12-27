# Docker Setup Guide

This guide explains how to run Spotify Playlist Sync using Docker.

## 🐳 Quick Start

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- Spotify API credentials ([Setup Guide](docs/GETTING_SPOTIFY_API.md))

### Setup Steps

1. **Clone and navigate to the repository**
   ```bash
   git clone https://github.com/jmartgmz/spotify-playlist-downloader.git
   cd spotify-playlist-downloader
   ```

2. **Create your environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your Spotify API credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

3. **Add your playlists**
   
   Edit `playlists.txt` and add your Spotify playlist URLs (one per line):
   ```
   https://open.spotify.com/playlist/your_playlist_id
   ```

4. **Build and start the container**
   ```bash
   docker-compose up -d
   ```

5. **Attach to the interactive launcher**
   ```bash
   docker attach spotify-playlist-sync
   ```

## 📋 Usage

### Interactive Mode (Recommended)

Attach to the running container to use the interactive launcher:

```bash
docker attach spotify-playlist-sync
```

Then use commands:
- `sync` - Download missing songs
- `watch` - Monitor playlists continuously
- `dashboard` - Launch web dashboard
- `discover` - Auto-discover playlists
- `help` - Show help
- `quit` - Exit (container keeps running)

**Note:** To detach without stopping the container, press `Ctrl+P` then `Ctrl+Q`

### Run One-Time Commands

Execute specific commands without attaching:

```bash
# Sync once
docker-compose exec spotify-sync python -m spotify_sync.commands.check

# Update CSV files
docker-compose exec spotify-sync python -m spotify_sync.commands.update_csv

# Discover playlists
docker-compose exec spotify-sync python -m spotify_sync.commands.update_playlists_txt
```

### Web Dashboard

The dashboard is accessible at `http://localhost:5000` when running:

```bash
docker attach spotify-playlist-sync
# Type: dashboard
```

Or run directly:
```bash
docker-compose exec spotify-sync python -m spotify_sync.dashboard.app
```

## 🔧 Docker Commands

### Container Management

```bash
# Start the container
docker-compose up -d

# Stop the container
docker-compose down

# View logs
docker-compose logs -f

# Restart the container
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build
```

### Accessing the Container

```bash
# Interactive launcher
docker attach spotify-playlist-sync

# Bash shell
docker-compose exec spotify-sync bash

# View running processes
docker-compose ps
```

## 📁 Data Persistence

Docker volumes ensure your data persists:

- **downloaded_songs/** - Your music files
- **playlist_songs/** - CSV tracking files
- **playlists.txt** - Your playlist configuration
- **.env** - Your API credentials

All these are mounted from your host machine, so they persist even if you remove the container.

## 🛠️ Configuration

### Environment Variables

Edit `.env` or set in `docker-compose.yml`:

```yaml
environment:
  - SPOTIFY_CLIENT_ID=your_id
  - SPOTIFY_CLIENT_SECRET=your_secret
  - SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
  - SPOTIFY_CHECK_INTERVAL=10
```

### Custom Download Location

To change the download location inside the container, modify the volume mount in `docker-compose.yml`:

```yaml
volumes:
  - /your/custom/path:/app/downloaded_songs
```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Remove and recreate
docker-compose down
docker-compose up -d --build
```

### Authentication issues
1. Ensure `.env` file has correct credentials
2. Delete `.spotify_cache` if it exists
3. Restart container: `docker-compose restart`

### Permission issues with downloaded files
```bash
# Check container user
docker-compose exec spotify-sync whoami

# Fix permissions on host
sudo chown -R $USER:$USER downloaded_songs/
```

### Can't attach to container
```bash
# Check if container is running
docker-compose ps

# Start if stopped
docker-compose up -d
```

## 🔐 Security Notes

- Never commit `.env` file to git
- Keep your Spotify credentials secure
- The `.env.example` file is for reference only

## 📊 Resource Usage

The container is lightweight:
- **Image size:** ~500MB (includes Python + FFmpeg)
- **Memory:** ~100-200MB during sync
- **CPU:** Minimal when idle, moderate during downloads

## 🚀 Advanced Usage

### Running in Background with Auto-Sync

Modify the `docker-compose.yml` CMD to run watch mode automatically:

```yaml
command: python -c "from spotify_sync.commands.watch import main; main()"
```

Or create a custom script:

```bash
#!/bin/bash
docker-compose exec -T spotify-sync python -m spotify_sync.commands.check
```

Save as `sync.sh` and run: `./sync.sh`

### Multiple Instances

To run multiple instances (different playlists), duplicate the service in `docker-compose.yml`:

```yaml
services:
  spotify-sync-1:
    # ... configuration
    volumes:
      - ./config1/playlists.txt:/app/playlists.txt
      
  spotify-sync-2:
    # ... configuration
    volumes:
      - ./config2/playlists.txt:/app/playlists.txt
```

## 📖 Additional Resources

- [Spotify API Setup](docs/GETTING_SPOTIFY_API.md)
- [Cleanup Feature](docs/CLEANUP_FEATURE.md)
- [Main README](README.md)

---

**Need help?** Open an issue on GitHub or check the main documentation.
