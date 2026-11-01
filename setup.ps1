# Setup script for Naukri Automator
$ErrorActionPreference = "Stop"
Write-Host "Checking Python..."

try {
    $pythonVersion = python --version
    Write-Host "Found: $pythonVersion"
} catch {
    Write-Host "Python is not installed. Installing Python via winget..."
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
    Write-Host "Python installed. Please reopen PowerShell or verify python command."
}

Write-Host "Installing Playwright..."
python -m pip install --upgrade pip
python -m pip install playwright
python -m playwright install chromium

Write-Host "Setup complete!"
