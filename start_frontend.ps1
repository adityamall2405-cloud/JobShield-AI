Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Checked {
  param(
    [string]$CommandPath,
    [string[]]$Arguments
  )
  & $CommandPath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed: $CommandPath $($Arguments -join ' ')"
  }
}

$npmCommand = Get-Command npm -ErrorAction SilentlyContinue
$npmCmd = $null
if ($npmCommand) {
  $npmCmd = $npmCommand.Source
}
if (-not $npmCmd) {
  $defaultNpmPath = Join-Path ${env:ProgramFiles} "nodejs\npm.cmd"
  if (Test-Path $defaultNpmPath) {
    $npmCmd = $defaultNpmPath
  }
}

if (-not $npmCmd) {
  throw "npm is not installed in PATH. Re-open terminal or install Node.js from https://nodejs.org and re-run this script."
}

$nodeDir = Split-Path -Parent $npmCmd
if ($nodeDir -and -not ($env:Path -like "*$nodeDir*")) {
  $env:Path = "$nodeDir;$env:Path"
}

Set-Location "$PSScriptRoot\frontend"
Write-Host "Installing frontend dependencies..."
Invoke-Checked -CommandPath $npmCmd -Arguments @("install")

$backendPortFile = "$PSScriptRoot\.jobshield_backend_port"
if (Test-Path $backendPortFile) {
  $backendPort = (Get-Content $backendPortFile -Raw).Trim()
  if ($backendPort) {
    $env:VITE_API_BASE_URL = "http://127.0.0.1:$backendPort"
    Write-Host "Using backend API at $env:VITE_API_BASE_URL"
  }
}

Write-Host "Starting JobShield UI on http://127.0.0.1:5173"
Invoke-Checked -CommandPath $npmCmd -Arguments @("run", "dev")
