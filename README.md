# Speed Reader

[![CI](https://github.com/yourusername/speed-reader/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/speed-reader/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A cross-platform speed reading application that displays one word at a time. Supports PDF, EPUB, Word documents (.docx), and plain text files. Perfect for improving reading speed and comprehension.

## Features

- **Multiple File Formats**: Supports PDF, EPUB, Word documents (.docx), and plain text files
- **Paste Text**: Paste text directly from clipboard
- **Customizable Speed**: Adjustable words per minute (WPM) from 50 to 1000 with speed presets and history
- **Enhanced Position Selection**:
  - See page numbers, chapter information, and percentage progress
  - Context preview showing surrounding text
  - Visual reference points like Calibre
- **Text-to-Speech**: Optional TTS that reads words aloud, automatically matching your WPM speed
- **Progress Tracking**: Visual progress bar and word counter with detailed statistics
- **File History**: Remembers recently opened files and reading positions
- **Speed Memory**: Remembers your preferred reading speed between sessions
- **Responsive UI**: Adapts to different window sizes with proper scaling and compact layouts
- **Dynamic Font Scaling**: Reading display font size automatically adjusts based on window dimensions
- **Menu Bar**: Top-level menu with File, View, and Help options for better organization
- **Fullscreen Mode**: Distraction-free reading with large text display and surrounding word context
- **Keyboard Shortcuts**:
  - `Space` - Play/Pause
  - `Left Arrow` - Previous word
  - `Right Arrow` - Next word
  - `R` - Reset to beginning
  - `F11` - Toggle fullscreen
  - `Escape` - Exit fullscreen
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Responsive UI**: Resizable window with compact, modern interface

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running from Source

Run the application:

```bash
python run.py
```

On first run, the app may download NLTK part-of-speech data (for the "Color by part of speech" feature); you'll see a one-time download message in the console.

Or directly:

```bash
python -m src.speed_reader.main
```

### Building an Executable

To create a standalone executable that can run without Python installed:

**Option 1 - Complete Build (Recommended):**
Run all tests, build executable, and create Python packages in one command:

**Windows:**
```bash
scripts\build_all.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/build_all.sh
./scripts/build_all.sh
```

**Option 2 - Individual Components:**
Build only the executable:

**Windows:**
```bash
scripts\build.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

The executable will be created in the `dist/` folder:
- Windows: `dist/SpeedReader.exe`
- Linux/macOS: `dist/SpeedReader`

You can distribute this executable to other computers without requiring Python installation.

### Loading a File

1. Click **"Load File"** button to browse and select a PDF, EPUB, Word document, or text file
2. Alternatively, copy text to your clipboard and click **"Paste Text"** to load it directly

### Reading

1. Use the **Starting Position** slider to navigate through the document
   - View page numbers, chapter information, and percentage progress
   - See context preview showing surrounding text for reference
   - Jump to any position in the document
2. Adjust the **WPM** using the spinbox or select from speed presets (200, 250, 300, 350, 400, 500)
3. Enable **TTS** checkbox to hear words spoken aloud (speed automatically matches WPM)
4. Click **"Play"** to start reading automatically, or use **"Next →"** / **"← Previous"** to navigate manually
5. Use **"⛶ Fullscreen"** button or press **F11** for distraction-free reading with large text display and surrounding word context
6. Press **Escape** or click the **✕** button to exit fullscreen mode
7. Monitor your progress using the progress bar and detailed statistics at the bottom

### Controls

- **Play/Pause**: Start or pause automatic word-by-word display
- **Reset**: Return to the beginning of the document
- **Previous/Next**: Navigate manually through words
- **Fullscreen**: Toggle distraction-free fullscreen reading mode
- **WPM Control**: Adjust reading speed (50-1000 words per minute) with presets
- **Speed Presets**: Quick selection of common reading speeds

## Supported File Formats

- **PDF** (.pdf) - Extracts text from PDF documents
- **EPUB** (.epub) - Reads EPUB e-book files
- **Word Documents** (.docx, .doc) - Extracts text from Microsoft Word files
- **Plain Text** (.txt) - Reads standard text files
- **Clipboard** - Paste any text directly

## Project Structure

```
speed-reader/
├── .github/
│   ├── workflows/
│   │   └── ci.yml              # GitHub Actions CI/CD pipeline
│   └── dependabot.yml          # Automated dependency updates
├── src/
│   └── speed_reader/
│       ├── __init__.py
│       ├── main.py              # Application entry point
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── window.py        # Main GUI window with speed history
│       │   └── styles.py        # Modern dark theme styling
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── file_parser.py   # Main parser interface
│       │   ├── base.py          # Base utilities
│       │   ├── pdf_parser.py    # PDF parser
│       │   ├── epub_parser.py   # EPUB parser
│       │   ├── docx_parser.py   # Word document parser
│       │   └── text_parser.py   # Plain text parser
│       ├── tts/
│       │   ├── __init__.py
│       │   └── manager.py       # Text-to-speech manager
│       ├── models/
│       │   ├── __init__.py
│       │   └── document.py      # Document metadata model
│       └── utils/
│           ├── __init__.py
│           └── file_history.py  # File and speed history management
├── scripts/
│   ├── build_all.bat            # Windows complete build script (tests + executable + packages)
│   ├── build_all.sh             # Linux/macOS complete build script (tests + executable + packages)
│   ├── build.bat                # Windows executable build script
│   └── build.sh                 # Linux/macOS executable build script
├── tests/                       # Test files
│   └── test_basic.py          # Basic functionality tests
├── run.py                       # Convenience run script
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Version history
├── .pre-commit-config.yaml      # Pre-commit hooks configuration
├── codecov.yml                  # Code coverage configuration
├── .gitignore                   # Git ignore rules
├── LICENSE                      # License file
└── README.md                    # This file
```

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/speed-reader.git
cd speed-reader
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python run.py
```

### Running Tests

```bash
python tests/test_basic.py
```

The tests use Python's built-in unittest framework and cover:
- File history management
- Speed preference persistence
- Document metadata creation
- File parsing functionality
- Recent files tracking

### Continuous Integration

This project uses GitHub Actions for continuous integration. The CI pipeline:

- **Tests** on multiple Python versions (3.8-3.11) and operating systems (Ubuntu, Windows, macOS)
- **Code Quality** checks with flake8, black, isort, and mypy
- **Build Verification** to ensure executables can be created on all platforms
- **Coverage Reporting** with codecov integration

All tests must pass before changes can be merged.

### Building for Distribution

The project uses PyInstaller to create standalone executables and setuptools for Python packages:

**Complete Build (Recommended):**
Run tests, build executable, and create Python packages:

**Windows:**
```bash
scripts\build_all.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/build_all.sh
./scripts/build_all.sh
```

**Individual Components:**
Build only specific components:

**Windows:**
```bash
scripts\build.bat          # Build executable only
python setup.py sdist bdist_wheel  # Build Python packages only
python -m unittest tests.test_basic -v  # Run tests only
```

**Linux/macOS:**
```bash
chmod +x scripts/build.sh
./scripts/build.sh         # Build executable only
python3 setup.py sdist bdist_wheel  # Build Python packages only
python3 -m unittest tests.test_basic -v  # Run tests only
```

### Code Style

This project follows PEP 8 style guidelines. Use the following tools:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking (future)

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
pip install pre-commit
pre-commit install
```

### Architecture

The application follows a modular architecture:

- **GUI Layer** (`gui/`): PyQt6-based interface with modern styling
- **Parser Layer** (`parsers/`): File format parsers for different document types
- **TTS Layer** (`tts/`): Text-to-speech functionality
- **Model Layer** (`models/`): Data structures for document metadata
- **Utils Layer** (`utils/`): Shared utilities like file history management

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests and ensure code style compliance
5. Submit a pull request

Please ensure your code includes appropriate documentation and follows the existing patterns.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## Technical Details

- **Framework**: PyQt6 for cross-platform GUI
- **Language**: Python 3.8+
- **Architecture**: Modular design with separate parsers, GUI, and TTS components
- **Libraries**:
  - PyPDF2 for PDF parsing with page tracking
  - ebooklib for EPUB parsing with chapter detection
  - python-docx for Word document parsing
  - BeautifulSoup4 for HTML parsing in EPUB files
  - pyttsx3 for cross-platform text-to-speech
  - lxml for XML/HTML parsing

## Troubleshooting

- **File won't load**: Ensure the file format is supported and the file is not corrupted
- **Text extraction issues**: Some PDFs with images or scanned text may not extract properly
- **Performance**: Very large files may take a moment to load and parse

## License

See LICENSE file for details.
