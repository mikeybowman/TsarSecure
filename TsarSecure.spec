# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

APP_NAME = "TsarSecure"
SCRIPT = "TsarSecure.py"
ICON = "ts.ico"

datas = [("eff_large_wordlist.txt", ".")]
datas += collect_data_files("certifi")

block_cipher = None

a = Analysis(
    [SCRIPT],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    strip=False,
    upx=True,
    console=False,      # consumer build
    icon=ICON,
    version="version.txt"   # <-- points to the file above
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, upx_exclude=[],
    name=APP_NAME
)
