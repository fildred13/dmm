# Media Management Tool

A comprehensive media management and pipelining tool for game development, built with Python Flask and modern web technologies.

## 🏗️ **Project Structure**

The project has been refactored into a modular architecture for better maintainability and extensibility:

```
dmm/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── media_registry.json         # Media registry (auto-generated)
├── media/                      # Processed media files (auto-generated)
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Home page
│   ├── upload.html            # Upload interface
│   └── preview.html           # Preview interface
├── media_processor/            # Core processing modules
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration settings
│   ├── registry.py            # Media registry management
│   ├── file_utils.py          # File utilities and validation
│   ├── image_processor.py     # Image processing operations
│   ├── video_processor.py     # Video processing operations
│   └── media_processor.py     # Main processing orchestrator
└── README.md                  # This file
```

## 🎯 **Core Functionality**

- **Automatic Media Processing**: Resizes all media to max 576×1024 while preserving aspect ratio
- **Format Conversion**: Converts to supported output formats (.webm, .mp4, .png, .gif, .jpg)
- **Centralized Registry**: JSON-based media registry for easy asset management
- **Batch Upload**: Support for multiple file uploads with drag & drop
- **Preview System**: Beautiful media preview with navigation controls

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
- **Images**: PNG, GIF, JPG
- **Videos**: WEBM, MP4

## 🏗️ **Modular Architecture**

### **Core Modules:**

1. **`config.py`** - Centralized configuration
   - File format definitions
   - Processing parameters
   - Directory settings

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

## 🚀 **Installation**

### Prerequisites
- Python 3.8 or higher
- FFmpeg (for video processing)

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

### Upload Mode
1. Navigate to the "Upload" page
2. Drag and drop files or click "Choose Files"
3. Watch as files are automatically processed and added to the registry
4. Supported formats will be converted and resized automatically

### Preview Mode
1. Navigate to the "Preview" page
2. Use the arrow buttons or keyboard arrow keys to navigate
3. View media information including filename and path
4. Videos can be played with standard video controls

## 🔧 **Technical Details**

### Media Processing
- **Image Processing**: Uses Pillow (PIL) for resizing and format conversion
- **Video Processing**: Uses FFmpeg for video resizing and format conversion
- **Aspect Ratio**: Maintains original aspect ratio while fitting within max dimensions
- **Quality**: High-quality output with optimized compression settings

### Registry System
The `media_registry.json` file contains a simple list of media entries:
```json
[
  {"path": "media/filename.png"},
  {"path": "media/video.mp4"}
]
```

This structure allows for easy expansion to include tags, metadata, and other properties in future iterations.

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
