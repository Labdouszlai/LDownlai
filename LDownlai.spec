# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['html'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PIL', 'Pillow', 'Image', 'ImageTk',
        'tkinter.test', 'test',
        'distutils', 'setuptools',
        'lib2to3', 'multiprocessing', 'concurrent',
        'http.server', 'http.cookies',
        'email', 'pydoc',
        'unittest', 'doctest',
        'pickle', 'dbm', 'sqlite3',
        'turtle', 'audiodev',
        'tcl8', 'tk8',
        'xml.dom', 'xml.sax', 'xml.parsers',
        'json.tool',
        'zipfile', 'tarfile',
        'bz2', 'lzma',
        'webbrowser',
        'msvcrt',
        'crypt',
        'symtable',
        'tabnanny',
        'profile', 'pstats',
        'this', 'antigravity',
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
