param(
    [string]$Region = "us-east-1",
    [string]$ClusterName = "trance-formation-prod"
)

$PROJECT_NAME = "trance-formation"
$APP_NAME = "api"
$AWS_REGION = $Region
$CLUSTER_NAME = $ClusterName

$ChecksPassed = 0
$ChecksFailed = 0
$ChecksWarning = 0

function Write-Header { param([string]$Message)
    Write-Host "`n$('='*60)" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host $('='*60) -ForegroundColor Blue
}

function Write-Success { param([string]$Message)
    Write-Host "✓ PASS: $Message" -ForegroundColor Green
    $script:ChecksPassed++
}

function Write-Failure { param([string]$Message)
    Write-Host "✗ FAIL: $Message" -ForegroundColor Red
    $script:ChecksFailed++
}

function Write-Warning { param([string]$Message)
    Write-Host "⚠ WARN: $Message" -ForegroundColor Yellow
    $script:ChecksWarning++
}

function Write-Info { param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

Write-Header "1. AWS CREDENTIALS & BASIC SETUP"

try {
    $Identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    $AccountId = $Identity.Account
    Write-Success "AWS credentials configured (Account: $AccountId)"
} catch {
    Write-Failure "AWS credentials not configured or invalid"
    exit 1
}

Write-Header "2. CHECKING DOCKER"

try {
    docker --version | Out-Null
    Write-Success "Docker is installed"
} catch {
    Write-Failure "Docker is not installed"
}

Write-Header "3. CHECKING DOCKERFILE"

if (Test-Path "Dockerfile") {
    Write-Success "Dockerfile exists"
} else {
    Write-Warning "Dockerfile not found"
}

Write-Header "SUMMARY"
Write-Host "`nResults:" -ForegroundColor Cyan
Write-Host "  Passed:  $ChecksPassed" -ForegroundColor Green
Write-Host "  Warnings: $ChecksWarning" -ForegroundColor Yellow
Write-Host "  Failed:  $ChecksFailed" -ForegroundColor Red

if ($ChecksFailed -eq 0) {
    Write-Host "`n✓ Prerequisites check passed!" -ForegroundColor Green
}
