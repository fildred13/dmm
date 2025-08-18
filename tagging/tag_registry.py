"""
Tag Registry Management
Handles loading, saving, and managing tags directly in the events_registry.json file
"""

import json
import logging
import os
import yaml
from typing import List, Dict, Any, Optional
from config import get_tag_registry_path

# Set up logging
logger = logging.getLogger(__name__)


class TagRegistry:
    """Manages tag operations directly in the events_registry.json file"""
    
    def __init__(self, media_registry_path: str):
        self.media_registry_path = media_registry_path
        self.yaml_config_path = os.path.join(os.path.dirname(media_registry_path), 'events_tags.yaml')
    
    def get_tag_registry_path(self) -> str:
        """Get the full path to the media registry file (which now contains tags)"""
        return os.path.abspath(self.media_registry_path)
    
    def get_tag_config(self) -> Dict[str, Any]:
        """Load tag configuration from the YAML file"""
        if os.path.exists(self.yaml_config_path):
            try:
                with open(self.yaml_config_path, 'r') as f:
                    return yaml.safe_load(f)
            except (yaml.YAMLError, IOError) as e:
                logger.error(f"Error loading tag configuration from YAML: {e}")
                return {"tags": {}}
        else:
            logger.warning(f"Tag configuration file not found: {self.yaml_config_path}")
            return {"tags": {}}
    
    def get_media_tags(self, media_path: str) -> Dict[str, Any]:
        """Get tags for a specific media file from events_registry.json"""
        registry_data = self.load_registry()
        for entry in registry_data:
            if entry.get('path') == media_path:
                return entry.get('tags', {})
        return {}
    
    def set_media_tags(self, media_path: str, tags: Dict[str, Any]) -> bool:
        """Set tags for a specific media file in events_registry.json"""
        registry_data = self.load_registry()
        
        # Find the media entry and update its tags
        for entry in registry_data:
            if entry.get('path') == media_path:
                entry['tags'] = tags
                return self.save_registry(registry_data)
        
        # If media not found, add it with tags
        registry_data.append({
            'path': media_path,
            'original_hash': '',  # Will be set by media processor
            'tags': tags
        })
        return self.save_registry(registry_data)
    
    def load_registry(self) -> List[Dict[str, Any]]:
        """Load the events registry from JSON file"""
        if os.path.exists(self.media_registry_path):
            try:
                with open(self.media_registry_path, 'r') as f:
                    data = json.load(f)
                    # Ensure each entry has a tags field
                    for entry in data:
                        if 'tags' not in entry:
                            entry['tags'] = {}
                    return data
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading events registry: {e}")
                return []
        else:
            logger.warning(f"Events registry file not found: {self.media_registry_path}")
            return []
    
    def save_registry(self, registry_data: List[Dict[str, Any]]) -> bool:
        """Save the events registry to JSON file"""
        try:
            # Ensure the directory exists (only if there is a directory)
            directory = os.path.dirname(self.media_registry_path)
            if directory:  # Only create directory if there is one
                os.makedirs(directory, exist_ok=True)
            with open(self.media_registry_path, 'w') as f:
                json.dump(registry_data, f, indent=2)
            return True
        except IOError as e:
            logger.error(f"Error saving events registry: {e}")
            return False
    
    def get_all_tags(self) -> Dict[str, Any]:
        """Get all tags from the registry (legacy method - returns empty dict)"""
        return {}
    
    def get_media_tags_old(self) -> Dict[str, Any]:
        """Get all media-tag associations from the registry"""
        registry_data = self.load_registry()
        media_tags = {}
        for entry in registry_data:
            if 'path' in entry and 'tags' in entry:
                media_tags[entry['path']] = entry['tags']
        return media_tags
    
    def get_tag_categories(self) -> Dict[str, Any]:
        """Get all tag categories from the registry (legacy method - returns empty dict)"""
        return {}
    
    def add_tag(self, tag_name: str, tag_info: Dict[str, Any]) -> bool:
        """Add a new tag to the registry (legacy method - no longer used)"""
        logger.warning("add_tag method is deprecated - tags are now defined in events_tags.yaml")
        return False
    
    def remove_tag(self, tag_name: str) -> bool:
        """Remove a tag from the registry (legacy method - no longer used)"""
        logger.warning("remove_tag method is deprecated - tags are now defined in events_tags.yaml")
        return False
    
    def add_media_tags(self, media_path: str, tags: List[str]) -> bool:
        """Add tags to a media file (legacy method - use set_media_tags instead)"""
        logger.warning("add_media_tags method is deprecated - use set_media_tags instead")
        return False
    
    def remove_media_tags(self, media_path: str) -> bool:
        """Remove all tags from a media file"""
        return self.set_media_tags(media_path, {})
