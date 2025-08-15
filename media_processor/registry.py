"""
Media Registry Management
Handles loading, saving, and managing the media registry JSON file
"""

import json
import os
from typing import List, Dict, Any, Optional
from .config import DEFAULT_REGISTRY_FILE


class MediaRegistry:
    """Manages the media registry file operations"""
    
    def __init__(self, registry_file: str = DEFAULT_REGISTRY_FILE):
        self.registry_file = registry_file
    
    def get_registry_path(self) -> str:
        """Get the full path to the registry file"""
        return os.path.abspath(self.registry_file)
    
    def get_registry_directory(self) -> str:
        """Get the directory containing the registry file"""
        return os.path.dirname(self.get_registry_path())
    
    def get_registry_name(self) -> str:
        """Get the name of the registry file"""
        return os.path.basename(self.registry_file)
    
    def get_display_name(self) -> str:
        """Get a display name for the registry (directory name or registry name)"""
        registry_dir = self.get_registry_directory()
        if registry_dir == os.getcwd():
            return "Active Registry"
        return os.path.basename(registry_dir) or "Root"
    
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
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving registry: {e}")
            return False
    
    def add_media(self, media_path: str, original_hash: str = None) -> bool:
        """Add a new media entry to the registry (most recent first)"""
        registry = self.load()
        # Insert at the beginning to maintain reverse chronological order
        entry = {'path': media_path}
        if original_hash:
            entry['original_hash'] = original_hash
        registry.insert(0, entry)
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
    
    def remove_media_by_index(self, index: int) -> bool:
        """Remove a media entry by index"""
        registry = self.load()
        if 0 <= index < len(registry):
            registry.pop(index)
            return self.save(registry)
        return False
    
    def clear_registry(self) -> bool:
        """Clear all entries from the registry"""
        return self.save([])
    
    def find_duplicate_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Find a media entry with the same hash, if it exists"""
        registry = self.load()
        for entry in registry:
            if entry.get('original_hash') == file_hash:
                return entry
        return None
    
    def find_filename_collision(self, filename: str) -> bool:
        """Check if a filename already exists in the registry"""
        registry = self.load()
        for entry in registry:
            if entry['path'].split('/')[-1] == filename:
                return True
        return False
    
    def get_unique_filename(self, base_filename: str) -> str:
        """Generate a unique filename by adding a numeric suffix if needed"""
        if not self.find_filename_collision(base_filename):
            return base_filename
        
        # Split filename into name and extension
        name, ext = os.path.splitext(base_filename)
        counter = 1
        
        while True:
            new_filename = f"{name}-{counter}{ext}"
            if not self.find_filename_collision(new_filename):
                return new_filename
            counter += 1
