# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

_ejs_hidden = collect_submodules('yt_dlp_ejs')
_ejs_datas = collect_data_files('yt_dlp_ejs')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=_ejs_datas,
    hiddenimports=['html'] + _ejs_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PIL', 'Pillow', 'Image', 'ImageTk',
        'tkinter.test', 'test',
        'turtle', 'audiodev',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LDownlai',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',
)
