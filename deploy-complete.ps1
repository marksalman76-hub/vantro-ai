param(
    [string]$Action = "help"
)

$AccountId = "685570573617"
$Region = "us-east-1"
$ClusterName = "trance-formation-prod"
$ServiceName = "trance-formation-api-service"
$DbUrlSecretArn = "arn:aws:secretsmanager:us-east-1:685570573617:secret:vantro/prod/database-url-hVRSA3"

function Register-TaskDef {
    Write-Host "Registering task definition..." -ForegroundColor Cyan
    
    $tmpJson = "$env:TEMP\container-def.json"
    $containerDef = '[{"name":"api","image":"' + $AccountId + '.dkr.ecr.' + $Region + '.amazonaws.com/trance-formation/api:latest","portMappings":[{"containerPort":8000,"hostPort":8000,"protocol":"tcp"}],"secrets":[{"name":"DATABASE_URL","valueFrom":"' + $DbUrlSecretArn + '"}],"environment":[{"name":"ENVIRONMENT","value":"production"},{"name":"PORT","value":"8000"}],"logConfiguration":{"logDriver":"awslogs","options":{"awslogs-group":"/ecs/trance-formation/api","awslogs-region":"' + $Region + '","awslogs-stream-prefix":"ecs"}}}]'
    Set-Content -Path $tmpJson -Encoding ASCII -Value $containerDef
    $jsonPath = "file://" + ($tmpJson -replace '\\', '/')
    aws ecs register-task-definition `
      --family trance-formation-api `
      --network-mode awsvpc `
      --requires-compatibilities FARGATE `
      --cpu 256 `
      --memory 512 `
      --execution-role-arn "arn:aws:iam::${AccountId}:role/ecsTaskExecutionRole" `
      --container-definitions $jsonPath `
      --region $Region
    
    Write-Host "[OK] Task definition registered" -ForegroundColor Green
}

function Get-SubnetAndSG {
    Write-Host "`nFetching your VPC resources..." -ForegroundColor Cyan
    
    $Subnet = aws ec2 describe-subnets --region $Region --query 'Subnets[0].SubnetId' --output text
    $SG = aws ec2 describe-security-groups --filters "Name=group-name,Values=default" --region $Region --query 'SecurityGroups[0].GroupId' --output text
    
    Write-Host "Subnet ID: $Subnet" -ForegroundColor Green
    Write-Host "Security Group: $SG" -ForegroundColor Green
    
    return @($Subnet, $SG)
}

function Create-Service {
    param([string]$SubnetId, [string]$SecurityGroupId)
    
    Write-Host "`nCreating ECS service..." -ForegroundColor Cyan

    $netConfig = 'awsvpcConfiguration={subnets=[' + $SubnetId + '],securityGroups=[' + $SecurityGroupId + '],assignPublicIp=ENABLED}'
    aws ecs create-service `
      --cluster $ClusterName `
      --service-name $ServiceName `
      --task-definition trance-formation-api `
      --desired-count 1 `
      --launch-type FARGATE `
      --network-configuration $netConfig `
      --region $Region
    
    Write-Host "[OK] Service created" -ForegroundColor Green
}

function Deploy-Image {
    Write-Host "`nDeploying Docker image..." -ForegroundColor Cyan

    $ecrRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com"
    $imageUri = "$ecrRepo/trance-formation/api:latest"

    # Create ECR repository if it doesn't exist
    Write-Host "Ensuring ECR repository exists..." -ForegroundColor Cyan
    aws ecr describe-repositories --repository-names trance-formation/api --region $Region 2>$null
    if ($LASTEXITCODE -ne 0) {
        aws ecr create-repository --repository-name trance-formation/api --region $Region
        Write-Host "[OK] ECR repository created" -ForegroundColor Green
    }

    docker build -t trance-formation/api:latest -f backend/Dockerfile backend/

    # Capture password and pass directly — avoids PowerShell pipe stdin issues
    $ecrPassword = aws ecr get-login-password --region $Region
    docker login --username AWS --password $ecrPassword $ecrRepo

    docker tag trance-formation/api:latest $imageUri
    docker push $imageUri
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Image push failed — skipping ECS deployment" -ForegroundColor Red
        return
    }

    aws ecs update-service --cluster $ClusterName --service $ServiceName --force-new-deployment --region $Region

    Write-Host "[OK] Deployment complete" -ForegroundColor Green
}

function Update-DbUrl {
    Write-Host "`nFetching RDS endpoint..." -ForegroundColor Cyan
    $rdsHost = aws rds describe-db-instances --db-instance-identifier vantro-prod-db --region $Region --query 'DBInstances[0].Endpoint.Address' --output text
    if (-not $rdsHost -or $rdsHost -eq "None") {
        Write-Host "[ERROR] RDS instance is not ready yet. Check status:" -ForegroundColor Red
        Write-Host "  aws rds describe-db-instances --db-instance-identifier vantro-prod-db --region $Region --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address]' --output text"
        return
    }
    Write-Host "RDS endpoint: $rdsHost" -ForegroundColor Green
    $dbUrl = "postgresql://postgres:VantroProd2024!RandomPass123@" + $rdsHost + ":5432/multi_industrial_dev"
    aws secretsmanager update-secret --secret-id $DbUrlSecretArn --secret-string $dbUrl --region $Region | Out-Null
    Write-Host "[OK] Secret updated with live RDS host" -ForegroundColor Green
    aws ecs update-service --cluster $ClusterName --service $ServiceName --task-definition trance-formation-api:3 --force-new-deployment --region $Region | Out-Null
    Write-Host "[OK] ECS redeployed with revision 3 (DATABASE_URL from Secrets Manager)" -ForegroundColor Green
}

switch($Action) {
    "task-def"      { Register-TaskDef }
    "get-resources" { Get-SubnetAndSG }
    "create-service" {
        $resources = Get-SubnetAndSG
        Create-Service $resources[0] $resources[1]
    }
    "deploy"        { Deploy-Image }
    "update-db-url" { Update-DbUrl }
    "all" {
        Register-TaskDef
        $resources = Get-SubnetAndSG
        Create-Service $resources[0] $resources[1]
        Deploy-Image
    }
    default {
        Write-Host "Usage:"
        Write-Host "  .\deploy-complete.ps1 task-def         # Register task definition"
        Write-Host "  .\deploy-complete.ps1 get-resources    # Get subnet and security group IDs"
        Write-Host "  .\deploy-complete.ps1 create-service   # Create ECS service"
        Write-Host "  .\deploy-complete.ps1 deploy           # Build and deploy Docker image"
        Write-Host "  .\deploy-complete.ps1 update-db-url   # Wire RDS endpoint into secret and redeploy"
        Write-Host "  .\deploy-complete.ps1 all              # Do everything above"
    }
}