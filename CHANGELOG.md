# Changelog

All notable changes to Speed Reader will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Speed history feature - remembers user's preferred reading speed between sessions
- Speed presets dropdown for quick selection of common reading speeds (200, 250, 300, 350, 400, 500 WPM)
- File history management with reading position memory
- Responsive UI with resizable window and improved layout
- **Fullscreen reading mode** with large text display and distraction-free interface
- **Fullscreen reading mode** with large text display and distraction-free interface
- Fullscreen toggle button and keyboard shortcuts (F11 to enter, Escape to exit)
- **Surrounding word context** in fullscreen mode with previous/next words shown in smaller grey text
- Modern dark theme with improved styling
- Modern dark theme with improved styling
- Modern dark theme with improved styling

### Changed
- Reduced default window size for better screen compatibility
- Improved WPM controls layout to prevent text cutoff
- Updated context preview to be more compact
- Enhanced progress tracking with better visual feedback

### Fixed
- UI text cutoff issues in controls
- Window resizing limitations
- Missing speed persistence between sessions

### Technical
- Refactored file history system to include speed preferences
- Improved code organization and modularity
- Updated dependencies and build process
- Cleaned up old files and improved project structure

## [1.0.0] - 2024-01-01

### Added
- Initial release of Speed Reader
- Support for PDF, EPUB, Word documents, and plain text files
- Text-to-speech functionality with automatic WPM matching
- Chapter navigation and position tracking
- Context preview with surrounding text
- Keyboard shortcuts for navigation
- Cross-platform support (Windows, Linux, macOS)
- Standalone executable builds

### Technical
- PyQt6-based GUI with modern styling
- Modular parser architecture
- File position and history tracking
- Comprehensive error handling