"""
File Utilities
Handles file type detection, path operations, and file validation
"""

from pathlib import Path
from typing import Optional, Tuple
from .config import SUPPORTED_INPUT_FORMATS, SUPPORTED_OUTPUT_FORMATS


class FileUtils:
    """Utility functions for file operations"""
    
    @staticmethod
    def get_file_type(filename: str) -> Optional[str]:
        """Determine if file is image or video based on extension"""
        ext = Path(filename).suffix.lower()
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
    def get_output_format(filename: str, file_type: str) -> str:
        """Determine the appropriate output format for a file"""
        input_ext = Path(filename).suffix.lower()
        
        # If input format is already supported, keep it
        if input_ext in SUPPORTED_OUTPUT_FORMATS:
            return input_ext
        
        # Otherwise, use default formats
        if file_type == 'image':
            return '.png'
        else:  # video
            return '.mp4'
    
    @staticmethod
    def create_output_filename(input_filename: str, output_ext: str) -> str:
        """Create output filename with new extension"""
        return Path(input_filename).stem + output_ext
    
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
            return "0 Bytes"
        
        size_names = ["Bytes", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
