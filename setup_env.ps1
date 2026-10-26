<#
.SYNOPSIS
  DryGYE - one-shot environment installer for Windows (PowerShell 5.1+).

.DESCRIPTION
  Creates (or updates) the "drygye" conda environment from environment.yml.
  If conda is not found, it installs Miniconda for the current user first.
  At the end it runs check_env.py to verify every library.
  Fallback: -Mode venv uses python -m venv + requirements.txt instead of conda.

.PARAMETER Mode
  conda (default) or venv.

.PARAMETER EnvName
  Name of the conda environment. Default: drygye.

.PARAMETER WithTelegram
  Also installs the optional extras from requirements-optional.txt (python-telegram-bot).

.PARAMETER SkipNetCheck
  Skips the Open-Meteo / OpenStreetMap connectivity test at the end.

.PARAMETER Recreate
  Deletes the environment first and builds it again from scratch.

.EXAMPLE
  .\setup_env.ps1
  .\setup_env.ps1 -WithTelegram
  .\setup_env.ps1 -Mode venv
  .\setup_env.ps1 -Recreate
#>
[CmdletBinding()]
param(
    [ValidateSet("conda", "venv")]
    [string]$Mode = "conda",
    [string]$EnvName = "drygye",
    [switch]$WithTelegram,
    [switch]$SkipNetCheck,
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok([string]$Message) {
    Write-Host "[OK]   $Message" -ForegroundColor Green
}

function Write-Warn2([string]$Message) {
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Invoke-Native {
    param([string]$Exe, [string[]]$CmdArgs)
    & $Exe @CmdArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo el comando: $Exe $($CmdArgs -join ' ') (codigo $LASTEXITCODE)"
    }
}

function Find-Conda {
    $cmd = Get-Command conda -ErrorAction SilentlyContinue
    if ($cmd) {
        if ($cmd.Source) { return $cmd.Source }
        return "conda"
    }
    $candidates = @(
        (Join-Path $env:USERPROFILE "miniconda3\Scripts\conda.exe"),
        (Join-Path $env:USERPROFILE "anaconda3\Scripts\conda.exe"),
        (Join-Path $env:LOCALAPPDATA "miniconda3\Scripts\conda.exe"),
        (Join-Path $env:LOCALAPPDATA "anaconda3\Scripts\conda.exe"),
        (Join-Path $env:ProgramData "miniconda3\Scripts\conda.exe"),
        (Join-Path $env:ProgramData "anaconda3\Scripts\conda.exe"),
        "C:\miniconda3\Scripts\conda.exe",
        "C:\anaconda3\Scripts\conda.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

function Install-Miniconda {
    # conda does not like spaces or non-ASCII characters in its install path.
    $dest = Join-Path $env:USERPROFILE "miniconda3"
    if ($dest -match '\s' -or $dest -match '[^\x00-\x7F]') { $dest = "C:\miniconda3" }
    $url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    $installer = Join-Path $env:TEMP "Miniconda3-latest-Windows-x86_64.exe"

    Write-Step "Descargando Miniconda"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing

    Write-Step "Instalando Miniconda en $dest (solo para tu usuario, unos minutos)"
    $proc = Start-Process -FilePath $installer -Wait -PassThru -ArgumentList @(
        "/InstallationType=JustMe", "/AddToPath=0", "/RegisterPython=0", "/S", "/D=$dest"
    )
    Remove-Item $installer -Force -ErrorAction SilentlyContinue
    if ($proc.ExitCode -ne 0) { throw "El instalador de Miniconda fallo (codigo $($proc.ExitCode))." }

    $conda = Join-Path $dest "Scripts\conda.exe"
    if (-not (Test-Path $conda)) { throw "Miniconda se instalo pero no se encontro $conda" }
    return $conda
}

function Get-EnvPrefix([string]$Conda, [string]$Name) {
    $json = & $Conda env list --json | Out-String
    if ($LASTEXITCODE -ne 0) { throw "No se pudo listar los entornos de conda." }
    $data = $json | ConvertFrom-Json
    foreach ($p in $data.envs) {
        if ((Split-Path $p -Leaf) -eq $Name) { return $p }
    }
    return $null
}

function Find-Python {
    $tries = @(
        @{ Exe = "py"; PyArgs = @("-3.11") },
        @{ Exe = "py"; PyArgs = @("-3.12") },
        @{ Exe = "py"; PyArgs = @("-3.10") },
        @{ Exe = "python"; PyArgs = @() }
    )
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        foreach ($t in $tries) {
            if (-not (Get-Command $t.Exe -ErrorAction SilentlyContinue)) { continue }
            $probe = $t.PyArgs + @("-c", "import sys; print('%d.%d' % sys.version_info[:2])")
            $ver = & $t.Exe @probe 2>$null
            if ($LASTEXITCODE -ne 0 -or -not $ver) { continue }
            $parts = ("$ver").Trim().Split(".")
            if ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 10) { return $t }
        }
    } finally {
        $ErrorActionPreference = $old
    }
    return $null
}

# ---------------------------------------------------------------------------
Write-Host "DryGYE - instalacion del entorno" -ForegroundColor White
Write-Host "Carpeta: $PSScriptRoot"

foreach ($f in @("environment.yml", "requirements.txt", "requirements-optional.txt", "check_env.py")) {
    if (-not (Test-Path (Join-Path $PSScriptRoot $f))) {
        throw "Falta el archivo '$f' junto a este script."
    }
}

$envPython = $null

if ($Mode -eq "conda") {
    Write-Step "Buscando conda"
    $conda = Find-Conda
    if (-not $conda) {
        Write-Warn2 "No se encontro conda. Se instalara Miniconda."
        $conda = Install-Miniconda
    }
    Write-Ok "conda: $conda"
    & $conda --version

    $prefix = Get-EnvPrefix $conda $EnvName
    if ($prefix -and $Recreate) {
        Write-Step "Eliminando el entorno '$EnvName' (-Recreate)"
        Invoke-Native $conda @("env", "remove", "-n", $EnvName, "-y")
        $prefix = $null
    }

    try {
        if ($prefix) {
            Write-Step "Actualizando el entorno '$EnvName' desde environment.yml"
            Invoke-Native $conda @("env", "update", "-n", $EnvName, "-f", "environment.yml", "--prune")
        } else {
            Write-Step "Creando el entorno '$EnvName' (puede tardar entre 5 y 15 minutos)"
            Invoke-Native $conda @("env", "create", "-n", $EnvName, "-f", "environment.yml")
        }
    } catch {
        Write-Warn2 "Fallo la instalacion con conda."
        Write-Warn2 "Si conda pide aceptar los Terms of Service, sigue la instruccion que muestra conda y vuelve a ejecutar."
        Write-Warn2 "Alternativa sin conda: .\setup_env.ps1 -Mode venv"
        throw
    }

    $prefix = Get-EnvPrefix $conda $EnvName
    if (-not $prefix) { throw "El entorno '$EnvName' no aparece en conda despues de crearlo." }
    $envPython = Join-Path $prefix "python.exe"
    if (-not (Test-Path $envPython)) { throw "No se encontro $envPython" }
}
else {
    Write-Step "Buscando Python 3.10 o superior"
    $py = Find-Python
    if (-not $py) {
        throw "No se encontro Python 3.10+. Instalalo con:  winget install Python.Python.3.11   y vuelve a ejecutar."
    }
    $venvDir = Join-Path $PSScriptRoot ".venv"
    if ((Test-Path $venvDir) -and $Recreate) {
        Write-Step "Eliminando .venv (-Recreate)"
        Remove-Item -Recurse -Force $venvDir
    }
    if (-not (Test-Path $venvDir)) {
        Write-Step "Creando el entorno virtual .venv"
        Invoke-Native $py.Exe ($py.PyArgs + @("-m", "venv", $venvDir))
    }
    $envPython = Join-Path $venvDir "Scripts\python.exe"
    Write-Step "Instalando librerias con pip (puede tardar varios minutos)"
    Invoke-Native $envPython @("-m", "pip", "install", "--upgrade", "pip")
    Invoke-Native $envPython @("-m", "pip", "install", "-r", "requirements.txt")
}

if ($WithTelegram) {
    Write-Step "Instalando extras opcionales (Telegram)"
    Invoke-Native $envPython @("-m", "pip", "install", "-r", "requirements-optional.txt")
}

Write-Step "Verificando la instalacion"
$checkArgs = @("check_env.py")
if (-not $SkipNetCheck) { $checkArgs += "--net" }
& $envPython @checkArgs
$checkExit = $LASTEXITCODE

Write-Host ""
if ($checkExit -ne 0) {
    Write-Host "La verificacion encontro errores. Revisa las lineas [FAIL] de arriba." -ForegroundColor Red
    Write-Host "Puedes reintentar desde cero con:  .\setup_env.ps1 -Recreate"
    exit $checkExit
}

Write-Host "Entorno listo." -ForegroundColor Green
Write-Host ""
Write-Host "Interprete de Python de este entorno:"
Write-Host "  $envPython"
Write-Host ""
Write-Host "En VS Code: Ctrl+Shift+P -> 'Python: Select Interpreter' -> elige '$EnvName' (o pega la ruta de arriba)."
if ($Mode -eq "conda") {
    Write-Host "En terminal:  conda activate $EnvName   (si 'conda' no se reconoce, abre 'Anaconda Prompt')"
} else {
    Write-Host "En terminal:  .\.venv\Scripts\Activate.ps1"
}
Write-Host "Sin activar:  & `"$envPython`" check_env.py"
Write-Host "Revisar el DEM:  & `"$envPython`" check_env.py --dem <ruta\al\archivo.tif>"
