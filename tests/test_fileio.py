"""
Test file I/O base class functionality
"""

import tempfile
import os
from kurucz.compat.fileio import BaseFileIO


def test_base_file_io():
    """Test the base file I/O class functionality."""
    
    # Test with filename
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_filename = f.name
        f.write("test content")
    
    try:
        # Test with filename
        reader = BaseFileIO(temp_filename)
        with reader:
            handle = reader._open_file('r')
            content = handle.read()
            assert content == "test content"
            
        # Test that file was closed properly
        # (We can't directly test this, but we can make sure it doesn't crash)
        
    finally:
        os.unlink(temp_filename)
    
    # Test with file object
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_filename = f.name
        f.write("test content")
    
    try:
        with open(temp_filename, 'r') as file_obj:
            reader = BaseFileIO(file_obj)
            with reader:
                # Should use the file object directly
                handle = reader._open_file('r')
                content = handle.read()
                assert content == "test content"
                
    finally:
        os.unlink(temp_filename)


if __name__ == "__main__":
    test_base_file_io()
    print("All tests passed!")