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
MAX_WIDTH = 576
MAX_HEIGHT = 1024

# Video Processing Settings
VIDEO_CRF_MP4 = 23
VIDEO_CRF_WEBM = 30

# Image Processing Settings
JPEG_QUALITY = 95

# Ensure media directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
