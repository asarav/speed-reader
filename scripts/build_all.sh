#!/bin/bash

echo "========================================"
echo "Speed Reader - Complete Build Script"
echo "========================================"
echo

echo "[1/4] Running tests..."
echo
python3 -m unittest tests.test_basic -v
if [ $? -ne 0 ]; then
    echo
    echo "Tests failed! Aborting build."
    exit 1
fi
echo
echo "Tests passed! Continuing with build..."
echo

echo "[2/4] Building executable..."
echo

# Check if PyInstaller is installed
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Build the executable
pyinstaller --name=SpeedReader --onefile --windowed --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=ebooklib --hidden-import=docx --hidden-import=PyPDF2 --hidden-import=bs4 --hidden-import=lxml --hidden-import=pyttsx3 --hidden-import=pyttsx3.drivers --collect-all=PyQt6 --add-data="src:src" src/speed_reader/main.py

if [ $? -ne 0 ]; then
    echo
    echo "Executable build failed!"
    exit 1
fi

echo
echo "Executable built successfully!"
echo

echo "[3/4] Building Python packages..."
echo
python3 setup.py sdist bdist_wheel

if [ $? -ne 0 ]; then
    echo
    echo "Python package build failed!"
    exit 1
fi

echo
echo "Python packages built successfully!"
echo

echo "[4/4] Verifying build output..."
echo

if [ -f "dist/SpeedReader" ]; then
    echo "Executable: $(ls -lh dist/SpeedReader | awk '{print $9 " (" $5 ")"}')"
else
    echo "ERROR: Executable not found!"
    exit 1
fi

if ls dist/speed_reader-*.whl 1> /dev/null 2>&1; then
    echo "Wheel: $(ls -lh dist/speed_reader-*.whl | awk '{print $9 " (" $5 ")"}')"
else
    echo "ERROR: Wheel package not found!"
    exit 1
fi

if ls dist/speed-reader-*.tar.gz 1> /dev/null 2>&1; then
    echo "Source: $(ls -lh dist/speed-reader-*.tar.gz | awk '{print $9 " (" $5 ")"}')"
else
    echo "ERROR: Source package not found!"
    exit 1
fi

echo
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo
echo "Generated files in dist/:"
ls -la dist/
echo
echo "Ready for release! 🚀"
echo