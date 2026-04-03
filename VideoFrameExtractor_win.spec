# -*- mode: python ; coding: utf-8 -*-
"""
Windows 打包配置
使用前需先安装 tesseract：
  choco install tesseract -y
语言包会自动下载到 C:\ProgramData\chocolatey\lib\tesseract\tools\tessdata
"""

import os, sys

block_cipher = None

a = Analysis(
    ['VideoFrameExtractor.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # tesseract 语言包（从安装目录复制到打包资源）
        (
            r'C:\Program Files\Tesseract-OCR\tessdata',
            'tessdata',
        ),
    ],
    hiddenimports=[
        'cv2',
        'tkinter', 'tkinter.ttk',
        'tkinter.filedialog', 'tkinter.messagebox',
        'pytesseract',
        'numpy', 'PIL', 'PIL._imaging',
        'tkinterdnd2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'scipy', 'pandas',
        'matplotlib.pyplot', 'scipy.optimize',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoFrameExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=None,
    version=None,
    manifest=None,
)

app = EXE(
    exe,
    [],
    exclude_binaries=False,
    name='VideoFrameExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
