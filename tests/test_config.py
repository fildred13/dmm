"""
Tests for configuration module
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from config import (
    get_last_registry_path,
    save_last_registry_path,
    get_media_folder_from_registry,
    get_tag_registry_path,
    ensure_media_folder_exists,
    DEFAULT_REGISTRY_FILE,
    CONFIG_FILE
)
from media_processor.config import (
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    LANDSCAPE_TARGET_WIDTH,
    PORTRAIT_TARGET_HEIGHT,
    SQUARE_TARGET_SIZE
)
from media_processor.file_utils import FileUtils


class TestConfig:
    """Test configuration constants and functions"""
    
    def test_supported_input_formats(self):
        """Test supported input formats"""
        assert 'image' in SUPPORTED_INPUT_FORMATS
        assert 'video' in SUPPORTED_INPUT_FORMATS
        assert '.jpg' in SUPPORTED_INPUT_FORMATS['image']
        assert '.mp4' in SUPPORTED_INPUT_FORMATS['video']
    
    def test_supported_output_formats(self):
        """Test supported output formats"""
        assert '.webm' in SUPPORTED_OUTPUT_FORMATS
        assert '.png' in SUPPORTED_OUTPUT_FORMATS
        assert '.jpg' in SUPPORTED_OUTPUT_FORMATS
        assert '.gif' not in SUPPORTED_OUTPUT_FORMATS  # GIF removed from output formats
    
    def test_dimension_constants(self):
        """Test dimension constants"""
        assert LANDSCAPE_TARGET_WIDTH == 1024
        assert PORTRAIT_TARGET_HEIGHT == 576
        assert SQUARE_TARGET_SIZE == 576


class TestCalculateDimensions:
    """Test dimension calculation function"""
    
    def test_calculate_dimensions_landscape(self):
        """Test landscape dimension calculation"""
        width, height = FileUtils.calculate_dimensions(2000, 1000)
        assert width == LANDSCAPE_TARGET_WIDTH  # 1024
        assert height == 512  # 1024 / 2
    
    def test_calculate_dimensions_portrait(self):
        """Test portrait dimension calculation"""
        width, height = FileUtils.calculate_dimensions(1000, 2000)
        assert height == PORTRAIT_TARGET_HEIGHT  # 576
        assert width == 288  # 576 / 2
    
    def test_calculate_dimensions_square(self):
        """Test square dimension calculation"""
        width, height = FileUtils.calculate_dimensions(1000, 1000)
        assert width == SQUARE_TARGET_SIZE  # 576
        assert height == SQUARE_TARGET_SIZE  # 576
    
    def test_calculate_dimensions_with_even_ensurance(self):
        """Test dimension calculation with even number enforcement"""
        width, height = FileUtils.calculate_dimensions(1001, 1001)
        assert width % 2 == 0
        assert height % 2 == 0
    
    def test_calculate_dimensions_invalid_input(self):
        """Test dimension calculation with invalid input"""
        width, height = FileUtils.calculate_dimensions(0, 0)
        assert width == SQUARE_TARGET_SIZE
        assert height == SQUARE_TARGET_SIZE
        
        width, height = FileUtils.calculate_dimensions(-100, 100)
        assert width == SQUARE_TARGET_SIZE
        assert height == SQUARE_TARGET_SIZE


class TestMediaFolderFunctions:
    """Test media folder utility functions"""
    
    def test_get_media_folder_from_registry(self):
        """Test getting media folder from registry path"""
        registry_path = "/path/to/registry.json"
        media_folder = get_media_folder_from_registry(registry_path)
        # Use os.path.normpath to handle cross-platform path differences
        expected_folder = os.path.normpath("/path/to/media")
        actual_folder = os.path.normpath(media_folder)
        assert actual_folder == expected_folder
    
    def test_get_tag_registry_path(self):
        """Test getting tag registry path from media registry path"""
        media_registry_path = "/path/to/media_registry.json"
        tag_registry_path = get_tag_registry_path(media_registry_path)
        expected_path = os.path.normpath("/path/to/tag_registry.json")
        actual_path = os.path.normpath(tag_registry_path)
        assert actual_path == expected_path
    
    def test_ensure_media_folder_exists(self, temp_dir):
        """Test ensuring media folder exists"""
        registry_path = os.path.join(temp_dir, "test_registry.json")
        media_folder = ensure_media_folder_exists(registry_path)
        
        assert os.path.exists(media_folder)
        assert media_folder == os.path.join(temp_dir, "media")


class TestPersistentRegistryPath:
    """Test persistent registry path functionality"""
    
    def test_get_last_registry_path_no_config_file(self):
        """Test getting last registry path when config file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            result = get_last_registry_path()
            assert result == DEFAULT_REGISTRY_FILE
    
    def test_get_last_registry_path_valid_config(self):
        """Test getting last registry path from valid config file"""
        config_data = {'last_registry_path': '/test/path/registry.json'}
        
        # Mock os.path.exists to return True for config file and the registry file
        def mock_exists(path):
            return path == CONFIG_FILE or path == '/test/path/registry.json'
        
        with patch('os.path.exists', side_effect=mock_exists), \
             patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            
            result = get_last_registry_path()
            assert result == '/test/path/registry.json'
    
    def test_get_last_registry_path_missing_key(self):
        """Test getting last registry path when config file has no registry path"""
        config_data = {'other_key': 'value'}
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            
            result = get_last_registry_path()
            assert result == DEFAULT_REGISTRY_FILE
    
    def test_get_last_registry_path_nonexistent_registry(self):
        """Test getting last registry path when saved registry doesn't exist"""
        config_data = {'last_registry_path': '/nonexistent/registry.json'}
        
        def mock_exists(path):
            return path == CONFIG_FILE  # Only config file exists, not the registry
        
        with patch('os.path.exists', side_effect=mock_exists), \
             patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            
            result = get_last_registry_path()
            assert result == DEFAULT_REGISTRY_FILE
    
    def test_get_last_registry_path_corrupted_config(self):
        """Test getting last registry path when config file is corrupted"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='invalid json')):
            
            result = get_last_registry_path()
            assert result == DEFAULT_REGISTRY_FILE
    
    def test_save_last_registry_path_success(self):
        """Test successfully saving registry path"""
        registry_path = '/test/path/registry.json'
        
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            result = save_last_registry_path(registry_path)
            
            assert result is True
            mock_file.assert_called_once_with(CONFIG_FILE, 'w')
            
            # Verify the correct JSON was written
            written_calls = mock_file().write.call_args_list
            written_data = ''.join(call[0][0] for call in written_calls)
            expected_data = json.dumps({'last_registry_path': registry_path}, indent=2)
            assert written_data == expected_data
    
    def test_save_last_registry_path_failure(self):
        """Test saving registry path when file write fails"""
        registry_path = '/test/path/registry.json'
        
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            result = save_last_registry_path(registry_path)
            assert result is False
    
    def test_save_last_registry_path_invalid_path(self):
        """Test saving registry path with invalid path that can't be JSON encoded"""
        # This is a bit contrived, but tests the JSON encoding error handling
        with patch('json.dump', side_effect=TypeError("Object not serializable")):
            result = save_last_registry_path("test")
            assert result is False
