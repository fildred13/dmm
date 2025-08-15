"""
Configuration settings for the Media Management Tool
"""

import os

# Flask Configuration
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# Registry Configuration
DEFAULT_REGISTRY_FILE = 'media_registry.json'

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


def get_media_folder_from_registry(registry_path: str) -> str:
    """Get the media folder path based on the registry file location"""
    registry_dir = os.path.dirname(registry_path)
    return os.path.join(registry_dir, 'media')


def ensure_media_folder_exists(registry_path: str) -> str:
    """Ensure the media folder exists and return its path"""
    media_folder = get_media_folder_from_registry(registry_path)
    os.makedirs(media_folder, exist_ok=True)
    return media_folder
