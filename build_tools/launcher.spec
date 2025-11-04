# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all spotify_sync submodules
spotify_sync_imports = collect_submodules('spotify_sync')

# Collect data files for spotify_sync
spotify_sync_datas = collect_data_files('spotify_sync')

# Additional hidden imports for dependencies
hidden_imports = [
    # Core dependencies
    'spotipy', 'spotipy.oauth2', 'spotipy.client', 'spotipy.cache_handler',
    'spotdl', 'spotdl.download', 'spotdl.search', 'spotdl.utils',
    'yt_dlp', 'yt_dlp.extractor', 'yt_dlp.downloader',
    'mutagen', 'mutagen.mp3', 'mutagen.easyid3', 'mutagen.id3',
    'python_dotenv', 'dotenv',
    'requests', 'urllib3', 'certifi',
    
    # Package modules
    'spotify_sync',
    'spotify_sync.core',
    'spotify_sync.core.settings_manager',
    'spotify_sync.core.logger', 
    'spotify_sync.core.spotify_api',
    'spotify_sync.core.downloader',
    'spotify_sync.core.file_manager',
    'spotify_sync.core.csv_manager',
    'spotify_sync.core.cleanup_manager',
    'spotify_sync.commands',
    'spotify_sync.commands.check',
    'spotify_sync.commands.watch',
    'spotify_sync.commands.update_csv',
    'spotify_sync.commands.update_playlists_txt',
    'spotify_sync.utils',
    'spotify_sync.utils.utils',
    'spotify_sync.utils.error_handler',
    'spotify_sync.utils.config',
    
    # Additional dependencies that might be missed
    'pkg_resources', 'packaging', 'setuptools',
    'json', 'csv', 'os', 'sys', 'subprocess', 'time',
] + spotify_sync_imports

a = Analysis(
    ['../launcher.py'],
    pathex=['..'],  # Add parent directory to path
    binaries=[],
    datas=[
        ('../spotify_sync', 'spotify_sync'),  # Include the package
        ('../config', 'config'),  # Include config files if they exist
    ] + spotify_sync_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy'],  # Exclude unused heavy packages
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SpotifyPlaylistSync',  # Better name for the executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here if you have one
)
