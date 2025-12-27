# Cleanup Feature

## Overview
The cleanup feature automatically keeps your downloaded music library in sync with your Spotify playlists. It runs automatically during sync and watch operations, removing files for songs that were deleted from playlists and cleaning up orphaned files that were never properly tracked.

## How it works

### Two Types of Cleanup

1. **Removed Songs**: Songs that were in the playlist and downloaded but are no longer in the Spotify playlist
   - The program compares current playlist contents with previously tracked songs in CSV
   - Automatically deletes files for removed songs
   - Updates CSV to reflect the removal

2. **Orphaned Files**: Audio files in the download folder that were never tracked in the CSV
   - Scans all audio files in playlist folders
   - Compares with CSV entries using fuzzy matching
   - Automatically deletes untracked files
   - Examples: manually copied files, failed CSV writes, corrupted tracking

## Usage

### Automatic Cleanup (Default)
The cleanup feature runs automatically when you use either `sync` or `watch` commands:

```bash
# Run via launcher
python launcher.py
> sync

# Or directly
python -m spotify_sync.commands.check
```

Both commands will:
- Download missing songs
- Delete files for songs removed from Spotify
- Delete orphaned files not tracked in CSV
- Maintain 1:1 sync with Spotify playlists

### Watch Mode
Continuous monitoring with automatic cleanup:

```bash
# Run via launcher
python launcher.py
> watch

# Or directly  
python -m spotify_sync.commands.watch
```

Watch mode checks every 5 minutes and automatically:
- Downloads new songs
- Removes deleted songs
- Cleans up orphaned files

## Example Output

```
Processing: spotify:playlist:37i9dQZF1DXcBWIGoYBM5M

Checking for removed songs...
Found 2 song(s) that were removed from the playlist
Found 2 downloaded file(s) for removal
Deleted: The Beatles - Hey Jude.mp3
Deleted: Queen - Bohemian Rhapsody.mp3
Cleaned up 2 removed song(s)

Found 1 orphaned file(s) not tracked in CSV
Deleted orphaned: Led Zeppelin - Stairway to Heaven.mp3
Cleaned up 1 orphaned file(s)

Cleanup Summary
Removed Songs Found: 2
Files Deleted: 2
Orphaned Files Found: 1
Orphaned Files Deleted: 1
```

## Technical Details

### Fuzzy Matching
The orphaned file detection uses fuzzy matching to handle:
- Special characters (`/`, `\`, `:`, `|`, `?`, `*`, `"`, `<`, `>`)
- Extra whitespace
- Different file naming conventions

### CSV Tracking
- Removed songs: status is already 'downloaded' in CSV
- Orphaned files: not in CSV at all
- CSV is updated after cleanup to reflect changes

## Notes
- Cleanup runs automatically - no flags needed
- Only affects files in playlist-specific folders
- Maintains true 1:1 sync with Spotify
- Uses fuzzy matching to handle filename variations
- Safe operation - only removes files for confirmed removed/orphaned songs