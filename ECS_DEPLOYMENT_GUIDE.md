# ECS Deployment Guide

## Prerequisites
- AWS Account with appropriate IAM permissions
- AWS CLI configured
- Docker installed and running
- ECR repository created: `trance-formation-backend`

## Environment Setup

### 1. Create AWS Secrets Manager entries

```bash
# Database URL
aws secretsmanager create-secret \
  --name trance-formation/database-url \
  --secret-string '{"DATABASE_URL":"postgresql://user:password@host:5432/multi_industrial_dev"}' \
  --region us-east-1

# Stripe credentials
aws secretsmanager create-secret \
  --name trance-formation/stripe-secret-key \
  --secret-string '{"STRIPE_SECRET_KEY":"sk_live_..."}' \
  --region us-east-1

aws secretsmanager create-secret \
  --name trance-formation/stripe-webhook-secret \
  --secret-string '{"STRIPE_WEBHOOK_SECRET":"whsec_..."}' \
  --region us-east-1
```

### 2. Build & Push Docker image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t trance-formation-backend:latest backend/

# Tag image
docker tag trance-formation-backend:latest \
  ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/trance-formation-backend:latest

# Push to ECR
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/trance-formation-backend:latest
```

### 3. Update task definition

Replace placeholders in `ecs-task-definition.json`:
- `ACCOUNT_ID` - Your AWS Account ID
- `REGION` - AWS region (e.g., us-east-1)

### 4. Register task definition

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json \
  --region us-east-1
```

### 5. Create ECS cluster (if not exists)

```bash
aws ecs create-cluster --cluster-name trance-formation-prod
```

### 6. Create ECS service

```bash
aws ecs create-service \
  --cluster trance-formation-prod \
  --service-name trance-formation-backend \
  --task-definition trance-formation-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration \
    "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers \
    "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:ACCOUNT_ID:targetgroup/trance-backend/xxx,containerName=trance-formation-backend,containerPort=8000" \
  --region us-east-1
```

## Local Testing

```bash
# Build locally
docker build -t trance-formation-backend:latest backend/

# Run locally
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://postgres:password@host:5432/multi_industrial_dev" \
  -e STRIPE_SECRET_KEY="sk_test_..." \
  -e STRIPE_WEBHOOK_SECRET="whsec_test_..." \
  trance-formation-backend:latest
```

## Monitoring

- CloudWatch Logs: `/ecs/trance-formation-backend`
- ECS Cluster: `trance-formation-prod`
- Service: `trance-formation-backend`

## Update process

```bash
# Push new image
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/trance-formation-backend:latest

# Update service (forces new task)
aws ecs update-service \
  --cluster trance-formation-prod \
  --service trance-formation-backend \
  --force-new-deployment \
  --region us-east-1
```

## Troubleshooting

- Check ECS task logs in CloudWatch
- Verify security groups allow inbound traffic on port 8000
- Ensure RDS is accessible from ECS tasks
- Check Secrets Manager permissions in IAM role