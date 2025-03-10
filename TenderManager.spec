# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Zack\\Desktop\\School stuff\\Sheet_Metal_Project\\sheet_metal_scraper\\tenderapp', '.'), ('C:\\Users\\Zack\\Desktop\\School stuff\\Sheet_Metal_Project\\sheet_metal_scraper\\tender_data', './tender_data')],
    hiddenimports=['PySide6', 'PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui'],
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
    [],
    exclude_binaries=True,
    name='TenderManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TenderManager',
)
