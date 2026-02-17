# Build Instructions for Speed Reader

This document provides platform-specific instructions for building Speed Reader executables for Windows, macOS, and Linux.

## Automated Cross-Platform Builds (GitHub Actions)

The easiest way to build for all platforms is to use GitHub Actions, which automatically builds for Windows, macOS, and Linux.

### Setting Up Automated Builds

A GitHub Actions workflow is included (`.github/workflows/release.yml`) that automatically:

1. **Runs tests** on every trigger
2. **Builds executables** for all platforms in parallel
3. **Creates a GitHub Release** with all binaries and packages

### How to Trigger a Build

#### Method 1: Create a Version Tag (Recommended)
```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers a full build and automatically creates a GitHub Release with all platform binaries.

#### Method 2: Manual Trigger
1. Go to GitHub repository → **Actions** tab
2. Select **Cross-Platform Build and Release** workflow
3. Click **Run workflow** → **Run workflow**

### Build Artifacts

After a successful build, GitHub Actions uploads:

| Platform | Executable | Size | Notes |
|----------|-----------|------|-------|
| Windows | `SpeedReader-Windows.exe` | ~130 MB | Standalone, no Python needed |
| macOS | `SpeedReader-macOS.app.zip` | ~150 MB | App bundle (zipped) |
| macOS (alt) | `SpeedReader-macOS.dmg` | ~150 MB | Disk image for easier distribution |
| Linux | `SpeedReader-Linux` | ~140 MB | Standalone, no Python needed |
| Python | `speed_reader-*.whl` | ~35 KB | For developers |
| Python | `speed-reader-*.tar.gz` | ~35 KB | For developers |

All artifacts are available for download from the GitHub Release page.

---

## Quick Start (Local Builds)

### Windows
```batch
scripts\build_all.bat
```

### macOS / Linux
```bash
bash scripts/build_all.sh
```

## Platform-Specific Builds

### Windows

**Requirements:**
- Python 3.8+
- PyInstaller
- All dependencies from `requirements.txt`

**Build Command:**
```batch
scripts\build_all.bat
```

**Output:**
- `dist/SpeedReader.exe` - Standalone Windows executable
- `dist/speed_reader-*.whl` - Python wheel package
- `dist/speed-reader-*.tar.gz` - Source distribution

**Individual Steps:**
```batch
# Just build the executable
scripts\build.bat

# Just build Python packages (requires setup.py)
python setup.py sdist bdist_wheel
```

### macOS

**Requirements:**
- Python 3.8+ (recommend using Homebrew)
- PyInstaller
- All dependencies from `requirements.txt`

**Build Command:**
```bash
bash scripts/build_all.sh
```

**Output:**
- `dist/SpeedReader.app` - macOS application bundle
- `dist/speed_reader-*.whl` - Python wheel package
- `dist/speed-reader-*.tar.gz` - Source distribution

**Individual Steps:**
```bash
# Just build the app
bash scripts/build.sh

# Just build Python packages
python3 setup.py sdist bdist_wheel
```

**Additional Notes:**
- The app bundle is packaged for macOS and can be distributed to users
- For distribution on the Mac App Store, additional signing and notarization is required
- The standalone app includes Python, so users don't need Python installed

### Linux

**Requirements:**
- Python 3.8+
- PyInstaller
- All dependencies from `requirements.txt`
- For GUI: ensure you have PyQt6 libraries available

**Build Command:**
```bash
bash scripts/build_all.sh
```

**Output:**
- `dist/SpeedReader` - Standalone Linux executable
- `dist/speed_reader-*.whl` - Python wheel package
- `dist/speed-reader-*.tar.gz` - Source distribution

**Individual Steps:**
```bash
# Just build the executable
bash scripts/build.sh

# Just build Python packages
python3 setup.py sdist bdist_wheel
```

**Additional Notes:**
- Make the executable available to users by placing it in `/usr/local/bin` or similar
- The standalone executable includes Python, so users don't need Python installed
- For distribution, consider creating an AppImage or packaging for package managers (deb, rpm, etc.)

## Build Configuration

The build process uses `SpeedReader.spec`, which is a PyInstaller configuration file that:
- Detects the platform automatically (Windows, macOS, Linux)
- Bundles all dependencies and data files
- Configures platform-specific options:
  - **Windows**: Creates single `.exe` file with UPX compression
  - **macOS**: Creates `.app` bundle with proper settings
  - **Linux**: Creates single executable with stripping

### Customizing the Build

To modify the build:

1. Edit `SpeedReader.spec` for PyInstaller options
2. Edit `scripts/build.sh` or `scripts/build.bat` for platform-specific build logic
3. Update `requirements.txt` to add/remove dependencies

## Dependency Bundles

The build creates three distribution formats:

| Format | Purpose | Installation |
|--------|---------|--------------|
| `.exe`/`.app`/executable | Standalone application for end-users | Run directly, no Python required |
| `.whl` (wheel) | Python package for developers | `pip install speed-reader-*.whl` |
| `.tar.gz` | Source distribution | Extract and install with `pip install` |

## Troubleshooting

### PyInstaller Errors

**"PyInstaller not found"**
```bash
pip install pyinstaller
```

**Hidden imports not found**
The `SpeedReader.spec` file includes all necessary hidden imports. If you add new dependencies, add them to the `hiddenimports` list.

### Build Fails on Linux

Ensure qt6 libraries are installed:
```bash
# Ubuntu/Debian
sudo apt-get install libqt6gui6

# Fedora
sudo dnf install qt6-qtbase

# macOS
brew install qt6
```

### Large Executable Size

The executables (150-200 MB) are expected because PyInstaller bundles:
- Python interpreter
- All dependencies (PyQt6, NLTK, etc.)
- Application code and resources

This is normal for PyInstaller-based applications.

## Distribution

### For Windows Users
Release the `SpeedReader.exe` file. No Python installation required.

### For macOS Users
Release the `SpeedReader.app` directory (or create a `.dmg` disk image). No Python installation required.

### For Linux Users
Release the `SpeedReader` executable. No Python installation required.

### For Developers
Release both the `.whl` and `.tar.gz` files. Users can install with:
```bash
pip install speed_reader-*.whl
```

## Cross-Platform Building

Currently, each platform must be built on that platform due to PyInstaller's design. To build for all platforms, you need:

- A Windows machine for building `.exe`
- A macOS machine for building `.app`
- A Linux machine for building the Linux executable

For automated cross-platform builds, consider using GitHub Actions or similar CI/CD:
- Set up separate jobs for each OS
- Build and release artifacts automatically on each commit

## GitHub Actions CI/CD

The `.github/workflows/release.yml` file is already included and automates cross-platform builds.

### GitHub Actions Workflow Details

**Trigger Events:**
- Create a git tag matching `v*` (e.g., `git tag v1.0.0`)
- Manual trigger via GitHub Actions UI

**Build Matrix:**
- Windows (windows-latest): Builds `.exe`
- macOS (macos-latest): Builds `.app` and `.dmg`
- Linux (ubuntu-latest): Builds Linux executable
- All platforms: Builds Python wheel and source distributions

**Automatic Release Creation:**
When a version tag is pushed, the workflow automatically:
1. Builds all platform executables
2. Creates a GitHub Release
3. Uploads all artifacts to the release page
4. Makes binaries available for download

### Troubleshooting GitHub Actions

**"Workflow file not found"**
Ensure `.github/workflows/release.yml` exists in the repository root.

**"Build failed on Linux"**
The workflow installs PyQt6 libraries automatically. If it still fails, check that `libqt6gui6` is available.

**"macOS build takes too long"**
The DMG creation step can be slow on GitHub-hosted runners. You can disable it by removing the "Create DMG" step.

**View Build Logs**
1. Go to GitHub repository → **Actions** tab
2. Select the failed workflow run
3. Click on the job to see detailed logs

---

## Manual Building

The local build scripts are still available for development and testing.
