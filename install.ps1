# Instala el comando wallpaper-google en Windows (sin ser administrador).
# Uso:  powershell -ExecutionPolicy Bypass -File .\install.ps1
$ErrorActionPreference = "Stop"
$dir = $PSScriptRoot

# Buscar Python 3 (el lanzador "py" del instalador de python.org, o "python").
$python = $null
$code = "import sys; print(sys.executable)"
foreach ($finder in @({ py -3 -c $code }, { python -c $code })) {
    try {
        $exe = & $finder 2>$null
        if ($LASTEXITCODE -eq 0 -and $exe -and (Test-Path $exe.Trim())) { $python = $exe.Trim(); break }
    } catch {}
}
if (-not $python) {
    Write-Host "No encontré Python 3. Instalalo con:  winget install Python.Python.3.12"
    Write-Host "y después abrí una terminal nueva y volvé a correr este instalador."
    exit 1
}

$bin = Join-Path $env:LOCALAPPDATA "wallpaper-google\bin"
New-Item -ItemType Directory -Force -Path $bin | Out-Null
$cmdFile = Join-Path $bin "wallpaper-google.cmd"
# Rutas con %USERPROFILE% para que no se rompan si el nombre de usuario tiene tildes o ñ.
function Portable($p) { $p.Replace($env:USERPROFILE, "%USERPROFILE%") }
$dirCmd = Portable $dir
$pythonCmd = Portable $python
Set-Content -Path $cmdFile -Encoding ASCII -Value @"
@echo off
set "PYTHONPATH=$dirCmd"
"$pythonCmd" -m wallpaper_google %*
"@

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
if (($userPath -split ";") -notcontains $bin) {
    [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(";") + ";" + $bin).TrimStart(";"), "User")
    Write-Host "Agregué $bin al PATH. Abrí una terminal nueva para usar el comando."
}
Write-Host "Instalado: wallpaper-google (usa $python)"
