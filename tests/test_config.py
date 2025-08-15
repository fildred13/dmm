"""
Tests for configuration module
"""

import pytest
import os
from media_processor.config import (
    UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH,
    REGISTRY_FILE,
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    MAX_WIDTH,
    MAX_HEIGHT,
    VIDEO_CRF_MP4,
    VIDEO_CRF_WEBM,
    JPEG_QUALITY
)


class TestConfig:
    """Test configuration settings"""
    
    def test_upload_folder(self):
        """Test upload folder configuration"""
        assert UPLOAD_FOLDER == 'media'
        assert isinstance(UPLOAD_FOLDER, str)
    
    def test_max_content_length(self):
        """Test max content length configuration"""
        assert MAX_CONTENT_LENGTH == 100 * 1024 * 1024  # 100MB
        assert isinstance(MAX_CONTENT_LENGTH, int)
    
    def test_registry_file(self):
        """Test registry file configuration"""
        assert REGISTRY_FILE == 'media_registry.json'
        assert isinstance(REGISTRY_FILE, str)
    
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
        assert '.mp4' in SUPPORTED_OUTPUT_FORMATS
        assert '.png' in SUPPORTED_OUTPUT_FORMATS
        assert '.jpg' in SUPPORTED_OUTPUT_FORMATS
        # Note: .gif is no longer a supported output format
        # Animated GIFs become .webm, static GIFs become .png
    
    def test_max_dimensions(self):
        """Test maximum dimensions configuration"""
        assert MAX_WIDTH == 576
        assert MAX_HEIGHT == 1024
        assert isinstance(MAX_WIDTH, int)
        assert isinstance(MAX_HEIGHT, int)
    
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
