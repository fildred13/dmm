"""
Media Registry Management
Handles loading, saving, and managing the media registry JSON file
"""

import json
import os
from typing import List, Dict, Any
from .config import REGISTRY_FILE


class MediaRegistry:
    """Manages the media registry file operations"""
    
    def __init__(self, registry_file: str = REGISTRY_FILE):
        self.registry_file = registry_file
    
    def load(self) -> List[Dict[str, Any]]:
        """Load the media registry from JSON file"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading registry: {e}")
                return []
        return []
    
    def save(self, registry: List[Dict[str, Any]]) -> bool:
        """Save the media registry to JSON file"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving registry: {e}")
            return False
    
    def add_media(self, media_path: str) -> bool:
        """Add a new media entry to the registry"""
        registry = self.load()
        registry.append({'path': media_path})
        return self.save(registry)
    
    def get_all_media(self) -> List[Dict[str, Any]]:
        """Get all media entries from the registry"""
        return self.load()
    
    def get_media_by_index(self, index: int) -> Dict[str, Any]:
        """Get a specific media entry by index"""
        registry = self.load()
        if 0 <= index < len(registry):
            return registry[index]
        return None
    
    def get_media_count(self) -> int:
        """Get the total number of media entries"""
        return len(self.load())
    
    def clear_registry(self) -> bool:
        """Clear all entries from the registry"""
        return self.save([])
