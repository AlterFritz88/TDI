# -*- mode: python ; coding: utf-8 -*-

#  python -m PyInstaller --onefile TDI.spec

from kivymd import hooks_path as kivymd_hooks_path


block_cipher = None


a = Analysis(['main.py'],
             pathex=['/home/sasha/PycharmProjects/TDI'],

             hookspath = [kivymd_hooks_path],
             datas=None,

             # тут надо перечислить все что я импортирую в kv файлах

             hiddenimports
             =['ui.popups', 'ui.checkbox_logic', 'main_utility'],

             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += [('ui/main_menu.kv', 'ui/main_menu.kv', 'DATA')]
a.datas += [('ui/popups.kv', 'ui/popups.kv', 'DATA')]



exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='TDI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

