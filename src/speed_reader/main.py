"""
Main entry point for Speed Reader application.
"""
import sys
from PyQt6.QtWidgets import QApplication

# Handle imports for both local development and bundled executable
try:
    # Try absolute import (works in bundled executable)
    from speed_reader.gui.window import SpeedReaderWindow
except ImportError:
    # Fall back to relative import (works in local development)
    from .gui.window import SpeedReaderWindow


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = SpeedReaderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
