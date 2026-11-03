import ctypes
import os
import sys
from pathlib import Path


def resource_root():
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            return Path(sys.executable).resolve().parent
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def user_data_dir():
    if sys.platform == "win32":
        buffer = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 0x001C, None, 0, buffer) != 0:
            raise OSError("Cannot resolve LocalAppData")
        base = Path(buffer.value)
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "SnoopyOS Company" / "ChimpiCode"


def preferred_ui_languages():
    if sys.platform == "win32":
        count = ctypes.c_ulong()
        size = ctypes.c_ulong()
        fn = ctypes.windll.kernel32.GetUserPreferredUILanguages
        if fn(8, ctypes.byref(count), None, ctypes.byref(size)):
            buffer = ctypes.create_unicode_buffer(size.value)
            if fn(8, ctypes.byref(count), buffer, ctypes.byref(size)):
                return buffer[:].rstrip("\0").split("\0")
        return []
    if sys.platform == "darwin":
        import plistlib
        import subprocess
        try:
            result = subprocess.run(["/usr/bin/defaults", "export", "NSGlobalDomain", "-"],
                                    capture_output=True, timeout=5, check=True)
            return plistlib.loads(result.stdout).get("AppleLanguages", [])
        except (OSError, ValueError, subprocess.SubprocessError):
            return []
    return [os.environ.get("LANGUAGE", "").split(":")[0], os.environ.get("LANG", "en")]
