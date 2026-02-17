@echo off
REM Windows-specific build and release script
REM Builds Speed Reader for Windows with all distribution formats

echo ========================================
echo Speed Reader - Windows Build Script
echo ========================================
echo.

REM Change to project root directory (use script location so calling dir doesn't matter)
pushd "%~dp0\.."

REM Clean up old build artifacts to avoid file locks
if exist "dist\SpeedReader.exe" (
    echo Cleaning up old executable...
    REM Give any running processes time to release the file
    timeout /t 2 /nobreak >nul
    del /F /Q "dist\SpeedReader.exe" 2>nul
    if exist "dist\SpeedReader.exe" (
        REM If file still exists, try using move to temp and then delete
        move /Y "dist\SpeedReader.exe" "%TEMP%\SpeedReader_old.exe" >nul 2>&1
    )
    REM Also remove the entire build directory to ensure clean state
    if exist "build\" (
        rmdir /S /Q "build" 2>nul
    )
    REM Give filesystem time to update
    timeout /t 1 /nobreak >nul
)

echo [1/5] Running tests...
echo.
python -m unittest tests.test_basic -v
if errorlevel 1 (
    echo.
    echo Tests failed! Aborting build.
    cd /d "%~dp0"
    pause
    exit /b 1
)
echo.
echo Tests passed! Continuing with build...
echo.

echo [2/5] Checking dependencies...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)
echo Dependencies OK
echo.

echo [3/5] Building Windows executable...
echo.

REM Build the executable with spec file for platform-aware config
pyinstaller --clean SpeedReader.spec

if errorlevel 1 (
    echo.
    echo Executable build failed!
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo.
echo Windows executable built successfully!
echo.

echo [4/5] Building Python packages...
echo.
python setup.py sdist bdist_wheel

if errorlevel 1 (
    echo.
    echo Python package build failed!
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo.
echo Python packages built successfully!
echo.

echo [5/5] Verifying build output...
echo.
if exist "dist\SpeedReader.exe" (
    echo [OK] Windows Executable: SpeedReader.exe
) else (
    echo [ERROR] Executable not found!
    cd /d "%~dp0"
    pause
    exit /b 1
)

if exist "dist\speed_reader-*.whl" (
    echo [OK] Wheel package: found
) else (
    echo [ERROR] Wheel package not found!
    cd /d "%~dp0"
    pause
    exit /b 1
)

if exist "dist\speed-reader-*.tar.gz" (
    echo [OK] Source package: found
) else (
    echo [ERROR] Source package not found!
    cd /d "%~dp0"
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
echo Build Summary:
echo   Platform: Windows (x86_64)
echo   Executable: SpeedReader.exe
echo   Distribution: Wheel + Source packages
echo.
echo Ready for release!
echo.
popd
cd /d "%~dp0"
pause