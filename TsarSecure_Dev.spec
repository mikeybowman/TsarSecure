# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import PyInstaller.versionfile

APP_NAME = "TsarSecure_Dev"
SCRIPT = "TsarSecure.py"
ICON = "ts.ico"

datas = [
    ("eff_large_wordlist.txt", "."),
]
datas += collect_data_files("certifi")

block_cipher = None

PyInstaller.versionfile.create_versionfile(
    output_file="versionfile_dev.txt",
    version="2.5.0-dev",
    company_name="TsarSecure Project",
    file_description="TsarSecure Development Build - Includes Console Output",
    internal_name=APP_NAME,
    legal_copyright="© 2025 TsarSecure Project",
    original_filename=f"{APP_NAME}.exe",
    product_name=APP_NAME,
    product_version="2.5.0-dev"
)

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
    console=True,  # Dev build – console ON
    icon=ICON,
    version="versionfile_dev.txt"
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, upx_exclude=[],
    name=APP_NAME
)
