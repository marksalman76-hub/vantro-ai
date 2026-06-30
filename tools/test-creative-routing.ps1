$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (!(Test-Path $Python)) {
  throw "Missing .venv Python at $Python. Run: py -3.11 -m venv .venv"
}

& $Python -m pytest `
  "$Root\backend\tests\test_creative_provider_routing.py" `
  "$Root\backend\tests\test_admin_run_agent.py" `
  -q
