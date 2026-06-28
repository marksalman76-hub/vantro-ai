# Vantro.ai Operational Launch Checklist

**Owner:** Mark Salman (mark.salman76@gmail.com)
**Stack:** FastAPI/ECS Fargate + RDS PostgreSQL + SQS + S3 + Secrets Manager + CloudWatch
**Region:** us-east-1
**Custom metric namespace:** `Vantro/AgentJobs`

---

## 1. ECS / Fargate

- [ ] ECS cluster exists:
  ```bash
  aws ecs describe-clusters --clusters vantro-production --query 'clusters[0].status'
  # Expected: "ACTIVE"
  ```
- [ ] Backend service running with at least 1 task:
  ```bash
  aws ecs describe-services --cluster vantro-production --services vantro-backend \
    --query 'services[0].{running:runningCount,desired:desiredCount,status:status}'
  # Expected: running >= 1, status = "ACTIVE"
  ```
- [ ] Task definition includes all required env vars:
  - `ENVIRONMENT=production`
  - `SQS_QUEUE_URL` (points to `vantro-agent-jobs`)
  - `DATABASE_REPLICA_URL` (if read replica exists)
  - All sensitive vars wired as Secrets Manager ARN references (not plaintext)
  ```bash
  aws ecs describe-task-definition --task-definition vantro-backend \
    --query 'taskDefinition.containerDefinitions[0].{env:environment,secrets:secrets}'
  ```
- [ ] Health check on task definition: path `/health`, interval 30s, timeout 5s, retries 3, startPeriod 60s
  ```bash
  aws ecs describe-task-definition --task-definition vantro-backend \
    --query 'taskDefinition.containerDefinitions[0].healthCheck'
  ```
- [ ] ECS service auto-scaling policy configured:
  - Target tracking: CPUUtilization target 60%
  - Min capacity: 1 task
  - Max capacity: 4 tasks
  ```bash
  aws application-autoscaling describe-scaling-policies \
    --service-namespace ecs \
    --resource-id service/vantro-production/vantro-backend
  ```
- [ ] Container logs routed to CloudWatch log group `/ecs/vantro-backend`:
  ```bash
  aws ecs describe-task-definition --task-definition vantro-backend \
    --query 'taskDefinition.containerDefinitions[0].logConfiguration'
  # Expected: logDriver=awslogs, options[awslogs-group]=/ecs/vantro-backend
  ```
- [ ] Task execution role has `secretsmanager:GetSecretValue` on `arn:aws:secretsmanager:us-east-1:*:secret:vantro/production/*`:
  ```bash
  aws iam get-role-policy --role-name vantro-ecs-execution-role \
    --policy-name SecretsManagerAccess
  # Or check attached managed policies:
  aws iam list-attached-role-policies --role-name vantro-ecs-execution-role
  ```
- [ ] Task role has `cloudwatch:PutMetricData` permission (required by `agent_worker.py _emit_metric`):
  ```bash
  aws iam simulate-principal-policy \
    --policy-source-arn <TASK_ROLE_ARN> \
    --action-names cloudwatch:PutMetricData \
    --resource-arns "*" \
    --query 'EvaluationResults[0].EvalDecision'
  # Expected: "allowed"
  ```
- [ ] Task role has `sqs:SendMessage`, `sqs:ReceiveMessage`, `sqs:DeleteMessage` on the agent jobs queue:
  ```bash
  aws iam simulate-principal-policy \
    --policy-source-arn <TASK_ROLE_ARN> \
    --action-names sqs:SendMessage sqs:ReceiveMessage sqs:DeleteMessage \
    --resource-arns arn:aws:sqs:us-east-1:<ACCOUNT_ID>:vantro-agent-jobs \
    --query 'EvaluationResults[*].{action:EvalActionName,decision:EvalDecision}'
  ```
- [ ] ECS service deployment circuit breaker enabled with auto-rollback:
  ```bash
  aws ecs describe-services --cluster vantro-production --services vantro-backend \
    --query 'services[0].deploymentConfiguration.deploymentCircuitBreaker'
  # Expected: {enable: true, rollback: true}
  ```

---

## 2. RDS PostgreSQL

- [ ] RDS instance class is `db.t3.medium` minimum (not `db.t3.small`) for production:
  ```bash
  aws rds describe-db-instances --db-instance-identifier vantro-production-db \
    --query 'DBInstances[0].DBInstanceClass'
  # Expected: "db.t3.medium" or larger
  ```
- [ ] Multi-AZ enabled:
  ```bash
  aws rds describe-db-instances --db-instance-identifier vantro-production-db \
    --query 'DBInstances[0].MultiAZ'
  # Expected: true
  ```
- [ ] Automated backups enabled with 7-day retention:
  ```bash
  aws rds describe-db-instances --db-instance-identifier vantro-production-db \
    --query 'DBInstances[0].BackupRetentionPeriod'
  # Expected: 7
  ```
- [ ] Manual snapshot taken immediately before launch:
  ```bash
  aws rds create-db-snapshot \
    --db-instance-identifier vantro-production-db \
    --db-snapshot-identifier vantro-prelaunch-$(date +%Y%m%d)
  # Wait for completion:
  aws rds wait db-snapshot-completed \
    --db-snapshot-identifier vantro-prelaunch-$(date +%Y%m%d)
  ```
- [ ] `alembic upgrade head` run against production DB (from migration-only ECS task or bastion host). Confirm current revision:
  ```bash
  # Connect to DB and run:
  SELECT version_num FROM alembic_version;
  # Expected: latest revision (021 as of last migration)
  ```
- [ ] RDS security group only allows inbound TCP 5432 from ECS task security group — no public access:
  ```bash
  aws ec2 describe-security-groups --group-ids <RDS_SG_ID> \
    --query 'SecurityGroups[0].IpPermissions'
  # Verify: source is ECS task SG ID, no 0.0.0.0/0 entries on port 5432
  ```
- [ ] RDS parameter group has `log_min_duration_statement=1000` (log queries >1s):
  ```bash
  aws rds describe-db-parameters \
    --db-parameter-group-name <PARAM_GROUP_NAME> \
    --query "Parameters[?ParameterName=='log_min_duration_statement'].ParameterValue"
  # Expected: "1000"
  ```
- [ ] Read replica created and `DATABASE_REPLICA_URL` set in ECS task definition (optional, skip if low traffic at launch):
  ```bash
  aws rds describe-db-instances \
    --query "DBInstances[?ReadReplicaSourceDBInstanceIdentifier=='vantro-production-db'].Endpoint.Address"
  ```
- [ ] pgvector extension installed in production database:
  ```sql
  -- Connect to production DB and run:
  SELECT extname FROM pg_extension WHERE extname = 'vector';
  -- Expected: 1 row returned
  ```
- [ ] RDS CloudWatch alarms configured (see Alarms section below)

---

## 3. SQS

- [ ] Queue `vantro-agent-jobs` exists as a standard queue (not FIFO):
  ```bash
  aws sqs get-queue-url --queue-name vantro-agent-jobs
  ```
- [ ] Dead-letter queue `vantro-agent-jobs-dlq` exists and is wired with `maxReceiveCount=3`:
  ```bash
  aws sqs get-queue-attributes \
    --queue-url <QUEUE_URL> \
    --attribute-names RedrivePolicy
  # Expected: maxReceiveCount=3, deadLetterTargetArn points to vantro-agent-jobs-dlq
  ```
- [ ] `SQS_QUEUE_URL` env var set in ECS task definition to the queue URL:
  ```bash
  aws ecs describe-task-definition --task-definition vantro-backend \
    --query "taskDefinition.containerDefinitions[0].environment[?name=='SQS_QUEUE_URL'].value"
  ```
- [ ] Visibility timeout set to 120 seconds (LLM_TIMEOUT_S=90 + 30s buffer):
  ```bash
  aws sqs get-queue-attributes \
    --queue-url <QUEUE_URL> \
    --attribute-names VisibilityTimeout
  # Expected: "120"
  ```
- [ ] Message retention period: 4 days (345600 seconds):
  ```bash
  aws sqs get-queue-attributes \
    --queue-url <QUEUE_URL> \
    --attribute-names MessageRetentionPeriod
  # Expected: "345600"
  ```
- [ ] Queue resource policy restricts send/receive/delete to ECS task role only (no public access)
- [ ] Smoke test — send a test message and verify worker picks it up:
  ```bash
  aws sqs send-message \
    --queue-url <QUEUE_URL> \
    --message-body '{"test": true, "job_id": "smoke-test-001"}'
  # Then check ECS task logs in CloudWatch for pickup confirmation
  ```

---

## 4. S3

- [ ] Bucket created with account ID suffix (ensures global uniqueness):
  ```bash
  ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
  aws s3api create-bucket \
    --bucket vantro-production-uploads-${ACCOUNT_ID} \
    --region us-east-1
  ```
- [ ] Block all public access enabled on bucket:
  ```bash
  aws s3api put-public-access-block \
    --bucket vantro-production-uploads-<ACCOUNT_ID> \
    --public-access-block-configuration \
      BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
  # Verify:
  aws s3api get-public-access-block --bucket vantro-production-uploads-<ACCOUNT_ID>
  ```
- [ ] Server-side encryption enabled (SSE-S3):
  ```bash
  aws s3api put-bucket-encryption \
    --bucket vantro-production-uploads-<ACCOUNT_ID> \
    --server-side-encryption-configuration \
      '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
  ```
- [ ] Lifecycle policy: abort incomplete multipart uploads after 7 days:
  ```bash
  aws s3api put-bucket-lifecycle-configuration \
    --bucket vantro-production-uploads-<ACCOUNT_ID> \
    --lifecycle-configuration '{
      "Rules":[{
        "ID":"abort-incomplete-mpu",
        "Status":"Enabled",
        "AbortIncompleteMultipartUpload":{"DaysAfterInitiation":7}
      }]
    }'
  ```
- [ ] CORS policy allows only `https://vantro.ai` origin:
  ```bash
  aws s3api put-bucket-cors \
    --bucket vantro-production-uploads-<ACCOUNT_ID> \
    --cors-configuration '{
      "CORSRules":[{
        "AllowedOrigins":["https://vantro.ai"],
        "AllowedMethods":["GET","PUT","POST"],
        "AllowedHeaders":["*"],
        "MaxAgeSeconds":3000
      }]
    }'
  ```
- [ ] Bucket policy restricts `s3:PutObject` and `s3:GetObject` to ECS task role ARN only:
  ```bash
  aws s3api put-bucket-policy \
    --bucket vantro-production-uploads-<ACCOUNT_ID> \
    --policy '{
      "Version":"2012-10-17",
      "Statement":[{
        "Effect":"Allow",
        "Principal":{"AWS":"<ECS_TASK_ROLE_ARN>"},
        "Action":["s3:PutObject","s3:GetObject"],
        "Resource":"arn:aws:s3:::vantro-production-uploads-<ACCOUNT_ID>/*"
      }]
    }'
  ```

---

## 5. Secrets Manager

- [ ] Secret `vantro/production/anthropic-api-key` created and contains `ANTHROPIC_API_KEY`:
  ```bash
  aws secretsmanager describe-secret --secret-id vantro/production/anthropic-api-key \
    --query '{name:Name,lastChanged:LastChangedDate}'
  ```
- [ ] Secret `vantro/production/database-url` created; value is `postgres://user:pass@host:5432/vantro`
- [ ] Secret `vantro/production/secret-key` created; value is randomly generated, minimum 32 characters:
  ```bash
  # Generate if needed:
  python3 -c "import secrets; print(secrets.token_urlsafe(48))"
  ```
- [ ] Secret `vantro/production/integration-encryption-key` created; value is a valid Fernet key:
  ```bash
  # Generate if needed:
  python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- [ ] Secret `vantro/production/openai-api-key` created; used by skill RAG embeddings (`agent_worker.py` silent-skips if missing but indexing won't work)
- [ ] Secret `vantro/production/stripe-secret-key` created; value is live key (`sk_live_...`)
- [ ] Secret `vantro/production/stripe-webhook-secret` created; value is `whsec_...` from Stripe dashboard
- [ ] ECS task execution role policy covers all vantro secrets:
  ```bash
  # Confirm the ARN wildcard covers all secrets:
  # arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:vantro/production/*
  aws iam get-role-policy --role-name vantro-ecs-execution-role \
    --policy-name SecretsManagerVantroAccess
  ```
- [ ] `SECRET_KEY` is NOT configured for auto-rotation (rotation would invalidate all active JWTs):
  ```bash
  aws secretsmanager describe-secret --secret-id vantro/production/secret-key \
    --query 'RotationEnabled'
  # Expected: false
  ```
- [ ] `ANTHROPIC_API_KEY` has no auto-rotation configured; rotate manually when needed by updating the secret value and redeploying ECS tasks

---

## 6. CloudWatch

- [ ] Log group `/ecs/vantro-backend` exists with 30-day retention:
  ```bash
  aws logs describe-log-groups --log-group-name-prefix /ecs/vantro-backend \
    --query 'logGroups[0].{name:logGroupName,retentionDays:retentionInDays}'
  # If retention not set:
  aws logs put-retention-policy --log-group-name /ecs/vantro-backend --retention-in-days 30
  ```
- [ ] Log group `/ecs/vantro-worker` exists with 30-day retention (if worker runs as separate ECS task):
  ```bash
  aws logs put-retention-policy --log-group-name /ecs/vantro-worker --retention-in-days 30
  ```
- [ ] Custom metrics are flowing into namespace `Vantro/AgentJobs` — verify after the first agent job completes:
  ```bash
  aws cloudwatch list-metrics --namespace "Vantro/AgentJobs" \
    --query 'Metrics[*].MetricName'
  # Expected after first run: JobsCompleted, JobsFailed, JobsPendingApproval, JobsPendingFinancialReview
  ```
- [ ] CloudWatch dashboard `vantro-production` created with these widgets:
  - `JobsCompleted` — line graph, 1-hour period, 24h window
  - `JobsFailed` — line graph, alert threshold line at >0
  - `JobsPendingApproval` — number widget (HITL-3 queue depth)
  - `JobsPendingFinancialReview` — number widget (financial scanner hits)
  - ECS CPUUtilization — line graph
  - RDS CPUUtilization — line graph
  - SQS `ApproximateNumberOfMessagesVisible` for `vantro-agent-jobs`
  - SQS `ApproximateNumberOfMessagesVisible` for `vantro-agent-jobs-dlq`
  ```bash
  # Verify dashboard exists:
  aws cloudwatch list-dashboards --query "DashboardEntries[?DashboardName=='vantro-production']"
  ```

---

## 7. CloudWatch Alarms

Create SNS topic first if not already done:
```bash
SNS_ARN=$(aws sns create-topic --name vantro-ops-alerts --query TopicArn --output text)
aws sns subscribe --topic-arn $SNS_ARN --protocol email --notification-endpoint mark.salman76@gmail.com
# Confirm the subscription via email before alarms will deliver
```

- [ ] **ECS High CPU** — CPUUtilization >80% for 5 consecutive minutes:
  ```bash
  aws cloudwatch put-metric-alarm \
    --alarm-name vantro-ecs-high-cpu \
    --alarm-description "ECS vantro-backend CPU above 80% for 5 minutes" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --dimensions Name=ServiceName,Value=vantro-backend Name=ClusterName,Value=vantro-production \
    --alarm-actions $SNS_ARN \
    --ok-actions $SNS_ARN
  ```

- [ ] **High 5xx Error Rate** — ALB HTTPCode_Target_5XX_Count >10 per 5 minutes:
  ```bash
  aws cloudwatch put-metric-alarm \
    --alarm-name vantro-alb-5xx-high \
    --alarm-description "Backend returning >10 5xx errors in 5 minutes" \
    --metric-name HTTPCode_Target_5XX_Count \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --dimensions Name=LoadBalancer,Value=<ALB_DIMENSION_VALUE> \
    --alarm-actions $SNS_ARN \
    --treat-missing-data notBreaching
  ```

- [ ] **RDS Connections Near Limit** — DatabaseConnections >80% of `max_connections` (check your parameter group; default for db.t3.medium ≈ 420, so threshold ≈ 336):
  ```bash
  aws cloudwatch put-metric-alarm \
    --alarm-name vantro-rds-connections-high \
    --alarm-description "RDS connection count above 80% of max_connections" \
    --metric-name DatabaseConnections \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 336 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --dimensions Name=DBInstanceIdentifier,Value=vantro-production-db \
    --alarm-actions $SNS_ARN
  ```

- [ ] **RDS High CPU** — CPUUtilization >80% for 5 minutes:
  ```bash
  aws cloudwatch put-metric-alarm \
    --alarm-name vantro-rds-high-cpu \
    --alarm-description "RDS CPU above 80% for 5 minutes" \
    --metric-name CPUUtilization \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --dimensions Name=DBInstanceIdentifier,Value=vantro-production-db \
    --alarm-actions $SNS_ARN
  ```

- [ ] **SQS DLQ Has Messages** — any message in `vantro-agent-jobs-dlq` means a job failed 3 retries:
  ```bash
  DLQ_URL=$(aws sqs get-queue-url --queue-name vantro-agent-jobs-dlq --query QueueUrl --output text)
  DLQ_ARN=$(aws sqs get-queue-attributes --queue-url $DLQ_URL \
    --attribute-names QueueArn --query Attributes.QueueArn --output text)

  aws cloudwatch put-metric-alarm \
    --alarm-name vantro-sqs-dlq-messages \
    --alarm-description "Messages in DLQ — agent jobs failing after 3 retries" \
    --metric-name ApproximateNumberOfMessagesVisible \
    --namespace AWS/SQS \
    --statistic Sum \
    --period 60 \
    --threshold 0 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --dimensions Name=QueueName,Value=vantro-agent-jobs-dlq \
    --alarm-actions $SNS_ARN \
    --treat-missing-data notBreaching
  ```

- [ ] **Financial Review Queue Backed Up** — any job flagged by `scan_for_financial_actions` (custom metric):
  ```bash
  aws cloudwatch put-metric-alarm \
    --alarm-name vantro-financial-review-pending \
    --alarm-description "Job flagged by financial output scanner — requires admin review" \
    --metric-name JobsPendingFinancialReview \
    --namespace "Vantro/AgentJobs" \
    --statistic Sum \
    --period 300 \
    --threshold 0 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions $SNS_ARN \
    --treat-missing-data notBreaching
  ```

- [ ] **HITL-3 Approval Backlog** — more than 10 jobs pending owner approval:
  ```bash
  aws cloudwatch put-metric-alarm \
    --alarm-name vantro-hitl3-backlog \
    --alarm-description "More than 10 HITL-3 jobs awaiting owner approval" \
    --metric-name JobsPendingApproval \
    --namespace "Vantro/AgentJobs" \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions $SNS_ARN \
    --treat-missing-data notBreaching
  ```

- [ ] Verify all alarms are in `OK` or `INSUFFICIENT_DATA` state (not `ALARM`) before launch:
  ```bash
  aws cloudwatch describe-alarms \
    --alarm-name-prefix vantro- \
    --query 'MetricAlarms[*].{name:AlarmName,state:StateValue}'
  ```

---

## 8. Networking

- [ ] VPC exists with private subnets for ECS tasks and RDS (no public IP assignment on those subnets):
  ```bash
  aws ec2 describe-vpcs --filters Name=tag:Name,Values=vantro-production-vpc \
    --query 'Vpcs[0].{id:VpcId,cidr:CidrBlock}'
  ```
- [ ] NAT gateway deployed in each AZ's public subnet; private subnet route tables point `0.0.0.0/0` to NAT (ECS tasks need outbound to Anthropic API, Stripe, Composio, OpenAI):
  ```bash
  aws ec2 describe-nat-gateways \
    --filter Name=tag:Name,Values=vantro-nat-* \
    --query 'NatGateways[*].{id:NatGatewayId,state:State,az:SubnetId}'
  ```
- [ ] Application Load Balancer deployed in public subnets, target group pointing to ECS tasks on port 8000:
  ```bash
  aws elbv2 describe-load-balancers \
    --query "LoadBalancers[?contains(LoadBalancerName,'vantro')].{name:LoadBalancerName,dns:DNSName,state:State.Code}"
  ```
- [ ] ACM certificate issued and validated for `api.vantro.ai` (and optionally `vantro.ai`):
  ```bash
  aws acm list-certificates --query \
    "CertificateSummaryList[?contains(DomainName,'vantro.ai')].{domain:DomainName,status:Status}"
  # Expected: Status = "ISSUED"
  ```
- [ ] HTTPS listener on ALB port 443 uses the ACM certificate; HTTP listener on port 80 redirects to HTTPS:
  ```bash
  aws elbv2 describe-listeners \
    --load-balancer-arn <ALB_ARN> \
    --query 'Listeners[*].{port:Port,protocol:Protocol,action:DefaultActions[0].Type}'
  ```
- [ ] ALB security group: inbound 443 from `0.0.0.0/0`, inbound 80 from `0.0.0.0/0` (for redirect); no other inbound:
  ```bash
  aws ec2 describe-security-groups --group-ids <ALB_SG_ID> \
    --query 'SecurityGroups[0].IpPermissions'
  ```
- [ ] ECS task security group: inbound TCP 8000 from ALB security group only; no direct inbound from internet:
  ```bash
  aws ec2 describe-security-groups --group-ids <ECS_TASK_SG_ID> \
    --query 'SecurityGroups[0].IpPermissions'
  # Source should be ALB SG ID, not 0.0.0.0/0
  ```
- [ ] Route 53 record `api.vantro.ai` is an ALIAS (or CNAME) pointing to ALB DNS name:
  ```bash
  aws route53 list-resource-record-sets \
    --hosted-zone-id <ZONE_ID> \
    --query "ResourceRecordSets[?Name=='api.vantro.ai.']"
  ```
- [ ] End-to-end connectivity test — health check returns 200 from public internet:
  ```bash
  curl -o /dev/null -s -w "%{http_code}" https://api.vantro.ai/health
  # Expected: 200
  ```
- [ ] OpenAPI docs disabled in production (`ENVIRONMENT=production` causes `docs_url=None, redoc_url=None`):
  ```bash
  curl -o /dev/null -s -w "%{http_code}" https://api.vantro.ai/docs
  # Expected: 404
  curl -o /dev/null -s -w "%{http_code}" https://api.vantro.ai/redoc
  # Expected: 404
  ```
- [ ] `Server` response header is absent (suppressed by `SecurityHeadersMiddleware`):
  ```bash
  curl -sI https://api.vantro.ai/health | grep -i server
  # Expected: no output
  ```
