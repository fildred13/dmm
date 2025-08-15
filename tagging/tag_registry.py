"""
Tag Registry Management
Handles loading, saving, and managing the tag registry JSON file
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
from config import get_tag_registry_path

# Set up logging
logger = logging.getLogger(__name__)


class TagRegistry:
    """Manages the tag registry file operations"""
    
    def __init__(self, media_registry_path: str):
        self.media_registry_path = media_registry_path
        self.tag_registry_path = get_tag_registry_path(media_registry_path)
    
    def get_tag_registry_path(self) -> str:
        """Get the full path to the tag registry file"""
        return os.path.abspath(self.tag_registry_path)
    
    def load(self) -> Dict[str, Any]:
        """Load the tag registry from JSON file"""
        if os.path.exists(self.tag_registry_path):
            try:
                with open(self.tag_registry_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading tag registry: {e}")
                return self._get_default_structure()
        else:
            # Create default structure if file doesn't exist
            default_structure = self._get_default_structure()
            self.save(default_structure)
            return default_structure
    
    def save(self, tag_data: Dict[str, Any]) -> bool:
        """Save the tag registry to JSON file"""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.tag_registry_path), exist_ok=True)
            with open(self.tag_registry_path, 'w') as f:
                json.dump(tag_data, f, indent=2)
            return True
        except IOError as e:
            logger.error(f"Error saving tag registry: {e}")
            return False
    
    def _get_default_structure(self) -> Dict[str, Any]:
        """Get the default tag registry structure"""
        return {
            "tags": {},
            "media_tags": {},
            "tag_categories": {},
            "version": "1.0"
        }
    
    def get_all_tags(self) -> Dict[str, Any]:
        """Get all tags from the registry"""
        return self.load().get('tags', {})
    
    def get_media_tags(self) -> Dict[str, Any]:
        """Get all media-tag associations from the registry"""
        return self.load().get('media_tags', {})
    
    def get_tag_categories(self) -> Dict[str, Any]:
        """Get all tag categories from the registry"""
        return self.load().get('tag_categories', {})
    
    def add_tag(self, tag_name: str, tag_info: Dict[str, Any]) -> bool:
        """Add a new tag to the registry"""
        tag_data = self.load()
        tag_data['tags'][tag_name] = tag_info
        return self.save(tag_data)
    
    def remove_tag(self, tag_name: str) -> bool:
        """Remove a tag from the registry"""
        tag_data = self.load()
        if tag_name in tag_data['tags']:
            del tag_data['tags'][tag_name]
            return self.save(tag_data)
        return False
    
    def add_media_tags(self, media_path: str, tags: List[str]) -> bool:
        """Add tags to a media file"""
        tag_data = self.load()
        tag_data['media_tags'][media_path] = tags
        return self.save(tag_data)
    
    def remove_media_tags(self, media_path: str) -> bool:
        """Remove all tags from a media file"""
        tag_data = self.load()
        if media_path in tag_data['media_tags']:
            del tag_data['media_tags'][media_path]
            return self.save(tag_data)
        return False
    
    def get_media_tags_for_file(self, media_path: str) -> List[str]:
        """Get tags for a specific media file"""
        tag_data = self.load()
        return tag_data.get('media_tags', {}).get(media_path, [])
    
    def add_tag_category(self, category_name: str, category_info: Dict[str, Any]) -> bool:
        """Add a new tag category to the registry"""
        tag_data = self.load()
        tag_data['tag_categories'][category_name] = category_info
        return self.save(tag_data)
    
    def remove_tag_category(self, category_name: str) -> bool:
        """Remove a tag category from the registry"""
        tag_data = self.load()
        if category_name in tag_data['tag_categories']:
            del tag_data['tag_categories'][category_name]
            return self.save(tag_data)
        return False
