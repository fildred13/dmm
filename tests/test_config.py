"""
Tests for configuration module
"""

import pytest
import os
from media_processor.config import (
    MAX_CONTENT_LENGTH,
    DEFAULT_REGISTRY_FILE,
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    LANDSCAPE_TARGET_WIDTH,
    PORTRAIT_TARGET_HEIGHT,
    SQUARE_TARGET_SIZE,
    VIDEO_CRF_MP4,
    VIDEO_CRF_WEBM,
    JPEG_QUALITY,
    get_media_folder_from_registry,
    ensure_media_folder_exists
)


class TestConfig:
    """Test configuration settings"""
    
    def test_default_registry_file(self):
        """Test default registry file configuration"""
        assert DEFAULT_REGISTRY_FILE == 'media_registry.json'
        assert isinstance(DEFAULT_REGISTRY_FILE, str)
    
    def test_max_content_length(self):
        """Test max content length configuration"""
        assert MAX_CONTENT_LENGTH == 100 * 1024 * 1024  # 100MB
        assert isinstance(MAX_CONTENT_LENGTH, int)
    
    def test_registry_file(self):
        """Test registry file configuration"""
        assert DEFAULT_REGISTRY_FILE == 'media_registry.json'
        assert isinstance(DEFAULT_REGISTRY_FILE, str)
    
    def test_supported_input_formats(self):
        """Test supported input formats configuration"""
        assert isinstance(SUPPORTED_INPUT_FORMATS, dict)
        assert 'image' in SUPPORTED_INPUT_FORMATS
        assert 'video' in SUPPORTED_INPUT_FORMATS
        
        # Check image formats
        image_formats = SUPPORTED_INPUT_FORMATS['image']
        assert '.jpg' in image_formats
        assert '.png' in image_formats
        assert '.gif' in image_formats
        assert '.webp' in image_formats
        
        # Check video formats
        video_formats = SUPPORTED_INPUT_FORMATS['video']
        assert '.mp4' in video_formats
        assert '.avi' in video_formats
        assert '.webm' in video_formats
    
    def test_supported_output_formats(self):
        """Test supported output formats configuration"""
        assert isinstance(SUPPORTED_OUTPUT_FORMATS, list)
        assert '.webm' in SUPPORTED_OUTPUT_FORMATS
        assert '.mp4' not in SUPPORTED_OUTPUT_FORMATS  # MP4 no longer supported as output
        assert '.png' in SUPPORTED_OUTPUT_FORMATS
        assert '.jpg' in SUPPORTED_OUTPUT_FORMATS
        # Note: .gif is no longer a supported output format
        # Animated GIFs become .webm, static GIFs become .png
    
    def test_max_dimensions(self):
        """Test target dimensions configuration"""
        assert LANDSCAPE_TARGET_WIDTH == 1024
        assert PORTRAIT_TARGET_HEIGHT == 576
        assert SQUARE_TARGET_SIZE == 576
        assert isinstance(LANDSCAPE_TARGET_WIDTH, int)
        assert isinstance(PORTRAIT_TARGET_HEIGHT, int)
        assert isinstance(SQUARE_TARGET_SIZE, int)
    
    def test_video_quality_settings(self):
        """Test video quality settings"""
        assert VIDEO_CRF_MP4 == 23
        assert VIDEO_CRF_WEBM == 30
        assert isinstance(VIDEO_CRF_MP4, int)
        assert isinstance(VIDEO_CRF_WEBM, int)
    
    def test_jpeg_quality(self):
        """Test JPEG quality setting"""
        assert JPEG_QUALITY == 95
        assert isinstance(JPEG_QUALITY, int)
        assert 0 <= JPEG_QUALITY <= 100
    
    def test_get_media_folder_from_registry(self, temp_dir):
        """Test getting media folder from registry path"""
        registry_path = os.path.join(temp_dir, "test_registry.json")
        media_folder = get_media_folder_from_registry(registry_path)
        expected_folder = os.path.join(temp_dir, "media")
        assert media_folder == expected_folder
    
    def test_ensure_media_folder_exists(self, temp_dir):
        """Test ensuring media folder exists"""
        registry_path = os.path.join(temp_dir, "test_registry.json")
        media_folder = ensure_media_folder_exists(registry_path)
        expected_folder = os.path.join(temp_dir, "media")
        assert media_folder == expected_folder
        assert os.path.exists(media_folder)
        assert os.path.isdir(media_folder)
