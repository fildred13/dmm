"""
Main Flask Application
Refactored to use modular media processor components
"""

import logging
import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect
from werkzeug.utils import secure_filename

from config import MAX_CONTENT_LENGTH, get_last_registry_path, save_last_registry_path
from media_processor.registry import MediaRegistry
from media_processor.media_processor import MediaProcessor
from tagging.tag_registry import TagRegistry

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = 'your-secret-key-here'  # Required for sessions

# Global state management
class AppState:
    """Manages global application state"""
    def __init__(self):
        # Use persistent registry path on startup
        initial_registry_path = get_last_registry_path()
        self.current_registry_path = initial_registry_path
        self.registry = MediaRegistry(initial_registry_path)
        self.media_processor = MediaProcessor(initial_registry_path)
        self.tag_registry = TagRegistry(initial_registry_path)
        logger.info(f"Initialized with registry: {initial_registry_path}")
    
    def update_registry(self, registry_path: str):
        """Update the registry and media processor to use a new registry path"""
        self.current_registry_path = registry_path
        self.registry = MediaRegistry(registry_path)
        self.media_processor = MediaProcessor(registry_path)
        self.tag_registry = TagRegistry(registry_path)
        logger.info(f"Updated registry to: {registry_path}")
        
        # Save the registry path for persistence
        if save_last_registry_path(registry_path):
            logger.info(f"Saved registry path for persistence: {registry_path}")
        else:
            logger.warning(f"Failed to save registry path for persistence: {registry_path}")

# Initialize global state
app_state = AppState()


@app.route('/')
def index():
    """Redirect root to upload page"""
    return redirect('/upload')


@app.route('/upload')
def upload_page():
    """Upload page"""
    return render_template('upload.html')


@app.route('/preview')
def preview_page():
    """Preview page"""
    media_count = app_state.registry.get_media_count()
    return render_template('preview.html', media_count=media_count)


@app.route('/tag-manager')
def tag_manager_page():
    """Tag Manager page"""
    return render_template('tag_manager.html')


@app.route('/tag-by-image')
def tag_by_image_page():
    """Tag By Image page"""
    return render_template('tag_by_image.html')


@app.route('/tag-by-tag')
def tag_by_tag_page():
    """Tag By Tag page"""
    return render_template('tag_by_tag.html')


@app.route('/api/registry/current')
def get_current_registry():
    """Get information about the current registry"""
    return jsonify({
        'path': app_state.registry.get_registry_path(),
        'directory': app_state.registry.get_registry_directory(),
        'name': app_state.registry.get_registry_name(),
        'display_name': app_state.registry.get_display_name(),
        'media_count': app_state.registry.get_media_count()
    })


@app.route('/api/registry/switch', methods=['POST'])
def switch_registry():
    """Switch to a different registry file"""
    data = request.get_json()
    if not data or 'registry_path' not in data:
        return jsonify({'error': 'Registry path is required'}), 400
    
    registry_path = data['registry_path']
    
    # Validate the path
    if not registry_path:
        return jsonify({'error': 'Registry path cannot be empty'}), 400
    
    try:
        # Update components to use the new registry
        app_state.update_registry(registry_path)
        
        # Store in session for persistence within browser session
        session['current_registry'] = registry_path
        
        return jsonify({
            'success': True,
            'registry_info': {
                'path': app_state.registry.get_registry_path(),
                'directory': app_state.registry.get_registry_directory(),
                'name': app_state.registry.get_registry_name(),
                'display_name': app_state.registry.get_display_name(),
                'media_count': app_state.registry.get_media_count()
            }
        })
    except Exception as e:
        logger.error(f"Failed to switch registry: {e}")
        return jsonify({'error': f'Failed to switch registry: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save uploaded file temporarily
    temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
    file.save(temp_path)
    
    try:
        # Calculate hash of uploaded file for duplicate detection
        file_hash = app_state.media_processor.get_file_hash(temp_path)
        
        # Check for duplicates
        duplicate_entry = app_state.registry.find_duplicate_by_hash(file_hash)
        
        if duplicate_entry:
            # This is a duplicate file - skip processing entirely
            return jsonify({
                'success': False,
                'is_duplicate': True,
                'duplicate_info': {
                    'path': duplicate_entry['path'],
                    'index': app_state.registry.get_all_media().index(duplicate_entry)
                },
                'message': f'Duplicate file detected: {file.filename}'
            }), 409  # 409 Conflict
        
        # Process the file (pass registry for filename collision handling)
        relative_path, error = app_state.media_processor.process_media_file(temp_path, app_state.registry)
        
        if error:
            logger.error(f"Failed to process file {file.filename}: {error}")
            return jsonify({'error': error}), 400
        
        # Add to registry with hash
        if app_state.registry.add_media(relative_path, file_hash):
            logger.info(f"Successfully processed and added to registry: {file.filename}")
            return jsonify({
                'success': True,
                'path': relative_path,
                'message': f'Successfully processed {file.filename}'
            })
        else:
            logger.error(f"Failed to save {file.filename} to registry")
            return jsonify({'error': 'Failed to save to registry'}), 500
        
    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/media')
def get_media_list():
    """Get list of all media files"""
    return jsonify(app_state.registry.get_all_media())


@app.route('/api/media/<int:index>')
def get_media_info(index):
    """Get info about a specific media file by index"""
    media_info = app_state.registry.get_media_by_index(index)
    if media_info:
        # Get additional file information including dimensions
        file_path = os.path.join(app_state.media_processor.upload_folder, media_info['path'].split('/')[-1])
        if os.path.exists(file_path):
            try:
                file_info = app_state.media_processor.get_processing_info(file_path)
                # Merge the registry info with file info
                media_info.update(file_info)
            except Exception as e:
                logger.warning(f"Could not get file info for index {index}: {e}")
                # If we can't get file info, just continue with basic info
                pass
        return jsonify(media_info)
    return jsonify({'error': 'Index out of range'}), 404


@app.route('/api/media/<int:index>', methods=['DELETE'])
def delete_media(index):
    """Delete a media file by index"""
    media_info = app_state.registry.get_media_by_index(index)
    if not media_info:
        return jsonify({'error': 'Index out of range'}), 404
    
    try:
        # Remove the file from the media directory
        file_path = os.path.join(app_state.media_processor.upload_folder, media_info['path'].split('/')[-1])
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted media file: {file_path}")
        
        # Remove from registry
        if app_state.registry.remove_media_by_index(index):
            return jsonify({'success': True, 'message': 'Media deleted successfully'})
        else:
            logger.error(f"Failed to remove media at index {index} from registry")
            return jsonify({'error': 'Failed to remove from registry'}), 500
    except Exception as e:
        logger.error(f"Failed to delete media at index {index}: {e}")
        return jsonify({'error': f'Failed to delete media: {str(e)}'}), 500


@app.route('/api/media/count')
def get_media_count():
    """Get the total number of media files"""
    return jsonify({'count': app_state.registry.get_media_count()})


@app.route('/<folder_name>/<path:filename>')
def serve_media(folder_name, filename):
    """Serve media files from the current registry's media directory"""
    # Verify that the folder name matches the current upload folder
    current_folder_name = os.path.basename(app_state.media_processor.upload_folder)
    if folder_name != current_folder_name:
        return jsonify({'error': 'Invalid media path'}), 404
    
    return send_from_directory(app_state.media_processor.upload_folder, filename)


# Initialize with session registry if available
def initialize_registry():
    """Initialize the registry from session if available"""
    try:
        if 'current_registry' in session:
            app_state.update_registry(session['current_registry'])
            logger.info(f"Initialized registry from session: {session['current_registry']}")
    except RuntimeError:
        # Session not available (e.g., during testing or module import)
        logger.debug("Session not available during initialization")
        pass

# Call initialization function
initialize_registry()


if __name__ == '__main__':
    app.run(debug=True)
