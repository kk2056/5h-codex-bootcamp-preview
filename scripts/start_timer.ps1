$ErrorActionPreference = "Stop"
$ProductRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProductRoot
$ServerPath = Join-Path $ProductRoot "timer\server.py"

$Launcher = Get-Command py -ErrorAction SilentlyContinue
if ($Launcher) {
    & py -3 $ServerPath
    exit $LASTEXITCODE
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    & python $ServerPath
    exit $LASTEXITCODE
}

Write-Error "Python 3.9 or newer is required. Install Python before starting the timer."
exit 1
