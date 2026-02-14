"""
Main entry point for Speed Reader application.
"""
import sys
from PyQt6.QtWidgets import QApplication

# Ensure NLTK POS data is available when running as main (e.g. python -m speed_reader.main)
try:
    from speed_reader.utils.pos_tagger import ensure_nltk_pos_data
except ImportError:
    from .utils.pos_tagger import ensure_nltk_pos_data

# Handle imports for both local development and bundled executable
try:
    # Try absolute import (works in bundled executable)
    from speed_reader.gui.window import SpeedReaderWindow
except ImportError:
    # Fall back to relative import (works in local development)
    from .gui.window import SpeedReaderWindow


def main():
    """Main entry point."""
    ensure_nltk_pos_data(quiet=True)  # Ensure tagger data present; no console spam if already there
    app = QApplication(sys.argv)
    window = SpeedReaderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
