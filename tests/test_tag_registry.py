"""
Tests for tag registry functionality
"""

import pytest
import json
import os
import tempfile
import yaml
from tagging.tag_registry import TagRegistry


class TestTagRegistry:
    """Test tag registry functionality"""
    
    def test_tag_registry_initialization(self, temp_dir):
        """Test tag registry initialization"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        expected_path = os.path.join(temp_dir, "events_registry.json")
        assert tag_registry.get_tag_registry_path() == os.path.abspath(expected_path)
    
    def test_tag_registry_default_structure(self, temp_dir):
        """Test that tag registry creates default structure when file doesn't exist"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Load should return empty list when file doesn't exist
        data = tag_registry.load_registry()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_tag_registry_save_and_load(self, temp_dir):
        """Test saving and loading events registry data"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create test data
        test_data = [
            {
                'path': 'events/test1.jpg',
                'original_hash': 'hash1',
                'tags': {'test_tag': 'value1'}
            },
            {
                'path': 'events/test2.jpg',
                'original_hash': 'hash2',
                'tags': {}
            }
        ]
        
        # Save data
        success = tag_registry.save_registry(test_data)
        assert success is True
        
        # Load data
        loaded_data = tag_registry.load_registry()
        assert loaded_data == test_data
    
    def test_get_and_set_media_tags(self, temp_dir):
        """Test getting and setting media tags"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create initial registry with one entry
        initial_data = [
            {
                'path': 'events/test.jpg',
                'original_hash': 'hash1',
                'tags': {}
            }
        ]
        tag_registry.save_registry(initial_data)
        
        # Set tags for media
        tags = {'tag1': 'value1', 'tag2': 'value2'}
        success = tag_registry.set_media_tags('events/test.jpg', tags)
        assert success is True
        
        # Get tags for specific media
        media_tags = tag_registry.get_media_tags('events/test.jpg')
        assert media_tags == tags
    
    def test_get_media_tags_for_nonexistent_file(self, temp_dir):
        """Test getting tags for a file that doesn't have any"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Get tags for nonexistent file
        tags = tag_registry.get_media_tags('events/nonexistent.jpg')
        assert tags == {}
    
    def test_set_media_tags_for_nonexistent_file(self, temp_dir):
        """Test setting tags for a file that doesn't exist in registry"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Set tags for nonexistent file
        tags = {'tag1': 'value1'}
        success = tag_registry.set_media_tags('events/newfile.jpg', tags)
        assert success is True
        
        # Verify the file was added to registry
        registry_data = tag_registry.load_registry()
        assert len(registry_data) == 1
        assert registry_data[0]['path'] == 'events/newfile.jpg'
        assert registry_data[0]['tags'] == tags
    
    def test_get_tag_config(self, temp_dir):
        """Test loading tag configuration from YAML"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create a test YAML file
        yaml_path = os.path.join(temp_dir, "events_tags.yaml")
        test_config = {
            'tags': {
                'girls': {
                    'desc': 'Number of girls in the scene.',
                    'type': 'int',
                    'values': ['0', '1', '2', '3', 'many']
                },
                'dance_style': {
                    'desc': 'What style of dance is the main person doing?',
                    'requires': 'girls > 0 || guys > 0',
                    'values': ['shuffle', 'swing', 'salsa', 'tango']
                }
            }
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Test loading the config
        config = tag_registry.get_tag_config()
        assert 'tags' in config
        assert 'girls' in config['tags']
        assert 'dance_style' in config['tags']
        assert config['tags']['girls']['desc'] == 'Number of girls in the scene.'
        assert config['tags']['dance_style']['requires'] == 'girls > 0 || guys > 0'
    
    def test_get_tag_config_nonexistent_file(self, temp_dir):
        """Test loading tag configuration when YAML file doesn't exist"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Test loading config when YAML doesn't exist
        config = tag_registry.get_tag_config()
        assert config == {"tags": {}}
    
    def test_media_tags_persistence(self, temp_dir):
        """Test that media tags persist correctly"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Set tags for multiple media files
        tags1 = {'girls': '2', 'action': 'dancing'}
        tags2 = {'girls': '1', 'action': 'existing'}
        
        tag_registry.set_media_tags('events/file1.jpg', tags1)
        tag_registry.set_media_tags('events/file2.jpg', tags2)
        
        # Create new instance to test persistence
        tag_registry2 = TagRegistry(media_registry_path)
        
        # Verify tags are still there
        loaded_tags1 = tag_registry2.get_media_tags('events/file1.jpg')
        loaded_tags2 = tag_registry2.get_media_tags('events/file2.jpg')
        
        assert loaded_tags1 == tags1
        assert loaded_tags2 == tags2
    
    def test_ensure_tags_field_exists(self, temp_dir):
        """Test that tags field is automatically added to existing entries"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create registry data without tags field
        initial_data = [
            {
                'path': 'events/test.jpg',
                'original_hash': 'hash1'
            }
        ]
        
        with open(media_registry_path, 'w') as f:
            json.dump(initial_data, f)
        
        # Load registry - should add tags field
        loaded_data = tag_registry.load_registry()
        assert len(loaded_data) == 1
        assert 'tags' in loaded_data[0]
        assert loaded_data[0]['tags'] == {}
    
    def test_remove_media_tags(self, temp_dir):
        """Test removing all tags from a media file"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create initial registry with tags
        initial_data = [
            {
                'path': 'events/test.jpg',
                'original_hash': 'hash1',
                'tags': {'tag1': 'value1', 'tag2': 'value2'}
            }
        ]
        tag_registry.save_registry(initial_data)
        
        # Remove tags
        success = tag_registry.remove_media_tags('events/test.jpg')
        assert success is True
        
        # Verify tags are removed
        media_tags = tag_registry.get_media_tags('events/test.jpg')
        assert media_tags == {}
