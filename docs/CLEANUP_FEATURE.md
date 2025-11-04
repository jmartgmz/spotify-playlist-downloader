# Cleanup Removed Songs Feature

## Overview
The cleanup feature helps you keep your downloaded music library in sync with your Spotify playlists by detecting songs that have been removed from playlists and providing options to clean up the corresponding files.

## How it works
1. **Detection**: The program compares the current playlist contents with the songs previously tracked in the CSV files
2. **Identification**: It identifies songs that were previously downloaded but are no longer in the playlist
3. **File matching**: It finds the actual downloaded files for these removed songs
4. **User choice**: It asks what you want to do with these files (unless you use auto options)

## Usage Options

### Interactive Cleanup (prompts for each playlist)
```bash
./run.sh sync --cleanup-removed
# or
run.bat sync --cleanup-removed
```

### Automatic Deletion (no prompts)
```bash
./run.sh sync --auto-delete-removed
# or  
run.bat sync --auto-delete-removed
```

### Keep Files (mark as kept, no deletion)
```bash
./run.sh sync --keep-removed
# or
run.bat sync --keep-removed
```

### Combined with other options
```bash
./run.sh sync --download-folder /path/to/music --cleanup-removed
```

## What happens when songs are found

### Interactive mode (--cleanup-removed)
- Shows list of removed songs
- Shows how many downloaded files were found
- Prompts for action:
  1. Delete the files (free up space)
  2. Keep the files (they'll remain in your download folder)
  3. Skip cleanup for now

### Automatic deletion (--auto-delete-removed)
- Automatically deletes all files for removed songs
- Shows summary of what was deleted

### Keep removed (--keep-removed)
- Marks removed songs as "kept after removal"
- Files remain in download folder
- No prompts

## Example Output

```
Checking for removed songs...
Found 3 song(s) that were removed from the playlist:
  1. The Beatles - Hey Jude
  2. Queen - Bohemian Rhapsody
  3. Led Zeppelin - Stairway to Heaven

Found 3 downloaded file(s) for these songs.

What would you like to do?
1. Delete the files (free up space)
2. Keep the files (they'll remain in your download folder)  
3. Skip cleanup for now
Enter your choice (1/2/3): 1

Deleted: The Beatles - Hey Jude.mp3
Deleted: Queen - Bohemian Rhapsody.mp3
Deleted: Led Zeppelin - Stairway to Heaven.mp3

Cleanup Summary
Removed Songs Found: 3
Files Deleted: 3
Files Kept: 0
```

## Notes
- Only songs that were previously marked as "downloaded" are considered for cleanup
- The feature uses fuzzy matching to find files that may have slightly different names
- CSV files are updated to reflect the cleanup actions taken
- This feature works with existing playlists and doesn't affect the main download functionality