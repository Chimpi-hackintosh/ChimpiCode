$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/install-windows.ps1"
Assert-ChimpiArguments @('my','computer','--install','chimpicode','--from','github.com')
foreach ($tokens in @(
    @('my','computer','--install','anotherapp','--from','github.com'),
    @('my','computer','--install','chimpicode','--from','example.com'),
    @('my','computer','--install','chimpicode')
)) {
    $rejected = $false
    try { Assert-ChimpiArguments $tokens } catch { $rejected = $true }
    if (!$rejected) { throw 'Invalid install arguments were accepted' }
}
$name = 'ChimpiCode-1.1.0-x64-Setup.exe'
$prefix = 'https://github.com/Chimpi-hackintosh/ChimpiCode/releases/download/v1.1.0-preview.1/'
$release = [pscustomobject]@{
    draft=$false;tag_name='v1.1.0-preview.1';published_at='2026-10-26T12:00:00Z';
    assets=@([pscustomobject]@{name=$name;browser_download_url=$prefix+$name},
             [pscustomobject]@{name='SHA256SUMS.txt';browser_download_url=$prefix+'SHA256SUMS.txt'})
}
$selected = Get-ChimpiRelease @($release)
if ($selected.Installer.name -ne $name) { throw 'Incorrect release asset selected' }
$release.assets[0].browser_download_url = 'https://example.com/installer.exe'
$rejected = $false
try { Get-ChimpiRelease @($release) } catch { $rejected = $true }
if (!$rejected) { throw 'External installer URL accepted' }
$temporary = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString('N'))
try {
    [IO.File]::WriteAllText($temporary,'checksum fixture')
    $hash = (Get-FileHash $temporary -Algorithm SHA256).Hash
    Assert-ChimpiChecksum $temporary "$hash  $name" $name
    $rejected = $false
    try { Assert-ChimpiChecksum $temporary ((('0' * 64) -join '') + "  $name") $name } catch { $rejected = $true }
    if (!$rejected) { throw 'Modified installer accepted' }
} finally { Remove-Item -LiteralPath $temporary -Force }
$launcher = Join-Path (Split-Path -Parent $PSScriptRoot) 'from.cmd'
$env:CHIMPI_FROM_ARGUMENTS = $null
& cmd.exe /d /c "`"$launcher`" --help"
if ($LASTEXITCODE -ne 0) { throw 'Standalone CMD launcher failed' }
Write-Host 'CLI arguments, repository allowlist, checksums and standalone help passed'
