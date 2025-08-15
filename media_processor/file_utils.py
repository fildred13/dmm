"""
File Utilities
Handles file type detection, path operations, and file validation
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
from .config import SUPPORTED_INPUT_FORMATS, SUPPORTED_OUTPUT_FORMATS

# Set up logging
logger = logging.getLogger(__name__)


class FileUtils:
    """Utility functions for file operations"""
    
    @staticmethod
    def is_animated_gif(file_path: str) -> bool:
        """Check if a GIF file is animated"""
        try:
            with Image.open(file_path) as img:
                # Check if the image has multiple frames
                return hasattr(img, 'n_frames') and img.n_frames > 1
        except Exception as e:
            logger.warning(f"Error checking if GIF is animated: {e}")
            return False
    
    @staticmethod
    def is_animated_webp(file_path: str) -> bool:
        """Check if a WebP file is animated"""
        try:
            with Image.open(file_path) as img:
                # Use PIL's built-in is_animated property
                return img.is_animated
        except Exception as e:
            logger.warning(f"Error checking if WebP is animated: {e}")
            return False
    
    @staticmethod
    def get_file_type(filename: str, file_path: str = None) -> Optional[str]:
        """Determine if file is image or video based on extension and content"""
        ext = Path(filename).suffix.lower()
        
        # Special handling for GIF files
        if ext == '.gif' and file_path:
            # Check if it's an animated GIF
            if FileUtils.is_animated_gif(file_path):
                return 'video'  # Animated GIFs are treated as videos
            else:
                return 'image'  # Static GIFs are treated as images
        
        # Special handling for WebP files
        if ext == '.webp' and file_path:
            # Check if it's an animated WebP
            if FileUtils.is_animated_webp(file_path):
                return 'video'  # Animated WebPs are treated as videos
            else:
                return 'image'  # Static WebPs are treated as images
        
        # Regular file type detection
        if ext in SUPPORTED_INPUT_FORMATS['image']:
            return 'image'
        elif ext in SUPPORTED_INPUT_FORMATS['video']:
            return 'video'
        return None
    
    @staticmethod
    def is_supported_format(filename: str) -> bool:
        """Check if file format is supported"""
        return FileUtils.get_file_type(filename) is not None
    
    @staticmethod
    def get_output_format(filename: str, file_type: str, file_path: str = None) -> str:
        """Determine the appropriate output format for a file"""
        input_ext = Path(filename).suffix.lower()
        
        # Special handling for GIF files
        if input_ext == '.gif':
            if file_path and FileUtils.is_animated_gif(file_path):
                return '.webm'  # Animated GIFs become WEBM videos
            else:
                return '.png'   # Static GIFs become PNG images
        
        # Special handling for WebP files
        if input_ext == '.webp':
            if file_path and FileUtils.is_animated_webp(file_path):
                return '.webm'  # Animated WebPs become WEBM videos
            else:
                return '.png'   # Static WebPs become PNG images
        
        # If input format is already supported, keep it
        if input_ext in SUPPORTED_OUTPUT_FORMATS:
            return input_ext
        
        # Otherwise, use default formats
        if file_type == 'image':
            return '.png'
        else:  # video
            return '.webm'  # All videos are converted to WebM
    
    @staticmethod
    def create_output_filename(input_filename: str, output_ext: str) -> str:
        """Create output filename with new extension"""
        return Path(input_filename).stem + output_ext
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate a fast hash of the file content for duplicate detection"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize path to use forward slashes for cross-platform compatibility"""
        return path.replace('\\', '/')
    
    @staticmethod
    def get_file_info(file_path: str) -> Tuple[str, str, int]:
        """Get basic file information (name, extension, size)"""
        path_obj = Path(file_path)
        return path_obj.name, path_obj.suffix.lower(), path_obj.stat().st_size
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def calculate_dimensions(width: int, height: int, ensure_even: bool = False) -> Tuple[int, int]:
        """
        Calculate new dimensions while maintaining aspect ratio.
        
        Args:
            width: Original width
            height: Original height
            ensure_even: Whether to ensure dimensions are even (for video codecs)
        
        Returns:
            Tuple of (new_width, new_height)
        """
        from .config import LANDSCAPE_TARGET_WIDTH, PORTRAIT_TARGET_HEIGHT, SQUARE_TARGET_SIZE
        
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
