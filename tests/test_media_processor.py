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
        """Test processor initialization with default upload folder"""
        processor = MediaProcessor()
        assert processor.upload_folder == 'media'
    
    def test_init_custom_folder(self, temp_dir):
        """Test processor initialization with custom upload folder"""
        custom_folder = os.path.join(temp_dir, "custom_media")
        processor = MediaProcessor(custom_folder)
        assert processor.upload_folder == custom_folder
    
    def test_process_media_file_image_success(self, temp_dir):
        """Test successful image processing"""
        # Create test image
        input_path = os.path.join(temp_dir, "test.jpg")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create upload folder
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        processor = MediaProcessor(upload_folder)
        relative_path, error = processor.process_media_file(input_path)
        
        assert error is None
        # Use normalized path comparison
        expected_path = f"{upload_folder}/test.jpg".replace('\\', '/')
        assert relative_path == expected_path
        assert os.path.exists(os.path.join(temp_dir, "media", "test.jpg"))
    
    def test_process_media_file_image_format_conversion(self, temp_dir):
        """Test image processing with format conversion"""
        # Create test image in unsupported format
        input_path = os.path.join(temp_dir, "test.bmp")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create upload folder
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        processor = MediaProcessor(upload_folder)
        relative_path, error = processor.process_media_file(input_path)
        
        assert error is None
        # Use normalized path comparison
        expected_path = f"{upload_folder}/test.png".replace('\\', '/')
        assert relative_path == expected_path  # Should convert to PNG
        assert os.path.exists(os.path.join(temp_dir, "media", "test.png"))
    
    def test_process_media_file_static_gif_success(self, temp_dir):
        """Test successful static GIF processing (should become PNG)"""
        # Create test static GIF
        input_path = os.path.join(temp_dir, "test.gif")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create upload folder
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        processor = MediaProcessor(upload_folder)
        relative_path, error = processor.process_media_file(input_path)
        
        assert error is None
        # Use normalized path comparison
        expected_path = f"{upload_folder}/test.png".replace('\\', '/')
        assert relative_path == expected_path  # Should convert to PNG
        assert os.path.exists(os.path.join(temp_dir, "media", "test.png"))
    
    def test_process_media_file_animated_gif_success(self, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test successful animated GIF processing (should become WEBM)"""
        # Create test animated GIF (simulated)
        input_path = os.path.join(temp_dir, "test.gif")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Create upload folder
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        # Mock the animated GIF detection
        from media_processor.file_utils import FileUtils
        with pytest.MonkeyPatch().context() as m:
            m.setattr(FileUtils, 'is_animated_gif', lambda x: True)
            
            processor = MediaProcessor(upload_folder)
            relative_path, error = processor.process_media_file(input_path)
            
            assert error is None
            # Use normalized path comparison
            expected_path = f"{upload_folder}/test.webm".replace('\\', '/')
            assert relative_path == expected_path  # Should convert to WEBM
            # Note: We don't check if the file exists because we're mocking FFmpeg
    
    def test_process_media_file_video_success(self, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test successful video processing"""
        # Create test video file
        input_path = os.path.join(temp_dir, "test.avi")
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        # Create upload folder
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        processor = MediaProcessor(upload_folder)
        relative_path, error = processor.process_media_file(input_path)
        
        assert error is None
        # Use normalized path comparison
        expected_path = f"{upload_folder}/test.mp4".replace('\\', '/')
        assert relative_path == expected_path  # Should convert to MP4
        # Note: We don't check if the file exists because we're mocking FFmpeg
    
    def test_process_media_file_unsupported_format(self, temp_dir):
        """Test processing unsupported file format"""
        # Create unsupported file
        input_path = os.path.join(temp_dir, "test.txt")
        with open(input_path, 'w') as f:
            f.write("text content")
        
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        processor = MediaProcessor(upload_folder)
        relative_path, error = processor.process_media_file(input_path)
        
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
        
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        processor = MediaProcessor(upload_folder)
        relative_path, error = processor.process_media_file(input_path)
        
        assert relative_path is None
        assert "Failed to process video" in error
    
    def test_process_media_file_image_failure(self, temp_dir):
        """Test image processing failure"""
        # Create corrupted image file
        input_path = os.path.join(temp_dir, "test.jpg")
        with open(input_path, 'w') as f:
            f.write("not an image")
        
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        processor = MediaProcessor(upload_folder)
        relative_path, error = processor.process_media_file(input_path)
        
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
        
        # Create upload folder
        upload_folder = os.path.join(temp_dir, "media")
        os.makedirs(upload_folder, exist_ok=True)
        
        processor = MediaProcessor(upload_folder)
        relative_path, error = processor.process_media_file(input_path)
        
        assert error is None
        # Should use forward slashes regardless of OS
        assert "\\" not in relative_path
        assert "/" in relative_path
