"""
Main Flask Application
Refactored to use modular media processor components
"""

import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename

from media_processor.config import MAX_CONTENT_LENGTH, DEFAULT_REGISTRY_FILE
from media_processor.registry import MediaRegistry
from media_processor.media_processor import MediaProcessor

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = 'your-secret-key-here'  # Required for sessions

# Initialize components with default registry
current_registry_path = DEFAULT_REGISTRY_FILE
registry = MediaRegistry(current_registry_path)
media_processor = MediaProcessor(current_registry_path)


def update_components(registry_path: str):
    """Update the registry and media processor to use a new registry path"""
    global registry, media_processor, current_registry_path
    current_registry_path = registry_path
    registry = MediaRegistry(registry_path)
    media_processor = MediaProcessor(registry_path)


@app.route('/')
def index():
    """Main page with navigation"""
    return render_template('index.html')


@app.route('/upload')
def upload_page():
    """Upload page"""
    return render_template('upload.html')


@app.route('/preview')
def preview_page():
    """Preview page"""
    media_count = registry.get_media_count()
    return render_template('preview.html', media_count=media_count)


@app.route('/api/registry/current')
def get_current_registry():
    """Get information about the current registry"""
    return jsonify({
        'path': registry.get_registry_path(),
        'directory': registry.get_registry_directory(),
        'name': registry.get_registry_name(),
        'display_name': registry.get_display_name(),
        'media_count': registry.get_media_count()
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
        update_components(registry_path)
        
        # Store in session for persistence
        session['current_registry'] = registry_path
        
        return jsonify({
            'success': True,
            'registry_info': {
                'path': registry.get_registry_path(),
                'directory': registry.get_registry_directory(),
                'name': registry.get_registry_name(),
                'display_name': registry.get_display_name(),
                'media_count': registry.get_media_count()
            }
        })
    except Exception as e:
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
        file_hash = media_processor.get_file_hash(temp_path)
        
        # Check for duplicates
        duplicate_entry = registry.find_duplicate_by_hash(file_hash)
        
        if duplicate_entry:
            # This is a duplicate file - skip processing entirely
            return jsonify({
                'success': False,
                'is_duplicate': True,
                'duplicate_info': {
                    'path': duplicate_entry['path'],
                    'index': registry.get_all_media().index(duplicate_entry)
                },
                'message': f'Duplicate file detected: {file.filename}'
            }), 409  # 409 Conflict
        
        # Process the file (pass registry for filename collision handling)
        relative_path, error = media_processor.process_media_file(temp_path, registry)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Add to registry with hash
        if registry.add_media(relative_path, file_hash):
            return jsonify({
                'success': True,
                'path': relative_path,
                'message': f'Successfully processed {file.filename}'
            })
        else:
            return jsonify({'error': 'Failed to save to registry'}), 500
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/media')
def get_media_list():
    """Get list of all media files"""
    return jsonify(registry.get_all_media())


@app.route('/api/media/<int:index>')
def get_media_info(index):
    """Get info about a specific media file by index"""
    media_info = registry.get_media_by_index(index)
    if media_info:
        # Get additional file information including dimensions
        file_path = os.path.join(media_processor.upload_folder, media_info['path'].split('/')[-1])
        if os.path.exists(file_path):
            try:
                file_info = media_processor.get_processing_info(file_path)
                # Merge the registry info with file info
                media_info.update(file_info)
            except Exception as e:
                # If we can't get file info, just continue with basic info
                pass
        return jsonify(media_info)
    return jsonify({'error': 'Index out of range'}), 404


@app.route('/api/media/<int:index>', methods=['DELETE'])
def delete_media(index):
    """Delete a media file by index"""
    media_info = registry.get_media_by_index(index)
    if not media_info:
        return jsonify({'error': 'Index out of range'}), 404
    
    try:
        # Remove the file from the media directory
        file_path = os.path.join(media_processor.upload_folder, media_info['path'].split('/')[-1])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from registry
        if registry.remove_media_by_index(index):
            return jsonify({'success': True, 'message': 'Media deleted successfully'})
        else:
            return jsonify({'error': 'Failed to remove from registry'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to delete media: {str(e)}'}), 500


@app.route('/api/media/count')
def get_media_count():
    """Get the total number of media files"""
    return jsonify({'count': registry.get_media_count()})


@app.route('/media/<path:filename>')
def serve_media(filename):
    """Serve media files from the current registry's media directory"""
    return send_from_directory(media_processor.upload_folder, filename)


# Initialize with session registry if available
def initialize_registry():
    """Initialize the registry from session if available"""
    try:
        if 'current_registry' in session:
            update_components(session['current_registry'])
    except RuntimeError:
        # Session not available (e.g., during testing or module import)
        pass

# Call initialization function
initialize_registry()


if __name__ == '__main__':
    app.run(debug=True)
