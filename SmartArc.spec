# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

sklearn_datas, sklearn_binaries, sklearn_hiddenimports = collect_all('sklearn')
ga_datas, ga_binaries, ga_hiddenimports = collect_all('geneticalgorithm2')
fitz_datas, fitz_binaries, fitz_hiddenimports = collect_all('fitz')
pymupdf_datas, pymupdf_binaries, pymupdf_hiddenimports = collect_all('pymupdf')

datas = [
    ('core.png', '.'),
    ('smartarc.ico', '.'),
    ('random_forest_model_final_newRange.pkl', '.'),
    ('app_data.bak', '.'),
    ('Help.xlsx', '.'),
    ('help.pdf', '.'),
] + sklearn_datas + ga_datas + fitz_datas + pymupdf_datas

binaries = [] + sklearn_binaries + ga_binaries + fitz_binaries + pymupdf_binaries

hiddenimports = [
    'random',
    'sys',
    'pickle',
    'numpy',
    'numpy.core._multiarray_umath',
    'numpy.core.multiarray',
    'pandas',
    'openpyxl',
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_qt5agg',
    'PyQt5',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtCore',
    'PyQt5.sip',
    're',
    'os',
    'base64',
    'fitz',
    'shutil',
    'datetime',
] + sklearn_hiddenimports + ga_hiddenimports + fitz_hiddenimports + pymupdf_hiddenimports

a = Analysis(
    ['v2.py'],
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
    name='SmartArc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['smartarc.ico'],
)
