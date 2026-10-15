"""
Base classes for file readers and writers.
"""

import io
from typing import Union, TextIO, BinaryIO
from contextlib import contextmanager


class BaseFileIO:
    """
    Base class for file readers and writers that handles file management properly.
    
    This class can accept either a filename (str) or an open file object.
    File opening is lazy - only opened when needed and closed when explicitly
    closed or when exiting a 'with' context.
    
    When an open file object is passed, it will not be closed when the object
    goes out of scope or exits a 'with' context.
    """
    
    def __init__(self, file_source: Union[str, TextIO, BinaryIO]):
        """
        Initialize the base class with a filename or open file object.
        
        Args:
            file_source: Either a filename (str) or an open file object
        """
        self._file_source = file_source
        self._file_handle = None
        self._is_file_opened = False
        # Check if it's a file object by checking if it has file-like attributes
        self._is_file_object = hasattr(file_source, 'read') or hasattr(file_source, 'write')
    
    def _open_file(self, mode: str = 'r'):
        """
        Open the file lazily if needed.
        
        Args:
            mode: File mode to open with ('r', 'w', etc.)
            
        Returns:
            The file handle
        """
        if self._file_handle is not None:
            return self._file_handle
            
        if self._is_file_object:
            # If it's already a file object, use it directly
            self._file_handle = self._file_source
        else:
            # If it's a filename, open it
            self._file_handle = open(self._file_source, mode)
            self._is_file_opened = True
            
        return self._file_handle
    
    def _close_file(self):
        """
        Close the file if it was opened by this class.
        """
        if self._file_handle is not None and self._is_file_opened:
            self._file_handle.close()
            self._file_handle = None
            self._is_file_opened = False
    
    def __enter__(self):
        """Enter the runtime context for 'with' statement."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context for 'with' statement."""
        self._close_file()
    
    @contextmanager
    def _get_file_handle(self, mode: str = 'r'):
        """
        Context manager to get a file handle.
        
        Args:
            mode: File mode to open with
            
        Yields:
            File handle
        """
        file_handle = self._open_file(mode)
        try:
            yield file_handle
        finally:
            # Don't close if it was passed in as a file object
            if not self._is_file_object and self._is_file_opened:
                self._close_file()