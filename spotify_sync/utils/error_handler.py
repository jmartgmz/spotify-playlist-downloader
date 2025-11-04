"""
Error handling and validation utilities.
Provides consistent error reporting and input validation.
"""

import os
from typing import Optional
from spotify_sync.core.logger import Logger


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class FileOperationError(Exception):
    """Raised when file operations fail."""
    pass


class DownloadError(Exception):
    """Raised when download operations fail."""
    pass


class SpotifyError(Exception):
    """Raised when Spotify API operations fail."""
    pass


class ErrorHandler:
    """Handles errors consistently across the application."""

    @staticmethod
    def validate_folder(folder_path: str, create: bool = True) -> bool:
        """
        Validate that a folder exists or can be created.
        
        Args:
            folder_path: Path to validate
            create: Whether to create folder if it doesn't exist
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If folder is invalid
        """
        try:
            if not os.path.exists(folder_path):
                if create:
                    os.makedirs(folder_path, exist_ok=True)
                    return True
                else:
                    raise ValidationError(f"Folder not found: {folder_path}")
            elif not os.path.isdir(folder_path):
                raise ValidationError(f"Path is not a folder: {folder_path}")
            return True
        except Exception as e:
            raise ValidationError(f"Folder validation failed: {e}")

    @staticmethod
    def validate_file(file_path: str, must_exist: bool = True) -> bool:
        """
        Validate that a file exists.
        
        Args:
            file_path: Path to validate
            must_exist: Whether file must exist
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If file is invalid
        """
        try:
            if must_exist and not os.path.exists(file_path):
                raise ValidationError(f"File not found: {file_path}")
            elif os.path.exists(file_path) and not os.path.isfile(file_path):
                raise ValidationError(f"Path is not a file: {file_path}")
            return True
        except Exception as e:
            raise ValidationError(f"File validation failed: {e}")

    @staticmethod
    def handle_exception(exception: Exception, context: str = "") -> None:
        """
        Handle an exception with appropriate logging.
        
        Args:
            exception: Exception to handle
            context: Context where exception occurred
        """
        error_msg = str(exception)
        if context:
            error_msg = f"{context}: {error_msg}"
        
        Logger.error(error_msg)

    @staticmethod
    def handle_fatal_exception(exception: Exception, context: str = "") -> None:
        """
        Handle a fatal exception and exit.
        
        Args:
            exception: Exception to handle
            context: Context where exception occurred
        """
        ErrorHandler.handle_exception(exception, context)
        raise SystemExit(1)
