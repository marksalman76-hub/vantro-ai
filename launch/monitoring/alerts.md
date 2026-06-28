# Vantro.ai — AWS CloudWatch Alerts & Runbooks

**Region:** us-east-1  
**Admin:** mark.salman76@gmail.com  
**Alert delivery:** SNS → Email (no PagerDuty)  
**Infrastructure:** ECS/Fargate (`vantro-cluster`) · RDS PostgreSQL (`vantro-db`) · SQS (`vantro-agent-jobs`) · ALB (`vantro-alb`)

---

## 1. SNS Topic Setup

Create three topics with separate urgency levels and subscribe your email to each.

```bash
# ── P0: Immediate (page now) ──────────────────────────────────────────────────
aws sns create-topic \
  --name vantro-p0-alerts \
  --region us-east-1

aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:$(aws sts get-caller-identity --query Account --output text):vantro-p0-alerts \
  --protocol email \
  --notification-endpoint mark.salman76@gmail.com \
  --region us-east-1

# ── P1: Alert within 15 min ──────────────────────────────────────────────────
aws sns create-topic \
  --name vantro-p1-alerts \
  --region us-east-1

aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:$(aws sts get-caller-identity --query Account --output text):vantro-p1-alerts \
  --protocol email \
  --notification-endpoint mark.salman76@gmail.com \
  --region us-east-1

# ── P2: Daily digest ─────────────────────────────────────────────────────────
aws sns create-topic \
  --name vantro-p2-alerts \
  --region us-east-1

aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:$(aws sts get-caller-identity --query Account --output text):vantro-p2-alerts \
  --protocol email \
  --notification-endpoint mark.salman76@gmail.com \
  --region us-east-1
```

> After running subscribe commands, check your inbox and confirm each SNS subscription before alarms can fire.

Store your account ID in a shell variable to keep the commands below readable:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
P0_ARN="arn:aws:sns:us-east-1:${ACCOUNT_ID}:vantro-p0-alerts"
P1_ARN="arn:aws:sns:us-east-1:${ACCOUNT_ID}:vantro-p1-alerts"
P2_ARN="arn:aws:sns:us-east-1:${ACCOUNT_ID}:vantro-p2-alerts"
```

---

## 2. P0 — Immediate Alerts

Threshold breached → SNS email fires within 1–2 minutes. Investigate immediately.

---

### P0-1: RDS Unreachable / 0 DB Connections Available

**Trigger:** `DatabaseConnections` drops to 0 for 2 consecutive 1-minute data points.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P0-RDS-NoConnections" \
  --alarm-description "P0: vantro-db has 0 database connections — instance may be unreachable or crashed" \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=vantro-db \
  --statistic Minimum \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --treat-missing-data breaching \
  --alarm-actions "${P0_ARN}" \
  --ok-actions "${P0_ARN}" \
  --region us-east-1
```

---

### P0-2a: ECS Backend Running 0 Tasks

**Trigger:** `RunningTaskCount` for `vantro-backend` is 0 for 2 consecutive 1-minute data points.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P0-ECS-Backend-ZeroTasks" \
  --alarm-description "P0: vantro-backend ECS service has 0 running tasks — service is down" \
  --namespace AWS/ECS \
  --metric-name RunningTaskCount \
  --dimensions Name=ClusterName,Value=vantro-cluster Name=ServiceName,Value=vantro-backend \
  --statistic Minimum \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --treat-missing-data breaching \
  --alarm-actions "${P0_ARN}" \
  --ok-actions "${P0_ARN}" \
  --region us-east-1
```

---

### P0-2b: ECS Frontend Running 0 Tasks

**Trigger:** `RunningTaskCount` for `vantro-frontend` is 0 for 2 consecutive 1-minute data points.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P0-ECS-Frontend-ZeroTasks" \
  --alarm-description "P0: vantro-frontend ECS service has 0 running tasks — frontend is down" \
  --namespace AWS/ECS \
  --metric-name RunningTaskCount \
  --dimensions Name=ClusterName,Value=vantro-cluster Name=ServiceName,Value=vantro-frontend \
  --statistic Minimum \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --treat-missing-data breaching \
  --alarm-actions "${P0_ARN}" \
  --ok-actions "${P0_ARN}" \
  --region us-east-1
```

---

### P0-3: ALB 5xx Error Rate > 5% for 2 Minutes

ALB reports `HTTPCode_Target_5XX_Count` and `RequestCount` separately. Use a CloudWatch Metric Math alarm.

```bash
# Get the ALB resource label first:
aws elbv2 describe-load-balancers \
  --names vantro-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text \
  --region us-east-1
# Output example: arn:aws:elasticloadbalancing:us-east-1:123456789:loadbalancer/app/vantro-alb/abc123def456
# The resource label is the part after "loadbalancer/": app/vantro-alb/abc123def456

ALB_SUFFIX="app/vantro-alb/abc123def456"   # replace with real value

aws cloudwatch put-metric-alarm \
  --alarm-name "P0-ALB-High5xxRate" \
  --alarm-description "P0: ALB 5xx error rate exceeded 5% for 2 consecutive minutes" \
  --metrics '[
    {
      "Id": "e1",
      "Expression": "m2 / m1 * 100",
      "Label": "5xx Error Rate %",
      "ReturnData": true
    },
    {
      "Id": "m1",
      "MetricStat": {
        "Metric": {
          "Namespace": "AWS/ApplicationELB",
          "MetricName": "RequestCount",
          "Dimensions": [{"Name": "LoadBalancer", "Value": "'"${ALB_SUFFIX}"'"}]
        },
        "Period": 60,
        "Stat": "Sum"
      },
      "ReturnData": false
    },
    {
      "Id": "m2",
      "MetricStat": {
        "Metric": {
          "Namespace": "AWS/ApplicationELB",
          "MetricName": "HTTPCode_Target_5XX_Count",
          "Dimensions": [{"Name": "LoadBalancer", "Value": "'"${ALB_SUFFIX}"'"}]
        },
        "Period": 60,
        "Stat": "Sum"
      },
      "ReturnData": false
    }
  ]' \
  --threshold 5 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 2 \
  --treat-missing-data notBreaching \
  --alarm-actions "${P0_ARN}" \
  --ok-actions "${P0_ARN}" \
  --region us-east-1
```

---

### P0-4: Financial Scanner Triggered

**Trigger:** Custom metric `Vantro/FinancialScanner/Triggers` > 0 in any 1-minute window.

Your FastAPI backend must emit this metric whenever `scan_for_financial_actions` routes a job to `pending_financial_review`. Add to `agent_executor.py`:

```python
import boto3

_cw = boto3.client("cloudwatch", region_name="us-east-1")

def _emit_financial_scan_trigger(job_id: str) -> None:
    """Emit a CloudWatch metric when the financial scanner fires."""
    _cw.put_metric_data(
        Namespace="Vantro/FinancialScanner",
        MetricData=[{
            "MetricName": "Triggers",
            "Value": 1,
            "Unit": "Count",
            "Dimensions": [{"Name": "Environment", "Value": "production"}],
        }],
    )
```

Call `_emit_financial_scan_trigger(job.id)` immediately after routing to `pending_financial_review`.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P0-FinancialScanner-Triggered" \
  --alarm-description "P0: Financial scanner flagged an agent response — job routed to pending_financial_review. Investigate immediately." \
  --namespace "Vantro/FinancialScanner" \
  --metric-name "Triggers" \
  --dimensions Name=Environment,Value=production \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 0 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P0_ARN}" \
  --region us-east-1
```

---

## 3. P1 — Alert Within 15 Minutes

---

### P1-1: SQS Agent Jobs Stuck > 5 Minutes

**Trigger:** `ApproximateAgeOfOldestMessage` on `vantro-agent-jobs` > 300 seconds.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P1-SQS-JobsStuck" \
  --alarm-description "P1: Oldest SQS message in vantro-agent-jobs is >5 min old — worker may be stalled or crashed" \
  --namespace AWS/SQS \
  --metric-name ApproximateAgeOfOldestMessage \
  --dimensions Name=QueueName,Value=vantro-agent-jobs \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 300 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P1_ARN}" \
  --ok-actions "${P1_ARN}" \
  --region us-east-1
```

---

### P1-2: Credit Deduction Failures

**Trigger:** Custom metric `Vantro/Credits/DeductionFailures` > 0.

Emit this metric in `credits_service.py` whenever a credit deduction raises an exception or returns a failure state:

```python
_cw.put_metric_data(
    Namespace="Vantro/Credits",
    MetricData=[{
        "MetricName": "DeductionFailures",
        "Value": 1,
        "Unit": "Count",
        "Dimensions": [{"Name": "Environment", "Value": "production"}],
    }],
)
```

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P1-Credits-DeductionFailure" \
  --alarm-description "P1: Credit deduction failure detected — jobs may run without billing" \
  --namespace "Vantro/Credits" \
  --metric-name "DeductionFailures" \
  --dimensions Name=Environment,Value=production \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 0 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P1_ARN}" \
  --region us-east-1
```

---

### P1-3: HITL-3 Pending Approval Queue > 10 Jobs

**Trigger:** Custom metric `Vantro/Jobs/PendingApproval` > 10.

Emit this metric from `agent_worker.py` as a gauge each time the worker loop runs:

```python
pending_count = db.query(AgentJob).filter(
    AgentJob.status == "pending_approval"
).count()

_cw.put_metric_data(
    Namespace="Vantro/Jobs",
    MetricData=[{
        "MetricName": "PendingApproval",
        "Value": pending_count,
        "Unit": "Count",
        "Dimensions": [{"Name": "Environment", "Value": "production"}],
    }],
)
```

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P1-HITL3-QueueBacklog" \
  --alarm-description "P1: More than 10 HITL-3 jobs awaiting owner approval — clients are blocked" \
  --namespace "Vantro/Jobs" \
  --metric-name "PendingApproval" \
  --dimensions Name=Environment,Value=production \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P1_ARN}" \
  --ok-actions "${P1_ARN}" \
  --region us-east-1
```

---

### P1-4: ECS CPU > 80% Sustained 10 Minutes

```bash
# Backend
aws cloudwatch put-metric-alarm \
  --alarm-name "P1-ECS-Backend-HighCPU" \
  --alarm-description "P1: vantro-backend ECS CPU >80% for 10 minutes — consider scaling up" \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=vantro-cluster Name=ServiceName,Value=vantro-backend \
  --statistic Average \
  --period 60 \
  --evaluation-periods 10 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P1_ARN}" \
  --ok-actions "${P1_ARN}" \
  --region us-east-1

# Frontend
aws cloudwatch put-metric-alarm \
  --alarm-name "P1-ECS-Frontend-HighCPU" \
  --alarm-description "P1: vantro-frontend ECS CPU >80% for 10 minutes" \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=vantro-cluster Name=ServiceName,Value=vantro-frontend \
  --statistic Average \
  --period 60 \
  --evaluation-periods 10 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P1_ARN}" \
  --ok-actions "${P1_ARN}" \
  --region us-east-1
```

---

## 4. P2 — Daily Digest / Early Warning

---

### P2-1: Slow RDS Queries

**Setup — `pg_stat_statements` + Performance Insights**

Step 1: Enable Performance Insights on `vantro-db` (if not already on):

```bash
aws rds modify-db-instance \
  --db-instance-identifier vantro-db \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --apply-immediately \
  --region us-east-1
```

Step 2: Enable `pg_stat_statements` parameter group:

```bash
# Create or update a parameter group
aws rds modify-db-parameter-group \
  --db-parameter-group-name vantro-db-params \
  --parameters "ParameterName=shared_preload_libraries,ParameterValue=pg_stat_statements,ApplyMethod=pending-reboot" \
  --region us-east-1

# Apply to vantro-db if not already using this group
aws rds modify-db-instance \
  --db-instance-identifier vantro-db \
  --db-parameter-group-name vantro-db-params \
  --apply-immediately \
  --region us-east-1
```

Step 3: After reboot, activate inside PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

Step 4: Query slow queries manually or via Lambda. Example manual query:

```sql
SELECT
  query,
  calls,
  round(total_exec_time::numeric, 2) AS total_ms,
  round(mean_exec_time::numeric, 2)  AS mean_ms,
  rows
FROM pg_stat_statements
WHERE mean_exec_time > 1000   -- queries averaging >1 second
ORDER BY mean_exec_time DESC
LIMIT 20;
```

**CloudWatch Alarm — RDS Read Latency**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P2-RDS-HighReadLatency" \
  --alarm-description "P2: RDS read latency >100ms average over 30 minutes — investigate slow queries via Performance Insights" \
  --namespace AWS/RDS \
  --metric-name ReadLatency \
  --dimensions Name=DBInstanceIdentifier,Value=vantro-db \
  --statistic Average \
  --period 300 \
  --evaluation-periods 6 \
  --threshold 0.1 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P2_ARN}" \
  --ok-actions "${P2_ARN}" \
  --region us-east-1
```

---

### P2-2: ECS Memory > 85% for 30 Consecutive Minutes

```bash
# Backend
aws cloudwatch put-metric-alarm \
  --alarm-name "P2-ECS-Backend-HighMemory" \
  --alarm-description "P2: vantro-backend ECS memory >85% for 30 minutes — memory leak or undersizing" \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ClusterName,Value=vantro-cluster Name=ServiceName,Value=vantro-backend \
  --statistic Average \
  --period 60 \
  --evaluation-periods 30 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P2_ARN}" \
  --ok-actions "${P2_ARN}" \
  --region us-east-1

# Frontend
aws cloudwatch put-metric-alarm \
  --alarm-name "P2-ECS-Frontend-HighMemory" \
  --alarm-description "P2: vantro-frontend ECS memory >85% for 30 minutes" \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ClusterName,Value=vantro-cluster Name=ServiceName,Value=vantro-frontend \
  --statistic Average \
  --period 60 \
  --evaluation-periods 30 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P2_ARN}" \
  --ok-actions "${P2_ARN}" \
  --region us-east-1
```

---

### P2-3: SQS Job Age Creeping (Early Warning: 60s–300s)

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "P2-SQS-JobsAgingEarlyWarning" \
  --alarm-description "P2: SQS oldest message 60–300s old — worker may be slow or falling behind" \
  --namespace AWS/SQS \
  --metric-name ApproximateAgeOfOldestMessage \
  --dimensions Name=QueueName,Value=vantro-agent-jobs \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 60 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions "${P2_ARN}" \
  --ok-actions "${P2_ARN}" \
  --region us-east-1
```

> Note: This alarm will re-fire into the P2 (email) topic. P1-1 uses a threshold of 300s on the same metric and goes to P1. Both can coexist.

---

## 5. Composite Alarm — "Platform Down"

Combines P0-2a (backend 0 tasks) + P0-1 (RDS no connections) into a single "everything is broken" alarm.

```bash
aws cloudwatch put-composite-alarm \
  --alarm-name "P0-COMPOSITE-PlatformDown" \
  --alarm-description "CRITICAL: Both vantro-backend ECS has 0 tasks AND RDS has 0 connections. Platform is fully down." \
  --alarm-rule "ALARM(\"P0-ECS-Backend-ZeroTasks\") AND ALARM(\"P0-RDS-NoConnections\")" \
  --alarm-actions "${P0_ARN}" \
  --ok-actions "${P0_ARN}" \
  --region us-east-1
```

Optional: add frontend to the composite:

```bash
aws cloudwatch put-composite-alarm \
  --alarm-name "P0-COMPOSITE-FullPlatformDown" \
  --alarm-description "CRITICAL: ECS backend + frontend both have 0 tasks AND RDS is unreachable." \
  --alarm-rule "ALARM(\"P0-ECS-Backend-ZeroTasks\") AND ALARM(\"P0-ECS-Frontend-ZeroTasks\") AND ALARM(\"P0-RDS-NoConnections\")" \
  --alarm-actions "${P0_ARN}" \
  --ok-actions "${P0_ARN}" \
  --region us-east-1
```

---

## 6. Auto-Remediation Alarm Actions

### ECS Service Force New Deployment (on 0 Tasks)

CloudWatch alarms cannot directly call ECS. Use an SNS → Lambda bridge.

**Step 1 — Create Lambda function `vantro-ecs-force-redeploy`:**

```python
# lambda_handler.py
import boto3, json, os

ecs = boto3.client("ecs", region_name="us-east-1")

CLUSTER  = os.environ.get("ECS_CLUSTER",  "vantro-cluster")
SERVICES = os.environ.get("ECS_SERVICES", "vantro-backend,vantro-frontend").split(",")

def handler(event, context):
    for record in event.get("Records", []):
        msg = json.loads(record["Sns"]["Message"])
        alarm_name = msg.get("AlarmName", "")
        if "ZeroTasks" in alarm_name or "PlatformDown" in alarm_name:
            for svc in SERVICES:
                print(f"Force redeploying {CLUSTER}/{svc}")
                ecs.update_service(
                    cluster=CLUSTER,
                    service=svc,
                    forceNewDeployment=True,
                )
    return {"statusCode": 200}
```

```bash
# Package and deploy
zip function.zip lambda_handler.py

aws lambda create-function \
  --function-name vantro-ecs-force-redeploy \
  --runtime python3.12 \
  --role arn:aws:iam::${ACCOUNT_ID}:role/vantro-lambda-ecs-role \
  --handler lambda_handler.handler \
  --zip-file fileb://function.zip \
  --environment "Variables={ECS_CLUSTER=vantro-cluster,ECS_SERVICES=vantro-backend}" \
  --timeout 30 \
  --region us-east-1

# Subscribe Lambda to the P0 SNS topic
aws sns subscribe \
  --topic-arn "${P0_ARN}" \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:${ACCOUNT_ID}:function:vantro-ecs-force-redeploy \
  --region us-east-1

# Grant SNS permission to invoke Lambda
aws lambda add-permission \
  --function-name vantro-ecs-force-redeploy \
  --statement-id sns-invoke \
  --action lambda:InvokeFunction \
  --principal sns.amazonaws.com \
  --source-arn "${P0_ARN}" \
  --region us-east-1
```

**Required IAM role `vantro-lambda-ecs-role` — minimum policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices"
      ],
      "Resource": "arn:aws:ecs:us-east-1:ACCOUNT_ID:service/vantro-cluster/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

> Auto-remediation is a safety net, not a substitute for root-cause investigation. If the service immediately goes back to 0 tasks after a force redeploy, the task definition itself has an error (bad image, failed health check, missing env vars). Check ECS task stopped reason.

---

## 7. P0 Runbooks

### Runbook: P0-RDS-NoConnections

**Symptom:** `DatabaseConnections` minimum = 0. Backend cannot reach the database.

**Step 1 — Check RDS instance status:**

```bash
aws rds describe-db-instances \
  --db-instance-identifier vantro-db \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address,AZ:AvailabilityZone}' \
  --output table \
  --region us-east-1
```

Look for `DBInstanceStatus`. Normal: `available`. Abnormal: `rebooting`, `incompatible-parameters`, `storage-full`, `failed`.

**Step 2 — Check recent RDS events:**

```bash
aws rds describe-events \
  --source-identifier vantro-db \
  --source-type db-instance \
  --duration 60 \
  --region us-east-1
```

Look for: `Recovery completed`, `Backing up`, `Multi-AZ failover`, `Storage-full`.

**Step 3 — Check ECS backend task logs to confirm connection errors:**

```bash
# Get the latest log stream for vantro-backend
aws logs describe-log-streams \
  --log-group-name /ecs/vantro-backend \
  --order-by LastEventTime \
  --descending \
  --max-items 1 \
  --query 'logStreams[0].logStreamName' \
  --output text \
  --region us-east-1

# Tail the last 100 events (replace STREAM_NAME)
aws logs get-log-events \
  --log-group-name /ecs/vantro-backend \
  --log-stream-name STREAM_NAME \
  --limit 100 \
  --region us-east-1 \
  | jq -r '.events[].message'
```

Grep for: `could not connect to server`, `connection refused`, `SSL SYSCALL error`.

---

### Runbook: P0-ECS-Backend-ZeroTasks / P0-ECS-Frontend-ZeroTasks

**Symptom:** ECS service desired count > 0 but running count = 0.

**Step 1 — Check service events:**

```bash
aws ecs describe-services \
  --cluster vantro-cluster \
  --services vantro-backend vantro-frontend \
  --query 'services[*].{Name:serviceName,Running:runningCount,Desired:desiredCount,Status:status,Events:events[0:5]}' \
  --output json \
  --region us-east-1
```

Look at the `events` array. Common causes: `task failed to start`, `ELB health check failed`, `unable to pull image`.

**Step 2 — Find stopped tasks and their stop reason:**

```bash
# List recently stopped tasks
aws ecs list-tasks \
  --cluster vantro-cluster \
  --service-name vantro-backend \
  --desired-status STOPPED \
  --region us-east-1 \
  --query 'taskArns' \
  --output text

# Describe stopped tasks (replace TASK_ARN)
aws ecs describe-tasks \
  --cluster vantro-cluster \
  --tasks TASK_ARN \
  --query 'tasks[0].{StopCode:stopCode,StoppedReason:stoppedReason,Containers:containers[*].{Name:name,Exit:exitCode,Reason:reason}}' \
  --output json \
  --region us-east-1
```

**Step 3 — Force a new deployment (if image/config looks correct):**

```bash
aws ecs update-service \
  --cluster vantro-cluster \
  --service vantro-backend \
  --force-new-deployment \
  --region us-east-1

aws ecs update-service \
  --cluster vantro-cluster \
  --service vantro-frontend \
  --force-new-deployment \
  --region us-east-1
```

Monitor recovery:

```bash
aws ecs wait services-stable \
  --cluster vantro-cluster \
  --services vantro-backend \
  --region us-east-1 && echo "Backend stable"
```

---

### Runbook: P0-ALB-High5xxRate

**Symptom:** ALB returning >5% 5xx responses over 2 minutes.

**Step 1 — Check which target group is unhealthy:**

```bash
# List target groups for vantro-alb
aws elbv2 describe-target-groups \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:${ACCOUNT_ID}:loadbalancer/app/vantro-alb/abc123def456 \
  --query 'TargetGroups[*].{Name:TargetGroupName,ARN:TargetGroupArn}' \
  --output table \
  --region us-east-1

# Check health of targets (replace TARGET_GROUP_ARN)
aws elbv2 describe-target-health \
  --target-group-arn TARGET_GROUP_ARN \
  --region us-east-1
```

Look for `HealthState: unhealthy` and `Reason`.

**Step 2 — Check ALB access logs for the error path:**

```bash
# If ALB access logs are enabled in S3 (enable if not):
aws elbv2 describe-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:${ACCOUNT_ID}:loadbalancer/app/vantro-alb/abc123def456 \
  --query 'Attributes[?Key==`access_logs.s3.enabled`]' \
  --region us-east-1

# Query CloudWatch for 5xx breakdown by URL (if using CloudWatch Container Insights):
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_Target_5XX_Count \
  --dimensions Name=LoadBalancer,Value=app/vantro-alb/abc123def456 \
  --start-time $(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 60 \
  --statistics Sum \
  --region us-east-1
```

**Step 3 — Check backend application logs for exception traces:**

```bash
aws logs filter-log-events \
  --log-group-name /ecs/vantro-backend \
  --filter-pattern "ERROR" \
  --start-time $(date -d '15 minutes ago' +%s)000 \
  --limit 50 \
  --region us-east-1 \
  | jq -r '.events[].message'
```

---

### Runbook: P0-FinancialScanner-Triggered

**Symptom:** `scan_for_financial_actions` matched a phrase in an agent response. Job is in `pending_financial_review`.

**Step 1 — Identify the job:**

```bash
# Connect to RDS (via bastion or RDS Proxy) and query:
# psql -h vantro-db.xxxx.us-east-1.rds.amazonaws.com -U vantro_user -d vantro

# SQL:
SELECT id, workspace_id, agent_id, status, created_at, updated_at
FROM agent_jobs
WHERE status = 'pending_financial_review'
ORDER BY updated_at DESC
LIMIT 10;
```

**Step 2 — Read the flagged output:**

```bash
SELECT id, output_data, error_message
FROM agent_jobs
WHERE status = 'pending_financial_review'
ORDER BY updated_at DESC
LIMIT 5;
```

**Step 3 — Approve or reject via admin API:**

```bash
# Reject (safe default until reviewed):
curl -X POST https://api.vantro.ai/api/admin/jobs/{JOB_ID}/reject \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Financial scanner triggered — manual rejection pending review"}'

# Approve only if output is safe after review:
curl -X POST https://api.vantro.ai/api/admin/jobs/{JOB_ID}/approve \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

---

## 8. Alarm Summary Table

| Alarm Name | Tier | Metric | Threshold | Periods |
|---|---|---|---|---|
| P0-RDS-NoConnections | P0 | RDS DatabaseConnections | < 1 | 2 × 1 min |
| P0-ECS-Backend-ZeroTasks | P0 | ECS RunningTaskCount (backend) | < 1 | 2 × 1 min |
| P0-ECS-Frontend-ZeroTasks | P0 | ECS RunningTaskCount (frontend) | < 1 | 2 × 1 min |
| P0-ALB-High5xxRate | P0 | ALB 5xx/total ratio | ≥ 5% | 2 × 1 min |
| P0-FinancialScanner-Triggered | P0 | Vantro/FinancialScanner/Triggers | > 0 | 1 × 1 min |
| P0-COMPOSITE-PlatformDown | P0 | Composite | Both backend+RDS | — |
| P1-SQS-JobsStuck | P1 | SQS ApproximateAgeOfOldestMessage | > 300s | 5 × 1 min |
| P1-Credits-DeductionFailure | P1 | Vantro/Credits/DeductionFailures | > 0 | 1 × 1 min |
| P1-HITL3-QueueBacklog | P1 | Vantro/Jobs/PendingApproval | > 10 | 3 × 5 min |
| P1-ECS-Backend-HighCPU | P1 | ECS CPUUtilization (backend) | > 80% | 10 × 1 min |
| P1-ECS-Frontend-HighCPU | P1 | ECS CPUUtilization (frontend) | > 80% | 10 × 1 min |
| P2-RDS-HighReadLatency | P2 | RDS ReadLatency | > 100ms | 6 × 5 min |
| P2-ECS-Backend-HighMemory | P2 | ECS MemoryUtilization (backend) | > 85% | 30 × 1 min |
| P2-ECS-Frontend-HighMemory | P2 | ECS MemoryUtilization (frontend) | > 85% | 30 × 1 min |
| P2-SQS-JobsAgingEarlyWarning | P2 | SQS ApproximateAgeOfOldestMessage | > 60s | 5 × 1 min |

---

## 9. Verify All Alarms Are Created

```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix "P0-" "P1-" "P2-" \
  --query 'MetricAlarms[*].{Name:AlarmName,State:StateValue,Action:AlarmActions[0]}' \
  --output table \
  --region us-east-1
```

Or verify by tier:

```bash
for prefix in P0 P1 P2; do
  echo "=== ${prefix} Alarms ==="
  aws cloudwatch describe-alarms \
    --alarm-name-prefix "${prefix}-" \
    --query 'MetricAlarms[*].[AlarmName,StateValue]' \
    --output text \
    --region us-east-1
done
```
