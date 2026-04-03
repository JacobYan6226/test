# -*- mode: python ; coding: utf-8 -*-

import os, sys, shutil

site_packages = '/Users/yanyu/Library/Python/3.11/lib/python/site-packages'
tkdnd_src     = os.path.join(site_packages, 'tkinterdnd2', 'tkdnd')
tesseract_bin = '/opt/homebrew/bin/tesseract'
tessdata_dir  = '/opt/homebrew/share/tessdata'

block_cipher  = None

a = Analysis(
    ['VideoFrameExtractor.py'],
    pathex=['/Users/yanyu/Desktop'],
    binaries=[],
    datas=[
        # tkinterdnd2
        (tkdnd_src,                                                       'tkinterdnd2/tkdnd'),
        (os.path.join(site_packages, 'tkinterdnd2', '__init__.py'),      'tkinterdnd2'),
        (os.path.join(site_packages, 'tkinterdnd2', 'TkinterDnD.py'),     'tkinterdnd2'),
        # tesseract 二进制（必须！）
        (tesseract_bin,                                                   'tesseract_bin'),
        # tesseract 语言包
        (os.path.join(tessdata_dir, 'eng.traineddata'),                  'tessdata'),
        (os.path.join(tessdata_dir, 'chi_sim.traineddata'),             'tessdata'),
        (os.path.join(tessdata_dir, 'osd.traineddata'),                  'tessdata'),
    ],
    hiddenimports=[
        'cv2',
        'tkinter', 'tkinter.ttk',
        'tkinter.filedialog', 'tkinter.messagebox',
        'tkinterdnd2',
        'pytesseract',
        'numpy', 'PIL', 'PIL._imaging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoFrameExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoFrameExtractor',
)

app = BUNDLE(
    coll,
    name='视频截图工具.app',
    icon=None,
    bundle_identifier='com.local.videoframeextractor',
    info_plist={
        'CFBundleShortVersionString': '1.2.0',
        'CFBundleVersion':           '1.2.0',
        'NSHighResolutionCapable':   True,
        'LSMinimumSystemVersion':    '11.0',
    },
)
