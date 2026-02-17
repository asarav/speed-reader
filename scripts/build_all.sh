#!/bin/bash
# Cross-platform build and release script
# Detects current OS and builds appropriate executables

OSTYPE=$(uname -s)
echo "========================================"
echo "Speed Reader - Cross-Platform Build"
echo "OS Detected: $OSTYPE"
echo "========================================"
echo

echo "[1/5] Running tests..."
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

echo "[2/5] Checking dependencies..."
echo
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi
echo "Dependencies OK"
echo

echo "[3/5] Building platform-specific executable..."
echo

if [ "$OSTYPE" = "darwin" ]; then
    echo "Building macOS app bundle..."
    pyinstaller SpeedReader.spec --clean
    if [ $? -ne 0 ]; then
        echo "macOS app bundle build failed!"
        exit 1
    fi
    EXEC_FILE="dist/SpeedReader.app"
    EXEC_DESC="macOS App Bundle"
elif [ "$OSTYPE" = "linux-gnu" ]; then
    echo "Building Linux executable..."
    pyinstaller SpeedReader.spec --clean
    if [ $? -ne 0 ]; then
        echo "Linux executable build failed!"
        exit 1
    fi
    chmod +x dist/SpeedReader
    EXEC_FILE="dist/SpeedReader"
    EXEC_DESC="Linux Executable"
else
    echo "Building executable for $OSTYPE..."
    pyinstaller SpeedReader.spec --clean
    if [ $? -ne 0 ]; then
        echo "Executable build failed!"
        exit 1
    fi
    EXEC_FILE="dist/SpeedReader"
    EXEC_DESC="Executable"
fi

echo
echo "Executable built successfully!"
echo

echo "[4/5] Building Python packages..."
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

echo "[5/5] Verifying build output..."
echo

if [ -e "$EXEC_FILE" ]; then
    if [ -d "$EXEC_FILE" ]; then
        echo "✓ $EXEC_DESC: $(du -sh "$EXEC_FILE" | awk '{print $1}')"
    else
        echo "✓ $EXEC_DESC: $(ls -lh "$EXEC_FILE" | awk '{print $5}')"
    fi
else
    echo "✗ ERROR: Executable not found!"
    exit 1
fi

if ls dist/speed_reader-*.whl 1> /dev/null 2>&1; then
    echo "✓ Wheel: $(ls dist/speed_reader-*.whl | awk '{print $NF}' | xargs ls -lh | awk '{print $5}')"
else
    echo "✗ ERROR: Wheel package not found!"
    exit 1
fi

if ls dist/speed-reader-*.tar.gz 1> /dev/null 2>&1; then
    echo "✓ Source: $(ls dist/speed-reader-*.tar.gz | awk '{print $NF}' | xargs ls -lh | awk '{print $5}')"
else
    echo "✗ ERROR: Source package not found!"
    exit 1
fi

echo
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo
echo "Generated files in dist/:"
ls -lh dist/ | grep -E '(SpeedReader|speed_reader|speed-reader)'
echo
echo "Build Summary:"
echo "  Platform: $OSTYPE"
echo "  Executable: $([ -e "$EXEC_FILE" ] && echo 'Ready' || echo 'Missing')"
echo "  Python Packages: Wheel + Source"
echo
echo "Ready for release! 🚀"
echo