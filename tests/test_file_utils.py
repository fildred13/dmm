"""
Tests for file utilities module
"""

import pytest
from media_processor.file_utils import FileUtils


class TestFileUtils:
    """Test file utility functions"""
    
    def test_get_file_type_image(self):
        """Test file type detection for images"""
        assert FileUtils.get_file_type("test.jpg") == "image"
        assert FileUtils.get_file_type("test.png") == "image"
        assert FileUtils.get_file_type("test.gif") == "image"
        assert FileUtils.get_file_type("test.webp") == "image"
        assert FileUtils.get_file_type("test.bmp") == "image"
        assert FileUtils.get_file_type("test.tiff") == "image"
    
    def test_get_file_type_video(self):
        """Test file type detection for videos"""
        assert FileUtils.get_file_type("test.mp4") == "video"
        assert FileUtils.get_file_type("test.avi") == "video"
        assert FileUtils.get_file_type("test.mov") == "video"
        assert FileUtils.get_file_type("test.webm") == "video"
        assert FileUtils.get_file_type("test.mkv") == "video"
        assert FileUtils.get_file_type("test.flv") == "video"
        assert FileUtils.get_file_type("test.wmv") == "video"
    
    def test_get_file_type_unsupported(self):
        """Test file type detection for unsupported formats"""
        assert FileUtils.get_file_type("test.txt") is None
        assert FileUtils.get_file_type("test.pdf") is None
        assert FileUtils.get_file_type("test.doc") is None
        assert FileUtils.get_file_type("test") is None
        assert FileUtils.get_file_type("") is None
    
    def test_get_file_type_case_insensitive(self):
        """Test file type detection is case insensitive"""
        assert FileUtils.get_file_type("test.JPG") == "image"
        assert FileUtils.get_file_type("test.PNG") == "image"
        assert FileUtils.get_file_type("test.MP4") == "video"
        assert FileUtils.get_file_type("test.AVI") == "video"
    
    def test_is_supported_format(self):
        """Test supported format checking"""
        assert FileUtils.is_supported_format("test.jpg") is True
        assert FileUtils.is_supported_format("test.mp4") is True
        assert FileUtils.is_supported_format("test.txt") is False
        assert FileUtils.is_supported_format("test") is False
    
    def test_get_output_format_supported_input(self):
        """Test output format for already supported formats"""
        assert FileUtils.get_output_format("test.jpg", "image") == ".jpg"
        assert FileUtils.get_output_format("test.png", "image") == ".png"
        assert FileUtils.get_output_format("test.mp4", "video") == ".mp4"
        assert FileUtils.get_output_format("test.webm", "video") == ".webm"
    
    def test_get_output_format_unsupported_input(self):
        """Test output format for unsupported input formats"""
        assert FileUtils.get_output_format("test.bmp", "image") == ".png"
        assert FileUtils.get_output_format("test.tiff", "image") == ".png"
        assert FileUtils.get_output_format("test.avi", "video") == ".mp4"
        assert FileUtils.get_output_format("test.mov", "video") == ".mp4"
    
    def test_create_output_filename(self):
        """Test output filename creation"""
        assert FileUtils.create_output_filename("test.jpg", ".png") == "test.png"
        assert FileUtils.create_output_filename("image.bmp", ".jpg") == "image.jpg"
        assert FileUtils.create_output_filename("video.avi", ".mp4") == "video.mp4"
        assert FileUtils.create_output_filename("file", ".png") == "file.png"
    
    def test_normalize_path(self):
        """Test path normalization"""
        # Test Windows backslashes
        assert FileUtils.normalize_path("media\\test.jpg") == "media/test.jpg"
        assert FileUtils.normalize_path("folder\\subfolder\\file.png") == "folder/subfolder/file.png"
        
        # Test already normalized paths
        assert FileUtils.normalize_path("media/test.jpg") == "media/test.jpg"
        assert FileUtils.normalize_path("folder/subfolder/file.png") == "folder/subfolder/file.png"
        
        # Test mixed slashes
        assert FileUtils.normalize_path("media\\test.jpg") == "media/test.jpg"
        assert FileUtils.normalize_path("folder/subfolder\\file.png") == "folder/subfolder/file.png"
    
    def test_get_file_info(self, temp_dir):
        """Test file info extraction"""
        import os
        
        # Create a test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        name, ext, size = FileUtils.get_file_info(test_file)
        
        assert name == "test.txt"
        assert ext == ".txt"
        assert size > 0
        assert isinstance(size, int)
    
    def test_format_file_size(self):
        """Test file size formatting"""
        assert FileUtils.format_file_size(0) == "0 Bytes"
        assert FileUtils.format_file_size(1024) == "1.0 KB"
        assert FileUtils.format_file_size(1024 * 1024) == "1.0 MB"
        assert FileUtils.format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        
        # Test intermediate values
        assert "KB" in FileUtils.format_file_size(1500)
        assert "MB" in FileUtils.format_file_size(1500000)
        assert "GB" in FileUtils.format_file_size(1500000000)
