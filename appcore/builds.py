"""Native build operations. No Tk calls are made from worker threads."""
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

DLL_SEARCH_LOCK = threading.Lock()


class BuildError(RuntimeError):
    def __init__(self, key, **values):
        super().__init__(key)
        self.key, self.values = key, values


@dataclass
class Result:
    ok: bool
    output: str


def child_environment():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    if getattr(sys, "frozen", False):
        for name in ("LD_LIBRARY_PATH", "LIBPATH"):
            if name + "_ORIG" in env:
                env[name] = env[name + "_ORIG"]
            else:
                env.pop(name, None)
    return env


def command(args, cwd=None, timeout=120):
    options = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}
    try:
        with DLL_SEARCH_LOCK:
            frozen_windows = sys.platform == "win32" and getattr(sys, "frozen", False)
            if frozen_windows:
                import ctypes
                ctypes.windll.kernel32.SetDllDirectoryW(None)
            try:
                proc = subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True,
                                      text=True, encoding="utf-8", errors="replace", timeout=timeout,
                                      env=child_environment(), **options)
            finally:
                if frozen_windows:
                    ctypes.windll.kernel32.SetDllDirectoryW(str(sys._MEIPASS))
        return Result(proc.returncode == 0, proc.stdout + proc.stderr)
    except subprocess.TimeoutExpired as exc:
        def decode(value):
            return value.decode("utf-8", "replace") if isinstance(value, bytes) else value or ""
        return Result(False, decode(exc.stdout) + decode(exc.stderr) + "\n[timeout]")


def python_command(configured=""):
    choices = [[configured]] if configured else []
    if not getattr(sys, "frozen", False):
        choices.append([sys.executable])
    if sys.platform == "win32":
        choices.append(["py", "-3"])
    choices += [["python3"], ["python"]]
    for candidate in choices:
        executable = shutil.which(candidate[0])
        if not executable:
            continue
        if getattr(sys, "frozen", False) and Path(executable).resolve() == Path(sys.executable).resolve():
            continue
        try:
            result = command(candidate + ["-c", "import sys; assert sys.version_info >= (3, 10); print('CHIMPICODE_PYTHON')"], timeout=10)
            if result.ok and "CHIMPICODE_PYTHON" in result.output:
                return [executable, *candidate[1:]]
        except OSError:
            continue
    raise BuildError("python_missing")


def build_and_run(source, python_path=""):
    source = Path(source).resolve()
    ext = source.suffix.lower()
    work = source.parent / ".chimpicode" / "work"
    work.mkdir(parents=True, exist_ok=True)
    if ext == ".py":
        return command(python_command(python_path) + [str(source)], cwd=source.parent, timeout=30)
    output = work / ("program.exe" if sys.platform == "win32" else "program")
    if ext == ".c":
        compiler = shutil.which("clang") or shutil.which("gcc")
        options, language, tools = [], "C", "Clang/GCC"
    elif ext in {".cpp", ".cc", ".cxx"}:
        compiler = shutil.which("clang++") or shutil.which("g++")
        options, language, tools = ["-std=c++20"], "C++", "Clang++/G++"
    elif ext == ".swift":
        text = source.read_text(encoding="utf-8")
        if "import SwiftUI" in text or "import UIKit" in text:
            raise BuildError("swift_ui")
        compiler = shutil.which("swiftc")
        options, language, tools = [], "Swift", "Swift toolchain"
    else:
        raise BuildError("unsupported", extension=ext)
    if not compiler:
        raise BuildError("compiler_missing", language=language, tools=tools)
    compiled = command([compiler, str(source), *options, "-o", str(output)], cwd=source.parent)
    if not compiled.ok:
        return compiled
    executed = command([str(output)], cwd=source.parent, timeout=30)
    return Result(executed.ok, compiled.output + executed.output)


def native_target(target, system=None):
    system = system or platform.system()
    required = "Darwin" if target == ".app" else "Windows"
    if target not in {".app", ".exe", ".msi"}:
        raise ValueError(target)
    if system != required:
        raise BuildError("native_only", target=target, system="macOS" if required == "Darwin" else "Windows")


def export_python(source, target, destination, name, python_path=""):
    native_target(target)
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,59}", name):
        raise BuildError("name_invalid")
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source.suffix.lower() != ".py":
        raise BuildError("python_export_only")
    final = destination / (name + ".app" if target == ".app" else name)
    msi = destination / f"{name}-1.0.0-x64.msi"
    if final.exists() or (target == ".msi" and msi.exists()):
        raise BuildError("export_exists")
    python = python_command(python_path)
    if target == ".msi":
        architecture = command(python + ["-c", "import sysconfig; print(sysconfig.get_platform())"])
        if not architecture.ok or architecture.output.strip() != "win-amd64":
            raise BuildError("msi_x64")
    checked = command(python + ["-c", "import PyInstaller"], cwd=source.parent)
    if not checked.ok:
        raise BuildError("pyinstaller_missing", command=subprocess.list2cmdline(python))
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="chimpicode-export-") as temporary:
        temp = Path(temporary)
        args = python + ["-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", "--windowed",
                         "--name", name, "--distpath", str(temp / "dist"),
                         "--workpath", str(temp / "work"), "--specpath", str(temp)]
        if target == ".app":
            args += ["--osx-bundle-identifier", "com.snoopyos." + name.lower()]
        result = command(args + [str(source)], cwd=source.parent, timeout=900)
        if not result.ok:
            return result, None
        built = temp / "dist" / (name + ".app" if target == ".app" else name)
        if not built.exists():
            return Result(False, result.output + "\nMissing package output"), None
        if target == ".msi":
            from .msi import build_msi
            build_msi(built, msi, name=name)
        shutil.copytree(built, final, symlinks=True)
        return result, msi if target == ".msi" else final
