# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['payroll/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('payroll/defaults/template.xlsx', 'defaults'),
        ('payroll/defaults/config.yaml', 'defaults'),
        ('payroll/defaults/Logo.png', 'defaults'),
        ('payroll/template.png', '.'),
    ],
    hiddenimports=['tkinter', 'customtkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PAYROLL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='PAYROLL',
)
app = BUNDLE(
    coll,
    name='PAYROLL.app',
    icon=None,
    bundle_identifier='com.bombon.payroll',
)
