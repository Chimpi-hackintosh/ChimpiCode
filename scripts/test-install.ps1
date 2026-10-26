# Disposable GitHub runner only. Exercises a previous-version fixture, upgrade,
# runtime resources, start-menu shortcut, per-user settings and uninstall.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$report = Join-Path $root 'release/installed-runtime-check.json'
$installed = Join-Path $env:ProgramFiles 'SnoopyOS Company/ChimpiCode/ChimpiCode.exe'
$settingsDir = Join-Path $env:LOCALAPPDATA 'SnoopyOS Company/ChimpiCode'
$settingsFile = Join-Path $settingsDir 'settings.json'

function Run-Installer([string]$file, [string[]]$arguments) {
  $process = Start-Process -FilePath $file -ArgumentList $arguments -Wait -PassThru
  if ($process.ExitCode -notin @(0, 3010)) { throw "Installer returned $($process.ExitCode)" }
}

New-Item -ItemType Directory -Force 'build' | Out-Null
python -c "from appcore.msi import build_msi; build_msi('dist/ChimpiCode','build/previous-version.msi',version='1.0.0')"
if ($LASTEXITCODE -ne 0) { throw 'Previous-version test fixture failed' }
$oldPackage = Join-Path $root 'build/previous-version.msi'
Run-Installer 'msiexec.exe' @('/i', "`"$oldPackage`"", '/qn', '/norestart', '/l*v', "`"$root/build/install-old.log`"")
New-Item -ItemType Directory -Force $settingsDir | Out-Null
'{"language":"pt-BR","model":"ci-sentinel","schema_version":1}' | Set-Content -Path $settingsFile -Encoding utf8
$before = Get-FileHash $settingsFile
$setup = Join-Path $root 'release/ChimpiCode-1.1.0-x64-Setup.exe'
Run-Installer $setup @('/S')
if (!(Test-Path $installed)) { throw 'Installed EXE is missing' }
if (!(Test-Path (Join-Path (Split-Path $installed) 'from.cmd'))) { throw 'Installed command launcher is missing' }
$machinePath = [Environment]::GetEnvironmentVariable('PATH','Machine')
if ((($machinePath -split ';') | ForEach-Object { $_.TrimEnd('\') }) -notcontains (Split-Path $installed)) { throw 'Command directory is missing from PATH' }
if ((Get-FileHash $settingsFile).Hash -ne $before.Hash) { throw 'Upgrade modified user settings' }
$shortcut = Join-Path $env:ProgramData 'Microsoft/Windows/Start Menu/Programs/ChimpiCode/ChimpiCode.lnk'
if (!(Test-Path $shortcut)) { throw 'Start-menu shortcut is missing' }
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($shortcut)
if ($link.TargetPath -ne $installed) { throw 'Incorrect shortcut target' }
$originalPath = $env:PATH
try {
  $env:PATH = "$env:WINDIR\system32;$env:WINDIR"
  $process = Start-Process -FilePath $link.TargetPath -ArgumentList @('--gui-smoke', "`"$report`"") -WorkingDirectory $env:TEMP -Wait -PassThru
  if ($process.ExitCode -ne 0 -or !(Test-Path $report)) { throw 'Installed GUI failed without Python in PATH' }
} finally { $env:PATH = $originalPath }
$newPackage = Join-Path $root 'release/ChimpiCode-1.1.0-x64.msi'
Run-Installer 'msiexec.exe' @('/x', "`"$newPackage`"", '/qn', '/norestart', '/l*v', "`"$root/build/uninstall.log`"")
if (Test-Path $installed) { throw 'Uninstall did not remove the EXE' }
$machinePath = [Environment]::GetEnvironmentVariable('PATH','Machine')
if ((($machinePath -split ';') | ForEach-Object { $_.TrimEnd('\') }) -contains (Split-Path $installed)) { throw 'Uninstall did not remove the command PATH entry' }
if ((Get-FileHash $settingsFile).Hash -ne $before.Hash) { throw 'Uninstall modified user settings' }
@{ok=$true; upgrade=$true; shortcut=$true; withoutPythonPath=$true; preservedSettings=$true; uninstall=$true} |
  ConvertTo-Json | Set-Content -Encoding utf8 'release/installer-check.json'
