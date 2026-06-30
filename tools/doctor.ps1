$ErrorActionPreference = "Continue"

$Root = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$VenvConfig = Join-Path $Root ".venv\pyvenv.cfg"
$VercelCmd = Join-Path $env:APPDATA "npm\vercel.cmd"
$HadError = $false

Write-Host "Vantro local tool check" -ForegroundColor Cyan
Write-Host "Root: $Root"

Write-Host "`nPython" -ForegroundColor Cyan
if (Test-Path $VenvPython) {
  & $VenvPython -c "import sys; print(sys.executable); print(sys.version)"
  if ($LASTEXITCODE -ne 0) {
    $HadError = $true
    Write-Host "The .venv launcher exists but its base Python is stale." -ForegroundColor Red
    if (Test-Path $VenvConfig) {
      Write-Host "Current .venv config:" -ForegroundColor Yellow
      Get-Content -LiteralPath $VenvConfig
    }
    Write-Host "Recreate it with:" -ForegroundColor Yellow
    Write-Host "  Remove-Item -Recurse -Force .venv" -ForegroundColor Yellow
    Write-Host "  py -3.11 -m venv .venv" -ForegroundColor Yellow
    Write-Host "  .\.venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Yellow
  }
} else {
  $HadError = $true
  Write-Host "Missing .venv Python: $VenvPython" -ForegroundColor Red
  Write-Host "Create it with: py -3.11 -m venv .venv" -ForegroundColor Yellow
}

Write-Host "`nVercel" -ForegroundColor Cyan
if (Test-Path $VercelCmd) {
  & $VercelCmd --version
} else {
  Write-Host "Vercel CLI not found at: $VercelCmd" -ForegroundColor Yellow
  Write-Host "Install with: npm.cmd install -g vercel" -ForegroundColor Yellow
}

Write-Host "`nAWS" -ForegroundColor Cyan
aws --version
aws configure get region

Write-Host "`nDocker" -ForegroundColor Cyan
docker --version

if ($HadError) {
  exit 1
}
