#!/bin/bash
# Cross-platform build script for Speed Reader
# Detects OS and builds appropriate executable

echo "Building Speed Reader executable for $(uname -s)..."
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Build using the spec file (platform-aware)
echo "Building with platform-specific configuration..."
pyinstaller SpeedReader.spec --clean

if [ $? -eq 0 ]; then
    echo ""
    if [ "$(uname -s)" = "Darwin" ]; then
        echo "Build successful!"
        echo "App bundle created at: dist/SpeedReader.app"
    else
        echo "Build successful!"
        echo "Executable created at: dist/SpeedReader"
    fi
else
    echo ""
    echo "Build failed!"
    exit 1
fi
