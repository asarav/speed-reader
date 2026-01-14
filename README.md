# Speed Reader

A cross-platform speed reading application that displays one word at a time. Supports PDF, EPUB, Word documents (.docx), and plain text files. Perfect for improving reading speed and comprehension.

## Features

- **Multiple File Formats**: Supports PDF, EPUB, Word documents (.docx), and plain text files
- **Paste Text**: Paste text directly from clipboard
- **Customizable Speed**: Adjustable words per minute (WPM) from 50 to 1000
- **Enhanced Position Selection**: 
  - See page numbers, chapter information, and percentage progress
  - Context preview showing surrounding text
  - Visual reference points like Calibre
- **Text-to-Speech**: Optional TTS that reads words aloud, automatically matching your WPM speed
- **Progress Tracking**: Visual progress bar and word counter with detailed statistics
- **Keyboard Shortcuts**: 
  - `Space` - Play/Pause
  - `Left Arrow` - Previous word
  - `Right Arrow` - Next word
  - `R` - Reset to beginning
- **Cross-Platform**: Works on Windows, Linux, and macOS

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

Or directly:

```bash
python -m src.speed_reader.main
```

### Building an Executable

To create a standalone executable that can run without Python installed:

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
2. Adjust the **Words Per Minute (WPM)** to your preferred reading speed
3. Enable **Text-to-Speech** checkbox to hear words spoken aloud (speed automatically matches WPM)
4. Click **"Play"** to start reading automatically, or use **"Next →"** / **"← Previous"** to navigate manually
5. Monitor your progress using the progress bar and detailed statistics at the bottom

### Controls

- **Play/Pause**: Start or pause automatic word-by-word display
- **Reset**: Return to the beginning of the document
- **Previous/Next**: Navigate manually through words
- **WPM Control**: Adjust reading speed (50-1000 words per minute)

## Supported File Formats

- **PDF** (.pdf) - Extracts text from PDF documents
- **EPUB** (.epub) - Reads EPUB e-book files
- **Word Documents** (.docx, .doc) - Extracts text from Microsoft Word files
- **Plain Text** (.txt) - Reads standard text files
- **Clipboard** - Paste any text directly

## Project Structure

```
speed-reader/
├── src/
│   └── speed_reader/
│       ├── __init__.py
│       ├── main.py              # Application entry point
│       ├── gui/
│       │   ├── __init__.py
│       │   └── window.py        # Main GUI window
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
│       └── models/
│           ├── __init__.py
│           └── document.py      # Document metadata model
├── scripts/
│   ├── build.bat                # Windows build script
│   └── build.sh                 # Linux/macOS build script
├── tests/                       # Test files (future)
├── run.py                       # Convenience run script
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Technical Details

- **Framework**: PyQt6 for cross-platform GUI
- **Language**: Python 3
- **Architecture**: Modular design with separate parsers, GUI, and TTS components
- **Libraries**:
  - PyPDF2 for PDF parsing with page tracking
  - ebooklib for EPUB parsing with chapter detection
  - python-docx for Word document parsing
  - BeautifulSoup4 for HTML parsing in EPUB files
  - pyttsx3 for cross-platform text-to-speech

## Troubleshooting

- **File won't load**: Ensure the file format is supported and the file is not corrupted
- **Text extraction issues**: Some PDFs with images or scanned text may not extract properly
- **Performance**: Very large files may take a moment to load and parse

## License

See LICENSE file for details.
