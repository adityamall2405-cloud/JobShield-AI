Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-FreePort {
  param(
    [int]$StartPort = 8000,
    [int]$MaxAttempts = 200
  )

  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $port = $StartPort + $i
    try {
      $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), $port)
      $listener.Start()
      $listener.Stop()
      return $port
    } catch {
      continue
    }
  }

  throw "Could not find a free port starting from $StartPort."
}

Set-Location "$PSScriptRoot\backend"

if (-not (Test-Path ".venv")) {
  Write-Host "Creating Python virtual environment..."
  python -m venv .venv
}

Write-Host "Installing backend dependencies..."
.\.venv\Scripts\python -m pip install -r requirements.txt

if (-not (Test-Path ".\models\jobshield_model.joblib")) {
  Write-Host "Training model (first-time setup)..."
  .\.venv\Scripts\python .\train_model.py --data ..\fake_job_postings.csv --output .\models\jobshield_model.joblib
}

Set-Location "$PSScriptRoot"
$port = Get-FreePort -StartPort 8000
Set-Content -Path "$PSScriptRoot\.jobshield_backend_port" -Value "$port"
Write-Host "Starting JobShield API on http://127.0.0.1:$port"
.\backend\.venv\Scripts\python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port $port
