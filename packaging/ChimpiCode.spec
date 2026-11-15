# Run through scripts/build.py from the repository root.
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH).parent
data = collect_data_files("customtkinter")
data += [(str(root / "locales"), "locales"), (str(root / "settings.default.json"), "."),
         (str(root / "LICENSE"), "."), (str(root / "README.md"), ".")]
if sys.platform == "win32":
    data += [(str(root / "from.cmd"), ".")]
a = Analysis([str(root / "chimpicode.py")], pathex=[str(root)], binaries=[], datas=data,
             hiddenimports=["appcore.msi", "PIL._tkinter_finder"], hookspath=[], hooksconfig={},
             runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="ChimpiCode", debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=False,
          contents_directory="lib", version=str(root / "packaging" / "version.txt") if sys.platform == "win32" else None)
collection = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="ChimpiCode")
if sys.platform == "darwin":
    app = BUNDLE(collection, name="ChimpiCode.app", bundle_identifier="com.snoopyos.chimpicode",
                 info_plist={"CFBundleName": "ChimpiCode", "CFBundleShortVersionString": "1.1.0",
                             "CFBundleVersion": "1.1.0", "NSHighResolutionCapable": True})
