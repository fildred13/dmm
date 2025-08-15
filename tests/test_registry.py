"""
Tests for registry module
"""

import pytest
import os
import json
from media_processor.registry import MediaRegistry


class TestMediaRegistry:
    """Test media registry functionality"""
    
    def test_init_default(self):
        """Test registry initialization with default file"""
        registry = MediaRegistry()
        assert registry.registry_file == 'media_registry.json'
    
    def test_init_custom_file(self, temp_dir):
        """Test registry initialization with custom file"""
        custom_file = os.path.join(temp_dir, "custom_registry.json")
        registry = MediaRegistry(custom_file)
        assert registry.registry_file == custom_file
    
    def test_load_empty_file(self, temp_dir):
        """Test loading from non-existent file"""
        registry_file = os.path.join(temp_dir, "nonexistent.json")
        registry = MediaRegistry(registry_file)
        result = registry.load()
        assert result == []
    
    def test_load_existing_file(self, sample_registry_file):
        """Test loading from existing file"""
        registry = MediaRegistry(sample_registry_file)
        result = registry.load()
        assert len(result) == 3
        assert result[0]["path"] == "media/test1.png"
        assert result[1]["path"] == "media/test2.mp4"
        assert result[2]["path"] == "media/test3.jpg"
    
    def test_load_invalid_json(self, temp_dir):
        """Test loading invalid JSON file"""
        registry_file = os.path.join(temp_dir, "invalid.json")
        with open(registry_file, 'w') as f:
            f.write("invalid json content")
        
        registry = MediaRegistry(registry_file)
        result = registry.load()
        assert result == []
    
    def test_save_success(self, temp_dir):
        """Test successful save operation"""
        registry_file = os.path.join(temp_dir, "test_save.json")
        registry = MediaRegistry(registry_file)
        
        test_data = [{"path": "media/test.png"}]
        result = registry.save(test_data)
        
        assert result is True
        assert os.path.exists(registry_file)
        
        # Verify saved content
        with open(registry_file, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == test_data
    
    def test_save_failure(self, temp_dir):
        """Test save operation failure"""
        # Create a directory with the same name as the file to cause write error
        registry_file = os.path.join(temp_dir, "test_save.json")
        os.makedirs(registry_file, exist_ok=True)
        
        registry = MediaRegistry(registry_file)
        test_data = [{"path": "media/test.png"}]
        result = registry.save(test_data)
        
        assert result is False
    
    def test_add_media(self, temp_dir):
        """Test adding media to registry (most recent first)"""
        registry_file = os.path.join(temp_dir, "test_add.json")
        registry = MediaRegistry(registry_file)
        
        # Add first media
        result1 = registry.add_media("media/test1.png")
        assert result1 is True
        
        # Add second media
        result2 = registry.add_media("media/test2.mp4")
        assert result2 is True
        
        # Verify registry content (most recent first)
        loaded_data = registry.load()
        assert len(loaded_data) == 2
        assert loaded_data[0]["path"] == "media/test2.mp4"  # Most recent
        assert loaded_data[1]["path"] == "media/test1.png"  # Older
    
    def test_get_all_media(self, sample_registry_file):
        """Test getting all media entries"""
        registry = MediaRegistry(sample_registry_file)
        result = registry.get_all_media()
        
        assert len(result) == 3
        assert all("path" in item for item in result)
        assert result[0]["path"] == "media/test1.png"
    
    def test_get_media_by_index_valid(self, sample_registry_file):
        """Test getting media by valid index"""
        registry = MediaRegistry(sample_registry_file)
        
        result0 = registry.get_media_by_index(0)
        result1 = registry.get_media_by_index(1)
        result2 = registry.get_media_by_index(2)
        
        assert result0["path"] == "media/test1.png"
        assert result1["path"] == "media/test2.mp4"
        assert result2["path"] == "media/test3.jpg"
    
    def test_get_media_by_index_invalid(self, sample_registry_file):
        """Test getting media by invalid index"""
        registry = MediaRegistry(sample_registry_file)
        
        result_negative = registry.get_media_by_index(-1)
        result_too_large = registry.get_media_by_index(10)
        
        assert result_negative is None
        assert result_too_large is None
    
    def test_get_media_count(self, sample_registry_file):
        """Test getting media count"""
        registry = MediaRegistry(sample_registry_file)
        count = registry.get_media_count()
        assert count == 3
    
    def test_get_media_count_empty(self, temp_dir):
        """Test getting media count for empty registry"""
        registry_file = os.path.join(temp_dir, "empty.json")
        registry = MediaRegistry(registry_file)
        count = registry.get_media_count()
        assert count == 0
    
    def test_clear_registry(self, sample_registry_file):
        """Test clearing registry"""
        registry = MediaRegistry(sample_registry_file)
        
        # Verify registry has content initially
        assert registry.get_media_count() == 3
        
        # Clear registry
        result = registry.clear_registry()
        assert result is True
        
        # Verify registry is empty
        assert registry.get_media_count() == 0
        assert registry.load() == []
    
    def test_remove_media_by_index(self, temp_dir):
        """Test removing media by index"""
        registry_file = os.path.join(temp_dir, "test_remove.json")
        registry = MediaRegistry(registry_file)
        
        # Add test entries
        registry.add_media("media/test1.jpg")
        registry.add_media("media/test2.png")
        registry.add_media("media/test3.webm")
        
        # Remove middle entry
        result = registry.remove_media_by_index(1)
        assert result is True
        
        # Check remaining entries
        remaining = registry.get_all_media()
        assert len(remaining) == 2
        assert remaining[0]['path'] == "media/test3.webm"  # Most recent
        assert remaining[1]['path'] == "media/test1.jpg"   # Oldest
    
    def test_remove_media_by_index_invalid(self, temp_dir):
        """Test removing media with invalid index"""
        registry_file = os.path.join(temp_dir, "test_remove_invalid.json")
        registry = MediaRegistry(registry_file)
        
        # Try to remove from empty registry
        result = registry.remove_media_by_index(0)
        assert result is False
        
        # Add one entry and try invalid index
        registry.add_media("media/test1.jpg")
        result = registry.remove_media_by_index(5)
        assert result is False
        assert registry.get_media_count() == 1
    
    def test_add_media_most_recent_first(self, temp_dir):
        """Test that new media is added at the beginning (most recent first)"""
        registry_file = os.path.join(temp_dir, "test_order.json")
        registry = MediaRegistry(registry_file)
        
        # Add entries in order
        registry.add_media("media/oldest.jpg")
        registry.add_media("media/newer.png")
        registry.add_media("media/newest.webm")
        
        # Check order (most recent first)
        all_media = registry.get_all_media()
        assert len(all_media) == 3
        assert all_media[0]['path'] == "media/newest.webm"  # Most recent
        assert all_media[1]['path'] == "media/newer.png"    # Middle
        assert all_media[2]['path'] == "media/oldest.jpg"   # Oldest
