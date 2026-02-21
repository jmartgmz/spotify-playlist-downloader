#!/usr/bin/env python3
"""
Spotify Playlist Sync - Interactive Launcher
Run once and type commands interactively.
"""

import warnings
# Suppress all third-party deprecation warnings before any imports
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import shlex
from datetime import datetime


# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    DIM = '\033[2m'
    PURPLE = '\033[35m'
    MAGENTA = '\033[95m'
    ORANGE = '\033[38;5;208m'


def print_banner():
    """Print welcome banner."""
    print(f"\n{Colors.CYAN}╭{'─' * 68}╮{Colors.RESET}")
    print(f"{Colors.CYAN}│{Colors.RESET}{Colors.BOLD}{Colors.GREEN}                      🎵 SPOTIFY PLAYLIST SYNC 🎵                     {Colors.RESET}{Colors.CYAN}│{Colors.RESET}")
    print(f"{Colors.CYAN}╰{'─' * 68}╯{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{Colors.UNDERLINE}AVAILABLE COMMANDS{Colors.RESET}\n")
    
    print(f"  {Colors.GREEN}▶ sync{Colors.RESET}     {Colors.DIM}(s){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Download missing songs from playlists")
    print(f"  {Colors.BLUE}▶ watch{Colors.RESET}    {Colors.DIM}(w){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Monitor playlists continuously")
    print(f"  {Colors.PURPLE}▶ discover{Colors.RESET} {Colors.DIM}(d){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Auto-discover your Spotify playlists")
    print(f"  {Colors.CYAN}▶ refresh{Colors.RESET}  {Colors.DIM}(r){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Update CSV files with current downloads")
    print(f"  {Colors.MAGENTA}▶ sanitize{Colors.RESET} {Colors.DIM}(z){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Clean up extra spaces in downloaded filenames")
    print(f"  {Colors.ORANGE}▶ flac{Colors.RESET}     {Colors.DIM}(f){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Upgrade existing MP3s to FLAC")
    print(f"  {Colors.DIM}▶ manual{Colors.RESET}   {Colors.DIM}(m){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Manually provide YouTube links for missing songs")
    print(f"  {Colors.YELLOW}▶ help{Colors.RESET}     {Colors.DIM}(h){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Show detailed help")
    print(f"  {Colors.RED}▶ quit{Colors.RESET}     {Colors.DIM}(q){Colors.RESET}  {Colors.DIM}│{Colors.RESET} Exit launcher")
    
    print(f"\n{Colors.CYAN}{'━' * 70}{Colors.RESET}\n")


def print_help():
    """Print help message."""
    print(f"\n{Colors.CYAN}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}  📚  Command Reference  📚{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Commands:{Colors.RESET}")
    print(f"  {Colors.GREEN}sync{Colors.RESET}, {Colors.DIM}s{Colors.RESET}       Download missing songs from playlists")
    print(f"  {Colors.BLUE}watch{Colors.RESET}, {Colors.DIM}w{Colors.RESET}      Monitor playlists continuously for new songs")
    print(f"  {Colors.PURPLE}discover{Colors.RESET}, {Colors.DIM}d{Colors.RESET}   Auto-discover your Spotify playlists")
    print(f"  {Colors.CYAN}refresh{Colors.RESET}, {Colors.DIM}r{Colors.RESET}    Update CSV files with current downloads")
    print(f"  {Colors.MAGENTA}sanitize{Colors.RESET}, {Colors.DIM}z{Colors.RESET}   Clean up extra spaces in downloaded filenames")
    print(f"  {Colors.ORANGE}flac{Colors.RESET}, {Colors.DIM}f{Colors.RESET}       Upgrade existing MP3s to FLAC")
    print(f"  {Colors.DIM}manual{Colors.RESET}, {Colors.DIM}m{Colors.RESET}     Manually provide YouTube links for each missing song")
    print(f"  {Colors.YELLOW}help{Colors.RESET}, {Colors.DIM}h{Colors.RESET}       Show this help message")
    print(f"  {Colors.RED}quit{Colors.RESET}, {Colors.DIM}q, exit{Colors.RESET} Exit the launcher")
    
    print(f"\n{Colors.BOLD}Sync Options:{Colors.RESET}")
    print(f"  {Colors.DIM}--download-folder PATH{Colors.RESET}    Save downloads to custom location")
    print(f"  {Colors.DIM}--dont-filter-results{Colors.RESET}     Disable result filtering")
    
    print(f"\n{Colors.BOLD}Watch Options:{Colors.RESET}")
    print(f"  {Colors.DIM}--interval N{Colors.RESET}              Check interval in minutes (default: 10)")
    
    print(f"\n{Colors.BOLD}Note:{Colors.RESET}")
    print(f"  {Colors.GREEN}✓ Automatic cleanup enabled{Colors.RESET} - Downloads stay in perfect sync with Spotify")
    print(f"  {Colors.DIM}Songs removed from playlists are automatically deleted locally{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Examples:{Colors.RESET}")
    print(f"  {Colors.GREEN}sync{Colors.RESET}")
    print(f"  {Colors.GREEN}sync{Colors.RESET} {Colors.DIM}--download-folder C:\\Music{Colors.RESET}")
    print(f"  {Colors.BLUE}watch{Colors.RESET} {Colors.DIM}--interval 5{Colors.RESET}")
    print(f"  {Colors.PURPLE}discover{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}\n")


def execute_command(command_line):
    """Execute a command from the interactive prompt."""
    try:
        # Parse the command line
        parts = shlex.split(command_line)
        if not parts:
            return True
        
        command = parts[0].lower()
        args = parts[1:]
        
        # Handle special commands
        if command in ['quit', 'q', 'exit']:
            return False
        
        if command in ['help', 'h', '?']:
            print_help()
            return True
        
        # Map command aliases
        command_map = {
            'sync': 'sync',
            's': 'sync',
            'manual': 'manual',
            'm': 'manual',
            'watch': 'watch',
            'w': 'watch',
            'discover': 'discover',
            'd': 'discover',
            'refresh': 'refresh',
            'r': 'refresh',
            'sanitize': 'sanitize',
            'z': 'sanitize',
            'flac': 'flac',
            'f': 'flac',
        }
        
        if command not in command_map:
            print(f"{Colors.RED}❌ Unknown command:{Colors.RESET} {command}")
            print(f"{Colors.DIM}Type 'help' for available commands.{Colors.RESET}\n")
            return True
        
        module_name = command_map[command]
        
        # Show what we're doing
        timestamp = datetime.now().strftime("%H:%M:%S")
        cmd_display = command_line
        print(f"\n{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.BOLD}Running:{Colors.RESET} {Colors.CYAN}{cmd_display}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")
        
        # Import and run the appropriate command
        if module_name == 'sync':
            from spotisyncer.commands.sync import main as cmd_main
        elif module_name == 'manual':
            from spotisyncer.commands.sync import main as cmd_main
            args.append('--manual')
        elif module_name == 'watch':
            from spotisyncer.commands.watch import main as cmd_main
        elif module_name == 'discover':
            from spotisyncer.commands.discover import main as cmd_main
        elif module_name == 'refresh':
            from spotisyncer.commands.refresh import main as cmd_main
        elif module_name == 'sanitize':
            from spotisyncer.commands.sanitize import main as cmd_main
        elif module_name == 'flac':
            from spotisyncer.commands.flac import main as cmd_main
        
        # Replace sys.argv for the command
        sys.argv = ['launcher.py'] + args
        
        # Run the command
        cmd_main()
        
        # Success footer
        print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")
        print(f"{Colors.GREEN}✓ Command completed{Colors.RESET} {Colors.DIM}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Command cancelled{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error:{Colors.RESET} {e}\n")
    
    return True


def main():
    """Main interactive launcher."""
    print_banner()
    
    try:
        while True:
            try:
                # Colored prompt
                prompt = f"{Colors.BOLD}{Colors.PURPLE}spotify-sync{Colors.RESET}{Colors.CYAN}>{Colors.RESET} "
                command_line = input(prompt).strip()
                
                if not command_line:
                    continue
                
                # Execute the command
                if not execute_command(command_line):
                    print(f"\n{Colors.GREEN}👋 Thanks for using Spotify Playlist Sync!{Colors.RESET}\n")
                    break
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}💡 Tip: Use 'quit' to exit gracefully{Colors.RESET}\n")
                continue
            except EOFError:
                print(f"\n\n{Colors.GREEN}👋 Goodbye!{Colors.RESET}\n")
                break
                
    except Exception as e:
        print(f"\n{Colors.RED}❌ Launcher error:{Colors.RESET} {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
