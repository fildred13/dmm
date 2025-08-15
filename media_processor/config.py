"""
Configuration settings for the Media Management Tool
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# Flask Configuration
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# Registry Configuration
DEFAULT_REGISTRY_FILE = 'media_registry.json'
CONFIG_FILE = '.dmm_config.json'

# Supported File Formats
SUPPORTED_INPUT_FORMATS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
}

SUPPORTED_OUTPUT_FORMATS = ['.webm', '.png', '.jpg']

# Media Processing Settings
# Landscape media: scale to width = 1024, height calculated proportionally
# Portrait media: scale to height = 576, width calculated proportionally
# Square media: scale to width = height = 576
LANDSCAPE_TARGET_WIDTH = 1024
PORTRAIT_TARGET_HEIGHT = 576
SQUARE_TARGET_SIZE = 576

# Video Processing Settings
VIDEO_CRF_MP4 = 23
VIDEO_CRF_WEBM = 30

# Image Processing Settings
JPEG_QUALITY = 95


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


def calculate_dimensions(width: int, height: int, ensure_even: bool = False) -> tuple[int, int]:
    """
    Calculate new dimensions while maintaining aspect ratio.
    
    Args:
        width: Original width
        height: Original height
        ensure_even: Whether to ensure dimensions are even (for video codecs)
    
    Returns:
        Tuple of (new_width, new_height)
    """
    # Handle edge cases where dimensions might be 0 or invalid
    if width <= 0 or height <= 0:
        # Default to square dimensions if we can't determine aspect ratio
        new_width = new_height = SQUARE_TARGET_SIZE
    else:
        aspect_ratio = width / height
        
        # Landscape media: scale to width = 1024, height calculated proportionally
        # Portrait media: scale to height = 576, width calculated proportionally
        # Square media: scale to width = height = 576
        if aspect_ratio > 1.0:
            # Landscape - scale to width = 1024
            new_width = LANDSCAPE_TARGET_WIDTH
            new_height = int(new_width / aspect_ratio)
        elif aspect_ratio < 1.0:
            # Portrait - scale to height = 576
            new_height = PORTRAIT_TARGET_HEIGHT
            new_width = int(new_height * aspect_ratio)
        else:
            # Square - scale to 576x576
            new_width = SQUARE_TARGET_SIZE
            new_height = SQUARE_TARGET_SIZE
    
    # Ensure dimensions are even (required for some video codecs)
    if ensure_even:
        new_width = new_width - (new_width % 2)
        new_height = new_height - (new_height % 2)
    
    return new_width, new_height


def get_media_folder_from_registry(registry_path: str) -> str:
    """Get the media folder path based on the registry file location"""
    registry_dir = os.path.dirname(registry_path)
    return os.path.join(registry_dir, 'media')


def ensure_media_folder_exists(registry_path: str) -> str:
    """Ensure the media folder exists and return its path"""
    media_folder = get_media_folder_from_registry(registry_path)
    os.makedirs(media_folder, exist_ok=True)
    return media_folder
