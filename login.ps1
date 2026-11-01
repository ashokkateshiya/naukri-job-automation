# One-time interactive login to Naukri
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$py = "C:\Users\Jainil\AppData\Local\Programs\Python\Python312\python.exe"
if (-not (Test-Path $py)) {
    $py = "python"
}

Write-Host "Opening browser for one-time Naukri login using $py..."
& $py "naukri_automator.py" --login
