#Requires -Version 5.1
<#
.SYNOPSIS
    Activate virtual environment and start Lapo - AI Code Review Assistant.

.PARAMETER Env
    Name of the virtual environment folder. Defaults to auto-detection.

.PARAMETER Host
    Server host. Defaults to value in .env or 0.0.0.0.

.PARAMETER Port
    Server port. Defaults to value in .env or 8000.

.PARAMETER NoReload
    Disable auto-reload (use in production).

.EXAMPLE
    .\start.ps1
    .\start.ps1 -Port 9000
    .\start.ps1 -Env venv -NoReload
#>
param(
    [string]$Env    = "",
    [string]$Host   = "",
    [int]   $Port   = 0,
    [switch]$NoReload
)

$Root = $PSScriptRoot

# ── Locate virtual environment ────────────────────────────────────────────────
$candidates = @("env311", "venv", ".venv", "env")
if ($Env) { $candidates = @($Env) + $candidates }

$venvActivate = $null
foreach ($name in $candidates) {
    $path = Join-Path $Root "$name\Scripts\Activate.ps1"
    if (Test-Path $path) {
        $venvActivate = $path
        Write-Host "Virtual environment : $name" -ForegroundColor Cyan
        break
    }
}

if (-not $venvActivate) {
    Write-Warning "No virtual environment found. Searched: $($candidates -join ', ')"
    Write-Warning "Create one with:  python -m venv env311"
    Write-Warning "Then install:     .\env311\Scripts\pip install -r requirements.txt"
    exit 1
}

# Activate
& $venvActivate

# ── Load .env for defaults ────────────────────────────────────────────────────
$envFile = Join-Path $Root ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+?)\s*=\s*(.*)$') {
            $key = $Matches[1].Trim()
            $val = $Matches[2].Trim().Trim('"').Trim("'")
            if (-not [System.Environment]::GetEnvironmentVariable($key)) {
                [System.Environment]::SetEnvironmentVariable($key, $val, "Process")
            }
        }
    }
}

# ── Resolve host / port (param > .env > default) ─────────────────────────────
if (-not $Host)  { $Host = $env:APP_HOST; if (-not $Host)  { $Host = "0.0.0.0" } }
if ($Port -eq 0) { $p    = $env:APP_PORT; if ($p)          { $Port = [int]$p }
                   if ($Port -eq 0)                         { $Port = 8000 } }

# ── Build uvicorn command ──────────────────────────────────────────────────────
$uvicornArgs = @(
    "app.main:app",
    "--host", $Host,
    "--port", $Port.ToString()
)
if (-not $NoReload) { $uvicornArgs += "--reload" }

Write-Host ""
Write-Host "Starting Lapo - AI Code Review Assistant" -ForegroundColor Green
Write-Host "  URL  : http://$($Host -replace '0\.0\.0\.0','localhost'):$Port" -ForegroundColor Green
Write-Host "  Docs : http://$($Host -replace '0\.0\.0\.0','localhost'):$Port/docs" -ForegroundColor Green
Write-Host "  Env  : $($env:APP_ENV ?? 'development')" -ForegroundColor Green
Write-Host ""

uvicorn @uvicornArgs
