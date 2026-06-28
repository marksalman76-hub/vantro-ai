# CloudWatch Alarms — Vantro.ai Production

**Region:** `us-east-1` (substitute your actual region if different)  
**Account:** Replace `ACCOUNT_ID` with your 12-digit AWS account ID throughout.

---

## One-Time Setup: SNS Topic + Email Subscription

Create the alert topic and subscribe the admin email before running any alarm commands.

```bash
# Create the SNS topic
aws sns create-topic \
  --name vantro-alerts \
  --region us-east-1

# Subscribe mark.salman76@gmail.com — AWS sends a confirmation email; click it
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --protocol email \
  --notification-endpoint mark.salman76@gmail.com \
  --region us-east-1
```

> After running the subscribe command, check your inbox and click **Confirm subscription** before alarms will deliver.

---

## 1. ECS Backend — CPU Utilization > 80% (5 min sustained)

Triggers if the `vantro-backend` ECS service averages above 80% CPU for two consecutive 5-minute periods.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-backend-cpu-high" \
  --alarm-description "ECS vantro-backend CPU > 80% for 10 minutes (2 x 5-min periods)" \
  --namespace "AWS/ECS" \
  --metric-name "CPUUtilization" \
  --dimensions \
      Name=ClusterName,Value=vantro-cluster \
      Name=ServiceName,Value=vantro-backend \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --ok-actions    arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

---

## 2. ECS Backend — Memory Utilization > 85%

Triggers on a single 5-minute breach (memory spikes tend to be immediate concerns).

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-backend-memory-high" \
  --alarm-description "ECS vantro-backend memory > 85%" \
  --namespace "AWS/ECS" \
  --metric-name "MemoryUtilization" \
  --dimensions \
      Name=ClusterName,Value=vantro-cluster \
      Name=ServiceName,Value=vantro-backend \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --ok-actions    arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

---

## 3. RDS — CPU > 70% (5 min sustained)

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-db-cpu-high" \
  --alarm-description "RDS vantro-db CPU > 70% for 10 minutes" \
  --namespace "AWS/RDS" \
  --metric-name "CPUUtilization" \
  --dimensions Name=DBInstanceIdentifier,Value=vantro-db \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --ok-actions    arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

---

## 4. RDS — DatabaseConnections > 48 (80% of 60 max_connections)

`db.t3.medium` has a PostgreSQL `max_connections` of 60. Alert at 48 (80%) to allow time to act before connections are exhausted.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-db-connections-high" \
  --alarm-description "RDS vantro-db connections > 48 (80% of 60 max)" \
  --namespace "AWS/RDS" \
  --metric-name "DatabaseConnections" \
  --dimensions Name=DBInstanceIdentifier,Value=vantro-db \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 48 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --ok-actions    arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

> **If you use pgBouncer or SQLAlchemy pool sizing**, adjust the threshold accordingly. Default SQLAlchemy pool size is 5 per worker; with e.g. 4 ECS tasks × 5 workers × pool_size=5 you can hit 100 connections fast — consider setting `max_overflow=0` and `pool_size` to safe values.

---

## 5. ALB — 5xx Error Rate > 1% (Metric Math Alarm)

CloudWatch alarms cannot natively divide two metrics. Use a **Metric Math** alarm with `FILL` to avoid division-by-zero on low-traffic periods.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-alb-5xx-rate-high" \
  --alarm-description "ALB 5xx error rate > 1% of requests over 5 minutes" \
  --metrics '[
    {
      "Id": "m1",
      "MetricStat": {
        "Metric": {
          "Namespace": "AWS/ApplicationELB",
          "MetricName": "HTTPCode_Target_5XX_Count",
          "Dimensions": [
            { "Name": "LoadBalancer", "Value": "app/vantro-alb/REPLACE_WITH_ALB_SUFFIX" }
          ]
        },
        "Period": 300,
        "Stat": "Sum"
      },
      "ReturnData": false
    },
    {
      "Id": "m2",
      "MetricStat": {
        "Metric": {
          "Namespace": "AWS/ApplicationELB",
          "MetricName": "RequestCount",
          "Dimensions": [
            { "Name": "LoadBalancer", "Value": "app/vantro-alb/REPLACE_WITH_ALB_SUFFIX" }
          ]
        },
        "Period": 300,
        "Stat": "Sum"
      },
      "ReturnData": false
    },
    {
      "Id": "e1",
      "Expression": "100 * m1 / FILL(m2, 1)",
      "Label": "5xx Error Rate Percent",
      "ReturnData": true
    }
  ]' \
  --comparison-operator GreaterThanThreshold \
  --threshold 1 \
  --evaluation-periods 1 \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --ok-actions    arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

> **Find your ALB suffix:** Run `aws elbv2 describe-load-balancers --names vantro-alb --query 'LoadBalancers[0].LoadBalancerArn' --output text --region us-east-1` — the suffix is the part after `app/vantro-alb/` in the ARN. Replace `REPLACE_WITH_ALB_SUFFIX` above with that value (e.g. `1a2b3c4d5e6f7890`).
>
> `FILL(m2, 1)` substitutes 1 for missing `RequestCount` data points, preventing division-by-zero during zero-traffic windows while keeping the ratio meaningful.

---

## 6. SQS — ApproximateAgeOfOldestMessage > 300 seconds

Jobs older than 5 minutes sitting unprocessed indicates the agent worker is stalled or overwhelmed.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-sqs-message-age-high" \
  --alarm-description "SQS vantro-agent-jobs oldest message > 5 minutes old" \
  --namespace "AWS/SQS" \
  --metric-name "ApproximateAgeOfOldestMessage" \
  --dimensions Name=QueueName,Value=vantro-agent-jobs \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 300 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --ok-actions    arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

> **Note:** `ApproximateAgeOfOldestMessage` only emits a metric when messages are present in the queue. `treat-missing-data notBreaching` ensures the alarm stays green when the queue is empty.

---

## 7. SQS — ApproximateNumberOfMessagesNotVisible > 50

Messages in-flight (being processed) exceeding 50 means many concurrent agent jobs are running simultaneously — useful as an early capacity signal.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-sqs-inflight-high" \
  --alarm-description "SQS vantro-agent-jobs in-flight messages > 50" \
  --namespace "AWS/SQS" \
  --metric-name "ApproximateNumberOfMessagesNotVisible" \
  --dimensions Name=QueueName,Value=vantro-agent-jobs \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --ok-actions    arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

---

## 8. FastAPI Log Errors > 10 per 5 Minutes

This requires two steps: a **metric filter** to extract error counts from CloudWatch Logs, then an alarm on the resulting custom metric.

### Step 8a: Create the Log Metric Filter

Replace `REPLACE_WITH_LOG_GROUP` with your ECS task log group (e.g. `/ecs/vantro-backend`).

```bash
# First, confirm your log group name
aws logs describe-log-groups \
  --log-group-name-prefix "/ecs/vantro" \
  --region us-east-1

# Create the metric filter — matches lines containing ERROR or CRITICAL
aws logs put-metric-filter \
  --log-group-name "/ecs/vantro-backend" \
  --filter-name "FastAPIErrorCount" \
  --filter-pattern "[timestamp, level=ERROR||level=CRITICAL, ...]" \
  --metric-transformations \
      metricName=FastAPIErrorCount,\
metricNamespace=Vantro/Application,\
metricValue=1,\
defaultValue=0 \
  --region us-east-1
```

> **Filter pattern explained:** `[timestamp, level=ERROR||level=CRITICAL, ...]` matches structured log lines where the second space-delimited token is `ERROR` or `CRITICAL`. If your FastAPI app uses JSON logging (e.g. via `structlog` or `python-json-logger`), change the pattern to `{ $.level = "ERROR" || $.level = "CRITICAL" }` for JSON-aware matching.

### Step 8b: Create the Alarm on the Custom Metric

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-backend-error-log-rate" \
  --alarm-description "FastAPI logged ERROR/CRITICAL > 10 events in 5 minutes" \
  --namespace "Vantro/Application" \
  --metric-name "FastAPIErrorCount" \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --ok-actions    arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

---

## 9. pending_financial_review Jobs > 0

### Step 9a: Emit the Custom Metric from FastAPI

This metric does not exist in AWS natively — the FastAPI app must emit it via `boto3`. Add this to `app/services/monitoring_service.py` (create if it does not exist) and call it from `agent_executor.py` wherever a job transitions to `pending_financial_review`.

```python
# app/services/monitoring_service.py
import boto3
import os
from datetime import datetime, timezone

_cloudwatch = None

def _get_cw_client():
    global _cloudwatch
    if _cloudwatch is None:
        _cloudwatch = boto3.client("cloudwatch", region_name=os.getenv("AWS_REGION", "us-east-1"))
    return _cloudwatch


def emit_pending_financial_review(workspace_id: str, count: int = 1) -> None:
    """
    Emit a custom CloudWatch metric each time a job enters pending_financial_review.
    Call this from agent_executor.py after setting job.status = 'pending_financial_review'.

    The alarm fires when count > 0 within any 1-minute window.
    """
    try:
        _get_cw_client().put_metric_data(
            Namespace="Vantro/FinancialGovernance",
            MetricData=[
                {
                    "MetricName": "PendingFinancialReviewJobs",
                    "Dimensions": [
                        {"Name": "WorkspaceId", "Value": workspace_id},
                    ],
                    "Timestamp": datetime.now(tz=timezone.utc),
                    "Value": count,
                    "Unit": "Count",
                }
            ],
        )
    except Exception:
        # Never let monitoring failures propagate into the job pipeline
        pass
```

Call it in `agent_executor.py` (or wherever `pending_financial_review` is set):

```python
from app.services.monitoring_service import emit_pending_financial_review

# ... existing code that routes to pending_financial_review ...
job.status = "pending_financial_review"
db.commit()
emit_pending_financial_review(workspace_id=str(job.workspace_id))
```

> **IAM requirement:** The ECS task role for `vantro-backend` must have `cloudwatch:PutMetricData` permission on resource `*`. Add this to your task role policy if not already present:
> ```json
> {
>   "Effect": "Allow",
>   "Action": "cloudwatch:PutMetricData",
>   "Resource": "*",
>   "Condition": {
>     "StringEquals": { "cloudwatch:namespace": "Vantro/FinancialGovernance" }
>   }
> }
> ```

### Step 9b: Create the Alarm

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "vantro-pending-financial-review" \
  --alarm-description "One or more agent jobs entered pending_financial_review — admin action required" \
  --namespace "Vantro/FinancialGovernance" \
  --metric-name "PendingFinancialReviewJobs" \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 0 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

> No `--ok-actions` here intentionally — "ok" means no new financial-review jobs in the last minute, which is normal and not worth a notification. The alarm fires immediately (1-minute period, 1 evaluation) because financial governance breaches are zero-latency concerns.

---

## Verification

After running all commands, confirm alarms exist:

```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix "vantro-" \
  --query 'MetricAlarms[*].{Name:AlarmName,State:StateValue,Threshold:Threshold}' \
  --output table \
  --region us-east-1
```

To force-test an alarm (set it to ALARM state manually):

```bash
aws cloudwatch set-alarm-state \
  --alarm-name "vantro-pending-financial-review" \
  --state-value ALARM \
  --state-reason "Manual test" \
  --region us-east-1
```

You should receive an email at mark.salman76@gmail.com within 1–2 minutes. Reset it afterward:

```bash
aws cloudwatch set-alarm-state \
  --alarm-name "vantro-pending-financial-review" \
  --state-value OK \
  --state-reason "Test complete" \
  --region us-east-1
```

---

## Alarm Summary

| # | Alarm Name | Namespace | Trigger |
|---|-----------|-----------|---------|
| 1 | `vantro-backend-cpu-high` | AWS/ECS | CPU > 80% × 2 periods |
| 2 | `vantro-backend-memory-high` | AWS/ECS | Memory > 85% |
| 3 | `vantro-db-cpu-high` | AWS/RDS | CPU > 70% × 2 periods |
| 4 | `vantro-db-connections-high` | AWS/RDS | Connections > 48 |
| 5 | `vantro-alb-5xx-rate-high` | AWS/ApplicationELB (math) | 5xx rate > 1% |
| 6 | `vantro-sqs-message-age-high` | AWS/SQS | Oldest message > 300s |
| 7 | `vantro-sqs-inflight-high` | AWS/SQS | In-flight > 50 |
| 8 | `vantro-backend-error-log-rate` | Vantro/Application | Log errors > 10/5min |
| 9 | `vantro-pending-financial-review` | Vantro/FinancialGovernance | Any financial review job |
