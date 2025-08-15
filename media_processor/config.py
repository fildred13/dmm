"""
Configuration settings for the Media Management Tool
"""

import os

# Flask Configuration
UPLOAD_FOLDER = 'media'
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# Registry Configuration
REGISTRY_FILE = 'media_registry.json'

# Supported File Formats
SUPPORTED_INPUT_FORMATS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
}

SUPPORTED_OUTPUT_FORMATS = ['.webm', '.mp4', '.png', '.jpg']

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

# Ensure media directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
