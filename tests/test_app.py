"""
Tests for Flask application
"""

import pytest
import json
import os
from unittest.mock import patch
from PIL import Image
import numpy as np
from app import app
from media_processor.registry import MediaRegistry


@pytest.fixture
def client(temp_dir):
    """Create a test client with isolated test environment"""
    # Create test registry file
    test_registry_file = os.path.join(temp_dir, "test_registry.json")
    test_data = []
    with open(test_registry_file, 'w') as f:
        json.dump(test_data, f)
    
    # Temporarily patch the global app_state to use test files
    from media_processor.registry import MediaRegistry
    from media_processor.media_processor import MediaProcessor
    import app as app_module
    
    # Store original app_state
    original_app_state = app_module.app_state
    
    # Create test instances
    test_registry = MediaRegistry(test_registry_file)
    test_media_processor = MediaProcessor(test_registry_file)
    
    # Create new app_state with test instances
    class TestAppState:
        def __init__(self):
            self.current_registry_path = test_registry_file
            self.registry = test_registry
            self.media_processor = test_media_processor
        
        def update_registry(self, registry_path: str):
            self.current_registry_path = registry_path
            self.registry = MediaRegistry(registry_path)
            self.media_processor = MediaProcessor(registry_path)
    
    # Patch the global app_state
    app_module.app_state = TestAppState()
    
    # Mock the config functions to prevent any real config file access
    with patch('config.get_last_registry_path', return_value=test_registry_file), \
         patch('config.save_last_registry_path', return_value=True):
        
        with app.test_client() as client:
            yield client
    
    # Restore original app_state
    app_module.app_state = original_app_state


@pytest.fixture
def test_image_file(temp_dir):
    """Create a test image file in temporary directory"""
    # Create test media directory
    test_media_dir = os.path.join(temp_dir, "test_media")
    os.makedirs(test_media_dir, exist_ok=True)
    
    # Create test image
    img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img_path = os.path.join(test_media_dir, "test_image.jpg")
    img.save(img_path)
    
    return img_path


class TestAppRoutes:
    """Test Flask application routes"""
    
    def test_index_route(self, client):
        """Test index route redirects to upload"""
        response = client.get('/')
        assert response.status_code == 302  # Redirect status code
        assert response.location == '/upload'
    
    def test_upload_route(self, client):
        """Test upload route"""
        response = client.get('/upload')
        assert response.status_code == 200
        assert b'Upload' in response.data
    
    def test_preview_route(self, client):
        """Test preview route"""
        response = client.get('/preview')
        assert response.status_code == 200
        assert b'Preview' in response.data
    
    def test_media_list_api(self, client):
        """Test media list API"""
        response = client.get('/api/media')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_media_info_api_valid_index(self, client, temp_dir):
        """Test media info API with valid index"""
        # Add test media to the temporary registry
        test_registry_file = os.path.join(temp_dir, "test_registry.json")
        test_data = [
            {"path": "media/test1.png"},
            {"path": "media/test2.mp4"}
        ]
        with open(test_registry_file, 'w') as f:
            json.dump(test_data, f)
        
        # Reload the registry to pick up the new data
        import app as app_module
        app_module.app_state.registry.load()
        
        response = client.get('/api/media/0')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['path'] == 'media/test1.png'
    
    def test_media_info_api_invalid_index(self, client):
        """Test media info API with invalid index"""
        response = client.get('/api/media/999')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Index out of range'
    
    def test_media_count_api(self, client):
        """Test media count API"""
        response = client.get('/api/media/count')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'count' in data
        assert isinstance(data['count'], int)
    
    def test_current_registry_api(self, client):
        """Test current registry API"""
        response = client.get('/api/registry/current')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'path' in data
        assert 'directory' in data
        assert 'name' in data
        assert 'display_name' in data
        assert 'media_count' in data
        assert isinstance(data['media_count'], int)
    
    def test_switch_registry_api_success(self, client, temp_dir):
        """Test switching registry API with success"""
        # Create a new registry file
        new_registry_file = os.path.join(temp_dir, "new_registry.json")
        with open(new_registry_file, 'w') as f:
            json.dump([], f)
        
        response = client.post('/api/registry/switch', 
                             json={'registry_path': new_registry_file})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'registry_info' in data
        assert data['registry_info']['path'] == os.path.abspath(new_registry_file)
    
    def test_switch_registry_api_missing_path(self, client):
        """Test switching registry API with missing path"""
        response = client.post('/api/registry/switch', json={})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Registry path is required' in data['error']
    
    def test_switch_registry_api_empty_path(self, client):
        """Test switching registry API with empty path"""
        response = client.post('/api/registry/switch', json={'registry_path': ''})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Registry path cannot be empty' in data['error']
    
    def test_serve_media(self, client, test_image_file, temp_dir):
        """Test serving media files"""
        # Create a test file in the media directory that corresponds to the test registry
        test_media_dir = os.path.join(temp_dir, "media")
        os.makedirs(test_media_dir, exist_ok=True)
        test_file = os.path.join(test_media_dir, 'test.jpg')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        response = client.get('/media/test.jpg')
        assert response.status_code == 200
        assert response.data == b'test content'
    
    def test_delete_media_api_success(self, client, temp_dir):
        """Test successful media deletion"""
        # Create a test file in the test media directory
        test_media_dir = os.path.join(temp_dir, "media")
        os.makedirs(test_media_dir, exist_ok=True)
        test_file = os.path.join(test_media_dir, "test_delete.jpg")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Add to registry (the client fixture already sets up a test registry)
        import app as app_module
        app_module.app_state.registry.add_media("test_delete.jpg")
        
        # Test deletion
        response = client.delete('/api/media/0')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'deleted successfully' in data['message']
    
    def test_delete_media_api_invalid_index(self, client):
        """Test media deletion with invalid index"""
        response = client.delete('/api/media/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Index out of range' in data['error']


class TestUploadAPI:
    """Test upload API functionality"""
    
    def test_upload_no_file(self, client):
        """Test upload without file"""
        response = client.post('/api/upload')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error'] == 'No file provided'
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename"""
        response = client.post('/api/upload', data={'file': (None, '')})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error'] == 'No file selected'
    
    def test_upload_unsupported_format(self, client):
        """Test upload with unsupported file format"""
        # Create a file-like object for testing
        from io import BytesIO
        file_data = BytesIO(b'test content')
        
        response = client.post('/api/upload', data={
            'file': (file_data, 'test.txt')
        })
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error'] == 'Unsupported file type'
    
    def test_upload_image_success(self, client, temp_dir):
        """Test successful image upload"""
        # Create test image
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img_path = os.path.join(temp_dir, 'test.jpg')
        img.save(img_path)
        
        with open(img_path, 'rb') as f:
            response = client.post('/api/upload', data={
                'file': (f, 'test.jpg')
            })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'path' in data
        assert data['message'] == 'Successfully processed test.jpg'
    
    def test_upload_image_format_conversion(self, client, temp_dir):
        """Test image upload with format conversion"""
        # Create test image in unsupported format
        img_array = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img_path = os.path.join(temp_dir, 'test.bmp')
        img.save(img_path)
        
        with open(img_path, 'rb') as f:
            response = client.post('/api/upload', data={
                'file': (f, 'test.bmp')
            })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['path'].endswith('.png')  # Should convert to PNG
    
    def test_upload_video_success(self, client, temp_dir, mock_ffmpeg_probe, mock_ffmpeg_stream):
        """Test successful video upload"""
        # Create test video file
        video_path = os.path.join(temp_dir, 'test.avi')
        with open(video_path, 'w') as f:
            f.write('dummy video content')
        
        with open(video_path, 'rb') as f:
            response = client.post('/api/upload', data={
                'file': (f, 'test.avi')
            })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'path' in data
        assert data['message'] == 'Successfully processed test.avi'
    
    def test_upload_video_failure(self, client, temp_dir, mock_ffmpeg_probe):
        """Test video upload failure"""
        # Mock ffmpeg.probe to raise an exception
        mock_ffmpeg_probe.side_effect = Exception("FFmpeg error")
        
        # Create test video file
        video_path = os.path.join(temp_dir, 'test.avi')
        with open(video_path, 'w') as f:
            f.write('dummy video content')
        
        with open(video_path, 'rb') as f:
            response = client.post('/api/upload', data={
                'file': (f, 'test.avi')
            })
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Failed to process video' in data['error']
