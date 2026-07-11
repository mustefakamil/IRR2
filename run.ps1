# =====================================================================
#  Smart Irrigation Scheduling Platform - FAO-56
#  One-command launcher for Windows (PowerShell).
#
#  Usage:   right-click -> Run with PowerShell,  OR  in a terminal:
#             powershell -ExecutionPolicy Bypass -File run.ps1
#
#  First run installs dependencies and builds the UI (a few minutes).
#  Later runs start instantly. Add -Rebuild to force a fresh UI build.
# =====================================================================
param([switch]$Rebuild, [int]$Port = 8000)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

function Section($m) { Write-Host "`n=== $m ===" -ForegroundColor Green }

# --- Prerequisites ----------------------------------------------------
Section "Checking prerequisites"
try { $py = (python --version) 2>&1; Write-Host "Python: $py" } catch { Write-Host "Python 3.10+ is required. Install from python.org" -ForegroundColor Red; exit 1 }
try { $nd = (node --version) 2>&1; Write-Host "Node:   $nd" } catch { Write-Host "Node.js 18+ is required (only for building the UI)." -ForegroundColor Yellow }

# --- Backend dependencies --------------------------------------------
Section "Installing backend dependencies"
python -m pip install --quiet --disable-pip-version-check -r (Join-Path $backend "requirements.txt")

# --- Frontend build ---------------------------------------------------
$dist = Join-Path $frontend "dist"
if ($Rebuild -or -not (Test-Path (Join-Path $dist "index.html"))) {
    Section "Building the web interface"
    Push-Location $frontend
    if (-not (Test-Path (Join-Path $frontend "node_modules"))) { npm install }
    npm run build
    Pop-Location
} else {
    Write-Host "UI already built (use -Rebuild to force). " -ForegroundColor DarkGray
}

# --- Launch -----------------------------------------------------------
Section "Starting the platform"
$url = "http://127.0.0.1:$Port"
Write-Host "Open your browser at:  $url" -ForegroundColor Cyan
Start-Process $url
Push-Location $backend
python -m uvicorn app.main:app --host 127.0.0.1 --port $Port
Pop-Location
