"""Build one readable CMD/PowerShell launcher; no WinGet or policy changes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = r'''@echo off
setlocal
set "CHIMPI_FROM_FILE=%~f0"
set "CHIMPI_FROM_ARGUMENTS=%*"
powershell.exe -NoLogo -NoProfile -Command "$text=[IO.File]::ReadAllText($env:CHIMPI_FROM_FILE); $marker='# POWERSHELL_START'; $body=$text.Substring($text.LastIndexOf($marker)+$marker.Length); & ([ScriptBlock]::Create($body))"
exit /b %ERRORLEVEL%
# POWERSHELL_START
'''


def make_launcher():
    content = HEADER + (ROOT / "scripts" / "install-windows.ps1").read_text(encoding="utf-8")
    # Explicit UTF-8 reading in the wrapper keeps pt-BR messages intact on Windows.
    (ROOT / "from.cmd").write_bytes(content.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))


if __name__ == "__main__":
    make_launcher()
