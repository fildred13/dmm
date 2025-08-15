"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import os
import json
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def temp_media_dir(temp_dir):
    """Create a temporary media directory for testing"""
    media_dir = os.path.join(temp_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    return media_dir


@pytest.fixture
def temp_registry_file(temp_dir):
    """Create a temporary registry file for testing"""
    registry_file = os.path.join(temp_dir, "test_registry.json")
    # Create empty registry file
    with open(registry_file, 'w') as f:
        json.dump([], f)
    return registry_file


@pytest.fixture
def sample_registry_data():
    """Sample registry data for testing"""
    return [
        {"path": "media/test1.png"},
        {"path": "media/test2.mp4"},
        {"path": "media/test3.jpg"}
    ]


@pytest.fixture
def sample_registry_file(temp_dir, sample_registry_data):
    """Create a sample registry file for testing"""
    registry_file = os.path.join(temp_dir, "test_registry.json")
    with open(registry_file, 'w') as f:
        json.dump(sample_registry_data, f, indent=2)
    return registry_file


@pytest.fixture
def sample_image_file(temp_dir):
    """Create a sample image file for testing"""
    from PIL import Image
    import numpy as np
    
    # Create a simple test image
    img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    image_path = os.path.join(temp_dir, "test_image.png")
    img.save(image_path)
    return image_path


@pytest.fixture
def sample_video_file(temp_dir):
    """Create a sample video file for testing"""
    video_path = os.path.join(temp_dir, "test_video.mp4")
    # Create a dummy video file
    with open(video_path, 'w') as f:
        f.write("dummy video content")
    return video_path


@pytest.fixture
def isolated_test_env(temp_dir, temp_media_dir, temp_registry_file):
    """Create an isolated test environment with temporary media and registry"""
    # Create the test environment
    test_env = {
        'temp_dir': temp_dir,
        'media_dir': temp_media_dir,
        'registry_file': temp_registry_file
    }
    
    yield test_env
    
    # Cleanup is handled by tempfile.TemporaryDirectory context manager


@pytest.fixture
def mock_ffmpeg_probe(mocker):
    """Mock ffmpeg.probe for video testing"""
    mock_probe = mocker.patch('ffmpeg.probe')
    mock_probe.return_value = {
        'streams': [
            {
                'codec_type': 'video',
                'width': 1920,
                'height': 1080,
                'codec_name': 'h264'
            },
            {
                'codec_type': 'audio',
                'codec_name': 'aac'
            }
        ],
        'format': {
            'duration': '10.5',
            'bit_rate': '1000000'
        }
    }
    return mock_probe


@pytest.fixture
def mock_ffmpeg_run(mocker):
    """Mock ffmpeg.run for video testing"""
    mock_run = mocker.patch('ffmpeg.run')
    mock_run.return_value = None
    return mock_run


@pytest.fixture
def mock_ffmpeg_input(mocker):
    """Mock ffmpeg.input for video testing"""
    mock_input = mocker.patch('ffmpeg.input')
    mock_stream = mocker.Mock()
    mock_input.return_value = mock_stream
    mock_stream.output.return_value = mock_stream
    return mock_input

@pytest.fixture
def mock_ffmpeg_output(mocker):
    """Mock ffmpeg.output for video testing"""
    mock_output = mocker.patch('ffmpeg.output')
    mock_stream = mocker.Mock()
    mock_output.return_value = mock_stream
    return mock_output

@pytest.fixture
def mock_ffmpeg_stream(mocker):
    """Mock ffmpeg stream for video testing"""
    # Create a proper mock that simulates the ffmpeg stream chaining
    mock_stream = mocker.Mock()
    
    # Mock the input method
    mock_input = mocker.patch('ffmpeg.input')
    mock_input.return_value = mock_stream
    
    # Mock the output method
    mock_output = mocker.patch('ffmpeg.output')
    mock_output.return_value = mock_stream
    
    # Mock the run method
    mock_run = mocker.patch('ffmpeg.run')
    mock_run.return_value = None
    
    return {
        'stream': mock_stream,
        'input': mock_input,
        'output': mock_output,
        'run': mock_run
    }
