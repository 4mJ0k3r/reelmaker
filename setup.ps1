<#
ReelForge first-run setup for Windows.

ReelForge renders with Linux tools (Python 3.12, Cairo, FFmpeg), so on Windows it runs inside
WSL2 Ubuntu 24.04. This script finds your WSL Ubuntu distro and runs setup.sh inside it.

  powershell -ExecutionPolicy Bypass -File .\setup.ps1
  powershell -ExecutionPolicy Bypass -File .\setup.ps1 -Distro Ubuntu-24.04

If WSL is missing:  wsl --install -d Ubuntu-24.04   (then reboot if asked, and re-run this script)
#>
[CmdletBinding()]
param([string]$Distro = "")

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

# PowerShell on Linux/macOS: just run the bash script.
if ($PSVersionTable.PSVersion.Major -ge 6 -and -not $IsWindows) {
    & bash "$Here/setup.sh"
    exit $LASTEXITCODE
}

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] WSL is not installed." -ForegroundColor Red
    Write-Host "       Install it with:  wsl --install -d Ubuntu-24.04   (then re-run setup.ps1)"
    exit 1
}

# `wsl -l -q` prints UTF-16; strip NULs before parsing.
$raw = (& wsl.exe -l -q) -join "`n"
$names = ($raw -replace "`0", "") -split "[\r\n]+" | ForEach-Object { $_.Trim() } | Where-Object { $_ }

if (-not $Distro) {
    $Distro = $names | Where-Object { $_ -eq "Ubuntu-24.04" } | Select-Object -First 1
    if (-not $Distro) { $Distro = $names | Where-Object { $_ -like "Ubuntu*" } | Select-Object -First 1 }
}
if (-not $Distro) {
    Write-Host "[FAIL] No Ubuntu WSL distribution found. Installed distros: $($names -join ', ')" -ForegroundColor Red
    Write-Host "       Install one with:  wsl --install -d Ubuntu-24.04"
    exit 1
}
Write-Host "[info] Using WSL distro: $Distro"

# `--cd` accepts a Windows path directly (no manual backslash translation needed).
$WslPath = ((& wsl.exe -d $Distro --cd "$Here" -- pwd) | Out-String).Trim()
if (-not $WslPath) {
    Write-Host "[FAIL] Could not open '$Here' inside WSL." -ForegroundColor Red
    exit 1
}
if ($WslPath -like "/mnt/*") {
    Write-Host "[info] Project is on a Windows drive ($WslPath). It works; a copy inside the WSL home (~/) is faster."
}

& wsl.exe -d $Distro --cd "$Here" -- bash ./setup.sh
$code = $LASTEXITCODE
if ($code -eq 0) {
    Write-Host ""
    Write-Host "Run reels from Windows with:"
    Write-Host "  wsl -d $Distro --cd `"$Here`" -- python3 run_reel.py `"Yellow Mellow discovers an emergency signal in snowy mountains`""
}
exit $code
