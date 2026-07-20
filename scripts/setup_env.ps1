$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectDir = Split-Path -Parent $scriptDir
$backendDir = Join-Path $projectDir "backend"

Write-Host "Setting up Python virtual environment in $backendDir..."
cd $backendDir

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "Virtual environment created."
} else {
    Write-Host "Virtual environment already exists."
}

Write-Host "Activating virtual environment and installing requirements..."
& .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Backend environment setup complete!"
