import sys

def is_frozen():
    """Return True if running as a PyInstaller bundle (.exe)."""
    return getattr(sys, 'frozen', False)
