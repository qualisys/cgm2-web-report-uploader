# -*- mode: python -*-

block_cipher = None


a = Analysis(['QWRI.py'],
             pathex=['E:\\Qualisys_repository\\Gait-Web-Importer\\Templates'],
             binaries=[('ffmpeg/bin/ffmpeg.exe','ffmpeg/bin')],
             datas=[('Normatives/normatives.xml', 'Normatives')],
			 hiddenimports=['scipy._lib.messagestream'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='QWRI',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='QWRI')
