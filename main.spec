# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ("qtmWebGaitReport\\Normatives\\normatives.xml","qtmWebGaitReport\\Normatives"),
]

a = Analysis(['main.py'],
             pathex=[''],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# add all normatives from pyCGM2 to datas

import pyCGM2

pyCGM2_path = os.path.abspath(os.path.join(os.path.dirname(pyCGM2.__file__),os.pardir))
pyCGM2_normative_path = os.path.join(pyCGM2_path,"pyCGM2\\Data\\normativeData")
pyCGM2_normatives = Tree( pyCGM2_normative_path, prefix="pyCGM2\\Data\\normativeData",excludes=['*.pyx','*.py','*.pyc'])
pyCGM2_settings_path = os.path.join(pyCGM2_path,"pyCGM2\\Settings")
pyCGM2_settings = Tree(pyCGM2_settings_path,prefix="pyCGM2\\Settings",excludes=['*.pyx','*.py','*.pyc'])

a.datas += pyCGM2_normatives
a.datas += pyCGM2_settings

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='QCGM2',
          version='file-version.py',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
