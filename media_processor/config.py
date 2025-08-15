"""
Media processing configuration settings
"""

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
