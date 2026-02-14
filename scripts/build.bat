@echo off
echo Building Speed Reader executable for Windows...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the executable
pyinstaller --name=SpeedReader --onefile --windowed --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=ebooklib --hidden-import=docx --hidden-import=PyPDF2 --hidden-import=bs4 --hidden-import=lxml --hidden-import=pyttsx3 --hidden-import=pyttsx3.drivers --hidden-import=nltk --hidden-import=nltk.tag --hidden-import=nltk.tag.perceptron --collect-all=PyQt6 --add-data="src;src" src/speed_reader/main.py

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
