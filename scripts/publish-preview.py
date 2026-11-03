"""Publish tested desktop artifacts from this workflow as a versioned preview."""
import hashlib
import os
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
artifacts = root / "packages"
release = root / "publish"
release.mkdir(exist_ok=True)
files = []
for source in sorted(artifacts.rglob("*")):
    if source.is_file() and source.suffix.lower() in {".exe", ".msi", ".zip"}:
        destination = release / source.name
        if destination.exists():
            raise RuntimeError(f"Duplicate asset name: {source.name}")
        shutil.copy2(source, destination)
        files.append(destination)
launcher = release / "from.cmd"
shutil.copy2(root / "from.cmd", launcher)
files.append(launcher)
required = {"ChimpiCode-1.1.0-x64-Setup.exe", "ChimpiCode-1.1.0-x64.msi",
            "ChimpiCode-1.1.0-x64-pt-BR.msi", "ChimpiCode-1.1.0-Windows-x64-portable.zip",
            "ChimpiCode-1.1.0-macOS-x86_64.zip", "ChimpiCode-1.1.0-macOS-arm64.zip"}
if not required.issubset({p.name for p in files}):
    raise RuntimeError("Missing native build assets")
checksums = release / "SHA256SUMS.txt"
checksums.write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n" for p in files), encoding="utf-8")
files.append(checksums)
tag = "v1.1.0-preview." + os.environ["GITHUB_RUN_NUMBER"]
notes = release / "notes.md"
notes.write_text('''ChimpiCode 1.1.0 — desktop preview

Windows x64: Setup EXE, MSI em inglês/pt-BR e ZIP portátil
macOS: aplicativos separados para Intel e Apple Silicon

Os testes e verificações nativas do workflow passaram antes desta publicação
Pacotes sem assinatura comercial ou notarização

Instalação no CMD sem WinGet: baixe `from.cmd`, abra o CMD nessa pasta e execute

```cmd
from my computer --install chimpicode --from github.com
```

O comando baixa o Setup deste repositório e confere o SHA-256 antes de executá-lo
''', encoding="utf-8")
subprocess.run(["gh", "release", "create", tag, "--repo", os.environ["GITHUB_REPOSITORY"],
                "--target", os.environ["GITHUB_SHA"], "--prerelease", "--title", "ChimpiCode 1.1.0 — Desktop Preview",
                "--notes-file", str(notes), *map(str, files)], check=True)
