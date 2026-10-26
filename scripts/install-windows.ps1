param([string[]]$CommandArguments)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:ChimpiVersion = '1.1.0'
$script:ChimpiRepository = 'Chimpi-hackintosh/ChimpiCode'

function Get-ChimpiText([string]$Portuguese, [string]$English) {
    if ([Globalization.CultureInfo]::CurrentUICulture.TwoLetterISOLanguageName -eq 'pt') { return $Portuguese }
    return $English
}

function Assert-ChimpiArguments([string[]]$Tokens) {
    $expected = @('my', 'computer', '--install', 'chimpicode', '--from', 'github.com')
    if ($Tokens.Count -ne $expected.Count) { throw 'from my computer --install chimpicode --from github.com' }
    for ($index = 0; $index -lt $expected.Count; $index++) {
        if ($Tokens[$index] -ine $expected[$index]) { throw 'from my computer --install chimpicode --from github.com' }
    }
}

function Get-ChimpiRelease([object[]]$Releases) {
    $installerName = "ChimpiCode-$script:ChimpiVersion-x64-Setup.exe"
    foreach ($release in @($Releases | Sort-Object -Property published_at -Descending)) {
        if ($release.draft -or $release.tag_name -notmatch '^v1\.1\.0-preview\.\d+$') { continue }
        $installer = @($release.assets | Where-Object { $_.name -ceq $installerName })
        $checksum = @($release.assets | Where-Object { $_.name -ceq 'SHA256SUMS.txt' })
        if ($installer.Count -ne 1 -or $checksum.Count -ne 1) { continue }
        $prefix = "https://github.com/$script:ChimpiRepository/releases/download/$($release.tag_name)/"
        foreach ($asset in @($installer[0], $checksum[0])) {
            if ($asset.browser_download_url -cne ($prefix + $asset.name)) {
                throw (Get-ChimpiText 'A URL do pacote não pertence ao repositório do ChimpiCode' 'The package URL does not belong to the ChimpiCode repository')
            }
        }
        return @{Installer=$installer[0]; Checksum=$checksum[0]; Tag=$release.tag_name}
    }
    throw (Get-ChimpiText 'Nenhum instalador compilado está disponível ainda — aguarde o build do GitHub' 'No compiled installer is available yet — wait for the GitHub build')
}

function Assert-ChimpiChecksum([string]$File, [string]$ChecksumText, [string]$Name) {
    $pattern = '^([A-Fa-f0-9]{64})\s+\*?' + [regex]::Escape($Name) + '$'
    $matches = @($ChecksumText -split '\r?\n' | Where-Object { $_ -match $pattern })
    if ($matches.Count -ne 1) { throw 'Missing or ambiguous SHA-256 checksum' }
    $expected = [regex]::Match($matches[0], $pattern).Groups[1].Value
    $actual = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash
    if ($actual -ine $expected) { throw 'SHA-256 verification failed' }
}

function Invoke-ChimpiInstall([string[]]$Tokens) {
    Assert-ChimpiArguments $Tokens
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT -or ![Environment]::Is64BitOperatingSystem) {
        throw (Get-ChimpiText 'Este instalador exige Windows de 64 bits' 'This installer requires 64-bit Windows')
    }
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $headers = @{'User-Agent'='ChimpiCode-from/1.1.0'; 'Accept'='application/vnd.github+json'}
    Write-Host (Get-ChimpiText 'Procurando o ChimpiCode no GitHub...' 'Looking up ChimpiCode on GitHub...')
    $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$script:ChimpiRepository/releases?per_page=30" -Headers $headers -TimeoutSec 45
    $package = Get-ChimpiRelease $releases
    $temporary = Join-Path ([IO.Path]::GetTempPath()) ('ChimpiCode-install-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $temporary | Out-Null
    try {
        $installer = Join-Path $temporary $package.Installer.name
        $checksum = Join-Path $temporary 'SHA256SUMS.txt'
        Write-Host (Get-ChimpiText 'Baixando o instalador...' 'Downloading the installer...')
        Invoke-WebRequest -UseBasicParsing -Uri $package.Checksum.browser_download_url -Headers $headers -OutFile $checksum -TimeoutSec 60
        Invoke-WebRequest -UseBasicParsing -Uri $package.Installer.browser_download_url -Headers $headers -OutFile $installer -TimeoutSec 600
        Assert-ChimpiChecksum $installer ([IO.File]::ReadAllText($checksum)) $package.Installer.name
        Write-Host (Get-ChimpiText 'Abrindo o instalador — confirme a solicitação do Windows' 'Opening the installer — confirm the Windows prompt')
        $process = Start-Process -FilePath $installer -Verb RunAs -Wait -PassThru
        if ($process.ExitCode -notin @(0, 3010)) { throw "Windows Installer: $($process.ExitCode)" }
        Write-Host (Get-ChimpiText 'ChimpiCode instalado — abra um novo CMD para usar o comando from em qualquer pasta' 'ChimpiCode installed — open a new CMD to use from in any folder')
    } finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Recurse -Force }
    }
}

# Dot-sourcing loads the functions for tests without downloading or executing anything.
if ($MyInvocation.InvocationName -ne '.') {
    try {
        $tokens = @($CommandArguments | Where-Object { $_ })
        if ($env:CHIMPI_FROM_ARGUMENTS) { $tokens = @($env:CHIMPI_FROM_ARGUMENTS.Trim() -split '\s+') }
        if ($tokens.Count -eq 0 -or ($tokens.Count -eq 1 -and $tokens[0] -in @('--help', '/?'))) {
            Write-Host 'from my computer --install chimpicode --from github.com'
            exit 0
        }
        Invoke-ChimpiInstall $tokens
        exit 0
    } catch {
        Write-Host ((Get-ChimpiText 'Não foi possível instalar: ' 'Unable to install: ') + $_.Exception.Message) -ForegroundColor Red
        exit 1
    }
}
