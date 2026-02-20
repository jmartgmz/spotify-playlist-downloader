import re
from unittest.mock import patch, MagicMock
from spotify_sync.core.cleanup_manager import CleanupManager

# Let's test simplify function on Japanese characters
def simplify(text: str) -> str:
    return re.sub(r'[\W_]+', '', str(text).lower()) if text else ""

s1 = "ASIAN KUNG-FU GENERATION - リライト"
s2 = "リライト"
print("simplify s1:", simplify(s1))
print("simplify s2:", simplify(s2))

# Also testing the loop that failed
tracked_songs = {('asian kung-fu generation', 'リライト'), ('', 'リライト')}

file_title = "リライト"
file_artist = "ASIAN KUNG-FU GENERATION"

simp_file_title = simplify(file_title)
simp_file_artist = simplify(file_artist)

simp_tracked_songs = {(simplify(a), simplify(t)) for a, t in tracked_songs}

is_tracked = (simp_file_artist, simp_file_title) in simp_tracked_songs
print("exact match:", is_tracked)

if not is_tracked:
    is_tracked = ('', simp_file_title) in simp_tracked_songs
print("title-only match:", is_tracked)

if not is_tracked:
    is_tracked = any(tracked_title and (tracked_title in simp_file_title or simp_file_title in tracked_title)
                    for _, tracked_title in simp_tracked_songs if tracked_title)
print("partial title match:", is_tracked)
