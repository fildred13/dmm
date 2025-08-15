"""
Tests for main media processor module
"""

import pytest
import os
from PIL import Image
import numpy as np
from media_processor.media_processor import MediaProcessor


class TestMediaProcessor:
    """Test main media processor functionality"""
    
    def test_init_default(self):
        """Test processor initialization with default registry"""
        processor = MediaProcessor()
        assert 'media' in processor.upload_folder
    
    def test_init_custom_registry(self, temp_dir):
        """Test processor initialization with custom registry"""
        custom_registry = os.path.join(temp_dir, "custom_registry.json")
        processor = MediaProcessor(custom_registry)
        expected_media_folder = os.path.join(temp_dir, "media")
        assert processor.upload_folder == expected_media_folder
    
    def test_process_media_file_image_success(self, temp_dir):
        """Test successful image processing"""
        # Create test image
        input_path = os.path.join(temp_dir, "test.jpg")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create registry file
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        processor = MediaProcessor(registry_file)
        relative_path, error = processor.process_media_file(input_path, None)
        
        assert error is None
        # Use normalized path comparison
        expected_path = "media/test.jpg"
        assert relative_path == expected_path
        assert os.path.exists(os.path.join(temp_dir, "media", "test.jpg"))
    
    def test_process_media_file_image_format_conversion(self, temp_dir):
        """Test image processing with format conversion"""
        # Create test image in unsupported format
        input_path = os.path.join(temp_dir, "test.bmp")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create registry file
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        processor = MediaProcessor(registry_file)
        relative_path, error = processor.process_media_file(input_path, None)
        
        assert error is None
        # Use normalized path comparison
        expected_path = "media/test.png"
        assert relative_path == expected_path  # Should convert to PNG
        assert os.path.exists(os.path.join(temp_dir, "media", "test.png"))
    
    def test_process_media_file_static_gif_success(self, temp_dir):
        """Test successful static GIF processing (should become PNG)"""
        # Create test static GIF
        input_path = os.path.join(temp_dir, "test.gif")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create registry file
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        processor = MediaProcessor(registry_file)
        relative_path, error = processor.process_media_file(input_path, None)
        
        assert error is None
        # Use normalized path comparison
        expected_path = "media/test.png"
        assert relative_path == expected_path  # Should convert to PNG
        assert os.path.exists(os.path.join(temp_dir, "media", "test.png"))
    
    def test_process_media_file_animated_gif_success(self, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test successful animated GIF processing (should become WEBM)"""
        # Create test animated GIF (simulated)
        input_path = os.path.join(temp_dir, "test.gif")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create registry file
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        # Mock the animated GIF detection
        from media_processor.file_utils import FileUtils
        with pytest.MonkeyPatch().context() as m:
            m.setattr(FileUtils, 'is_animated_gif', lambda x: True)
            
            processor = MediaProcessor(registry_file)
            relative_path, error = processor.process_media_file(input_path, None)
            
            assert error is None
            # Use normalized path comparison
            expected_path = "media/test.webm"
            assert relative_path == expected_path  # Should convert to WEBM
            # Note: We don't check if the file exists because we're mocking FFmpeg
    
    def test_process_media_file_animated_webp_success(self, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test successful animated WebP processing (should become WEBM)"""
        # Create test animated WebP (simulated)
        input_path = os.path.join(temp_dir, "test.webp")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create registry file
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        # Mock the animated WebP detection and Wand conversion
        from media_processor.file_utils import FileUtils
        from media_processor.video_processor import VideoProcessor
        with pytest.MonkeyPatch().context() as m:
            m.setattr(FileUtils, 'is_animated_webp', lambda x: True)
            # Mock the Wand conversion to return success
            m.setattr(VideoProcessor, 'convert_webp_to_webm', lambda x, y: True)
            
            processor = MediaProcessor(registry_file)
            relative_path, error = processor.process_media_file(input_path, None)
            
            assert error is None
            # Use normalized path comparison
            expected_path = "media/test.webm"
            assert relative_path == expected_path  # Should convert to WEBM
            # Note: We don't check if the file exists because we're mocking FFmpeg
    
    def test_process_media_file_static_webp_success(self, temp_dir):
        """Test successful static WebP processing (should become PNG)"""
        # Create test static WebP
        input_path = os.path.join(temp_dir, "test.webp")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create registry file
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        # Mock the static WebP detection (both animation methods return False)
        from media_processor.file_utils import FileUtils
        with pytest.MonkeyPatch().context() as m:
            m.setattr(FileUtils, 'is_animated_webp', lambda x: False)
            
            processor = MediaProcessor(registry_file)
            relative_path, error = processor.process_media_file(input_path, None)
            
            assert error is None
            # Use normalized path comparison
            expected_path = "media/test.png"
            assert relative_path == expected_path  # Should convert to PNG
            assert os.path.exists(os.path.join(temp_dir, "media", "test.png"))
    
    def test_process_media_file_video_success(self, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test successful video processing"""
        # Create test video file
        input_path = os.path.join(temp_dir, "test.avi")
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        # Create registry file
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        processor = MediaProcessor(registry_file)
        relative_path, error = processor.process_media_file(input_path, None)
        
        assert error is None
        # Use normalized path comparison
        expected_path = "media/test.webm"
        assert relative_path == expected_path  # Should convert to WebM
        # Note: We don't check if the file exists because we're mocking FFmpeg
    
    def test_process_media_file_unsupported_format(self, temp_dir):
        """Test processing unsupported file format"""
        # Create unsupported file
        input_path = os.path.join(temp_dir, "test.txt")
        with open(input_path, 'w') as f:
            f.write("text content")
        
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        processor = MediaProcessor(registry_file)
        relative_path, error = processor.process_media_file(input_path, None)
        
        assert relative_path is None
        assert error == "Unsupported file type"
    
    def test_process_media_file_video_failure(self, temp_dir, mock_ffmpeg_probe):
        """Test video processing failure"""
        # Mock ffmpeg.probe to raise an exception
        mock_ffmpeg_probe.side_effect = Exception("FFmpeg error")
        
        # Create test video file
        input_path = os.path.join(temp_dir, "test.avi")
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        processor = MediaProcessor(registry_file)
        relative_path, error = processor.process_media_file(input_path, None)
        
        assert relative_path is None
        assert "Failed to process video" in error
    
    def test_process_media_file_image_failure(self, temp_dir):
        """Test image processing failure"""
        # Create corrupted image file
        input_path = os.path.join(temp_dir, "test.jpg")
        with open(input_path, 'w') as f:
            f.write("not an image")
        
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        processor = MediaProcessor(registry_file)
        relative_path, error = processor.process_media_file(input_path, None)
        
        assert relative_path is None
        assert error is not None
    
    def test_get_processing_info_image(self, temp_dir):
        """Test getting processing info for image"""
        # Create test image
        input_path = os.path.join(temp_dir, "test.jpg")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        processor = MediaProcessor()
        info = processor.get_processing_info(input_path)
        
        assert info['filename'] == "test.jpg"
        assert info['file_type'] == "image"
        assert 'original_size' in info
        assert info['width'] == 150
        assert info['height'] == 100
        assert info['mode'] == 'RGB'
        assert info['format'] == 'JPEG'
    
    def test_get_processing_info_video(self, temp_dir, mock_ffmpeg_probe):
        """Test getting processing info for video"""
        # Create test video file
        input_path = os.path.join(temp_dir, "test.mp4")
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        processor = MediaProcessor()
        info = processor.get_processing_info(input_path)
        
        assert info['filename'] == "test.mp4"
        assert info['file_type'] == "video"
        assert 'original_size' in info
        assert info['width'] == 1920
        assert info['height'] == 1080
        assert info['duration'] == 10.5
        assert info['video_codec'] == 'h264'
        assert info['audio_codec'] == 'aac'
        assert info['bitrate'] == 1000000
    
    def test_get_processing_info_unsupported(self, temp_dir):
        """Test getting processing info for unsupported file"""
        # Create unsupported file
        input_path = os.path.join(temp_dir, "test.txt")
        with open(input_path, 'w') as f:
            f.write("text content")
        
        processor = MediaProcessor()
        info = processor.get_processing_info(input_path)
        
        assert info['error'] == 'Unsupported file type'
    
    def test_path_normalization(self, temp_dir):
        """Test that paths are normalized to forward slashes"""
        # Create test image
        input_path = os.path.join(temp_dir, "test.jpg")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create registry file
        registry_file = os.path.join(temp_dir, "test_registry.json")
        
        processor = MediaProcessor(registry_file)
        relative_path, error = processor.process_media_file(input_path, None)
        
        assert error is None
        # Should use forward slashes regardless of OS
        assert "\\" not in relative_path
        assert "/" in relative_path
