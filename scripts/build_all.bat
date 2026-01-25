@echo off
echo ========================================
echo Speed Reader - Complete Build Script
echo ========================================
echo.

REM Change to project root directory
cd ..

REM Clean up old build artifacts to avoid file locks
if exist "dist\SpeedReader.exe" (
    echo Cleaning up old executable...
    REM Give any running processes time to release the file
    timeout /t 2 /nobreak >nul
    del /F /Q "dist\SpeedReader.exe" 2>nul
    REM Give filesystem time to update
    timeout /t 1 /nobreak >nul
)

echo [1/4] Running tests...
echo.
python -m unittest tests.test_basic -v
if errorlevel 1 (
    echo.
    echo Tests failed! Aborting build.
    cd scripts
    pause
    exit /b 1
)
echo.
echo Tests passed! Continuing with build...
echo.

echo [2/4] Building Windows executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the executable with --clean flag to force rebuild
pyinstaller --clean --name=SpeedReader --onefile --windowed --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=ebooklib --hidden-import=docx --hidden-import=PyPDF2 --hidden-import=bs4 --hidden-import=lxml --hidden-import=pyttsx3 --hidden-import=pyttsx3.drivers --collect-all=PyQt6 --add-data="src;src" src/speed_reader/main.py

if errorlevel 1 (
    echo.
    echo Executable build failed!
    cd scripts
    pause
    exit /b 1
)

echo.
echo Executable built successfully!
echo.

echo [3/4] Building Python packages...
echo.
python setup.py sdist bdist_wheel

if errorlevel 1 (
    echo.
    echo Python package build failed!
    cd scripts
    pause
    exit /b 1
)

echo.
echo Python packages built successfully!
echo.

echo [4/4] Verifying build output...
echo.
if exist "dist\SpeedReader.exe" (
    echo Executable: SpeedReader.exe found
) else (
    echo ERROR: Executable not found!
    cd scripts
    pause
    exit /b 1
)

if exist "dist\speed_reader-*.whl" (
    echo Wheel package: found
) else (
    echo ERROR: Wheel package not found!
    cd scripts
    pause
    exit /b 1
)

if exist "dist\speed-reader-*.tar.gz" (
    echo Source package: found
) else (
    echo ERROR: Source package not found!
    cd scripts
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Generated files in dist\:
dir /b dist\
echo.
echo Ready for release!
echo.
cd scripts
pause
pause