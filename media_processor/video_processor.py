"""
Video Processing
Handles video resizing, format conversion, and optimization
"""

from pathlib import Path
import ffmpeg
from typing import Tuple
from .config import LANDSCAPE_TARGET_WIDTH, PORTRAIT_TARGET_HEIGHT, SQUARE_TARGET_SIZE, VIDEO_CRF_MP4, VIDEO_CRF_WEBM


class VideoProcessor:
    """Handles video processing operations"""
    
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
        
        # Ensure dimensions are even (required for some codecs)
        new_width = new_width - (new_width % 2)
        new_height = new_height - (new_height % 2)
        
        return new_width, new_height
    
    @staticmethod
    def resize_video(video_path: str, output_path: str) -> bool:
        """Resize video to fit within max dimensions while maintaining aspect ratio"""
        try:
            # Get video properties
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            width = int(video_info['width'])
            height = int(video_info['height'])
            
            # Calculate new dimensions
            new_width, new_height = VideoProcessor.calculate_dimensions(width, height)
            
            # Convert video
            output_ext = Path(output_path).suffix.lower()
            if output_ext == '.webm':
                stream = ffmpeg.input(video_path)
                stream = ffmpeg.output(stream, output_path, 
                                     vcodec='libvpx-vp9', 
                                     acodec='libopus',
                                     vf=f'scale={new_width}:{new_height}',
                                     crf=VIDEO_CRF_WEBM)
            elif output_ext == '.mp4':
                stream = ffmpeg.input(video_path)
                stream = ffmpeg.output(stream, output_path,
                                     vcodec='libx264',
                                     acodec='aac',
                                     vf=f'scale={new_width}:{new_height}',
                                     crf=VIDEO_CRF_MP4)
            else:
                # Default to MP4
                stream = ffmpeg.input(video_path)
                stream = ffmpeg.output(stream, output_path,
                                     vcodec='libx264',
                                     acodec='aac',
                                     vf=f'scale={new_width}:{new_height}',
                                     crf=VIDEO_CRF_MP4)
            
            ffmpeg.run(stream, overwrite_output=True)
            return True
            
        except Exception as e:
            print(f"Error processing video {video_path}: {e}")
            return False
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """Get information about a video file"""
        try:
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            return {
                'width': int(video_info['width']),
                'height': int(video_info['height']),
                'duration': float(probe['format']['duration']),
                'video_codec': video_info['codec_name'],
                'audio_codec': audio_info['codec_name'] if audio_info else None,
                'bitrate': int(probe['format']['bit_rate'])
            }
        except Exception as e:
            print(f"Error getting video info for {video_path}: {e}")
            return {}
