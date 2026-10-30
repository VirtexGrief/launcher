# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['run.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/virtex_launcher/resources', 'virtex_launcher/resources')],
    hiddenimports=collect_submodules('virtex_launcher') + ['minecraft_launcher_lib'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='VirtexLauncher',
    debug=False,
    strip=False,
    upx=False,          # UPX ломает minecraft_launcher_lib — не включай!
    console=False,
    icon=None,          # положи icon.ico и укажи 'icon.ico'
)