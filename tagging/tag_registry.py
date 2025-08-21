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
from .tag_dependency_manager import TagDependencyManager

# Set up logging
logger = logging.getLogger(__name__)


class TagRegistry:
    """Manages tag operations directly in the events_registry.json file"""
    
    def __init__(self, media_registry_path: str):
        self.media_registry_path = media_registry_path
        self.yaml_config_path = os.path.join(os.path.dirname(media_registry_path), 'events_tags.yaml')
        self.dependency_manager = TagDependencyManager()
    
    def get_tag_registry_path(self) -> str:
        """Get the full path to the media registry file (which now contains tags)"""
        return os.path.abspath(self.media_registry_path)
    
    def get_tag_config(self) -> Dict[str, Any]:
        """Load tag configuration from the YAML file"""
        if os.path.exists(self.yaml_config_path):
            try:
                with open(self.yaml_config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    
                    # In Python 3.7+, dict keys preserve insertion order
                    # The YAML loader should preserve the order from the file
                    if 'tags' in config:
                        tag_order = list(config['tags'].keys())
                        print(f"Tag order from YAML: {tag_order}")
                        
                        # Analyze dependencies and get ordered tags
                        dependencies = self.dependency_manager.analyze_dependencies(config)
                        ordered_tags = self.dependency_manager.get_ordered_tags(tag_order)
                        
                        # Add both to the response
                        config['tag_order'] = tag_order
                        config['ordered_tags'] = ordered_tags
                        config['dependencies'] = dependencies
                        
                        print(f"Analyzed dependencies: {dependencies}")
                        print(f"Final ordered tags: {ordered_tags}")
                        
                    return config
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
        
        # Convert tag values to appropriate types based on tag configuration
        converted_tags = self._convert_tag_types(tags)
        
        # Find the media entry and update its tags
        for entry in registry_data:
            if entry.get('path') == media_path:
                entry['tags'] = converted_tags
                return self.save_registry(registry_data)
        
        # If media not found, add it with tags
        registry_data.append({
            'path': media_path,
            'original_hash': '',  # Will be set by media processor
            'tags': converted_tags
        })
        return self.save_registry(registry_data)
    
    def _convert_tag_types(self, tags: Dict[str, Any]) -> Dict[str, Any]:
        """Convert tag values to appropriate types based on tag configuration"""
        tag_config = self.get_tag_config()
        converted_tags = {}
        
        for tag_name, tag_value in tags.items():
            if tag_name in tag_config.get('tags', {}):
                tag_info = tag_config['tags'][tag_name]
                tag_type = tag_info.get('type', 'string')
                
                # Convert value based on type
                if tag_type == 'int' and tag_value is not None:
                    try:
                        # Handle special case where value might be 'many' or other non-numeric
                        if isinstance(tag_value, str) and tag_value.lower() == 'many':
                            converted_tags[tag_name] = tag_value
                        else:
                            converted_tags[tag_name] = int(tag_value)
                    except (ValueError, TypeError):
                        # If conversion fails, keep original value
                        converted_tags[tag_name] = tag_value
                else:
                    # For other types, keep as is
                    converted_tags[tag_name] = tag_value
            else:
                # If tag not in config, keep as is
                converted_tags[tag_name] = tag_value
        
        # Do not apply default values here - they should only be applied when we reach the tag
        
        return converted_tags
    
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
