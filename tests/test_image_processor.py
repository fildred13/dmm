"""
Tests for image processor module
"""

import pytest
import os
from PIL import Image
import numpy as np
from media_processor.image_processor import ImageProcessor


class TestImageProcessor:
    """Test image processing functionality"""
    
    def test_calculate_dimensions_landscape(self):
        """Test dimension calculation for landscape images"""
        # Test landscape image that needs resizing
        width, height = ImageProcessor.calculate_dimensions(1920, 1080)
        assert width == 1024  # Landscape: scale to width = 1024
        assert height == 576  # 1024 * (1080/1920) = 576
        
        # Test landscape image that needs upscaling
        width, height = ImageProcessor.calculate_dimensions(400, 300)
        assert width == 1024  # Landscape: scale to width = 1024
        assert height == 768  # 1024 * (300/400) = 768
    
    def test_calculate_dimensions_portrait(self):
        """Test dimension calculation for portrait images"""
        # Test portrait image that needs resizing
        width, height = ImageProcessor.calculate_dimensions(1080, 1920)
        assert width == 324  # Portrait: scale to height = 576, width = 576 * (1080/1920) = 324
        assert height == 576  # Portrait: scale to height = 576
        
        # Test portrait image that needs upscaling
        width, height = ImageProcessor.calculate_dimensions(300, 400)
        assert width == 432  # Portrait: scale to height = 576, width = 576 * (300/400) = 432
        assert height == 576  # Portrait: scale to height = 576
    
    def test_calculate_dimensions_square(self):
        """Test dimension calculation for square images"""
        # Test square image that needs resizing
        width, height = ImageProcessor.calculate_dimensions(1500, 1500)
        assert width == 576
        assert height == 576
        
        # Test square image that needs upscaling
        width, height = ImageProcessor.calculate_dimensions(500, 500)
        assert width == 576  # Upscaled to max width
        assert height == 576  # Square aspect ratio maintained
    
    def test_calculate_dimensions_edge_cases(self):
        """Test dimension calculation edge cases"""
        # Test portrait image (576x1024) - should scale to height = 576
        width, height = ImageProcessor.calculate_dimensions(576, 1024)
        assert width == 324  # Portrait: scale to height = 576, width = 576 * (576/1024) = 324
        assert height == 576  # Portrait: scale to height = 576
        
        # Test very small landscape image (100x50) - should scale to width = 1024
        width, height = ImageProcessor.calculate_dimensions(100, 50)
        assert width == 1024  # Landscape: scale to width = 1024
        assert height == 512  # 1024 * (50/100) = 512
    
    def test_resize_image_success(self, temp_dir):
        """Test successful image resizing"""
        # Create test image
        input_path = os.path.join(temp_dir, "input.png")
        output_path = os.path.join(temp_dir, "output.jpg")
        
        # Create a test image (1920x1080)
        img_array = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Resize image
        result = ImageProcessor.resize_image(input_path, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify output image dimensions
        with Image.open(output_path) as output_img:
            assert output_img.size[0] == 1024  # Landscape: should be resized to width = 1024
            assert output_img.size[1] == 576  # Should maintain aspect ratio
    
    def test_resize_image_different_formats(self, temp_dir):
        """Test image resizing with different output formats"""
        # Create test image
        input_path = os.path.join(temp_dir, "input.png")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(input_path)
        
        # Test PNG output
        png_output = os.path.join(temp_dir, "output.png")
        result_png = ImageProcessor.resize_image(input_path, png_output)
        assert result_png is True
        assert os.path.exists(png_output)
        
        # Test JPG output
        jpg_output = os.path.join(temp_dir, "output.jpg")
        result_jpg = ImageProcessor.resize_image(input_path, jpg_output)
        assert result_jpg is True
        assert os.path.exists(jpg_output)
        
        # Test GIF output
        gif_output = os.path.join(temp_dir, "output.gif")
        result_gif = ImageProcessor.resize_image(input_path, gif_output)
        assert result_gif is True
        assert os.path.exists(gif_output)
    
    def test_resize_image_rgba_conversion(self, temp_dir):
        """Test RGBA image conversion to RGB"""
        # Create RGBA test image
        input_path = os.path.join(temp_dir, "input_rgba.png")
        output_path = os.path.join(temp_dir, "output_rgb.jpg")
        
        # Create RGBA image
        img_array = np.random.randint(0, 255, (100, 150, 4), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img = img.convert('RGBA')
        img.save(input_path)
        
        # Resize image (should convert to RGB)
        result = ImageProcessor.resize_image(input_path, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify output image is RGB
        with Image.open(output_path) as output_img:
            assert output_img.mode == 'RGB'
    
    def test_resize_image_failure(self, temp_dir):
        """Test image resizing failure"""
        # Try to resize non-existent file
        input_path = os.path.join(temp_dir, "nonexistent.png")
        output_path = os.path.join(temp_dir, "output.jpg")
        
        result = ImageProcessor.resize_image(input_path, output_path)
        assert result is False
    
    def test_get_image_info_success(self, temp_dir):
        """Test getting image information"""
        # Create test image
        image_path = os.path.join(temp_dir, "test.png")
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(image_path)
        
        # Get image info
        info = ImageProcessor.get_image_info(image_path)
        
        assert info['width'] == 150
        assert info['height'] == 100
        assert info['mode'] == 'RGB'
        assert info['format'] == 'PNG'
    
    def test_get_image_info_failure(self, temp_dir):
        """Test getting image information for non-existent file"""
        image_path = os.path.join(temp_dir, "nonexistent.png")
        info = ImageProcessor.get_image_info(image_path)
        assert info == {}
