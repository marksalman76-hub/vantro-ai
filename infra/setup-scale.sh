#!/usr/bin/env bash
# =============================================================================
# Vantro Scale Infrastructure Setup
# Run once to provision SQS, ElastiCache Redis, and the worker ECS service.
# All resources are tagged and named consistently for easy cost tracking.
# =============================================================================
set -euo pipefail

REGION="us-east-1"
ACCOUNT="685570573617"
CLUSTER="trance-formation-prod"
ECR_REPO="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/trance-formation"
VPC_ID="${VPC_ID:-}"                          # set in environment or pass as arg
PRIVATE_SUBNET_IDS="${PRIVATE_SUBNET_IDS:-}"  # comma-separated private subnet IDs
SECURITY_GROUP_ID="${SECURITY_GROUP_ID:-}"    # ECS tasks security group

echo "==> [1/8] Creating SQS FIFO queue for video jobs..."
QUEUE_URL=$(aws sqs create-queue \
  --queue-name "vantro-video-jobs.fifo" \
  --attributes '{
    "FifoQueue": "true",
    "ContentBasedDeduplication": "false",
    "VisibilityTimeout": "900",
    "MessageRetentionPeriod": "86400",
    "ReceiveMessageWaitTimeSeconds": "20",
    "RedrivePolicy": "{\"deadLetterTargetArn\":\"__DLQ_ARN__\",\"maxReceiveCount\":\"3\"}"
  }' \
  --tags Project=vantro,Env=prod \
  --region "${REGION}" \
  --query QueueUrl --output text 2>/dev/null || \
  aws sqs get-queue-url --queue-name "vantro-video-jobs.fifo" \
    --region "${REGION}" --query QueueUrl --output text)

echo "    Queue URL: ${QUEUE_URL}"

echo "==> [2/8] Creating dead-letter queue for failed jobs..."
DLQ_URL=$(aws sqs create-queue \
  --queue-name "vantro-video-jobs-dlq.fifo" \
  --attributes '{"FifoQueue":"true","MessageRetentionPeriod":"604800"}' \
  --tags Project=vantro,Env=prod \
  --region "${REGION}" \
  --query QueueUrl --output text 2>/dev/null || \
  aws sqs get-queue-url --queue-name "vantro-video-jobs-dlq.fifo" \
    --region "${REGION}" --query QueueUrl --output text)

DLQ_ARN=$(aws sqs get-queue-attributes \
  --queue-url "${DLQ_URL}" \
  --attribute-names QueueArn \
  --region "${REGION}" \
  --query Attributes.QueueArn --output text)

# Patch the main queue with the real DLQ ARN
aws sqs set-queue-attributes \
  --queue-url "${QUEUE_URL}" \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"${DLQ_ARN}\\\",\\\"maxReceiveCount\\\":\\\"3\\\"}\"}" \
  --region "${REGION}"

echo "    DLQ ARN: ${DLQ_ARN}"

echo "==> [3/8] Creating ElastiCache Redis cluster (cache.t3.micro)..."
# This creates a serverless/single-node Redis cluster.
# Upgrade to cache.r7g.large + Multi-AZ for production at scale.
REDIS_CLUSTER_ID="vantro-redis"

aws elasticache create-cache-cluster \
  --cache-cluster-id "${REDIS_CLUSTER_ID}" \
  --cache-node-type "cache.t3.micro" \
  --engine "redis" \
  --engine-version "7.1" \
  --num-cache-nodes 1 \
  --cache-parameter-group-name "default.redis7" \
  --tags "Key=Project,Value=vantro" "Key=Env,Value=prod" \
  --region "${REGION}" 2>/dev/null \
  && echo "    Redis cluster creation initiated (takes ~5 minutes)..." \
  || echo "    Redis cluster already exists — skipping"

echo "==> [4/8] Waiting for Redis endpoint..."
for i in $(seq 1 30); do
  REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
    --cache-cluster-id "${REDIS_CLUSTER_ID}" \
    --show-cache-node-info \
    --region "${REGION}" \
    --query "CacheClusters[0].CacheNodes[0].Endpoint.Address" \
    --output text 2>/dev/null || echo "None")
  if [ "${REDIS_ENDPOINT}" != "None" ] && [ -n "${REDIS_ENDPOINT}" ]; then
    REDIS_URL="redis://${REDIS_ENDPOINT}:6379"
    echo "    Redis URL: ${REDIS_URL}"
    break
  fi
  echo "    Waiting... (${i}/30)"
  sleep 10
done

echo "==> [5/8] Storing secrets in AWS Secrets Manager..."
_put_secret() {
  local name="$1" value="$2"
  aws secretsmanager create-secret --name "${name}" --secret-string "${value}" \
    --region "${REGION}" 2>/dev/null || \
  aws secretsmanager put-secret-value --secret-id "${name}" --secret-string "${value}" \
    --region "${REGION}"
  echo "    Stored: ${name}"
}

_put_secret "REDIS_URL"          "${REDIS_URL}"
_put_secret "SQS_JOBS_QUEUE_URL" "${QUEUE_URL}"

echo "    *** Remember to also store HEYGEN_API_KEY if not already present ***"
echo "    aws secretsmanager put-secret-value --secret-id HEYGEN_API_KEY --secret-string 'YOUR_KEY'"

echo "==> [6/8] Building and pushing worker Docker image..."
aws ecr get-login-password --region "${REGION}" | \
  docker login --username AWS --password-stdin "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"

cd "$(dirname "$0")/../backend"
docker build -f Dockerfile.worker -t vantro-worker .
docker tag vantro-worker:latest "${ECR_REPO}/worker:latest"
docker push "${ECR_REPO}/worker:latest"
cd -

echo "==> [7/8] Registering worker task definition..."
WORKER_TASK_DEF_ARN=$(aws ecs register-task-definition \
  --cli-input-json file://"$(dirname "$0")/../task-def-worker.json" \
  --region "${REGION}" \
  --query taskDefinition.taskDefinitionArn --output text)
echo "    Worker task def: ${WORKER_TASK_DEF_ARN}"

echo "==> [8/8] Creating worker ECS service..."
# Worker service: starts at 2 tasks, scales out based on SQS queue depth.
# No load balancer — workers pull from SQS directly.
aws ecs create-service \
  --cluster "${CLUSTER}" \
  --service-name "vantro-worker" \
  --task-definition "${WORKER_TASK_DEF_ARN}" \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${PRIVATE_SUBNET_IDS}],securityGroups=[${SECURITY_GROUP_ID}],assignPublicIp=DISABLED}" \
  --scheduling-strategy REPLICA \
  --deployment-configuration "minimumHealthyPercent=50,maximumPercent=200" \
  --tags "key=Project,value=vantro" "key=Env,value=prod" \
  --region "${REGION}" 2>/dev/null \
  || echo "    Worker service already exists — updating desired count"

echo ""
echo "==> Configuring autoscaling for web API tier..."
# Web tier: target 20 tasks max, scale on CPU > 70%
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id "service/${CLUSTER}/trance-formation-api-service" \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 20 \
  --region "${REGION}" 2>/dev/null || true

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id "service/${CLUSTER}/trance-formation-api-service" \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name "vantro-api-cpu-tracking" \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {"PredefinedMetricType": "ECSServiceAverageCPUUtilization"},
    "ScaleInCooldown": 120,
    "ScaleOutCooldown": 30
  }' \
  --region "${REGION}" 2>/dev/null || true

echo ""
echo "==> Configuring autoscaling for worker tier (SQS queue depth)..."
# Worker tier: scale based on number of messages in the SQS queue.
# Target: ~5 messages per worker task.
QUEUE_ARN=$(aws sqs get-queue-attributes \
  --queue-url "${QUEUE_URL}" \
  --attribute-names QueueArn \
  --region "${REGION}" \
  --query Attributes.QueueArn --output text)

aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id "service/${CLUSTER}/vantro-worker" \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 10 \
  --region "${REGION}" 2>/dev/null || true

# SQS-based step scaling: add 2 tasks per 10 queued messages
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id "service/${CLUSTER}/vantro-worker" \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name "vantro-worker-sqs-scaling" \
  --policy-type StepScaling \
  --step-scaling-policy-configuration '{
    "AdjustmentType": "ChangeInCapacity",
    "Cooldown": 60,
    "StepAdjustments": [
      {"MetricIntervalLowerBound": 0,  "MetricIntervalUpperBound": 10, "ScalingAdjustment": 1},
      {"MetricIntervalLowerBound": 10, "MetricIntervalUpperBound": 50, "ScalingAdjustment": 2},
      {"MetricIntervalLowerBound": 50,                                 "ScalingAdjustment": 5}
    ]
  }' \
  --region "${REGION}" 2>/dev/null || true

echo ""
echo "==> Creating CloudWatch alarm to trigger worker scale-out..."
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-worker-queue-depth" \
  --alarm-description "Scale out workers when SQS queue depth rises" \
  --metric-name "ApproximateNumberOfMessagesVisible" \
  --namespace "AWS/SQS" \
  --dimensions "Name=QueueName,Value=vantro-video-jobs.fifo" \
  --statistic Sum \
  --period 60 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --alarm-actions "$(aws application-autoscaling describe-scaling-policies \
    --service-namespace ecs \
    --resource-id "service/${CLUSTER}/vantro-worker" \
    --query "ScalingPolicies[?PolicyName=='vantro-worker-sqs-scaling'].PolicyARN" \
    --output text --region "${REGION}" 2>/dev/null || echo 'REPLACE_WITH_POLICY_ARN')" \
  --region "${REGION}" 2>/dev/null || true

echo ""
echo "============================================================"
echo " Vantro scale infrastructure setup complete"
echo "============================================================"
echo ""
echo " SQS queue:   ${QUEUE_URL}"
echo " SQS DLQ:     ${DLQ_URL}"
echo " Redis:       ${REDIS_URL:-'(check ElastiCache console)'}"
echo ""
echo " Next steps:"
echo "  1. Re-deploy the web API with the updated task-def.json:"
echo "     aws ecs register-task-definition --cli-input-json file://task-def.json"
echo "     aws ecs update-service --cluster ${CLUSTER} --service trance-formation-api-service --task-definition vantro-api"
echo ""
echo "  2. Run the DB migration:"
echo "     alembic upgrade head"
echo ""
echo "  3. Verify ElastiCache security group allows inbound 6379 from ECS tasks SG"
echo "  4. Store HEYGEN_API_KEY + avatar/voice mapping env vars in Secrets Manager"
echo "  5. Verify SES sender noreply@vantro.ai is verified in us-east-1"
echo "============================================================"
