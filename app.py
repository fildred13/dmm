"""
Main Flask Application
Refactored to use modular media processor components
"""

import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from media_processor.config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from media_processor.registry import MediaRegistry
from media_processor.media_processor import MediaProcessor

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize components
registry = MediaRegistry()
media_processor = MediaProcessor()



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
        # Process the file
        relative_path, error = media_processor.process_media_file(temp_path)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Add to registry
        if registry.add_media(relative_path):
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
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], media_info['path'].split('/')[-1])
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
    try:
        media_info = registry.get_media_by_index(index)
        if not media_info:
            return jsonify({'error': 'Index out of range'}), 404
        
        # Get the file path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], media_info['path'].split('/')[-1])
        
        # Delete the file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from registry
        registry.remove_media_by_index(index)
        
        return jsonify({'message': 'Media file deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Error deleting media file: {str(e)}'}), 500

@app.route('/api/media/count')
def get_media_count():
    """Get the total number of media files"""
    return jsonify({'count': registry.get_media_count()})

@app.route('/media/<path:filename>')
def serve_media(filename):
    """Serve media files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
