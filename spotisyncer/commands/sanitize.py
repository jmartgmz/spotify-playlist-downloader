#!/usr/bin/env python3
"""
Global sanization command.
Iterates over all playlist folders and downloaded audio files,
and cleans up any extra spaces or invalid characters in their filenames.

Usage:
    python sanitize.py --download-folder "/path/to/folder"
"""

import warnings
warnings.simplefilter('ignore')
warnings.filterwarnings('ignore')

import os
import argparse
from spotify_sync.utils.utils import FilenameSanitizer
from spotify_sync.core.logger import Logger
from spotify_sync.utils.error_handler import ErrorHandler
from spotify_sync.core.settings_manager import settings, Config

def main():
    """Main entry point for directory sanitization."""
    parser = argparse.ArgumentParser(description="Sanitize downloaded filenames")
    parser.add_argument("--download-folder", default=Config.get_downloads_folder(), help="Folder where songs are downloaded")
    
    args = parser.parse_args()
    
    try:
        ErrorHandler.validate_folder(args.download_folder)
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "Invalid download folder")
        return

    Logger.header("Filename Sanitization")
    Logger.set_debug_mode(settings.is_debug_mode())
    Logger.set_timestamps(settings.get('ui', 'enable_timestamps'))

    Logger.info(f"Scanning downloads in: {args.download_folder}")
    
    total_files = 0
    renamed_files = 0
    failed_files = 0

    try:
        # Iterate over folder structure looking for audio files
        for root, dirs, files in os.walk(args.download_folder):
            for filename in files:
                if not filename.lower().endswith(('.flac', '.mp3', '.ogg', '.m4a', '.wav')):
                    continue
                    
                total_files += 1
                old_path = os.path.join(root, filename)
                new_name = FilenameSanitizer.clean_extra_spaces(filename)
                
                if new_name != filename:
                    new_path = os.path.join(root, new_name)
                    
                    # Handle potential collisions if an intentionally named file exists
                    if os.path.exists(new_path):
                        try:
                            os.remove(new_path)
                        except Exception as e:
                            Logger.warning(f"Could not remove existing file {new_name}: {e}")
                            failed_files += 1
                            continue
                            
                    try:
                        os.rename(old_path, new_path)
                        Logger.success(f"Renamed: '{filename}' -> '{new_name}'")
                        renamed_files += 1
                    except Exception as e:
                        Logger.error(f"Failed to rename {filename}: {e}")
                        failed_files += 1
                        
    except Exception as e:
        ErrorHandler.handle_fatal_exception(e, "An error occurred during sanitization")
        return

    Logger.header("Sanitization Summary")
    Logger.summary("Total Audio Files Scanned", str(total_files))
    Logger.summary("Files Renamed", str(renamed_files))
    if failed_files > 0:
        Logger.summary("Failed to Rename", str(failed_files))

if __name__ == "__main__":
    main()
