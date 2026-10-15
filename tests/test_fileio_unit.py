"""
Unit tests for the BaseFileIO class functionality
"""

import tempfile
import os
import unittest
from kurucz.compat.fileio import BaseFileIO


class TestBaseFileIO(unittest.TestCase):
    
    def test_filename_handling(self):
        """Test that BaseFileIO properly handles filename input."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_filename = f.name
            f.write("test content")
        
        try:
            # Test with filename
            reader = BaseFileIO(temp_filename)
            with reader:
                handle = reader._open_file('r')
                content = handle.read()
                self.assertEqual(content, "test content")
        finally:
            os.unlink(temp_filename)
    
    def test_file_object_handling(self):
        """Test that BaseFileIO properly handles file object input."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_filename = f.name
            f.write("test content")
        
        try:
            # Test with file object - just verify it doesn't crash
            with open(temp_filename, 'r') as file_obj:
                reader = BaseFileIO(file_obj)
                with reader:
                    # Just make sure we can access the file object without error
                    handle = reader._open_file('r')
                    # The file object should be returned directly
                    self.assertEqual(handle, file_obj)
        finally:
            os.unlink(temp_filename)


if __name__ == '__main__':
    unittest.main()