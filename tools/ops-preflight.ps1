param(
  [switch]$Fix,
  [switch]$Deep,
  [string]$AwsRegion = "us-east-1",
  [string]$VercelScope = "marksalman76-5799s-projects",
  [string]$VercelProject = "vantro-ai"
)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$Frontend = Join-Path $Root "frontend"
$NpmGlobalBin = Join-Path $env:APPDATA "npm"
$VercelCmd = Join-Path $NpmGlobalBin "vercel.cmd"
$HadError = $false
$HadWarning = $false

function Write-Section([string]$Text) {
  Write-Host ""
  Write-Host $Text -ForegroundColor Cyan
}

function Write-Ok([string]$Text) {
  Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Warn([string]$Text) {
  $script:HadWarning = $true
  Write-Host "[WARN] $Text" -ForegroundColor Yellow
}

function Write-Fail([string]$Text) {
  $script:HadError = $true
  Write-Host "[FAIL] $Text" -ForegroundColor Red
}

function Ensure-NpmGlobalPath {
  $pathParts = @($env:Path -split ";" | Where-Object { $_ })
  if ($pathParts -contains $NpmGlobalBin) {
    Write-Ok "Current shell PATH includes npm global bin: $NpmGlobalBin"
  } elseif ($Fix) {
    $env:Path = "$env:Path;$NpmGlobalBin"
    Write-Ok "Added npm global bin to this shell PATH"
  } elseif ((@([Environment]::GetEnvironmentVariable("Path", "User") -split ";" | Where-Object { $_ }) -contains $NpmGlobalBin)) {
    Write-Host "[INFO] Current shell started before npm global bin was available; restart VS Code/PowerShell to inherit it." -ForegroundColor Gray
  } else {
    Write-Warn "Current shell PATH does not include npm global bin: $NpmGlobalBin"
    Write-Host "       Run: npm run ops:fix"
  }

  $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
  $userParts = @($userPath -split ";" | Where-Object { $_ })
  if ($userParts -contains $NpmGlobalBin) {
    Write-Ok "User PATH includes npm global bin"
  } elseif ($Fix) {
    $newPath = ($userPath.TrimEnd(";") + ";$NpmGlobalBin").TrimStart(";")
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Ok "Added npm global bin to User PATH; restart VS Code/PowerShell to inherit it"
  } else {
    Write-Warn "User PATH does not include npm global bin"
    Write-Host "       Run: npm run ops:fix"
  }
}

function Test-CommandAvailable([string]$Name, [string]$InstallHint = "") {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($cmd) {
    Write-Ok "$Name found at $($cmd.Source)"
    return $true
  }
  Write-Fail "$Name is not available in this shell"
  if ($InstallHint) {
    Write-Host "       $InstallHint"
  }
  return $false
}

function Invoke-CheckedCommand([string]$Label, [scriptblock]$Command, [switch]$Required) {
  try {
    & $Command
    if ($LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE) {
      Write-Ok $Label
      return
    }
    if ($Required) {
      Write-Fail "$Label failed with exit code $LASTEXITCODE"
    } else {
      Write-Warn "$Label failed with exit code $LASTEXITCODE"
    }
  } catch {
    if ($Required) {
      Write-Fail "$Label failed: $($_.Exception.Message)"
    } else {
      Write-Warn "$Label failed: $($_.Exception.Message)"
    }
  }
  return
}

Write-Host "Vantro DevOps automation preflight" -ForegroundColor Cyan
Write-Host "Root: $Root"
Write-Host "Mode: $(if ($Fix) { 'fix' } else { 'check' })"

Write-Section "Shell PATH"
Ensure-NpmGlobalPath

Write-Section "Git and GitHub"
$gitOk = Test-CommandAvailable "git" "Install Git for Windows."
if ($gitOk) {
  Push-Location $Root
  Invoke-CheckedCommand "Git remote is configured" { git remote get-url origin | Out-Host } -Required
  Invoke-CheckedCommand "Git worktree status readable" { git status --short | Out-Host } -Required
  Pop-Location
}

$gh = Get-Command "gh" -ErrorAction SilentlyContinue
if ($gh) {
  try {
    gh auth status | Out-Host
    if ($LASTEXITCODE -eq 0) {
      Write-Ok "GitHub CLI auth status"
    } else {
      Write-Host "[INFO] GitHub CLI is installed but not logged in; GitHub Actions still runs through the git remote." -ForegroundColor Gray
    }
  } catch {
    Write-Host "[INFO] GitHub CLI auth check skipped: $($_.Exception.Message)" -ForegroundColor Gray
  }
} else {
  Write-Host "[INFO] GitHub CLI is not installed; GitHub deploys still work through git remote and Actions." -ForegroundColor Gray
}

Write-Section "Vercel"
if (Test-Path $VercelCmd) {
  Invoke-CheckedCommand "Vercel CLI version" { & $VercelCmd --version | Out-Host } -Required
  Invoke-CheckedCommand "Vercel CLI authenticated" { & $VercelCmd whoami --scope $VercelScope | Out-Host } -Required

  Invoke-CheckedCommand "Vercel project deployments visible" { & $VercelCmd ls $VercelProject --scope $VercelScope --format json | Out-Null } -Required

  $projectJson = Join-Path $Frontend ".vercel\project.json"
  if (Test-Path $projectJson) {
    $linked = Get-Content -LiteralPath $projectJson -Raw | ConvertFrom-Json
    if ($linked.projectName -eq $VercelProject) {
      Write-Ok "Frontend linked to Vercel project '$VercelProject'"
    } else {
      Write-Warn "Frontend is linked to Vercel project '$($linked.projectName)', expected '$VercelProject'"
      if ($Fix) {
        Push-Location $Frontend
        Invoke-CheckedCommand "Relink frontend to Vercel project '$VercelProject'" { & $VercelCmd link --project $VercelProject --scope $VercelScope --yes | Out-Host } -Required
        Pop-Location
      }
    }
  } elseif (Test-Path (Join-Path $Frontend ".env.local")) {
    Write-Ok "Frontend has local Vercel CLI env state; project access is verified through '$VercelProject'"
  } elseif ($Fix) {
    Push-Location $Frontend
    Invoke-CheckedCommand "Link frontend to Vercel project '$VercelProject'" { & $VercelCmd link --project $VercelProject --scope $VercelScope --yes | Out-Host } -Required
    Pop-Location
  } else {
    Write-Warn "Frontend is not linked locally to Vercel; run: npm run ops:fix"
  }
} else {
  Write-Fail "Vercel CLI shim not found at $VercelCmd"
  Write-Host "       Install with: npm.cmd install -g vercel"
}

Write-Section "AWS"
$awsOk = Test-CommandAvailable "aws" "Install AWS CLI v2."
if ($awsOk) {
  Invoke-CheckedCommand "AWS caller identity" { aws sts get-caller-identity --region $AwsRegion | Out-Host } -Required
  Invoke-CheckedCommand "AWS default/current region" { aws configure get region | Out-Host } | Out-Null
  Invoke-CheckedCommand "Production ECS services visible" {
    aws ecs describe-services `
      --cluster trance-formation-prod `
      --services trance-formation-api-service vantro-worker vantro-agent-worker `
      --region $AwsRegion `
      --query "services[].{name:serviceName,status:status,desired:desiredCount,running:runningCount,taskDef:taskDefinition}" `
      --output table | Out-Host
  } -Required
  if ($Deep) {
    Invoke-CheckedCommand "Fargate vCPU quota visible" {
      aws service-quotas get-service-quota `
        --service-code fargate `
        --quota-code L-3032A538 `
        --region $AwsRegion `
        --query "Quota.{Name:QuotaName,Value:Value,Adjustable:Adjustable}" `
        --output table | Out-Host
    } | Out-Null
  }
}

Write-Section "Docker"
$dockerOk = Test-CommandAvailable "docker" "Install/start Docker Desktop."
if ($dockerOk) {
  Invoke-CheckedCommand "Docker daemon reachable" { docker info --format "{{.ServerVersion}}" | Out-Host } -Required
  if ($Deep) {
    Push-Location $Root
    Invoke-CheckedCommand "API Dockerfile builds" { docker build -f backend/Dockerfile -t vantro-preflight-api:local backend/ | Out-Host } -Required
    Invoke-CheckedCommand "Worker Dockerfile builds" { docker build -f backend/Dockerfile.worker -t vantro-preflight-worker:local backend/ | Out-Host } -Required
    Invoke-CheckedCommand "Agent worker Dockerfile builds" { docker build -f backend/Dockerfile.agent-worker -t vantro-preflight-agent-worker:local backend/ | Out-Host } -Required
    Pop-Location
  }
}

Write-Section "Summary"
if ($HadError) {
  Write-Host "Preflight failed. Fix the [FAIL] items before deploy work." -ForegroundColor Red
  exit 1
}
if ($HadWarning) {
  Write-Host "Preflight passed with warnings." -ForegroundColor Yellow
  exit 0
}
Write-Host "Preflight passed." -ForegroundColor Green
