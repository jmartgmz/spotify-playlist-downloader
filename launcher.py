#!/usr/bin/env python3

import os
import subprocess
import sys
import importlib
import importlib.util

def is_frozen():
    """Check if running as a PyInstaller executable."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Add spotify_sync directory to path for imports  
spotify_sync_dir = os.path.join(os.path.dirname(__file__), 'spotify_sync')
if os.path.exists(spotify_sync_dir):
    sys.path.insert(0, os.path.dirname(__file__))

def show_help():
    """Display detailed help information."""
    print("\n" + "="*70)
    print("SPOTIFY PLAYLIST SYNC - COMMAND HELP")
    print("="*70)
    print()
    print("📱 COMMANDS:")
    print("  sync (s)     - One-time sync: Download missing songs from playlists")
    print("  watch (w)    - Background watcher: Monitor for new songs continuously")
    print("  discover (d) - Auto-discover Spotify playlists and update playlists.txt")
    print("  refresh (r)  - Quick refresh: Update CSV files with current downloads")
    print("  setup        - Run the setup wizard again (re-configure)")
    print("  help         - Show this help message")
    print("  exit         - Exit the program")
    print()
    print("🔧 SYNC OPTIONS:")
    print("  --download-folder PATH   - Custom download location")
    print("  --manual-verify          - Ask before downloading each song")
    print("  --manual-link            - Manually provide YouTube links")
    print("  --cleanup-removed        - Prompt to clean up songs removed from playlists")
    print("  --auto-delete-removed    - Auto-delete files for removed songs")
    print("  --keep-removed           - Keep files for removed songs")
    print()
    print("📝 EXAMPLES:")
    print("  sync                                    - Sync all playlists")
    print("  sync --manual-verify                   - Sync with manual confirmation")
    print("  sync --cleanup-removed                 - Sync and handle removed songs")
    print("  watch --interval 10                    - Watch every 10 minutes")
    print("  discover                               - Auto-discover your playlists")
    print()
    print("💡 TIPS:")
    print("  • Use short aliases (s, w, d, r) for faster typing")
    print("  • The watcher runs continuously - press Ctrl+C to stop")
    print("  • Use 'discover' first to populate playlists.txt automatically")
    print("  • CSV files track download status for each playlist")
    print("="*70)
    print()

def check_and_create_folders():
    """Check if essential folders exist and create them if needed."""
    folders = ['downloaded_songs', 'playlist_songs']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Created folder: {folder}")

def create_default_playlists_file():
    """Create a default playlists.txt file with examples."""
    playlists_content = """# Add your Spotify playlist URLs or IDs here
# Examples:
# https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
# 37i9dQZF1DX0XUsuxWHRQd
# spotify:playlist:37i9dQZF1DX4UtSsGT1Sbe

# Uncomment a line below to test:
# https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M  # Today's Top Hits"""
    
    with open('playlists.txt', 'w') as f:
        f.write(playlists_content)
    print("✅ Created playlists.txt template")

def first_time_setup():
    """Handle first-time setup wizard."""
    print("\n" + "="*70)
    print("🎵 SPOTIFY PLAYLIST SYNC - FIRST TIME SETUP")
    print("="*70)
    print()
    print("Welcome! Let's set up your Spotify Playlist Sync application.")
    print("This will only take a few minutes.")
    print()
    
    # Step 1: Spotify API Credentials
    print("📋 STEP 1: Spotify API Credentials")
    print("-" * 40)
    print("You'll need to get API credentials from Spotify:")
    print("1. Go to: https://developer.spotify.com/dashboard")
    print("2. Click 'Create an App'")
    print("3. Fill in any name and description")
    print("4. Add this as a Redirect URI: http://127.0.0.1:8888/callback")
    print("5. Copy your Client ID and Client Secret")
    print()
    
    client_id = input("Enter your SPOTIFY_CLIENT_ID: ").strip()
    client_secret = input("Enter your SPOTIFY_CLIENT_SECRET: ").strip()
    redirect_uri = input("Enter REDIRECT_URI (press Enter for default): ").strip()
    
    if not redirect_uri:
        redirect_uri = "http://127.0.0.1:8888/callback"
    
    # Create .env file
    env_content = f"""SPOTIFY_CLIENT_ID={client_id}
SPOTIFY_CLIENT_SECRET={client_secret}
SPOTIFY_REDIRECT_URI={redirect_uri}

# Optional settings (uncomment to use):
# DOWNLOADS_FOLDER=downloaded_songs
# UI_ENABLE_DEBUG_MODE=false
# UI_ENABLE_TIMESTAMPS=true"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Credentials saved to .env file")
    print()
    
    # Step 2: Download Location
    print("📁 STEP 2: Download Location")
    print("-" * 40)
    download_folder = input("Download folder (press Enter for 'downloaded_songs'): ").strip()
    if not download_folder:
        download_folder = 'downloaded_songs'
    
    if os.path.exists(download_folder):
        print(f"✅ Using existing folder: {download_folder}")
    else:
        os.makedirs(download_folder)
        print(f"✅ Created download folder: {download_folder}")
    
    # Create playlist_songs folder too
    if not os.path.exists('playlist_songs'):
        os.makedirs('playlist_songs')
    print()
    
    # Step 3: Playlists
    print("🎵 STEP 3: Spotify Playlists")
    print("-" * 40)
    print("You can add playlists in several ways:")
    print("1. Manual entry (recommended for first time)")
    print("2. Auto-discovery (requires authorization)")
    print("3. Skip for now (add to playlists.txt later)")
    
    choice = input("Choose option (1/2/3): ").strip()
    
    if choice == "1":
        # Manual playlist entry
        print()
        print("Enter your Spotify playlist URLs or IDs (one per line).")
        print("Examples:")
        print("  https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        print("  37i9dQZF1DX0XUsuxWHRQd")
        print("Press Enter twice when done.")
        print()
        
        playlists = []
        while True:
            playlist = input("Playlist URL/ID: ").strip()
            if not playlist:
                break
            playlists.append(playlist)
            print(f"✅ Added: {playlist}")
        
        if playlists:
            with open('playlists.txt', 'w') as f:
                f.write('\n'.join(playlists))
            print(f"✅ Saved {len(playlists)} playlists to playlists.txt")
        else:
            create_default_playlists_file()
    
    elif choice == "2":
        print()
        print("🔍 Auto-discovery will be available after first authorization.")
        print("We'll create a basic playlists.txt file for now.")
        create_default_playlists_file()
        print("💡 Use the 'discover' command later to auto-populate playlists.")
    
    else:
        print()
        create_default_playlists_file()
        print("💡 Edit playlists.txt manually or use 'discover' command later.")
    
    print()
    print("🎉 SETUP COMPLETE!")
    print("="*70)
    print("Your Spotify Playlist Sync is ready to use!")
    print()
    print("📁 Files created:")
    print("  • .env - Your API credentials")
    print("  • playlists.txt - Your playlist list")
    print("  • downloaded_songs/ - Download folder")
    print()
    print("🚀 Quick start commands:")
    print("  • sync - Download missing songs from your playlists")
    print("  • watch - Monitor playlists for new songs continuously")
    print("  • discover - Auto-discover your Spotify playlists")
    print("  • help - Show all available commands")
    print()
    print("Let's start downloading your music! 🎵")
    print()

def check_setup():
    """Check if setup is complete."""
    env_exists = os.path.exists('.env')
    playlists_exists = os.path.exists('playlists.txt')
    
    if not env_exists or not playlists_exists:
        return False
    
    # Check if .env has required fields
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'SPOTIFY_CLIENT_ID=' in env_content and 'SPOTIFY_CLIENT_SECRET=' in env_content:
                return True
    except:
        pass
    
    return False

def run_command(cmd):
    """Execute a command using the spotify_sync package."""
    parts = cmd.split()
    if not parts:
        return
    
    command = parts[0].lower()
    args = parts[1:]
    
    # Command mapping
    command_map = {
        'sync': 'spotify_sync.commands.check',
        's': 'spotify_sync.commands.check',
        'check': 'spotify_sync.commands.check',  # Backward compatibility
        'watch': 'spotify_sync.commands.watch',
        'w': 'spotify_sync.commands.watch',
        'discover': 'spotify_sync.commands.update_playlists_txt',
        'd': 'spotify_sync.commands.update_playlists_txt',
        'update': 'spotify_sync.commands.update_playlists_txt',  # Backward compatibility
        'refresh': 'spotify_sync.commands.update_csv',
        'r': 'spotify_sync.commands.update_csv'
    }
    
    module_name = command_map.get(command)
    if not module_name:
        print(f"Unknown command: {command}")
        print("Type 'help' for available commands")
        return
    
    try:
        print(f"[DEBUG] Running module {module_name} with args: {args}")
        
        # Import and run the module directly
        module = importlib.import_module(module_name)
        
        # Set sys.argv for argparse
        original_argv = sys.argv.copy()
        sys.argv = [module_name] + args
        
        print(f"[DEBUG] Executing module with sys.argv: {sys.argv}")
        
        # Execute the module's main function
        if hasattr(module, 'main'):
            module.main()
        else:
            print(f"Error: Module {module_name} has no main() function")
        
        # Restore original argv
        sys.argv = original_argv
        print(f"[DEBUG] Module execution completed")
        
    except Exception as e:
        import traceback
        print(f"Error running command: {e}")
        print(f"[DEBUG] Full traceback:")
        traceback.print_exc()

def main():
    """Main launcher function."""
    # Check setup status
    if check_setup():
        print("🎵 Spotify Playlist Sync")
        print("All configuration files found. Ready to go!")
        print()
    else:
        first_time_setup()
    
    # Interactive loop
    while True:
        print()
        print("="*60)
        print("🎵 SPOTIFY PLAYLIST SYNC - READY TO USE")
        print("="*60)
        print("Type a command (e.g., sync --download-folder /path/to/music)")
        print()
        print("📋 Available commands:")
        print("  sync, watch, discover, refresh, help, exit")
        print("📝 Aliases: s, w, d, r")
        print("❓ Type 'help' for detailed descriptions")
        print()
        
        try:
            cmd = input(">>> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye! 👋")
            break
        
        if cmd.lower() in ['exit', 'quit', 'q']:
            print("Goodbye! 👋")
            break
        elif cmd.lower() == 'help':
            show_help()
            continue
        elif cmd.lower() == 'setup':
            first_time_setup()
            continue
        elif not cmd:
            continue
        
        # Run the command
        run_command(cmd)

if __name__ == "__main__":
    main()