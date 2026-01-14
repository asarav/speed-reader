"""
Main entry point for Speed Reader application.
"""
import sys
from PyQt6.QtWidgets import QApplication
from .gui.window import SpeedReaderWindow


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = SpeedReaderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
