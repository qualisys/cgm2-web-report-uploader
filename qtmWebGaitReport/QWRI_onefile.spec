# -*- mode: python -*-

block_cipher = None


a = Analysis(['QWRI.py'],
             pathex=['E:\\Qualisys_repository\\Gait-Web-Importer\\Templates'],
             binaries=[('ffmpeg/bin/ffmpeg.exe','ffmpeg/bin'),('ffmpeg/bin/avcodec-57.dll','ffmpeg/bin'),('ffmpeg/bin/avdevice-57.dll','ffmpeg/bin'),('ffmpeg/bin/avfilter-6.dll','ffmpeg/bin'),('ffmpeg/bin/avformat-57.dll','ffmpeg/bin'),('ffmpeg/bin/avutil-55.dll','ffmpeg/bin'),('ffmpeg/bin/postproc-54.dll','ffmpeg/bin'),('ffmpeg/bin/swresample-2.dll','ffmpeg/bin'),('ffmpeg/bin/swscale-4.dll','ffmpeg/bin')],
             datas=[('Normatives/normatives.xml', 'Normatives')],
			 hiddenimports=['scipy._lib.messagestream'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['mkl_avx512_mic.dll','mkl_avx512.dll','mkl_avx.dll','mkl_mc3.dll','mkl_mc.dll','mkl_def.dll','mkl_pgi_thread.dll','mkl_tbb_thread.dll','mkl_sequential.dll','mkl_vml_avx512_mic.dll','mkl_vml_avx.dll','mkl_vml_avx512.dll','mkl_vml_mc.dll','mkl_vml_mc3.dll','mkl_vml_mc2.dll','mkl_scalapack_ilp64.dll','mkl_scalapack_lp64.dll','mkl_vml_def.dll','mkl_vml_cmpt.dll','mfc90u.dll','mfc90.dll'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries - [('mkl_avx512_mic.dll',None, 'BINARY'),('mkl_avx512.dll',None, 'BINARY'),('mkl_avx.dll',None, 'BINARY'),('mkl_mc3.dll',None, 'BINARY'),('mkl_mc.dll',None, 'BINARY'),('mkl_def.dll',None, 'BINARY'),('mkl_pgi_thread.dll',None, 'BINARY'),('mkl_tbb_thread.dll',None, 'BINARY'),('mkl_sequential.dll',None, 'BINARY'),('mkl_vml_avx512_mic.dll',None, 'BINARY'),('mkl_vml_avx.dll',None, 'BINARY'),('mkl_vml_avx512.dll',None, 'BINARY'),('mkl_vml_mc.dll',None, 'BINARY'),('mkl_vml_mc3.dll',None, 'BINARY'),('mkl_vml_mc2.dll',None, 'BINARY'),('mkl_scalapack_ilp64.dll',None, 'BINARY'),('mkl_scalapack_lp64.dll',None, 'BINARY'),('mkl_vml_def.dll',None, 'BINARY'),('mkl_vml_cmpt.dll',None, 'BINARY'),('mfc90u.dll',None, 'BINARY'),('mfc90.dll',None, 'BINARY')],
          a.zipfiles,
          a.datas,
          name='QWRI',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
