// Dashboard state
let watchRunning = false;
let logEventSource = null;
let logs = []; // Store logs in memory

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Restore state FIRST before anything else
    restoreState();
    
    loadStats();
    loadPlaylists();
    checkWatchStatus();
    connectLogStream();
    
    // Refresh stats every 30 seconds
    setInterval(loadStats, 30000);
    
    // Check watch status every 5 seconds
    setInterval(checkWatchStatus, 5000);
    
    // Save state periodically
    setInterval(saveState, 2000);
    
    // Save interval on change
    document.getElementById('watch-interval').addEventListener('change', function() {
        localStorage.setItem('watchInterval', this.value);
    });
    
    // Save download folder on change
    document.getElementById('download-folder').addEventListener('change', function() {
        const folder = this.value.trim();
        if (folder) {
            localStorage.setItem('downloadFolder', folder);
        } else {
            localStorage.removeItem('downloadFolder');
        }
    });
});

// Restore state from localStorage
function restoreState() {
    // Restore check interval
    const savedInterval = localStorage.getItem('watchInterval');
    if (savedInterval) {
        document.getElementById('watch-interval').value = savedInterval;
    }
    
    // Restore download folder
    const savedFolder = localStorage.getItem('downloadFolder');
    if (savedFolder) {
        document.getElementById('download-folder').value = savedFolder;
    }
    
    // Restore logs
    const savedLogs = localStorage.getItem('activityLogs');
    if (savedLogs) {
        try {
            logs = JSON.parse(savedLogs);
            const logsDiv = document.getElementById('logs');
            logs.forEach(log => {
                const entry = createLogEntry(log);
                logsDiv.appendChild(entry);
            });
            logsDiv.scrollTop = logsDiv.scrollHeight;
        } catch (e) {
            console.error('Error restoring logs:', e);
        }
    }
}

// Save state to localStorage
function saveState() {
    // Save logs (keep last 200)
    const logsToSave = logs.slice(-200);
    localStorage.setItem('activityLogs', JSON.stringify(logsToSave));
    
    // Save download folder
    const downloadFolder = document.getElementById('download-folder').value;
    if (downloadFolder) {
        localStorage.setItem('downloadFolder', downloadFolder);
    }
}

// Get download folder (returns value or null for default)
function getDownloadFolder() {
    const folder = document.getElementById('download-folder').value.trim();
    return folder || null; // Return null if empty to use default
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('total-playlists').textContent = data.total_playlists;
        document.getElementById('total-tracks').textContent = data.total_tracks;
        document.getElementById('total-downloaded').textContent = data.total_downloaded;
        document.getElementById('total-missing').textContent = data.total_missing;
        
        if (data.last_sync) {
            document.getElementById('last-sync').textContent = data.last_sync;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load playlists
async function loadPlaylists() {
    const listDiv = document.getElementById('playlists-list');
    
    try {
        const response = await fetch('/api/playlists');
        const playlists = await response.json();
        
        if (playlists.length === 0) {
            listDiv.innerHTML = '<div class="loading">No playlists found</div>';
            return;
        }
        
        listDiv.innerHTML = playlists.map(playlist => `
            <div class="playlist-item" onclick="togglePlaylistDetails('${playlist.id}')">
                <div class="playlist-header">
                    <div class="playlist-name">
                        <span class="expand-icon" id="expand-${playlist.id}">▶</span>
                        ${escapeHtml(playlist.name)}
                    </div>
                    <div class="playlist-stats">
                        <span>📀 ${playlist.tracks} tracks</span>
                        <span>✅ ${playlist.downloaded} downloaded</span>
                        <span>⏳ ${playlist.missing} missing</span>
                    </div>
                </div>
                <div class="playlist-details" id="details-${playlist.id}" style="display: none;">
                    <div class="loading">Loading tracks...</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading playlists:', error);
        listDiv.innerHTML = '<div class="loading">Error loading playlists</div>';
    }
}

// Toggle playlist details view
async function togglePlaylistDetails(playlistId) {
    const detailsDiv = document.getElementById(`details-${playlistId}`);
    const expandIcon = document.getElementById(`expand-${playlistId}`);
    
    // If already open, close it
    if (detailsDiv.style.display === 'block') {
        detailsDiv.style.display = 'none';
        expandIcon.textContent = '▶';
        return;
    }
    
    // Open and load details
    detailsDiv.style.display = 'block';
    expandIcon.textContent = '▼';
    
    // Load track details if not already loaded
    if (detailsDiv.innerHTML.includes('Loading tracks')) {
        try {
            const response = await fetch(`/api/playlist/${encodeURIComponent(playlistId)}/details`);
            const data = await response.json();
            
            if (data.tracks && data.tracks.length > 0) {
                detailsDiv.innerHTML = `
                    <div class="tracks-table">
                        <div class="tracks-header">
                            <span class="track-artist">Artist</span>
                            <span class="track-title">Title</span>
                            <span class="track-status">Status</span>
                            <span class="track-size">Size</span>
                        </div>
                        ${data.tracks.map(track => `
                            <div class="track-row ${track.status}">
                                <span class="track-artist">${escapeHtml(track.artist)}</span>
                                <span class="track-title">${escapeHtml(track.title)}</span>
                                <span class="track-status status-${track.status}">
                                    ${track.status === 'downloaded' ? '✅' : track.status === 'missing' ? '⏳' : '❌'}
                                    ${track.status}
                                </span>
                                <span class="track-size">
                                    ${track.file_info && track.file_info.exists ? track.file_info.size_mb + ' MB' : '-'}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                detailsDiv.innerHTML = '<div class="loading">No tracks found</div>';
            }
        } catch (error) {
            console.error('Error loading playlist details:', error);
            detailsDiv.innerHTML = '<div class="loading">Error loading tracks</div>';
        }
    }
}

// Connect to log stream
function connectLogStream() {
    if (logEventSource) {
        logEventSource.close();
    }
    
    logEventSource = new EventSource('/api/logs');
    
    logEventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (!data.keepalive) {
            addLogEntry(data);
        }
    };
    
    logEventSource.onerror = function(error) {
        console.error('Log stream error:', error);
        setTimeout(connectLogStream, 5000);
    };
}

// Add log entry
function addLogEntry(log) {
    const logsDiv = document.getElementById('logs');
    const entry = createLogEntry(log);
    
    logsDiv.appendChild(entry);
    logsDiv.scrollTop = logsDiv.scrollHeight;
    
    // Store in memory
    logs.push(log);
    
    // Keep only last 200 entries in DOM and memory
    while (logsDiv.children.length > 200) {
        logsDiv.removeChild(logsDiv.firstChild);
    }
    while (logs.length > 200) {
        logs.shift();
    }
    
    // Save immediately to localStorage
    saveState();
}

// Create log entry element
function createLogEntry(log) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${log.level}`;
    entry.innerHTML = `
        <span class="log-timestamp">[${log.timestamp}]</span>
        <span class="log-message">${escapeHtml(log.message)}</span>
    `;
    return entry;
}

// Clear logs
function clearLogs() {
    document.getElementById('logs').innerHTML = '';
    logs = [];
    localStorage.removeItem('activityLogs');
}

// Sync playlists
async function syncPlaylists() {
    const btn = event.target.closest('.btn');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-icon">⏳</span> Syncing...';
    
    try {
        const downloadFolder = getDownloadFolder();
        const body = downloadFolder ? { download_folder: downloadFolder } : {};
        
        const response = await fetch('/api/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        const result = await response.json();
        
        if (result.success) {
            await loadStats();
            await loadPlaylists();
        }
    } catch (error) {
        console.error('Sync error:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// Discover playlists
async function discoverPlaylists() {
    const btn = event.target.closest('.btn');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-icon">⏳</span> Discovering...';
    
    try {
        const response = await fetch('/api/discover', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            await loadPlaylists();
        }
    } catch (error) {
        console.error('Discover error:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// Start watch mode
async function startWatch() {
    const interval = document.getElementById('watch-interval').value;
    
    try {
        const response = await fetch('/api/watch/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ interval: parseInt(interval) })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateWatchUI(true);
        }
    } catch (error) {
        console.error('Error starting watch:', error);
    }
}

// Stop watch mode
async function stopWatch() {
    try {
        const response = await fetch('/api/watch/stop', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateWatchUI(false);
        }
    } catch (error) {
        console.error('Error stopping watch:', error);
    }
}

// Check watch status
async function checkWatchStatus() {
    try {
        const response = await fetch('/api/watch/status');
        const data = await response.json();
        
        if (data.running !== watchRunning) {
            watchRunning = data.running;
            updateWatchUI(watchRunning);
        }
    } catch (error) {
        console.error('Error checking watch status:', error);
    }
}

// Update watch UI
function updateWatchUI(running) {
    watchRunning = running;
    
    const indicator = document.getElementById('watch-indicator');
    const statusText = document.getElementById('watch-status-text');
    const startBtn = document.getElementById('start-watch-btn');
    const stopBtn = document.getElementById('stop-watch-btn');
    const intervalInput = document.getElementById('watch-interval');
    
    if (running) {
        indicator.classList.add('running');
        statusText.textContent = 'Watch Mode: Running';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'flex';
        intervalInput.disabled = true;
    } else {
        indicator.classList.remove('running');
        statusText.textContent = 'Watch Mode: Stopped';
        startBtn.style.display = 'flex';
        stopBtn.style.display = 'none';
        intervalInput.disabled = false;
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
