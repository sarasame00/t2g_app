# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

block_cipher = None

project_dir = Path().resolve()

a = Analysis(
    ['app/run.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        ('app/pages', 'pages'),
        ('app/assets', 'assets'),
        ('app/run.py', 'app/run.py'),
        ('logic', 'logic'),
        ('sync', 'sync'),
        ('plots', 'plots'),
        ('data', 'data'),
        ('drive_service_account.json', '.'),
    ],
    hiddenimports=[
        'h5py',
        'h5py._conv',      # needed sometimes
        'h5py.defs',        # needed for type info
        'h5py._hl.group',   # internal modules
        'h5py._hl.files',
        'h5py._hl.dataset',
        'h5py._hl.selections',
        'h5py._hl.datatype',
        'h5py._hl.attrs',
        'dash_bootstrap_components',
        'sklearn',
        'scipy',
        'matplotlib',
        'pandas',
        'numpy',
        'googleapiclient',
        'google',
        'google.auth',
        'google_auth_httplib2',
        'googleapiclient.discovery',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run',
)
