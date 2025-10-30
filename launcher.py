
import os
import subprocess
import sys
import importlib.util
from launcher_utils import is_frozen

# Add src directory to path for imports
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if os.path.exists(src_dir):
    sys.path.insert(0, src_dir)

def prompt_env():
    print("Enter your Spotify API credentials:")
    client_id = input("SPOTIFY_CLIENT_ID: ").strip()
    client_secret = input("SPOTIFY_CLIENT_SECRET: ").strip()
    redirect_uri = input("SPOTIFY_REDIRECT_URI (default: http://127.0.0.1:8888/callback): ").strip() or "http://127.0.0.1:8888/callback"

    with open(".env", "w") as f:
        f.write(f"SPOTIFY_CLIENT_ID={client_id}\n")
        f.write(f"SPOTIFY_CLIENT_SECRET={client_secret}\n")
        f.write(f"SPOTIFY_REDIRECT_URI={redirect_uri}\n")
    print("✓ .env file created/updated.")

def main():

    if not os.path.exists(".env"):
        prompt_env()
    else:
        print(".env file already exists. Edit it if you want to change credentials.")


    playlist = None
    if is_frozen():
        playlist = input("Enter Spotify playlist URL or ID (leave blank to use playlists.txt): ").strip()
        if playlist:
            # Write playlist to playlists.txt in the exe directory
            exe_dir = os.path.dirname(sys.executable)
            playlists_txt_path = os.path.join(exe_dir, "playlists.txt")
            with open(playlists_txt_path, "w", encoding="utf-8") as f:
                f.write(playlist + "\n")
            print(f"✓ playlists.txt created at {playlists_txt_path}")

    print("\nType a command (e.g., check --download-folder C:\\Users\\...\\Music)")
    print("Available commands: check, watch, update, update-csv, exit\n")

    while True:
        try:
            cmd = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if cmd.lower() in ("exit", "quit"):
            break
        if not cmd:
            continue
        if is_frozen():
            # Directly import and call the script functions when running as an exe
            parts = cmd.split()
            if not parts:
                continue
            command = parts[0].lower()
            args = parts[1:]
            
            try:
                script_map = {
                    "check": "check.py",
                    "watch": "watch.py",
                    "update": "update_playlists_txt.py",
                    "update-csv": "update_csv.py"
                }
                
                script_name = script_map.get(command)
                if not script_name:
                    print(f"Unknown command: {command}")
                    continue
                
                # Find the script file
                script_path = os.path.join(src_dir, script_name)
                print(f"[DEBUG] Looking for script at: {script_path}")
                
                if not os.path.exists(script_path):
                    print(f"Error: Script {script_name} not found at {script_path}")
                    print(f"[DEBUG] src_dir is: {src_dir}")
                    print(f"[DEBUG] Contents of src_dir: {os.listdir(src_dir) if os.path.exists(src_dir) else 'DIR NOT FOUND'}")
                    continue
                
                # Load the module dynamically
                module_name = script_name.replace(".py", "")
                print(f"[DEBUG] Loading module: {module_name} from {script_path}")
                
                spec = importlib.util.spec_from_file_location(module_name, script_path)
                if spec is None or spec.loader is None:
                    print(f"Error: Could not load {script_name}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                
                # Set sys.argv for argparse
                sys.argv = [module_name] + args
                if playlist:
                    sys.argv.append(playlist)
                
                print(f"[DEBUG] Executing module with sys.argv: {sys.argv}")
                # Execute the module
                spec.loader.exec_module(module)
                print(f"[DEBUG] Module execution completed")
                
            except Exception as e:
                import traceback
                print(f"Error running command: {e}")
                print(f"[DEBUG] Full traceback:")
                traceback.print_exc()
        else:
            # Use run.bat for normal (non-frozen) usage
            full_cmd = ["cmd", "/c", "run.bat"] + cmd.split()
            subprocess.call(full_cmd)

if __name__ == "__main__":
    main()
