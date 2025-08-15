"""
Tests for video processor module
"""

import pytest
import os
from media_processor.video_processor import VideoProcessor


class TestVideoProcessor:
    """Test video processing functionality"""
    
    def test_calculate_dimensions_landscape(self):
        """Test dimension calculation for landscape videos"""
        # Test landscape video that needs resizing
        width, height = VideoProcessor.calculate_dimensions(1920, 1080)
        assert width == 576
        assert height == 324
        
        # Test landscape video that needs upscaling
        width, height = VideoProcessor.calculate_dimensions(400, 300)
        assert width == 576  # Upscaled to max width
        assert height == 432  # 576 * (300/400) = 432
    
    def test_calculate_dimensions_portrait(self):
        """Test dimension calculation for portrait videos"""
        # Test portrait video that needs resizing
        width, height = VideoProcessor.calculate_dimensions(1080, 1920)
        assert width == 576  # 1024 * (1080/1920) = 576
        assert height == 1024  # min(1920, 1024) = 1024
        
        # Test portrait video that needs upscaling
        width, height = VideoProcessor.calculate_dimensions(300, 400)
        assert width == 576  # Upscaled to max width
        assert height == 768  # 576 * (400/300) = 768
    
    def test_calculate_dimensions_even_numbers(self):
        """Test that dimensions are always even numbers"""
        # Test various dimensions to ensure they're even
        width, height = VideoProcessor.calculate_dimensions(1921, 1081)
        assert width % 2 == 0
        assert height % 2 == 0
        
        width, height = VideoProcessor.calculate_dimensions(100, 101)
        assert width % 2 == 0
        assert height % 2 == 0
    
    def test_resize_video_webm(self, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test video resizing to WebM format"""
        input_path = os.path.join(temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.webm")
        
        # Create dummy input file
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        # Resize video
        result = VideoProcessor.resize_video(input_path, output_path)
        
        assert result is True
        mock_ffmpeg_probe.assert_called_once_with(input_path)
        mock_ffmpeg_stream['input'].assert_called_once_with(input_path)
        mock_ffmpeg_stream['run'].assert_called_once()
    
    def test_resize_video_mp4(self, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test video resizing to MP4 format"""
        input_path = os.path.join(temp_dir, "input.avi")
        output_path = os.path.join(temp_dir, "output.mp4")
        
        # Create dummy input file
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        # Resize video
        result = VideoProcessor.resize_video(input_path, output_path)
        
        assert result is True
        mock_ffmpeg_probe.assert_called_once_with(input_path)
        mock_ffmpeg_stream['input'].assert_called_once_with(input_path)
        mock_ffmpeg_stream['run'].assert_called_once()
    
    def test_resize_video_default_format(self, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test video resizing with default format"""
        input_path = os.path.join(temp_dir, "input.mov")
        output_path = os.path.join(temp_dir, "output.avi")
        
        # Create dummy input file
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        # Resize video
        result = VideoProcessor.resize_video(input_path, output_path)
        
        assert result is True
        mock_ffmpeg_probe.assert_called_once_with(input_path)
        mock_ffmpeg_stream['input'].assert_called_once_with(input_path)
        mock_ffmpeg_stream['run'].assert_called_once()
    
    def test_resize_video_failure(self, temp_dir, mock_ffmpeg_probe):
        """Test video resizing failure"""
        # Mock ffmpeg.probe to raise an exception
        mock_ffmpeg_probe.side_effect = Exception("FFmpeg error")
        
        input_path = os.path.join(temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.mp4")
        
        # Create dummy input file
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        # Resize video should fail
        result = VideoProcessor.resize_video(input_path, output_path)
        assert result is False
    
    def test_get_video_info_success(self, temp_dir, mock_ffmpeg_probe):
        """Test getting video information"""
        input_path = os.path.join(temp_dir, "input.mp4")
        
        # Create dummy input file
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        # Get video info
        info = VideoProcessor.get_video_info(input_path)
        
        assert info['width'] == 1920
        assert info['height'] == 1080
        assert info['duration'] == 10.5
        assert info['video_codec'] == 'h264'
        assert info['audio_codec'] == 'aac'
        assert info['bitrate'] == 1000000
    
    def test_get_video_info_no_audio(self, temp_dir, mock_ffmpeg_probe):
        """Test getting video information for video without audio"""
        # Mock ffmpeg.probe to return video without audio
        mock_ffmpeg_probe.return_value = {
            'streams': [
                {
                    'codec_type': 'video',
                    'width': 1920,
                    'height': 1080,
                    'codec_name': 'h264'
                }
            ],
            'format': {
                'duration': '10.5',
                'bit_rate': '1000000'
            }
        }
        
        input_path = os.path.join(temp_dir, "input.mp4")
        
        # Create dummy input file
        with open(input_path, 'w') as f:
            f.write("dummy video content")
        
        # Get video info
        info = VideoProcessor.get_video_info(input_path)
        
        assert info['width'] == 1920
        assert info['height'] == 1080
        assert info['duration'] == 10.5
        assert info['video_codec'] == 'h264'
        assert info['audio_codec'] is None
        assert info['bitrate'] == 1000000
    
    def test_get_video_info_failure(self, temp_dir, mock_ffmpeg_probe):
        """Test getting video information for non-existent file"""
        # Mock ffmpeg.probe to raise an exception
        mock_ffmpeg_probe.side_effect = Exception("FFmpeg error")
        
        input_path = os.path.join(temp_dir, "nonexistent.mp4")
        info = VideoProcessor.get_video_info(input_path)
        assert info == {}
