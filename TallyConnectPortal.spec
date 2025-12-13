# -*- mode: python ; coding: utf-8 -*-
# TallyConnect Portal - PyInstaller Specification File
# Standalone portal server executable

a = Analysis(
    ['portal_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('reports', 'reports'),
        ('database', 'database'),
        ('portal_server.py', '.'),
    ],
    hiddenimports=[
        'sqlite3', 'http.server', 'socketserver', 'webbrowser',
        'reports', 'reports.report_generator', 'reports.utils',
        'database', 'database.queries',
        'json', 'urllib.parse',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'tkinter'],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TallyConnectPortal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console (can be minimized, useful for debugging)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

