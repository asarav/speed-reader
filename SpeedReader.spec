# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

# Platform-aware configuration
if sys.platform == 'win32':
    entry_point = 'src\\speed_reader\\main.py'
    exe_name = 'SpeedReader'
else:  # macOS or Linux
    entry_point = 'src/speed_reader/main.py'
    exe_name = 'SpeedReader'

datas = [('src', 'src')]
binaries = []
hiddenimports = ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'ebooklib', 'docx', 'PyPDF2', 'bs4', 'lxml', 'pyttsx3', 'pyttsx3.drivers', 'nltk', 'nltk.tag', 'nltk.tag.perceptron']
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    [entry_point],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=sys.platform != 'win32',  # Strip on Unix-like systems
    upx=False if sys.platform != 'win32' else True,  # UPX not available on all platforms
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS-specific app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='SpeedReader.app',
        icon=None,
        bundle_identifier='com.speedreader.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
