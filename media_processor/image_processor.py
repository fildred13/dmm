"""
Image Processing Module
Handles image resizing and format conversion
"""

import logging
from pathlib import Path
from typing import Tuple
from PIL import Image
from .config import JPEG_QUALITY
from .file_utils import FileUtils

# Set up logging
logger = logging.getLogger(__name__)


class ImageProcessor:
    """Image processing operations"""
    
    @staticmethod
    def calculate_dimensions(width: int, height: int) -> Tuple[int, int]:
        """Calculate new dimensions for image processing"""
        return FileUtils.calculate_dimensions(width, height, ensure_even=False)
    
    @staticmethod
    def resize_image(image_path: str, output_path: str) -> bool:
        """Resize image to fit within max dimensions while maintaining aspect ratio"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Calculate new dimensions
                new_width, new_height = ImageProcessor.calculate_dimensions(img.size[0], img.size[1])
                
                # Resize image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save with appropriate format
                output_ext = Path(output_path).suffix.lower()
                if output_ext == '.jpg':
                    resized_img.save(output_path, 'JPEG', quality=JPEG_QUALITY)
                elif output_ext == '.png':
                    resized_img.save(output_path, 'PNG')
                else:
                    resized_img.save(output_path)
                
                return True
                
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return False
    
    @staticmethod
    def get_image_info(image_path: str) -> dict:
        """Get information about an image file"""
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.size[0],
                    'height': img.size[1],
                    'mode': img.mode,
                    'format': img.format
                }
        except Exception as e:
            logger.error(f"Error getting image info for {image_path}: {e}")
            return {}
