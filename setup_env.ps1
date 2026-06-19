# ============================================================
# Agentic Traffic Management — Environment Setup Script
# Run this once to set up the project on Windows.
# Usage: Right-click > Run with PowerShell, or:
#   powershell -ExecutionPolicy Bypass -File setup_env.ps1
# ============================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Agentic Traffic Management - Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# --- Step 1: Check Python ---
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# --- Step 2: Create virtual environment ---
Write-Host "[2/5] Creating virtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $ProjectRoot "venv"
if (Test-Path $venvPath) {
    Write-Host "  Virtual environment already exists at $venvPath" -ForegroundColor Green
} else {
    python -m venv $venvPath
    Write-Host "  Created virtual environment at $venvPath" -ForegroundColor Green
}

# --- Step 3: Activate and install dependencies ---
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

pip install --upgrade pip
pip install -r (Join-Path $ProjectRoot "requirements.txt")
Write-Host "  Dependencies installed." -ForegroundColor Green

# --- Step 4: Check SUMO ---
Write-Host "[4/5] Checking SUMO installation..." -ForegroundColor Yellow
$sumoHome = $env:SUMO_HOME
if ($sumoHome -and (Test-Path $sumoHome)) {
    Write-Host "  SUMO_HOME is set: $sumoHome" -ForegroundColor Green
    $sumoBin = Join-Path $sumoHome "bin\sumo.exe"
    if (Test-Path $sumoBin) {
        $sumoVersion = & $sumoBin --version 2>&1 | Select-Object -First 1
        Write-Host "  SUMO version: $sumoVersion" -ForegroundColor Green
    }
} else {
    Write-Host "  WARNING: SUMO_HOME is not set or SUMO is not installed." -ForegroundColor Red
    Write-Host "  Please install SUMO from: https://sumo.dlr.de/docs/Downloads.php" -ForegroundColor Red
    Write-Host "  Then set SUMO_HOME environment variable to the install directory." -ForegroundColor Red
    Write-Host "  Example: setx SUMO_HOME 'C:\Program Files\Eclipse\Sumo'" -ForegroundColor Yellow
}

# --- Step 5: Verify Python packages ---
Write-Host "[5/5] Verifying key packages..." -ForegroundColor Yellow
python -c "
import pandas; print(f'  pandas {pandas.__version__}')
import numpy; print(f'  numpy {numpy.__version__}')
import xgboost; print(f'  xgboost {xgboost.__version__}')
import streamlit; print(f'  streamlit {streamlit.__version__}')
try:
    import traci; print('  traci OK')
    import sumolib; print('  sumolib OK')
except ImportError as e:
    print(f'  SUMO Python libs: {e} (install SUMO first)')
print('All checks complete!')
"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "  To activate the environment:" -ForegroundColor Cyan
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  To run the pipeline:" -ForegroundColor Cyan
Write-Host "    python run_pipeline.py" -ForegroundColor White
Write-Host "  To launch the dashboard:" -ForegroundColor Cyan
Write-Host "    streamlit run app.py" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
