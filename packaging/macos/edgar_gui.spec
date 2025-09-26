# -*- mode: python ; coding: utf-8 -*-

import pathlib
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, BUNDLE
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.datastruct import Tree

block_cipher = None

project_root = pathlib.Path(__file__).resolve().parents[1]
scripts_dir = project_root / "scripts"

# Core data directories that the scanner relies on.
config_tree = Tree(str(project_root / "config"), prefix="config", excludes=["*.pyc", "__pycache__"])
examples_tree = Tree(str(project_root / "examples"), prefix="examples", excludes=["*.pyc", "__pycache__"])
# Bundle every script so that subprocess calls (scan.py, report.py, etc.) are available.
script_tree = Tree(str(scripts_dir), prefix="embedded_scripts", excludes=["*.pyc", "__pycache__"])

hiddenimports = collect_submodules("pygame") + [
    "numpy",
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.ttk",
]

datas = collect_data_files("pygame")
datas += config_tree.toc
datas += examples_tree.toc
datas += script_tree.toc

a = Analysis(
    [str(scripts_dir / "edgar_gui.py")],
    pathex=[str(scripts_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
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
    name="Edgar",
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Edgar",
)
app = BUNDLE(
    coll,
    name="Edgar.app",
    icon=None,
    bundle_identifier="com.academicevidence.edgar",
)
