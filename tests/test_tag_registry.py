"""
Tests for tag registry functionality
"""

import pytest
import json
import os
import tempfile
from tagging.tag_registry import TagRegistry


class TestTagRegistry:
    """Test tag registry functionality"""
    
    def test_tag_registry_initialization(self, temp_dir):
        """Test tag registry initialization"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        expected_tag_path = os.path.join(temp_dir, "tag_registry.json")
        assert tag_registry.get_tag_registry_path() == os.path.abspath(expected_tag_path)
    
    def test_tag_registry_default_structure(self, temp_dir):
        """Test that tag registry creates default structure when file doesn't exist"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Load should create default structure
        data = tag_registry.load()
        
        assert 'tags' in data
        assert 'media_tags' in data
        assert 'tag_categories' in data
        assert 'version' in data
        assert data['version'] == '1.0'
        assert isinstance(data['tags'], dict)
        assert isinstance(data['media_tags'], dict)
        assert isinstance(data['tag_categories'], dict)
    
    def test_tag_registry_save_and_load(self, temp_dir):
        """Test saving and loading tag registry data"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Create test data
        test_data = {
            'tags': {'test_tag': {'description': 'A test tag'}},
            'media_tags': {'events/test.jpg': ['test_tag']},
            'tag_categories': {'test_category': {'description': 'A test category'}},
            'version': '1.0'
        }
        
        # Save data
        success = tag_registry.save(test_data)
        assert success is True
        
        # Load data
        loaded_data = tag_registry.load()
        assert loaded_data == test_data
    
    def test_add_and_get_tags(self, temp_dir):
        """Test adding and getting tags"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Add a tag
        tag_info = {'description': 'A test tag', 'category': 'test'}
        success = tag_registry.add_tag('test_tag', tag_info)
        assert success is True
        
        # Get all tags
        all_tags = tag_registry.get_all_tags()
        assert 'test_tag' in all_tags
        assert all_tags['test_tag'] == tag_info
    
    def test_remove_tag(self, temp_dir):
        """Test removing tags"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Add a tag first
        tag_info = {'description': 'A test tag'}
        tag_registry.add_tag('test_tag', tag_info)
        
        # Remove the tag
        success = tag_registry.remove_tag('test_tag')
        assert success is True
        
        # Verify it's gone
        all_tags = tag_registry.get_all_tags()
        assert 'test_tag' not in all_tags
    
    def test_add_and_get_media_tags(self, temp_dir):
        """Test adding and getting media tags"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Add tags to media
        tags = ['tag1', 'tag2', 'tag3']
        success = tag_registry.add_media_tags('events/test.jpg', tags)
        assert success is True
        
        # Get tags for specific media
        media_tags = tag_registry.get_media_tags_for_file('events/test.jpg')
        assert media_tags == tags
        
        # Get all media tags
        all_media_tags = tag_registry.get_media_tags()
        assert 'events/test.jpg' in all_media_tags
        assert all_media_tags['events/test.jpg'] == tags
    
    def test_remove_media_tags(self, temp_dir):
        """Test removing media tags"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Add tags first
        tags = ['tag1', 'tag2']
        tag_registry.add_media_tags('events/test.jpg', tags)
        
        # Remove tags
        success = tag_registry.remove_media_tags('events/test.jpg')
        assert success is True
        
        # Verify they're gone
        media_tags = tag_registry.get_media_tags_for_file('events/test.jpg')
        assert media_tags == []
    
    def test_add_and_get_tag_categories(self, temp_dir):
        """Test adding and getting tag categories"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Add a category
        category_info = {'description': 'A test category', 'color': '#ff0000'}
        success = tag_registry.add_tag_category('test_category', category_info)
        assert success is True
        
        # Get all categories
        all_categories = tag_registry.get_tag_categories()
        assert 'test_category' in all_categories
        assert all_categories['test_category'] == category_info
    
    def test_remove_tag_category(self, temp_dir):
        """Test removing tag categories"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Add a category first
        category_info = {'description': 'A test category'}
        tag_registry.add_tag_category('test_category', category_info)
        
        # Remove the category
        success = tag_registry.remove_tag_category('test_category')
        assert success is True
        
        # Verify it's gone
        all_categories = tag_registry.get_tag_categories()
        assert 'test_category' not in all_categories
    
    def test_get_media_tags_for_nonexistent_file(self, temp_dir):
        """Test getting tags for a file that doesn't have any"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Get tags for nonexistent file
        tags = tag_registry.get_media_tags_for_file('events/nonexistent.jpg')
        assert tags == []
    
    def test_remove_nonexistent_tag(self, temp_dir):
        """Test removing a tag that doesn't exist"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Try to remove nonexistent tag
        success = tag_registry.remove_tag('nonexistent_tag')
        assert success is False
    
    def test_remove_nonexistent_media_tags(self, temp_dir):
        """Test removing tags for media that doesn't have any"""
        media_registry_path = os.path.join(temp_dir, "events_registry.json")
        tag_registry = TagRegistry(media_registry_path)
        
        # Try to remove tags for nonexistent media
        success = tag_registry.remove_media_tags('events/nonexistent.jpg')
        assert success is False
