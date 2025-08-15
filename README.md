# Media Management Tool

A comprehensive media management and pipelining tool for game development, built with Python Flask and modern web technologies.

## 🏗️ **Project Structure**

The project has been refactored into a modular architecture for better maintainability and extensibility:

```
dmm/
├── app.py                      # Main Flask application
├── config.py                   # Global application configuration
├── requirements.txt            # Python dependencies
├── media_registry.json         # Media registry (auto-generated)
├── tag_registry.json           # Tag registry (auto-generated)
├── .dmm_config.json           # App configuration (auto-generated)
├── media/                      # Processed media files (auto-generated)
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── upload.html            # Upload interface
│   ├── preview.html           # Preview interface
│   ├── tag_manager.html       # Tag management interface
│   ├── tag_by_image.html      # Tag by image interface
│   └── tag_by_tag.html        # Tag by tag interface
├── media_processor/            # Core media processing modules
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Media processing configuration
│   ├── registry.py            # Media registry management
│   ├── file_utils.py          # File utilities and validation
│   ├── image_processor.py     # Image processing operations
│   ├── video_processor.py     # Video processing operations
│   └── media_processor.py     # Main processing orchestrator
├── tagging/                    # Tagging system modules
│   ├── __init__.py            # Package initialization
│   └── tag_registry.py        # Tag registry management
└── README.md                  # This file
```

## 🎯 **Core Functionality**

- **Automatic Media Processing**: Resizes all media to max 576×1024 while preserving aspect ratio
- **Format Conversion**: Converts to supported output formats (.webm, .png, .jpg)
- **Dynamic Registry System**: Switch between different media registries on any path on your system
- **Centralized Registry**: JSON-based media registry for easy asset management
- **Batch Upload**: Support for multiple file uploads with drag & drop
- **Preview System**: Beautiful media preview with navigation controls
- **Delete Functionality**: Delete media files with confirmation dialog
- **Chronological Ordering**: Media files ordered by upload time (most recent first)
- **Duplicate Detection**: Hash-based duplicate detection with visual indicators and quick access to existing files
- **Tagging System**: Comprehensive tagging system for organizing and categorizing media files

## 🏷️ **Tagging System**

The tool includes a powerful tagging system for organizing your media files:

### **Tag Registry Structure**
Every `media_registry.json` automatically gets a corresponding `tag_registry.json` file in the same directory:

```json
{
  "tags": {
    "character": {
      "description": "Character-related content",
      "category": "content_type"
    }
  },
  "media_tags": {
    "media/character_sprite.png": ["character", "sprite", "player"]
  },
  "tag_categories": {
    "content_type": {
      "description": "Type of content",
      "color": "#ff0000"
    }
  },
  "version": "1.0"
}
```

### **Tagging Interfaces**

1. **Tag Manager** (`/tag-manager`)
   - View all tags in the active registry
   - Create and manage tag categories
   - Add, edit, and delete tags
   - See tag usage statistics
   - Organize your tagging system

2. **Tag By Image** (`/tag-by-image`)
   - Browse through media files visually
   - View images and videos in gallery format
   - Select multiple files for batch tagging
   - Apply tags to individual or multiple files
   - See existing tags on files
   - Quick tag suggestions based on content

3. **Tag By Tag** (`/tag-by-tag`)
   - Browse and select tags from your tag library
   - Find media files that need specific tags
   - Apply tags to multiple files at once
   - See which files are missing certain tags
   - Filter and search media by tag criteria
   - Manage tag relationships and hierarchies

### **Automatic Tag Registry Creation**
- Tag registry files are automatically created when you first use tagging features
- Each registry maintains its own tag data independently
- Tag data persists across app sessions
- Tag registry files are excluded from version control for privacy

## 🎨 **User Interface**

- **Modern Web GUI**: Responsive design with beautiful gradients and animations
- **Drag & Drop Upload**: Intuitive file upload interface
- **Media Preview**: Full-screen preview with keyboard navigation (arrow keys)
- **Real-time Processing**: Live progress indicators and status updates

## 📁 **Supported Formats**

**Input Formats:**
- **Images**: JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP
- **Videos**: MP4, AVI, MOV, MKV, WEBM, FLV, WMV

**Output Formats:**
- **Images**: PNG, JPG
- **Videos**: WEBM (all videos are converted to WebM format)

**Special Handling:**
- **Animated GIFs**: Converted to animated WEBM videos
- **Animated WebPs**: Converted to animated WEBM videos
- **Static GIFs**: Converted to PNG images
- **Static WebPs**: Converted to PNG images

## 🔍 **Duplicate Detection**

The tool includes intelligent duplicate detection to prevent accidental re-uploads:

- **Hash-Based Detection**: Uses MD5 hashing to identify duplicate files by content, not just filename
- **Visual Indicators**: Duplicate files are highlighted with orange styling and clear labels
- **Quick Access**: Click "View duplicate" to open the existing file in preview mode
- **Content-Aware**: Different files with the same name are treated as unique, while identical files with different names are detected as duplicates
- **Efficient Processing**: Hash calculation is fast and doesn't impact upload performance

**How It Works:**
1. When a file is uploaded, its content is hashed using MD5
2. The hash is compared against all existing files in the registry
3. If a match is found, the upload is flagged as a duplicate and processing is skipped entirely
4. The user can click to view the existing file for verification
5. Non-duplicate files proceed with normal processing and storage
6. If files have the same name but different content, a unique `-<integer>` suffix is automatically added

**Upload History:**
- Upload results persist until explicitly cleared with the "Clear Upload History" button
- **Automatic persistence** - Upload history is saved to browser localStorage and survives page refreshes/navigation
- **Visual indicator** - Clear message shows that upload history is automatically saved
- **Batch review capability** - Can handle multiple upload batches and review all results without losing context
- **Safe duplicate viewing** - "View duplicate" links open in new tabs without affecting the upload page
- **Manual control** - Clear button appears automatically when uploads are completed
- **Smart UI sync** - Upload status automatically syncs with server when returning to the page
- **Background processing** - Files continue processing on server even if you navigate away
- **Real-time updates** - UI updates to show actual processing results when you return

## 🏗️ **Modular Architecture**

### **Core Modules:**

#### **Global Configuration (`config.py`):**
1. **`config.py`** - Global application configuration
   - Flask settings (MAX_CONTENT_LENGTH)
   - Registry persistence (get_last_registry_path, save_last_registry_path)
   - Path utilities (get_media_folder_from_registry, get_tag_registry_path)
   - App configuration file management

#### **Media Processing (`media_processor/`):**
1. **`config.py`** - Media processing configuration
   - File format definitions
   - Processing parameters (dimensions, quality)
   - Dimension calculation algorithms

2. **`registry.py`** - Media registry management
   - JSON file operations
   - Media entry management
   - Registry validation

3. **`file_utils.py`** - File operations
   - Type detection
   - Path normalization
   - Format validation

4. **`image_processor.py`** - Image processing
   - Resizing algorithms
   - Format conversion
   - Quality optimization

5. **`video_processor.py`** - Video processing
   - FFmpeg integration
   - Codec selection
   - Dimension calculation

6. **`media_processor.py`** - Main orchestrator
   - Workflow coordination
   - Error handling
   - Processing pipeline

#### **Tagging System (`tagging/`):**
1. **`tag_registry.py`** - Tag registry management
   - Tag CRUD operations
   - Media-tag associations
   - Tag category management
   - Registry persistence

## 🚀 **Installation**

### Prerequisites
- Python 3.8 or higher
- FFmpeg (for video processing)
- ImageMagick (for animated WebP processing) - automatically installed via Wand Python package

### FFmpeg Installation

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Setup

1. **Clone or download the project**
2. **Create and activate virtual environment:**
   
   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   ```
   
   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

### Quick Start Scripts

For Windows users, you can use the provided batch files:

- **`activate_venv.bat`** - Activates the virtual environment
- **`run_app.bat`** - Runs the Flask application
- **`run_tests.bat`** - Runs the test suite with coverage

Simply double-click these files or run them from the command line.

## 📖 **Usage**

### Registry Management
1. **Current Registry**: The navbar displays the current registry path and media count
2. **Switch Registry**: Click the "Switch" button in the navbar to change to a different registry
3. **Registry Path**: Enter the full path to any `media_registry.json` file on your system
4. **Auto Media Directory**: The tool automatically creates/uses a `media/` folder relative to the registry file

### Upload Mode
1. Navigate to the "Upload" page
2. Drag and drop files or click "Choose Files"
3. Watch as files are automatically processed and added to the current registry
4. Supported formats will be converted and resized automatically

### Preview Mode
1. Navigate to the "Preview" page
2. Use the arrow buttons or keyboard arrow keys to navigate
3. View media information including filename and path
4. Videos can be played with standard video controls

## 🔧 **Technical Details**

### Media Processing
- **Image Processing**: Uses Pillow (PIL) for resizing and format conversion
- **Video Processing**: Uses FFmpeg for video resizing and format conversion (all videos converted to WebM)
- **Animated WebP Processing**: Uses Wand (ImageMagick) for reliable animated WebP to WebM conversion
- **Aspect Ratio**: Maintains original aspect ratio while fitting within max dimensions
- **Quality**: High-quality output with optimized compression settings

### Registry System
The `media_registry.json` file contains a simple list of media entries:
```json
[
  {"path": "media/filename.png"},
  {"path": "media/video.webm"}
]
```

This structure allows for easy expansion to include tags, metadata, and other properties in future iterations.

### Dynamic Registry Paths
- **Registry Location**: The tool can work with `media_registry.json` files located anywhere on your system
- **Media Directory**: For each registry file at `/path/to/media_registry.json`, the tool automatically uses `/path/to/media/` for storing processed files
- **Session Persistence**: Your current registry selection is remembered across browser sessions
- **Cross-Platform**: Registry paths work on Windows, macOS, and Linux

### Cross-Platform Compatibility
- All paths use forward slashes (`/`) for cross-platform compatibility
- Registry files are compatible with any operating system
- Media files are processed consistently across platforms

### Security Features
- File type validation
- Secure filename handling
- Maximum file size limits (100MB)
- Temporary file cleanup

## 🔮 **Future Enhancements**

The modular architecture makes it easy to add new features:

### **Planned Features:**
- **Tagging System**: Add tags and categories to media files
- **Search & Filter**: Find media by tags, filename, or metadata
- **Bulk Operations**: Select multiple files for batch operations
- **Metadata Editing**: Edit file properties and descriptions
- **Export Options**: Export media lists and metadata
- **Thumbnail Generation**: Automatic thumbnail creation for videos

### **Easy Extension Points:**
- Add new processors in `media_processor/`
- Extend registry schema in `registry.py`
- Add new file formats in `config.py`
- Create new API endpoints in `app.py`

## 🧪 **Testing**

The project includes a comprehensive test suite using pytest to ensure code quality and reliability.

### **Test Structure**
```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_config.py           # Configuration module tests
├── test_file_utils.py       # File utilities tests
├── test_registry.py         # Registry management tests
├── test_image_processor.py  # Image processing tests
├── test_video_processor.py  # Video processing tests
├── test_media_processor.py  # Main processor tests
├── test_app.py              # Flask application tests
└── run_tests.py             # Test runner script
```

### **Running Tests**

**Install test dependencies:**
```bash
pip install pytest pytest-cov pytest-mock
```

**Run all tests with coverage:**
```bash
# Make sure virtual environment is activated first
python -m pytest
```

**Run specific test modules:**
```bash
python -m pytest tests/test_config.py -v
python -m pytest tests/test_registry.py -v
python -m pytest tests/test_image_processor.py -v
```

**Run tests with coverage report:**
```bash
python -m pytest --cov=media_processor --cov=app --cov-report=html
```

**Use the test runner script:**
```bash
python tests/run_tests.py
```

**Windows users can use the batch file:**
```cmd
run_tests.bat
```

### **Test Coverage**

The test suite provides comprehensive coverage for:
- ✅ **Configuration Management**: All settings and constants
- ✅ **File Utilities**: Type detection, path normalization, format validation
- ✅ **Registry Management**: JSON operations, media entry management
- ✅ **Image Processing**: Resizing, format conversion, error handling
- ✅ **Video Processing**: FFmpeg integration, codec selection, dimension calculation
- ✅ **Main Processor**: Workflow orchestration, error handling
- ✅ **Flask Application**: API endpoints, file uploads, media serving

### **Test Features**

- **Mocked Dependencies**: FFmpeg operations are mocked for reliable testing
- **Temporary Files**: Tests use temporary directories for file operations
- **Error Scenarios**: Comprehensive error handling and edge case testing
- **Cross-Platform**: Tests work on Windows, macOS, and Linux
- **Coverage Reports**: HTML and XML coverage reports generated automatically

## 🛠️ **Development**

### **Adding New Features:**
1. **New File Format**: Update `config.py` with format definitions
2. **New Processor**: Create new module in `media_processor/`
3. **New API**: Add routes in `app.py`
4. **New UI**: Create templates in `templates/`

### **Writing Tests:**
1. **Follow Naming**: Test files should be named `test_*.py`
2. **Use Fixtures**: Leverage shared fixtures in `conftest.py`
3. **Mock External Dependencies**: Use `pytest-mock` for external services
4. **Test Edge Cases**: Include error scenarios and boundary conditions
5. **Maintain Coverage**: Aim for >90% test coverage for new features

### **Testing Best Practices:**
- Write tests for all new functionality
- Use descriptive test names and docstrings
- Test both success and failure scenarios
- Mock external dependencies (FFmpeg, file system)
- Use temporary directories for file operations
- Run tests before committing changes

## 🐛 **Troubleshooting**

### Common Issues

**FFmpeg not found:**
- Ensure FFmpeg is installed and in your system PATH
- Restart your terminal/command prompt after installation

**Video processing fails:**
- Check that input video format is supported
- Ensure sufficient disk space for processing
- Verify FFmpeg installation with `ffmpeg -version`

**Upload fails:**
- Check file size (max 100MB)
- Verify file format is supported
- Ensure media directory has write permissions

### Performance Tips
- Large video files may take time to process
- Consider processing videos in smaller batches
- Monitor disk space during large uploads

## 📄 **License**

This project is open source and available under the MIT License.

## 🤝 **Contributing**

Feel free to submit issues, feature requests, or pull requests to improve the tool!

### **Development Guidelines:**
- Follow the modular architecture
- Add type hints to new functions
- Include docstrings for new classes and methods
- Test new features thoroughly
- Update documentation as needed
