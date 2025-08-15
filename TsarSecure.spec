# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import PyInstaller.versionfile

APP_NAME = "TsarSecure"
SCRIPT = "TsarSecure.py"
ICON = "ts.ico"

# Add runtime data files
datas = [
    ("eff_large_wordlist.txt", "."),
]
datas += collect_data_files("certifi")

block_cipher = None

# Embed Windows version info
PyInstaller.versionfile.create_versionfile(
    output_file="versionfile.txt",
    version="2.5.0",
    company_name="TsarSecure Project",
    file_description="TsarSecure - Secure Password & Passphrase Generator",
    internal_name=APP_NAME,
    legal_copyright="© 2025 TsarSecure Project",
    original_filename=f"{APP_NAME}.exe",
    product_name=APP_NAME,
    product_version="2.5.0"
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
    console=False,  # Consumer build – no console
    icon=ICON,
    version="versionfile.txt"
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, upx_exclude=[],
    name=APP_NAME
)
