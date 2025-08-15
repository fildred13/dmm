"""
Global configuration settings for the Media Management Tool
"""

import json
import logging
import os
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# Flask Configuration
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# Registry Configuration
DEFAULT_REGISTRY_FILE = 'events_registry.json'
CONFIG_FILE = '.dmm_config.json'


def get_last_registry_path() -> str:
    """
    Get the last active registry path from config file.
    
    Returns:
        The last registry path if valid, otherwise DEFAULT_REGISTRY_FILE
    """
    try:
        if not os.path.exists(CONFIG_FILE):
            logger.debug(f"Config file {CONFIG_FILE} not found, using default registry")
            return DEFAULT_REGISTRY_FILE
        
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        registry_path = config.get('last_registry_path')
        if not registry_path:
            logger.warning("No registry path found in config file, using default")
            return DEFAULT_REGISTRY_FILE
        
        # Validate that the registry file exists
        if not os.path.exists(registry_path):
            logger.warning(f"Saved registry path {registry_path} does not exist, using default")
            return DEFAULT_REGISTRY_FILE
        
        logger.info(f"Loaded last registry path: {registry_path}")
        return registry_path
        
    except (json.JSONDecodeError, IOError, KeyError) as e:
        logger.warning(f"Error reading config file {CONFIG_FILE}: {e}, using default registry")
        return DEFAULT_REGISTRY_FILE


def save_last_registry_path(registry_path: str) -> bool:
    """
    Save the registry path to config file for persistence.
    
    Args:
        registry_path: The registry path to save
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        config = {'last_registry_path': registry_path}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved registry path to config: {registry_path}")
        return True
    except (IOError, TypeError, ValueError) as e:
        logger.error(f"Error saving registry path to config file: {e}")
        return False


def get_media_folder_from_registry(registry_path: str) -> str:
    """Get the media folder path based on the registry file location"""
    registry_dir = os.path.dirname(registry_path)
    return os.path.join(registry_dir, 'events')


def get_tag_registry_path(media_registry_path: str) -> str:
    """Get the tag registry path based on the media registry file location"""
    registry_dir = os.path.dirname(media_registry_path)
    registry_name = os.path.basename(media_registry_path)
    # Replace events_registry.json with tag_registry.json
    tag_registry_name = registry_name.replace('events_registry.json', 'tag_registry.json')
    return os.path.join(registry_dir, tag_registry_name)


def ensure_media_folder_exists(registry_path: str) -> str:
    """Ensure the media folder exists and return its path"""
    media_folder = get_media_folder_from_registry(registry_path)
    os.makedirs(media_folder, exist_ok=True)
    return media_folder
