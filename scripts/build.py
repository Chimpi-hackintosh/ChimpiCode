"""Build ChimpiCode on its target OS; never fabricate cross-platform outputs."""
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from appcore import VERSION
from appcore.msi import build_msi


def run(args):
    subprocess.run([str(x) for x in args], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--installers", action="store_true")
    args = parser.parse_args()
    if sys.platform not in {"win32", "darwin"}:
        raise SystemExit("Build .exe/.msi on Windows and .app on macOS")
    if sys.platform == "win32" and sysconfig.get_platform() != "win-amd64":
        raise SystemExit("Use Windows x64 Python for this Windows package")
    release = ROOT / "release"
    release.mkdir(exist_ok=True)
    run([sys.executable, "scripts/make-launcher.py"])
    run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "packaging/ChimpiCode.spec"])
    staging = ROOT / "dist" / ("ChimpiCode" if sys.platform == "win32" else "ChimpiCode.app")
    if sys.platform == "win32":
        for name in ("locales", "settings.default.json", "LICENSE", "README.md", "from.cmd"):
            source, target = staging / "lib" / name, staging / name
            if source.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                elif target.exists():
                    target.unlink()
                shutil.move(source, target)
    sources = [p for p in staging.rglob("*") if p.is_file() and p.suffix.lower() in {".py", ".pyw"}]
    if sources:
        raise RuntimeError(f"Unexpected source files in distribution: {sources[:5]}")
    dependencies = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    (release / "build-dependencies.txt").write_text(dependencies, encoding="utf-8")
    if sys.platform == "darwin":
        # ditto preserves symlinks and executable modes required by .app bundles.
        archive = release / f"ChimpiCode-{VERSION}-macOS-{platform.machine()}.zip"
        run(["/usr/bin/ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", staging, archive])
    else:
        shutil.make_archive(str(release / f"ChimpiCode-{VERSION}-Windows-x64-portable"), "zip", staging.parent, staging.name)
        if args.installers:
            build_msi(staging, release / f"ChimpiCode-{VERSION}-x64.msi", version=VERSION)
            build_msi(staging, release / f"ChimpiCode-{VERSION}-x64-pt-BR.msi", version=VERSION, language="pt-BR")
            nsis = shutil.which("makensis") or str(Path(r"C:\Program Files (x86)\NSIS\makensis.exe"))
            run([nsis, f"/DVERSION={VERSION}", f"/DRELEASE_DIR={release}", ROOT / "packaging" / "setup.nsi"])
    sums = []
    for file in sorted(release.iterdir()):
        if file.suffix.lower() in {".zip", ".msi", ".exe"}:
            sums.append(hashlib.sha256(file.read_bytes()).hexdigest() + "  " + file.name)
    (release / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
