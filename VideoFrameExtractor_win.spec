# -*- mode: python ; coding: utf-8 -*-
"""
Windows 打包配置
tesseract 安装路径通过动态检测获取，兼容 GitHub Actions 云端构建
"""

import os, sys

block_cipher = None

# ── 动态检测 tesseract 安装路径 ──
tesseract_bin = None
tessdata_dir  = None
for base in [r'C:\Program Files\Tesseract-OCR',
             r'C:\Program Files (x86)\Tesseract-OCR',
             r'C:\ProgramData\chocolatey\lib\tesseract\tools']:
    tb = os.path.join(base, 'tesseract.exe')
    td = os.path.join(base, 'tessdata')
    if os.path.isfile(tb):
        tesseract_bin = tb
    if os.path.isdir(td):
        tessdata_dir = td

print(f"[PyInstaller] tesseract_bin : {tesseract_bin}")
print(f"[PyInstaller] tessdata_dir   : {tessdata_dir}")

# ── 构建 datas 列表 ──
datas = []
if tessdata_dir:
    for lang in ['eng.traineddata', 'chi_sim.traineddata', 'osd.traineddata']:
        lp = os.path.join(tessdata_dir, lang)
        if os.path.isfile(lp):
            datas.append((lp, 'tessdata'))

a = Analysis(
    ['VideoFrameExtractor.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'cv2',
        'tkinter', 'tkinter.ttk',
        'tkinter.filedialog', 'tkinter.messagebox',
        'pytesseract',
        'numpy', 'PIL', 'PIL._imaging',
    ],
    excludes=['matplotlib', 'scipy', 'pandas'],
    cipher=block_cipher,
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
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=None,
)
