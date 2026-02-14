#!/bin/bash
# Build script for Linux and macOS

echo "Building Speed Reader executable..."
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Build the executable
pyinstaller --name=SpeedReader \
    --onefile \
    --windowed \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=ebooklib \
    --hidden-import=docx \
    --hidden-import=PyPDF2 \
    --hidden-import=bs4 \
    --hidden-import=lxml \
    --hidden-import=pyttsx3 \
    --hidden-import=pyttsx3.drivers \
    --hidden-import=nltk \
    --hidden-import=nltk.tag \
    --hidden-import=nltk.tag.perceptron \
    --collect-all=PyQt6 \
    --add-data="src:src" \
    src/speed_reader/main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful!"
    echo "Executable created at: dist/SpeedReader"
else
    echo ""
    echo "Build failed!"
    exit 1
fi
