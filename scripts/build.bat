@echo off
REM Windows-specific build script for Speed Reader
REM This script builds a Windows .exe executable

echo Building Speed Reader executable for Windows...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the executable using the spec file
echo Building with platform-specific configuration...
pyinstaller SpeedReader.spec --clean

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable created at: dist\SpeedReader.exe
echo.
pause
