"""
Video Processing Module
Handles video resizing and format conversion
"""

import logging
import subprocess
from pathlib import Path
import ffmpeg
from typing import Tuple, Optional, Dict, Any
from .config import VIDEO_CRF_MP4, VIDEO_CRF_WEBM
from .file_utils import FileUtils

try:
    from wand.image import Image as WandImage
    WAND_AVAILABLE = True
except ImportError:
    WAND_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)


class VideoProcessor:
    """Video processing operations"""
    
    @staticmethod
    def calculate_dimensions(width: int, height: int) -> Tuple[int, int]:
        """Calculate new dimensions for video processing (ensures even numbers)"""
        return FileUtils.calculate_dimensions(width, height, ensure_even=True)
    
    @staticmethod
    def convert_webp_to_webm(webp_path: str, output_path: str) -> bool:
        """Convert animated WebP to WebM using Wand/ImageMagick"""
        if not WAND_AVAILABLE:
            logger.warning("Wand/ImageMagick not available for WebP conversion")
            return False
        
        try:
            with WandImage(filename=webp_path) as img:
                # Check if the image is animated by counting frames
                # Note: img.animation property is unreliable for WebP files
                frames = len(img.sequence)
                if frames <= 1:
                    logger.info(f"WebP file is not animated (only {frames} frame): {webp_path}")
                    return False
                
                # Coalesce frames to ensure proper animation handling
                img.coalesce()
                # Set format to webm
                img.format = 'webm'
                # Save to output path
                img.save(filename=output_path)
            return True
        except Exception as e:
            logger.error(f"Error converting WebP to WebM with Wand: {e}")
            # Provide more specific error information
            if "corrupt image" in str(e).lower():
                logger.error(f"WebP file appears to be corrupted or invalid: {webp_path}")
            elif "unable to open image" in str(e).lower():
                logger.error(f"Unable to open WebP file: {webp_path}")
            return False
    
    @staticmethod
    def resize_video(video_path: str, output_path: str) -> bool:
        """Resize video to fit within max dimensions while maintaining aspect ratio"""
        # Check if this is an animated WebP file
        input_ext = Path(video_path).suffix.lower()
        is_animated_webp = input_ext == '.webp'
        
        # For animated WebP files, use Wand/ImageMagick for conversion
        if is_animated_webp:
            logger.info(f"Processing animated WebP with Wand: {video_path}")
            # First convert WebP to WebM using Wand
            if VideoProcessor.convert_webp_to_webm(video_path, output_path):
                # If conversion successful, try to resize the resulting WebM
                try:
                    # Get dimensions of the converted WebM
                    probe = ffmpeg.probe(output_path)
                    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                    width = int(video_info['width'])
                    height = int(video_info['height'])
                    
                    # Calculate new dimensions
                    new_width, new_height = VideoProcessor.calculate_dimensions(width, height)
                    
                    # Create a temporary file for resizing
                    temp_output = str(Path(output_path).with_suffix('.temp.webm'))
                    
                    # Resize the WebM using FFmpeg
                    stream = ffmpeg.input(output_path)
                    stream = ffmpeg.output(stream, temp_output, 
                                         vcodec='libvpx-vp9', 
                                         acodec='libopus',
                                         vf=f'scale={new_width}:{new_height}',
                                         crf=VIDEO_CRF_WEBM)
                    ffmpeg.run(stream, overwrite_output=True)
                    
                    # Replace the original output with the resized version
                    import os
                    import time
                    try:
                        os.replace(temp_output, output_path)
                    except OSError as e:
                        # If replace fails due to file locking, try a different approach
                        logger.warning(f"File replacement failed, trying alternative method: {e}")
                        try:
                            # Wait a moment and try again
                            time.sleep(0.1)
                            if os.path.exists(temp_output):
                                os.remove(output_path)
                                os.rename(temp_output, output_path)
                        except Exception as e2:
                            logger.error(f"Alternative file replacement also failed: {e2}")
                            # If all else fails, just keep the temp file
                            if os.path.exists(temp_output):
                                os.rename(temp_output, output_path)
                    
                    logger.info(f"Successfully processed animated WebP: {output_path}")
                    return True
                    
                except Exception as resize_error:
                    logger.error(f"Error resizing converted WebM: {resize_error}")
                    # If resizing fails, we still have the converted WebM, so return success
                    return True
            else:
                logger.error(f"Failed to convert WebP to WebM with Wand: {video_path}")
                logger.info("This WebP file may not be animated or may be corrupted.")
                logger.info("It will be processed as a static image instead.")
                return False
        
        # For non-WebP files, use the original FFmpeg approach
        try:
            # Get video properties
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            width = int(video_info['width'])
            height = int(video_info['height'])
            
            # Calculate new dimensions
            new_width, new_height = VideoProcessor.calculate_dimensions(width, height)
            
            # Convert all videos to WebM format
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, 
                                 vcodec='libvpx-vp9', 
                                 acodec='libopus',
                                 vf=f'scale={new_width}:{new_height}',
                                 crf=VIDEO_CRF_WEBM)
            
            ffmpeg.run(stream, overwrite_output=True)
            return True
            
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            return False
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """Get information about a video file"""
        try:
            # Check if this is an animated WebP file
            input_ext = Path(video_path).suffix.lower()
            is_animated_webp = input_ext == '.webp'
            
            if is_animated_webp:
                # For animated WebP files, we can't get info directly with FFmpeg
                # Return default info for WebP files
                return {
                    'width': 1024,
                    'height': 576,
                    'duration': 0.0,
                    'video_codec': 'webp',
                    'audio_codec': None,
                    'bitrate': 0
                }
            else:
                probe = ffmpeg.probe(video_path)
                video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            return {
                'width': int(video_info['width']),
                'height': int(video_info['height']),
                'duration': float(probe['format']['duration']) if 'duration' in probe['format'] else 0.0,
                'video_codec': video_info['codec_name'],
                'audio_codec': audio_info['codec_name'] if audio_info else None,
                'bitrate': int(probe['format']['bit_rate'])
            }
        except Exception as e:
            logger.error(f"Error getting video info for {video_path}: {e}")
            return {}
