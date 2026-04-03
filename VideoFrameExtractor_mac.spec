# -*- mode: python ; coding: utf-8 -*-
"""
macOS 打包配置（兼容 GitHub Actions 云端构建）
路径全部动态获取，不硬编码本地路径
"""

import os, sys, sysconfig, site

block_cipher = None

# ── 动态获取 site-packages 路径 ──
site_packages = site.getsitepackages()[0]

# ── tkdnd 源码路径（尝试多个可能的位置） ──
tkdnd_base = os.path.join(site_packages, 'tkinterdnd2')
tkdnd_src  = None
for candidate in [
    os.path.join(tkdnd_base, 'tkdnd'),
    '/opt/homebrew/lib/tkinterdnd2/tkdnd',
    '/usr/local/lib/tkinterdnd2/tkdnd',
]:
    if os.path.isdir(candidate):
        tkdnd_src = candidate
        break

# ── tesseract & tessdata 路径 ──
tesseract_bin = None
tessdata_dir  = None
for base in ['/opt/homebrew', '/usr/local', '/usr']:
    tb = os.path.join(base, 'bin', 'tesseract')
    td = os.path.join(base, 'share', 'tessdata')
    if os.path.isfile(tb):
        tesseract_bin = tb
    if os.path.isdir(td):
        tessdata_dir = td
    if tesseract_bin and tessdata_dir:
        break

# ── 构建 datas 列表（跳过不存在的内容） ──
datas = [
    (os.path.join(tkdnd_base, '__init__.py'),   'tkinterdnd2'),
    (os.path.join(tkdnd_base, 'TkinterDnD.py'), 'tkinterdnd2'),
]
if tkdnd_src:
    datas.append((tkdnd_src, 'tkinterdnd2/tkdnd'))
if tesseract_bin:
    datas.append((tesseract_bin, 'tesseract_bin'))
if tessdata_dir:
    for lang in ['eng.traineddata', 'chi_sim.traineddata', 'osd.traineddata']:
        lp = os.path.join(tessdata_dir, lang)
        if os.path.isfile(lp):
            datas.append((lp, 'tessdata'))

print(f"[PyInstaller] site-packages : {site_packages}")
print(f"[PyInstaller] tkdnd_src     : {tkdnd_src}")
print(f"[PyInstaller] tesseract_bin  : {tesseract_bin}")
print(f"[PyInstaller] tessdata_dir   : {tessdata_dir}")
print(f"[PyInstaller] datas count    : {len(datas)}")

a = Analysis(
    ['VideoFrameExtractor.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'cv2',
        'tkinter', 'tkinter.ttk',
        'tkinter.filedialog', 'tkinter.messagebox',
        'tkinterdnd2',
        'pytesseract',
        'numpy', 'PIL', 'PIL._imaging',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas'],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='VideoFrameExtractor',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, name='VideoFrameExtractor',
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
