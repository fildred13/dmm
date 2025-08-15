"""
Tests for file utilities module
"""

import pytest
import os
from media_processor.file_utils import FileUtils


class TestFileUtils:
    """Test file utility functions"""
    
    def test_get_file_type_image(self, temp_dir):
        """Test file type detection for images"""
        # Create a static GIF for testing
        from PIL import Image
        import numpy as np
        
        static_gif_path = os.path.join(temp_dir, "static.gif")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(static_gif_path)
        
        assert FileUtils.get_file_type("test.jpg") == "image"
        assert FileUtils.get_file_type("test.png") == "image"
        assert FileUtils.get_file_type("test.gif", static_gif_path) == "image"  # Static GIF
        assert FileUtils.get_file_type("test.webp") == "image"
        assert FileUtils.get_file_type("test.bmp") == "image"
        assert FileUtils.get_file_type("test.tiff") == "image"
    
    def test_get_file_type_webp_files(self, temp_dir):
        """Test file type detection for WebP files"""
        # Create a static WebP for testing
        from PIL import Image
        import numpy as np
        
        static_webp_path = os.path.join(temp_dir, "static.webp")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(static_webp_path)
        
        # Create an animated WebP for testing (simulated)
        animated_webp_path = os.path.join(temp_dir, "animated.webp")
        img.save(animated_webp_path)
        
        # Test static WebP (should be detected as image)
        assert FileUtils.get_file_type("test.webp", static_webp_path) == "image"
        
        # Test animated WebP (should be detected as video)
        # We need to mock the is_animated_webp function for this test
        with pytest.MonkeyPatch().context() as m:
            m.setattr(FileUtils, 'is_animated_webp', lambda x: True)
            assert FileUtils.get_file_type("test.webp", animated_webp_path) == "video"
    
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
    
    def test_get_output_format_gif_files(self, temp_dir):
        """Test output format for GIF files"""
        # Create a static GIF for testing
        from PIL import Image
        import numpy as np
        
        static_gif_path = os.path.join(temp_dir, "static.gif")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(static_gif_path)
        
        # Create an animated GIF for testing (simulated)
        animated_gif_path = os.path.join(temp_dir, "animated.gif")
        # For testing, we'll create a simple GIF and mock it as animated
        img.save(animated_gif_path)
        
        # Test static GIF (should become PNG)
        assert FileUtils.get_output_format("test.gif", "image", static_gif_path) == ".png"
        
        # Test animated GIF (should become WEBM)
        # We need to mock the is_animated_gif function for this test
        with pytest.MonkeyPatch().context() as m:
            m.setattr(FileUtils, 'is_animated_gif', lambda x: True)
            assert FileUtils.get_output_format("test.gif", "video", animated_gif_path) == ".webm"
    
    def test_is_animated_gif_static(self, temp_dir):
        """Test animated GIF detection for static GIFs"""
        from PIL import Image
        import numpy as np
        
        static_gif_path = os.path.join(temp_dir, "static.gif")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(static_gif_path)
        
        assert FileUtils.is_animated_gif(static_gif_path) is False
    
    def test_get_output_format_webp_files(self, temp_dir):
        """Test output format for WebP files"""
        # Create a static WebP for testing
        from PIL import Image
        import numpy as np
        
        static_webp_path = os.path.join(temp_dir, "static.webp")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(static_webp_path)
        
        # Create an animated WebP for testing (simulated)
        animated_webp_path = os.path.join(temp_dir, "animated.webp")
        # For testing, we'll create a simple WebP and mock it as animated
        img.save(animated_webp_path)
        
        # Test static WebP (should become PNG)
        assert FileUtils.get_output_format("test.webp", "image", static_webp_path) == ".png"
        
        # Test animated WebP (should become WEBM)
        # We need to mock the is_animated_webp function for this test
        with pytest.MonkeyPatch().context() as m:
            m.setattr(FileUtils, 'is_animated_webp', lambda x: True)
            assert FileUtils.get_output_format("test.webp", "video", animated_webp_path) == ".webm"
    
    def test_is_animated_webp_static(self, temp_dir):
        """Test animated WebP detection for static WebPs"""
        from PIL import Image
        import numpy as np
        
        static_webp_path = os.path.join(temp_dir, "static.webp")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(static_webp_path)
        
        assert FileUtils.is_animated_webp(static_webp_path) is False
    
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
