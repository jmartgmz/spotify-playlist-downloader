"""
Logging utilities for consistent output formatting and progress tracking.
Provides color-coded messages, progress indicators, and timestamps.
"""

import sys
import time
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Message types with color codes."""
    INFO = "\033[94m"      # Blue
    SUCCESS = "\033[92m"   # Green
    WARNING = "\033[93m"   # Yellow
    ERROR = "\033[91m"     # Red
    RESET = "\033[0m"      # Reset color


class Logger:
    """Provides consistent logging with color support and timestamps."""
    
    ENABLE_COLORS = sys.stdout.isatty()  # Only use colors if terminal supports it
    ENABLE_TIMESTAMPS = True
    DEBUG_MODE = False
    _progress_start_time = None

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp string."""
        if not Logger.ENABLE_TIMESTAMPS:
            return ""
        return f"[{datetime.now().strftime('%H:%M:%S')}] "

    @staticmethod
    def _format_message(message_type: MessageType, message: str, prefix: str = "") -> str:
        """Format a message with color, prefix, and timestamp."""
        timestamp = Logger._get_timestamp()
        
        if not Logger.ENABLE_COLORS:
            return f"{timestamp}{prefix}{message}"
        
        color = message_type.value
        reset = MessageType.RESET.value
        return f"{timestamp}{color}{prefix}{message}{reset}"

    @staticmethod
    def info(message: str) -> None:
        """Log an info message."""
        print(Logger._format_message(MessageType.INFO, message, "ℹ "))

    @staticmethod
    def success(message: str) -> None:
        """Log a success message."""
        print(Logger._format_message(MessageType.SUCCESS, message, "✓ "))

    @staticmethod
    def warning(message: str) -> None:
        """Log a warning message."""
        print(Logger._format_message(MessageType.WARNING, message, "⚠ "))

    @staticmethod
    def error(message: str) -> None:
        """Log an error message."""
        print(Logger._format_message(MessageType.ERROR, message, "✗ "))

    @staticmethod
    def header(message: str) -> None:
        """Log a section header."""
        timestamp = Logger._get_timestamp()
        print(f"\n{'='*70}")
        print(Logger._format_message(MessageType.INFO, f"{message}", "🎵 "))
        print(f"{'='*70}\n")

    @staticmethod
    def progress(current: int, total: int, item_name: str = "", show_eta: bool = False) -> None:
        """Log progress with a detailed progress bar and optional ETA."""
        if total == 0:
            return
            
        percentage = (current / total * 100)
        bar_length = 30
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Format the progress line
        progress_text = f"[{bar}] {current}/{total} ({percentage:.1f}%)"
        
        if item_name:
            progress_text += f" - {item_name}"
        
        if show_eta and current > 0:
            # Simple ETA calculation based on current progress
            elapsed = time.time() - getattr(Logger, '_progress_start_time', time.time())
            if current > 0:
                eta_seconds = (elapsed / current) * (total - current)
                eta_minutes = int(eta_seconds // 60)
                eta_seconds = int(eta_seconds % 60)
                progress_text += f" - ETA: {eta_minutes:02d}:{eta_seconds:02d}"
        
        print(Logger._format_message(MessageType.INFO, progress_text, "📊 "))

    @staticmethod
    def start_progress(item_name: str = ""):
        """Mark the start of a progress operation for ETA calculation."""
        Logger._progress_start_time = time.time()
        if item_name:
            Logger.info(f"Starting {item_name}...")

    @staticmethod
    def section(message: str) -> None:
        """Log a section divider."""
        timestamp = Logger._get_timestamp()
        print(f"\n{timestamp}--- {message} ---")

    @staticmethod
    def summary(label: str, value: str, success: bool = True) -> None:
        """Log a summary line."""
        msg_type = MessageType.SUCCESS if success else MessageType.WARNING
        print(Logger._format_message(msg_type, f"{label}: {value}", "📈 " if success else "📉 "))

    @staticmethod
    def step(step_num: int, total_steps: int, description: str) -> None:
        """Log a step in a multi-step process."""
        print(Logger._format_message(
            MessageType.INFO, 
            f"Step {step_num}/{total_steps}: {description}", 
            "🔄 "
        ))

    @staticmethod
    def debug(message: str) -> None:
        """Log a debug message (only in debug mode)."""
        if getattr(Logger, 'DEBUG_MODE', False):
            print(Logger._format_message(MessageType.INFO, f"DEBUG: {message}", "🐛 "))

    @staticmethod
    def set_debug_mode(enabled: bool) -> None:
        """Enable or disable debug logging."""
        Logger.DEBUG_MODE = enabled

    @staticmethod
    def set_timestamps(enabled: bool) -> None:
        """Enable or disable timestamps."""
        Logger.ENABLE_TIMESTAMPS = enabled
