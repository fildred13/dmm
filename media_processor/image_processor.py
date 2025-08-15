"""
Image Processing
Handles image resizing, format conversion, and optimization
"""

from pathlib import Path
from PIL import Image
from typing import Tuple
from .config import LANDSCAPE_TARGET_WIDTH, PORTRAIT_TARGET_HEIGHT, SQUARE_TARGET_SIZE, JPEG_QUALITY


class ImageProcessor:
    """Handles image processing operations"""
    
    @staticmethod
    def calculate_dimensions(width: int, height: int) -> Tuple[int, int]:
        """Calculate new dimensions while maintaining aspect ratio"""
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
        
        return new_width, new_height
    
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
            print(f"Error processing image {image_path}: {e}")
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
            print(f"Error getting image info for {image_path}: {e}")
            return {}
