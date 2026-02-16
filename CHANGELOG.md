# Changelog

All notable changes to Speed Reader will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2-alpha] - 2026-02-14

### Added
- **Color-by-part-of-speech** feature for enhanced comprehension - pronouns (orange/italic), nouns (blue/bold), verbs (green/italic)
- **Session summarization** - automatic summaries of what you've read in the current session
- **Fullscreen HUD improvements** - progress percentage and time remaining display
- Multiple summarization methods: OpenAI API (optional), sumy LSA, NLTK-based, and fallback regex methods
- Part-of-speech tagging with NLTK support for color coding

### Changed
- Improved fullscreen layout with 1:2:1 proportions for better word visibility
- Enhanced TTS integration with async queue-based speaking system
- TTS limited to max 192 WPM (Windows SAPI limitation)
- Speed presets expanded to include lower values (50-125 WPM) for accessibility

### Technical
- Added `pos_tagger.py` module for NLTK POS tagging and color styling
- Added `summarizer.py` module with multiple extraction and abstractive methods
- Improved TTS worker thread with lock-based engine management
- Enhanced error handling and logging in TTS subsystem
- Updated build scripts with NLTK hidden imports

## [0.0.1-alpha] - 2026-01-24

### Added
- Speed history feature - remembers user's preferred reading speed between sessions
- Speed presets dropdown for quick selection of common reading speeds (200, 250, 300, 350, 400, 500 WPM)
- File history management with reading position memory
- Responsive UI with resizable window and improved layout
- **Fullscreen reading mode** with large text display and distraction-free interface
- Fullscreen toggle button and keyboard shortcuts (F11 to enter, Escape to exit)
- **Surrounding word context** in fullscreen mode with previous/next words shown in smaller grey text
- Modern dark theme with improved styling
- Support for PDF, EPUB, Word documents, and plain text files
- Text-to-speech functionality with automatic WPM matching
- Chapter navigation and position tracking
- Context preview with surrounding text
- Keyboard shortcuts for navigation
- Cross-platform support (Windows, Linux, macOS)
- Standalone executable builds

### Changed
- Updated README with demo video sections
- Reduced default window size for better screen compatibility
- Improved WPM controls layout to prevent text cutoff
- Updated context preview to be more compact
- Enhanced progress tracking with better visual feedback
- Enhanced build artifact cleanup to prevent file lock issues

### Fixed
- Build script compatibility issues (path handling in Windows batch and Unix shell)
- UI text cutoff issues in controls
- Window resizing limitations
- Missing speed persistence between sessions

### Technical
- PyQt6-based GUI with modern styling
- Modular parser architecture
- File position and history tracking
- Comprehensive error handling
- Refactored file history system to include speed preferences
- Improved code organization and modularity
- Updated dependencies and build process
- Cleaned up old files and improved project structure
- Added video demo references to documentation
- Improved dependency documentation for NLTK usage

## [Unreleased]