"""
Main Media Processor
Orchestrates the media processing workflow
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from .config import ensure_media_folder_exists
from .file_utils import FileUtils
from .image_processor import ImageProcessor
from .video_processor import VideoProcessor


class MediaProcessor:
    """Main media processing orchestrator"""
    
    def __init__(self, registry_path: str = None):
        """
        Initialize the media processor
        
        Args:
            registry_path: Path to the registry file. If None, uses default.
        """
        if registry_path is None:
            from .config import DEFAULT_REGISTRY_FILE
            registry_path = DEFAULT_REGISTRY_FILE
        
        self.registry_path = registry_path
        # Ensure media folder exists and get its path
        self.upload_folder = ensure_media_folder_exists(registry_path)
    
    def process_media_file(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Process a single media file: resize and convert if necessary
        
        Returns:
            Tuple of (relative_path, error_message)
            If successful: (relative_path, None)
            If failed: (None, error_message)
        """
        filename = Path(file_path).name
        file_type = FileUtils.get_file_type(filename, file_path)
        
        if not file_type:
            return None, "Unsupported file type"
        
        # Determine output format
        output_ext = FileUtils.get_output_format(filename, file_type, file_path)
        
        # Create output filename
        output_filename = FileUtils.create_output_filename(filename, output_ext)
        output_path = os.path.join(self.upload_folder, output_filename)
        
        try:
            if file_type == 'image':
                success = ImageProcessor.resize_image(file_path, output_path)
            else:  # video
                success = VideoProcessor.resize_video(file_path, output_path)
            
            if not success:
                return None, f"Failed to process {file_type}"
            
            # Return relative path for registry (always use forward slashes for cross-platform compatibility)
            relative_path = FileUtils.normalize_path(f'media/{output_filename}')
            return relative_path, None
            
        except Exception as e:
            return None, str(e)
    
    def get_processing_info(self, file_path: str) -> dict:
        """Get information about a file before processing"""
        filename = Path(file_path).name
        file_type = FileUtils.get_file_type(filename, file_path)
        
        if not file_type:
            return {'error': 'Unsupported file type'}
        
        info = {
            'filename': filename,
            'file_type': file_type,
            'original_size': FileUtils.format_file_size(Path(file_path).stat().st_size)
        }
        
        if file_type == 'image':
            image_info = ImageProcessor.get_image_info(file_path)
            info.update(image_info)
        else:  # video
            video_info = VideoProcessor.get_video_info(file_path)
            info.update(video_info)
        
        return info
