# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['v2.py'],
    pathex=[],
    binaries=[],
    datas=[('core.png', '.'), ('smartarc.ico', '.'), ('random_forest_model_final.pkl', '.'), ('app_data.bak', '.'), ('Help.xlsx', '.'), ('help.pdf', '.')],
    hiddenimports=['random', 'sys', 'pickle', 'numpy', 'numpy.core._multiarray_umath', 'numpy.core.multiarray', 'pandas', 'openpyxl', 'matplotlib', 'matplotlib.pyplot', 'matplotlib.backends.backend_qt5agg', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.sip', 'PyQt5.QtWebEngineWidgets', 'sklearn.model_selection', 'sklearn.ensemble', 'sklearn.metrics', 'geneticalgorithm2', 're', 'os', 'base64', 'fitz', 'tools', 'frontend', 'frontend.events'],
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
