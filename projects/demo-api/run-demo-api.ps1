$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot
$env:PYTHONPATH = "src"
$logFile = Join-Path $PSScriptRoot "run-logs\launcher.log"

if (-not (Test-Path (Split-Path $logFile))) {
    New-Item -ItemType Directory -Path (Split-Path $logFile) | Out-Null
}

"[$(Get-Date -Format s)] starting demo api launcher" | Add-Content $logFile

& ".\.venv\Scripts\python.exe" -m uvicorn student_behavior_demo_api.main:app --host 127.0.0.1 --port 8000
