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
                    'req': 'girls > 0 || guys > 0',
                    'values': [
                        {'value': 'shuffle', 'req': 'girls > 0'},
                        {'value': 'swing', 'req': 'girls > 0 || guys > 0'},
                        {'value': 'salsa', 'req': 'girls > 0 && guys > 0'},
                        {'value': 'tango', 'req': 'girls > 0 && guys > 0'}
                    ]
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
        assert config['tags']['dance_style']['req'] == 'girls > 0 || guys > 0'
    
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
        """Test that tags field is added to entries that don't have it"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create registry data without tags field
        registry_data = [
            {'path': 'events/file1.jpg', 'original_hash': 'hash1'},
            {'path': 'events/file2.jpg', 'original_hash': 'hash2', 'tags': {'existing': 'tag'}}
        ]
        
        # Save the data
        tag_registry.save_registry(registry_data)
        
        # Load the data back
        loaded_data = tag_registry.load_registry()
        
        # Verify tags field was added
        assert 'tags' in loaded_data[0]
        assert loaded_data[0]['tags'] == {}
        assert loaded_data[1]['tags'] == {'existing': 'tag'}
    
    def test_tag_type_conversion(self, temp_dir):
        """Test that tag values are converted to appropriate types based on configuration"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create a test YAML file with type definitions
        yaml_path = os.path.join(temp_dir, "events_tags.yaml")
        test_config = {
            'tags': {
                'girls': {
                    'desc': 'Number of girls in the scene.',
                    'type': 'int',
                    'values': ['0', '1', '2', '3', 'many']
                },
                'guys': {
                    'desc': 'Number of guys in the scene.',
                    'type': 'int',
                    'values': ['0', '1', '2', '3', 'many']
                },
                'action': {
                    'desc': 'High level category of what the main person is doing.',
                    'values': ['existing', 'dancing', 'climbing']
                }
            }
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Test setting tags with string values that should be converted to integers
        tags_with_strings = {
            'girls': '2',
            'guys': '1',
            'action': 'dancing'
        }
        
        success = tag_registry.set_media_tags('events/test.jpg', tags_with_strings)
        assert success is True
        
        # Verify the tags were converted to appropriate types
        loaded_tags = tag_registry.get_media_tags('events/test.jpg')
        assert loaded_tags['girls'] == 2  # Should be integer
        assert loaded_tags['guys'] == 1   # Should be integer
        assert loaded_tags['action'] == 'dancing'  # Should remain string
        
        # Test with 'many' value which should remain string
        tags_with_many = {
            'girls': 'many',
            'guys': '0'
        }
        
        success = tag_registry.set_media_tags('events/test2.jpg', tags_with_many)
        assert success is True
        
        loaded_tags2 = tag_registry.get_media_tags('events/test2.jpg')
        assert loaded_tags2['girls'] == 'many'  # Should remain string
        assert loaded_tags2['guys'] == 0        # Should be integer
        
        # Test with invalid integer value (should keep original value)
        tags_with_invalid = {
            'girls': 'invalid_number',
            'guys': '3'
        }
        
        success = tag_registry.set_media_tags('events/test3.jpg', tags_with_invalid)
        assert success is True
        
        loaded_tags3 = tag_registry.get_media_tags('events/test3.jpg')
        assert loaded_tags3['girls'] == 'invalid_number'  # Should keep original
        assert loaded_tags3['guys'] == 3                  # Should be integer
    
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
