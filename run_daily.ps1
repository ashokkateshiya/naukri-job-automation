# Run the daily Naukri automation routine
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$py = "C:\Users\Jainil\AppData\Local\Programs\Python\Python312\python.exe"
if (-not (Test-Path $py)) {
    $py = "python"
}

Write-Host "Executing Daily Naukri Automation using $py..."
& $py "naukri_automator.py" --daily
Write-Host "Completed. Check last_run.log for details."
