# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

import vgamepad

ROOT = Path(SPECPATH).parent  # Python/
VGAMEPAD_DIR = os.path.dirname(vgamepad.__file__)

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[(os.path.join(VGAMEPAD_DIR, "win"), "vgamepad/win")],
    hiddenimports=["vgamepad", "pycaw.pycaw", "comtypes.stream"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Soundproject",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(Path(SPECPATH) / "icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="Soundproject",
)
